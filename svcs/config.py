import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

@dataclass
class Config:
    username: str = "default_user"
    ignored: List[str] = field(default_factory=lambda: [".svcs", "*.pyc", "__pycache__"])

def read_config(svcs_dir: Path) -> Config:
    config_path = svcs_dir / "config.txt"
    if not config_path.exists():
        return Config()
        
    username = "default_user"
    ignored = []
    
    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if key == "username":
                    username = value
                elif key == "ignore":
                    ignored.append(value)
                    
    return Config(username=username, ignored=ignored)

def write_config(svcs_dir: Path, config: Config) -> None:
    config_path = svcs_dir / "config.txt"
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(f"username={config.username}\n")
        for ig in config.ignored:
            f.write(f"ignore={ig}\n")
