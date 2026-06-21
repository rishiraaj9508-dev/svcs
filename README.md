# SVCS — Simplified Version Control System

A lightweight local version control system with a Streamlit web UI.

![palette](https://img.shields.io/badge/050505-black?style=flat&color=050505)
![palette](https://img.shields.io/badge/004FFF-blue?style=flat&color=004FFF)
![palette](https://img.shields.io/badge/31AFD4-teal?style=flat&color=31AFD4)
![palette](https://img.shields.io/badge/902D41-rose?style=flat&color=902D41)
![palette](https://img.shields.io/badge/FF007F-pink?style=flat&color=FF007F)

---

## Requirements

- Python 3.10+
- Streamlit

```bash
pip install streamlit
```

---

## Run

```bash
python main.py
```

Or directly:

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## Workflow

| Step | Page | What to do |
|------|------|------------|
| 1 | Sidebar | Paste your project folder path |
| 2 | Dashboard | Click **Initialize Project** (first time only) |
| 3 | Stage Files | Enter `.` to stage everything, or a specific path |
| 4 | Commit | Write a message and create a version snapshot |
| 5 | History | Browse all versions in a table |
| 6 | Diff | Pick two versions and see color-coded line diffs |
| 7 | Restore | Roll back to any previous version |
| 8 | Settings | Change username and ignore patterns |

---

## Project Structure

```
app.py               # Streamlit UI (replaces gui.py)
main.py              # Entry point — launches streamlit run
svcs/
├── core.py          # Init, stage, commit, restore, diff logic
├── config.py        # Username + ignore patterns
├── index.py         # Staging area (index.txt)
├── hasher.py        # SHA-256 file hashing
├── diff_engine.py   # Unified diff
├── exceptions.py    # Custom exception types
└── __init__.py
```

---

## `.svcs` Layout

```
.svcs/
├── config.txt
├── index.txt
└── versions/
    ├── v1/
    │   ├── history.txt
    │   └── <staged files>
    └── v2/ ...
```

---

## Notes

- Restoring overwrites all current files — commit first if needed
- Hard links are used across versions to deduplicate identical files
- Binary files are stored as-is; diff shows a placeholder for them
