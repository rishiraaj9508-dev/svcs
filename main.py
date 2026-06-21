import sys
import subprocess
from pathlib import Path

if __name__ == "__main__":
    app = Path(__file__).parent / "app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app)], check=True)
