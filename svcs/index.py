import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass
class IndexEntry:
    rel_path: str
    sha256: str

def read_index(svcs_dir: Path) -> List[IndexEntry]:
    index_path = svcs_dir / "index.txt"
    if not index_path.exists():
        return []
    
    entries = []
    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) == 2:
                entries.append(IndexEntry(rel_path=parts[0], sha256=parts[1]))
    return entries

def write_index(svcs_dir: Path, entries: List[IndexEntry]) -> None:
    index_path = svcs_dir / "index.txt"
    with open(index_path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(f"{entry.rel_path}\t{entry.sha256}\n")
