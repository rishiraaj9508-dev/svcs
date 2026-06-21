from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from pathlib import Path
from datetime import datetime

from .core import (
    initialize_project, add_item, create_version, list_versions,
    restore_version, show_diff, wait_for_svcs
)
from .config import read_config, write_config, Config
from .index import read_index
from .exceptions import SVCSError

# ── Colour palette ────────────────────────────────────────────────────────────
DARK_BG   = "#1e1e2e"
PANEL_BG  = "#2a2a3e"
ACCENT    = "#7c6af7"
ACCENT2   = "#56cfb2"
BTN_BG    = "#3a3a55"
BTN_HOVER = "#4e4e70"
TEXT_FG   = "#cdd6f4"
DIM_FG    = "#6c7086"
GREEN_FG  = "#a6e3a1"
RED_FG    = "#f38ba8"
YELLOW_FG = "#f9e2af"
BLUE_FG   = "#89b4fa"
FONT_MONO = ("Cascadia Code", 10) if True else ("Consolas", 10)
FONT_UI   = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")


class HoverButton(tk.Button):
    """Flat button with hover highlight."""
    def __init__(self, master, **kw):
        kw.setdefault("relief", tk.FLAT)
        kw.setdefault("bg", BTN_BG)
        kw.setdefault("fg", TEXT_FG)
        kw.setdefault("activebackground", BTN_HOVER)
        kw.setdefault("activeforeground", TEXT_FG)
        kw.setdefault("cursor", "hand2")
        kw.setdefault("padx", 10)
        kw.setdefault("pady", 6)
        kw.setdefault("font", FONT_UI)
        kw.setdefault("bd", 0)
        super().__init__(master, **kw)
        self.bind("<Enter>", lambda _: self.config(bg=BTN_HOVER))
        self.bind("<Leave>", lambda _: self.config(bg=BTN_BG))


class SVCSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SVCS — Simplified Version Control System")
        self.geometry("1100x680")
        self.minsize(800, 500)
        self.configure(bg=DARK_BG)
        self.current_dir: Path | None = None
        self._setup_styles()
        self._build_ui()

    # ── Styles ────────────────────────────────────────────────────────────────
    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background=DARK_BG, foreground=TEXT_FG, font=FONT_UI)
        style.configure("TFrame", background=DARK_BG)
        style.configure("Panel.TFrame", background=PANEL_BG)
        style.configure("TLabel", background=DARK_BG, foreground=TEXT_FG, font=FONT_UI)
        style.configure("Dim.TLabel", background=DARK_BG, foreground=DIM_FG, font=FONT_UI)
        style.configure("Title.TLabel", background=DARK_BG, foreground=ACCENT,
                        font=("Segoe UI", 14, "bold"))
        style.configure("Status.TLabel", background=PANEL_BG, foreground=DIM_FG,
                        font=("Segoe UI", 8))
        style.configure("TSeparator", background=ACCENT)
        style.configure("Vertical.TScrollbar", background=BTN_BG, troughcolor=DARK_BG,
                        arrowcolor=TEXT_FG, bordercolor=DARK_BG)
        style.configure("Horizontal.TScrollbar", background=BTN_BG, troughcolor=DARK_BG,
                        arrowcolor=TEXT_FG, bordercolor=DARK_BG)

    # ── UI Construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Header bar ──
        header = tk.Frame(self, bg=PANEL_BG, height=48)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="⬡  SVCS", bg=PANEL_BG, fg=ACCENT,
                 font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT, padx=14, pady=10)

        self._dir_label = tk.Label(header, text="No project selected",
                                   bg=PANEL_BG, fg=DIM_FG, font=FONT_UI)
        self._dir_label.pack(side=tk.LEFT, padx=4)

        HoverButton(header, text="⊕  Open Project",
                    command=self._select_directory,
                    bg=ACCENT, fg="#ffffff",
                    activebackground="#6355d4").pack(side=tk.RIGHT, padx=12, pady=8)

        # ── Body ──
        body = tk.Frame(self, bg=DARK_BG)
        body.pack(fill=tk.BOTH, expand=True)

        # Left sidebar
        self._sidebar = tk.Frame(body, bg=PANEL_BG, width=200)
        self._sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self._sidebar.pack_propagate(False)
        self._build_sidebar()

        # Right area: tabs
        right = tk.Frame(body, bg=DARK_BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._build_right(right)

        # ── Status bar ──
        self._status_bar = tk.Frame(self, bg=PANEL_BG, height=24)
        self._status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self._status_bar.pack_propagate(False)
        self._status_var = tk.StringVar(value="Ready")
        tk.Label(self._status_bar, textvariable=self._status_var,
                 bg=PANEL_BG, fg=DIM_FG, font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=10)
        self._user_label = tk.Label(self._status_bar, text="",
                                    bg=PANEL_BG, fg=ACCENT2, font=("Segoe UI", 8))
        self._user_label.pack(side=tk.RIGHT, padx=10)

    def _build_sidebar(self):
        tk.Label(self._sidebar, text="ACTIONS", bg=PANEL_BG, fg=DIM_FG,
                 font=("Segoe UI", 8, "bold")).pack(anchor=tk.W, padx=14, pady=(14, 4))

        groups = [
            ("Project", [
                ("⬡  Initialize", self._do_initialize),
                ("⚙  Settings",   self._do_settings),
            ]),
            ("Staging", [
                ("＋  Stage Files", self._do_add),
                ("●  View Staged", self._do_view_staged),
            ]),
            ("Versions", [
                ("✔  Commit",       self._do_commit),
                ("≡  List Versions", self._do_list),
                ("↺  Restore",      self._do_restore),
                ("⇄  Diff",         self._do_diff),
            ]),
        ]

        for group_name, btns in groups:
            sep = tk.Frame(self._sidebar, bg=DIM_FG, height=1)
            sep.pack(fill=tk.X, padx=10, pady=(10, 2))
            tk.Label(self._sidebar, text=group_name.upper(), bg=PANEL_BG,
                     fg=DIM_FG, font=("Segoe UI", 7, "bold")).pack(anchor=tk.W, padx=14, pady=(2, 2))
            for label, cmd in btns:
                HoverButton(self._sidebar, text=label, command=cmd,
                            anchor=tk.W).pack(fill=tk.X, padx=8, pady=2)

        # Clear button at bottom
        tk.Frame(self._sidebar, bg=PANEL_BG).pack(fill=tk.Y, expand=True)
        HoverButton(self._sidebar, text="✕  Clear Output", command=self._clear_output,
                    fg=DIM_FG).pack(fill=tk.X, padx=8, pady=(0, 12))

    def _build_right(self, parent):
        # Tab strip
        self._notebook = ttk.Notebook(parent)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Output tab
        out_frame = tk.Frame(self._notebook, bg=DARK_BG)
        self._notebook.add(out_frame, text="  Output  ")
        self._out_text = self._make_text(out_frame)

        # Diff tab
        diff_frame = tk.Frame(self._notebook, bg=DARK_BG)
        self._notebook.add(diff_frame, text="  Diff  ")
        self._diff_text = self._make_text(diff_frame)

        # Staged tab
        staged_frame = tk.Frame(self._notebook, bg=DARK_BG)
        self._notebook.add(staged_frame, text="  Staged Files  ")
        self._staged_text = self._make_text(staged_frame)

        # Configure diff colour tags
        self._diff_text.tag_configure("add",    foreground=GREEN_FG)
        self._diff_text.tag_configure("remove", foreground=RED_FG)
        self._diff_text.tag_configure("header", foreground=BLUE_FG, font=("Consolas", 10, "bold"))
        self._diff_text.tag_configure("meta",   foreground=YELLOW_FG)
        self._diff_text.tag_configure("same",   foreground=DIM_FG)

        # Output colour tags
        for widget in (self._out_text, self._staged_text):
            widget.tag_configure("info",    foreground=ACCENT2)
            widget.tag_configure("success", foreground=GREEN_FG)
            widget.tag_configure("error",   foreground=RED_FG)
            widget.tag_configure("warn",    foreground=YELLOW_FG)
            widget.tag_configure("dim",     foreground=DIM_FG)
            widget.tag_configure("bold",    foreground=TEXT_FG, font=("Consolas", 10, "bold"))

    def _make_text(self, parent) -> tk.Text:
        frame = tk.Frame(parent, bg=DARK_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        text = tk.Text(frame, state=tk.DISABLED, wrap=tk.NONE,
                       font=("Consolas", 10),
                       bg=DARK_BG, fg=TEXT_FG,
                       insertbackground=TEXT_FG,
                       selectbackground=ACCENT,
                       relief=tk.FLAT, bd=0, padx=10, pady=8)

        sy = ttk.Scrollbar(frame, orient=tk.VERTICAL,   command=text.yview)
        sx = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=text.xview)
        text.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)

        sy.pack(side=tk.RIGHT,  fill=tk.Y)
        sx.pack(side=tk.BOTTOM, fill=tk.X)
        text.pack(fill=tk.BOTH, expand=True)
        return text

    # ── Logging helpers ───────────────────────────────────────────────────────
    def _ts(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def _log(self, message: str, tag: str = "", widget: tk.Text = None):
        target = widget or self._out_text
        target.config(state=tk.NORMAL)
        target.insert(tk.END, f"[{self._ts()}] ", "dim")
        if tag:
            target.insert(tk.END, message + "\n", tag)
        else:
            target.insert(tk.END, message + "\n")
        target.see(tk.END)
        target.config(state=tk.DISABLED)
        self._status_var.set(message[:100])

    def _log_section(self, title: str, widget: tk.Text = None):
        target = widget or self._out_text
        target.config(state=tk.NORMAL)
        target.insert(tk.END, f"\n{'─' * 60}\n", "dim")
        target.insert(tk.END, f"  {title}\n", "bold")
        target.insert(tk.END, f"{'─' * 60}\n", "dim")
        target.see(tk.END)
        target.config(state=tk.DISABLED)

    def _clear_output(self):
        for widget in (self._out_text, self._diff_text, self._staged_text):
            widget.config(state=tk.NORMAL)
            widget.delete("1.0", tk.END)
            widget.config(state=tk.DISABLED)

    def _set_status(self, msg: str):
        self._status_var.set(msg)

    # ── Directory / project helpers ───────────────────────────────────────────
    def _select_directory(self):
        d = filedialog.askdirectory(title="Select Project Directory")
        if d:
            self.current_dir = Path(d)
            short = self.current_dir.name
            self._dir_label.config(text=f"📁  {short}", fg=ACCENT2)
            self._log(f"Opened project: {self.current_dir}", "info")
            self._refresh_user_label()

    def _refresh_user_label(self):
        if not self.current_dir:
            return
        try:
            svcs_dir = wait_for_svcs(self.current_dir)
            cfg = read_config(svcs_dir)
            self._user_label.config(text=f"👤  {cfg.username}")
        except Exception:
            self._user_label.config(text="")

    def _check_dir(self) -> bool:
        if not self.current_dir:
            messagebox.showwarning("No Project", "Open a project directory first.")
            return False
        return True

    def _handle_error(self, exc: Exception):
        if isinstance(exc, SVCSError):
            self._log(f"Error: {exc}", "error")
            messagebox.showerror("SVCS Error", str(exc))
        else:
            self._log(f"Unexpected error: {exc}", "error")
            messagebox.showerror("Error", str(exc))

    # ── Action handlers ───────────────────────────────────────────────────────
    def _do_initialize(self):
        if not self._check_dir():
            return
        try:
            initialize_project(self.current_dir)
            self._log("Project initialized — .svcs directory created.", "success")
            messagebox.showinfo("Initialized", "Project initialized successfully.")
            self._refresh_user_label()
        except Exception as e:
            self._handle_error(e)

    def _do_settings(self):
        if not self._check_dir():
            return
        try:
            svcs_dir = wait_for_svcs(self.current_dir)
            cfg = read_config(svcs_dir)
        except Exception as e:
            self._handle_error(e)
            return

        win = tk.Toplevel(self)
        win.title("Project Settings")
        win.geometry("400x220")
        win.configure(bg=DARK_BG)
        win.resizable(False, False)

        tk.Label(win, text="Username", bg=DARK_BG, fg=TEXT_FG, font=FONT_BOLD).grid(
            row=0, column=0, padx=16, pady=(20, 6), sticky=tk.W)
        user_var = tk.StringVar(value=cfg.username)
        tk.Entry(win, textvariable=user_var, bg=BTN_BG, fg=TEXT_FG,
                 insertbackground=TEXT_FG, relief=tk.FLAT, font=FONT_UI,
                 width=30).grid(row=0, column=1, padx=16, pady=(20, 6))

        tk.Label(win, text="Ignored patterns\n(one per line)", bg=DARK_BG,
                 fg=TEXT_FG, font=FONT_BOLD).grid(row=1, column=0, padx=16, pady=6, sticky=tk.NW)
        ig_text = tk.Text(win, bg=BTN_BG, fg=TEXT_FG, insertbackground=TEXT_FG,
                          relief=tk.FLAT, font=("Consolas", 9), width=30, height=4)
        ig_text.insert(tk.END, "\n".join(cfg.ignored))
        ig_text.grid(row=1, column=1, padx=16, pady=6)

        def _save():
            cfg.username = user_var.get().strip() or "default_user"
            cfg.ignored = [l.strip() for l in ig_text.get("1.0", tk.END).splitlines() if l.strip()]
            write_config(svcs_dir, cfg)
            self._log(f"Settings saved. Username: {cfg.username}", "success")
            self._refresh_user_label()
            win.destroy()

        HoverButton(win, text="Save", command=_save, bg=ACCENT, fg="#fff",
                    activebackground="#6355d4").grid(row=2, column=1, sticky=tk.E,
                                                      padx=16, pady=12)

    def _do_add(self):
        if not self._check_dir():
            return
        target = simpledialog.askstring(
            "Stage Files",
            "Enter relative path to file/folder\nor '.' to stage everything:",
            parent=self
        )
        if target is not None:
            try:
                add_item(self.current_dir, target)
                self._log(f"Staged: {target}", "success")
                self._do_view_staged()
                self._notebook.select(2)  # Switch to Staged tab
            except Exception as e:
                self._handle_error(e)

    def _do_view_staged(self):
        if not self._check_dir():
            return
        try:
            svcs_dir = wait_for_svcs(self.current_dir)
            entries = read_index(svcs_dir)
        except Exception as e:
            self._handle_error(e)
            return

        w = self._staged_text
        w.config(state=tk.NORMAL)
        w.delete("1.0", tk.END)

        if not entries:
            w.insert(tk.END, "\n  No files staged yet.\n", "dim")
        else:
            w.insert(tk.END, f"\n  {len(entries)} file(s) in staging area\n\n", "info")
            for entry in entries:
                w.insert(tk.END, f"  ●  {entry.rel_path}\n", "success")
                w.insert(tk.END, f"      sha256: {entry.sha256[:16]}...\n", "dim")

        w.config(state=tk.DISABLED)
        self._notebook.select(2)

    def _do_commit(self):
        if not self._check_dir():
            return
        msg = simpledialog.askstring("Commit", "Enter commit message:", parent=self)
        if msg:
            try:
                v = create_version(self.current_dir, msg)
                self._log(f"Version {v} created: {msg}", "success")
                messagebox.showinfo("Committed", f"Version {v} created.")
            except Exception as e:
                self._handle_error(e)

    def _do_list(self):
        if not self._check_dir():
            return
        try:
            versions = list_versions(self.current_dir)
        except Exception as e:
            self._handle_error(e)
            return

        self._log_section(f"Version History — {self.current_dir.name}")
        if not versions:
            self._log("No versions yet.", "warn")
            return
        for v in versions:
            ts = v.timestamp[:19].replace("T", " ")
            self._log(f"v{v.number:<4} {ts}  {v.username:<16} {v.message}", "info")
        self._notebook.select(0)

    def _do_restore(self):
        if not self._check_dir():
            return
        v_str = simpledialog.askstring("Restore Version", "Version number to restore:", parent=self)
        if not v_str:
            return
        try:
            v_num = int(v_str)
        except ValueError:
            messagebox.showerror("Error", "Enter a valid integer.")
            return
        if messagebox.askyesno("Confirm Restore",
                               f"Restore v{v_num}? All uncommitted changes will be lost.",
                               icon="warning"):
            try:
                restore_version(self.current_dir, v_num)
                self._log(f"Restored to version {v_num}.", "success")
                messagebox.showinfo("Restored", f"Project restored to v{v_num}.")
            except Exception as e:
                self._handle_error(e)

    def _do_diff(self):
        if not self._check_dir():
            return
        diff_str = simpledialog.askstring(
            "Diff Versions", "Enter two version numbers (e.g. '1 2'):", parent=self)
        if not diff_str:
            return
        parts = diff_str.strip().split()
        if len(parts) != 2:
            messagebox.showerror("Error", "Enter exactly two version numbers.")
            return
        try:
            v1, v2 = int(parts[0]), int(parts[1])
        except ValueError:
            messagebox.showerror("Error", "Versions must be integers.")
            return
        try:
            diffs = show_diff(self.current_dir, v1, v2)
        except Exception as e:
            self._handle_error(e)
            return

        w = self._diff_text
        w.config(state=tk.NORMAL)
        w.delete("1.0", tk.END)

        w.insert(tk.END, f"  Diff  v{v1}  →  v{v2}\n", "header")
        w.insert(tk.END, f"  {'─' * 56}\n\n", "dim")

        if not diffs:
            w.insert(tk.END, "  No differences found.\n", "dim")
        else:
            for file_diff in diffs:
                w.insert(tk.END, f"  ⊞  {file_diff.rel_path}\n", "meta")
                for line in file_diff.lines:
                    if line.startswith("+++") or line.startswith("---"):
                        w.insert(tk.END, line + "\n", "header")
                    elif line.startswith("@@"):
                        w.insert(tk.END, line + "\n", "meta")
                    elif line.startswith("+"):
                        w.insert(tk.END, line + "\n", "add")
                    elif line.startswith("-"):
                        w.insert(tk.END, line + "\n", "remove")
                    else:
                        w.insert(tk.END, line + "\n", "same")
                w.insert(tk.END, "\n")

        w.config(state=tk.DISABLED)
        self._notebook.select(1)  # Switch to Diff tab


def run_app():
    app = SVCSApp()
    app.mainloop()
