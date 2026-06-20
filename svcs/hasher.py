import hashlib
from pathlib import Path

def sha256_file(path: Path) -> str:
    """Return hex-encoded SHA-256 digest of file at path."""
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        # Read in chunks to avoid blowing up memory on large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
