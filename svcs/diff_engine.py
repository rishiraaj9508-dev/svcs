import difflib
from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass
class FileDiff:
    rel_path: str
    lines: List[str]  # prefixed with '+', '-', or ' '

def compute_diff(path_a: Path, path_b: Path, rel_path: str) -> FileDiff:
    def read_file(p: Path) -> List[str]:
        if p.exists() and p.is_file():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return f.read().splitlines(keepends=False)
            except UnicodeDecodeError:
                return ["<Binary file or encoding issue>"]
        return []

    lines_a = read_file(path_a)
    lines_b = read_file(path_b)
    
    diff_generator = difflib.unified_diff(
        lines_a, lines_b,
        fromfile=rel_path + " (Version A)",
        tofile=rel_path + " (Version B)",
        lineterm=""
    )
    
    diff_lines = list(diff_generator)
    
    # Strip the header of unified_diff (---, +++, @@ .. @@) if we just want basic lines,
    # or keep it. We'll keep it but ensure '+' '-' ' ' structure.
    return FileDiff(rel_path=rel_path, lines=diff_lines)
