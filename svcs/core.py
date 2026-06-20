import os
import shutil
import fnmatch
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

from .exceptions import *
from .hasher import sha256_file
from .config import read_config, write_config, Config
from .index import read_index, write_index, IndexEntry
from .diff_engine import compute_diff, FileDiff

@dataclass
class VersionInfo:
    number: int
    message: str
    timestamp: str
    username: str
    files: Dict[str, str]

def wait_for_svcs(project_dir: Path) -> Path:
    svcs_dir = project_dir / ".svcs"
    if not svcs_dir.exists():
        raise NotInitializedError("Project not initialized. Run 'Initialize' first.")
    return svcs_dir

def initialize_project(project_dir: Path) -> None:
    svcs_dir = project_dir / ".svcs"
    if svcs_dir.exists():
        raise AlreadyInitializedError("Project already initialized.")
    
    # Create structure
    svcs_dir.mkdir(parents=True)
    (svcs_dir / "versions").mkdir()
    
    # Create empty index and config
    write_index(svcs_dir, [])
    write_config(svcs_dir, Config())

def _is_ignored(rel_path: str, config: Config) -> bool:
    for pattern in config.ignored:
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(Path(rel_path).name, pattern):
            return True
    return False

def add_item(project_dir: Path, item_path: str) -> None:
    svcs_dir = wait_for_svcs(project_dir)
    config = read_config(svcs_dir)
    
    target_path = project_dir / item_path
    
    if not target_path.exists():
        raise FileNotFoundInProjectError(f"File not found: {item_path}")
        
    entries = {e.rel_path: e for e in read_index(svcs_dir)}
    
    def process_file(p: Path):
        rel_p = p.relative_to(project_dir).as_posix()
        if not _is_ignored(rel_p, config):
            file_hash = sha256_file(p)
            entries[rel_p] = IndexEntry(rel_path=rel_p, sha256=file_hash)

    if target_path.is_file():
        process_file(target_path)
    elif target_path.is_dir():
        for root, dirs, files in os.walk(target_path):
            # remove ignored dirs to stop traversing
            dirs[:] = [d for d in dirs if not _is_ignored((Path(root) / d).relative_to(project_dir).as_posix(), config)]
            for file in files:
                fpath = Path(root) / file
                process_file(fpath)
                
    write_index(svcs_dir, list(entries.values()))

def create_version(project_dir: Path, commit_message: str) -> int:
    svcs_dir = wait_for_svcs(project_dir)
    if not commit_message.strip():
        raise EmptyCommitMessageError("Commit message cannot be empty.")
        
    entries = read_index(svcs_dir)
    if not entries:
        raise EmptyIndexError("Nothing staged. Use 'Add item' first.")
        
    versions_dir = svcs_dir / "versions"
    existing_versions = []
    for d in versions_dir.iterdir():
        if d.is_dir() and d.name.startswith("v"):
            try:
                existing_versions.append(int(d.name[1:]))
            except ValueError:
                pass
                
    next_version = max(existing_versions, default=0) + 1
    new_v_dir = versions_dir / f"v{next_version}"
    new_v_dir.mkdir(parents=True)
    
    # Store files using hard links if possible
    # We look for the same hash in previous versions
    hash_to_path = {}
    for ver in range(1, next_version):
        v_dir = versions_dir / f"v{ver}"
        hist_path = v_dir / "history.txt"
        if hist_path.exists():
            with open(hist_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("file="):
                        _, val = line.split("=", 1)
                        rpath, h = val.strip().split("\t")
                        if h not in hash_to_path:
                            hash_to_path[h] = v_dir / rpath
    
    # Copy/link staged files
    for entry in entries:
        src_path = project_dir / entry.rel_path
        dest_path = new_v_dir / entry.rel_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        if entry.sha256 in hash_to_path and hash_to_path[entry.sha256].exists():
            try:
                os.link(hash_to_path[entry.sha256], dest_path)
            except OSError:
                shutil.copy2(src_path, dest_path)
        else:
            shutil.copy2(src_path, dest_path)
            
    # Write history.txt
    config = read_config(svcs_dir)
    hist_path = new_v_dir / "history.txt"
    timestamp = datetime.now().isoformat()
    with open(hist_path, "w", encoding="utf-8") as f:
        f.write(f"version={next_version}\n")
        f.write(f"message={commit_message}\n")
        f.write(f"timestamp={timestamp}\n")
        f.write(f"username={config.username}\n")
        for entry in entries:
            f.write(f"file={entry.rel_path}\t{entry.sha256}\n")
            
    return next_version

def _read_history(v_dir: Path) -> VersionInfo:
    hist_path = v_dir / "history.txt"
    info = {"version": 0, "message": "", "timestamp": "", "username": "", "files": {}}
    if hist_path.exists():
        with open(hist_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    if k == "file":
                        rp, h = v.split("\t")
                        info["files"][rp] = h
                    elif k == "version":
                        info["version"] = int(v)
                    else:
                        info[k] = v
    return VersionInfo(
        number=info["version"],
        message=info["message"],
        timestamp=info["timestamp"],
        username=info["username"],
        files=info["files"]
    )

def list_versions(project_dir: Path) -> List[VersionInfo]:
    svcs_dir = wait_for_svcs(project_dir)
    versions_dir = svcs_dir / "versions"
    
    versions = []
    for d in versions_dir.iterdir():
        if d.is_dir() and d.name.startswith("v"):
            versions.append(_read_history(d))
            
    versions.sort(key=lambda x: x.number)
    return versions

def restore_version(project_dir: Path, version: int) -> None:
    svcs_dir = wait_for_svcs(project_dir)
    v_dir = svcs_dir / "versions" / f"v{version}"
    if not v_dir.exists():
        raise InvalidVersionError(f"Version {version} does not exist.")
        
    # Clear user files
    for item in project_dir.iterdir():
        if item.name == ".svcs":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
            
    # Copy from version
    v_info = _read_history(v_dir)
    for rel_path in v_info.files.keys():
        src = v_dir / rel_path
        dest = project_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        
    # Overwrite the index state to match the restored version
    # So the staging area matches exactly what was restored
    entries = [IndexEntry(rel_path=rp, sha256=h) for rp, h in v_info.files.items()]
    write_index(svcs_dir, entries)

def show_diff(project_dir: Path, v1: int, v2: int) -> List[FileDiff]:
    svcs_dir = wait_for_svcs(project_dir)
    dir_v1 = svcs_dir / "versions" / f"v{v1}"
    dir_v2 = svcs_dir / "versions" / f"v{v2}"
    
    if not dir_v1.exists():
        raise InvalidVersionError(f"Version {v1} does not exist.")
    if not dir_v2.exists():
        raise InvalidVersionError(f"Version {v2} does not exist.")
        
    hist1 = _read_history(dir_v1)
    hist2 = _read_history(dir_v2)
    
    all_files = set(hist1.files.keys()).union(set(hist2.files.keys()))
    diffs = []
    
    for rp in sorted(all_files):
        h1 = hist1.files.get(rp)
        h2 = hist2.files.get(rp)
        
        # If hash is same, no line diff
        if h1 == h2:
            continue
            
        p1 = dir_v1 / rp if h1 else Path("NUL")  # Doesn't exist placeholder
        p2 = dir_v2 / rp if h2 else Path("NUL")
        
        diff = compute_diff(p1, p2, rp)
        if diff.lines:
            diffs.append(diff)
            
    return diffs
