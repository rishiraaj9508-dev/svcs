import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from pathlib import Path

from .core import (
    initialize_project, add_item, create_version, list_versions, 
    restore_version, show_diff
)
from .exceptions import SVCSError, InvalidVersionError

class SVCSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simplified Version Control System (SVCS)")
        self.geometry("900x600")
        self.current_dir = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Top Frame for Directory Selection
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Active Project:").pack(side=tk.LEFT)
        self.dir_var = tk.StringVar(value="No directory selected")
        ttk.Label(top_frame, textvariable=self.dir_var, font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=10)
        ttk.Button(top_frame, text="Select Directory", command=self.select_directory).pack(side=tk.RIGHT)
        
        # Main Layout: Sidebar for actions, Text for output
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sidebar
        sidebar = ttk.Frame(main_pane, width=200)
        main_pane.add(sidebar, weight=0)
        
        actions = [
            ("Initialize Project", self.do_initialize),
            ("Add Item / Stage Files", self.do_add),
            ("Create Version (Commit)", self.do_commit),
            ("List Versions", self.do_list),
            ("Restore Version", self.do_restore),
            ("Show Diff", self.do_diff),
            ("Clear Screen", self.clear_screen)
        ]
        
        for text, cmd in actions:
            btn = ttk.Button(sidebar, text=text, command=cmd)
            btn.pack(fill=tk.X, pady=5)
            
        # Text Output Area
        output_frame = ttk.Frame(main_pane)
        main_pane.add(output_frame, weight=1)
        
        self.out_text = tk.Text(output_frame, state=tk.DISABLED, wrap=tk.NONE, font=("Consolas", 10))
        scroll_y = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.out_text.yview)
        scroll_x = ttk.Scrollbar(output_frame, orient=tk.HORIZONTAL, command=self.out_text.xview)
        self.out_text.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.out_text.pack(fill=tk.BOTH, expand=True)

    def log(self, message: str):
        self.out_text.config(state=tk.NORMAL)
        self.out_text.insert(tk.END, message + "\n")
        self.out_text.see(tk.END)
        self.out_text.config(state=tk.DISABLED)
        
    def clear_screen(self):
        self.out_text.config(state=tk.NORMAL)
        self.out_text.delete(1.0, tk.END)
        self.out_text.config(state=tk.DISABLED)

    def select_directory(self):
        d = filedialog.askdirectory(title="Select Project Directory")
        if d:
            self.current_dir = Path(d)
            self.dir_var.set(str(self.current_dir))
            self.log(f"[*] Switched to project directory: {self.current_dir}")
            
    def _check_dir(self) -> bool:
        if not self.current_dir:
            messagebox.showwarning("Warning", "Please select a directory first.")
            return False
        return True
        
    def handle_error(self, exc: Exception):
        if isinstance(exc, SVCSError):
            messagebox.showerror("SVCS Error", str(exc))
            self.log(f"[ERROR] {exc}")
        else:
            messagebox.showerror("System Error", str(exc))
            self.log(f"[CRITICAL] {exc}")

    def do_initialize(self):
        if not self._check_dir(): return
        try:
            initialize_project(self.current_dir)
            self.log("[+] Project initialized successfully .svcs directory created.")
            messagebox.showinfo("Success", "Project Initialized!")
        except Exception as e:
            self.handle_error(e)

    def do_add(self):
        if not self._check_dir(): return
        # Ask what to add, we can allow picking a file, dir, or '.'
        target = simpledialog.askstring("Add Item", "Enter relative path to file/folder or '.' for all:")
        if target is not None:
            try:
                add_item(self.current_dir, target)
                self.log(f"[+] Added '{target}' to staging area.")
            except Exception as e:
                self.handle_error(e)

    def do_commit(self):
        if not self._check_dir(): return
        msg = simpledialog.askstring("Commit", "Enter commit message:")
        if msg:
            try:
                v = create_version(self.current_dir, msg)
                self.log(f"[+] Created Version {v}: {msg}")
                messagebox.showinfo("Success", f"Version {v} created!")
            except Exception as e:
                self.handle_error(e)

    def do_list(self):
        if not self._check_dir(): return
        self.log(f"\n--- Versions in {self.current_dir.name} ---")
        try:
            versions = list_versions(self.current_dir)
            if not versions:
                self.log("No versions found.")
            for v in versions:
                self.log(f"v{v.number} | {v.timestamp} | {v.username} | {v.message}")
        except Exception as e:
            self.handle_error(e)

    def do_restore(self):
        if not self._check_dir(): return
        v_str = simpledialog.askstring("Restore", "Enter version number to restore:")
        if not v_str: return
        
        try:
            v_num = int(v_str)
        except ValueError:
            messagebox.showerror("Error", "Version must be an integer.")
            return
            
        if messagebox.askyesno("Confirm", f"This will overwrite all uncommitted files. Restore v{v_num}?"):
            try:
                restore_version(self.current_dir, v_num)
                self.log(f"[*] Restored to Version {v_num}.")
                messagebox.showinfo("Success", f"Project restored to version {v_num}!")
            except Exception as e:
                self.handle_error(e)

    def do_diff(self):
        if not self._check_dir(): return
        diff_str = simpledialog.askstring("Diff", "Enter two version numbers separated by space (e.g. '1 2'):")
        if not diff_str: return
        
        parts = diff_str.strip().split()
        if len(parts) != 2:
            messagebox.showerror("Error", "Please enter exactly two numbers.")
            return
            
        try:
            v1, v2 = int(parts[0]), int(parts[1])
        except ValueError:
            messagebox.showerror("Error", "Versions must be integers.")
            return
            
        try:
            diffs = show_diff(self.current_dir, v1, v2)
            self.log(f"\n--- Diff between v{v1} and v{v2} ---")
            if not diffs:
                self.log("No differences found.")
            else:
                for file_diff in diffs:
                    for line in file_diff.lines:
                        self.log(line)
        except Exception as e:
            self.handle_error(e)

def run_app():
    app = SVCSApp()
    app.mainloop()
