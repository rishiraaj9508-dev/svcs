import sys
from pathlib import Path

# Add the parent directory to sys.path so 'svcs' can be imported easily
sys.path.insert(0, str(Path(__file__).parent))

from svcs.gui import run_app

if __name__ == "__main__":
    run_app()
