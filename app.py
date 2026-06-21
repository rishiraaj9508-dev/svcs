from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from svcs.core import (
    initialize_project, add_item, create_version,
    list_versions, restore_version, show_diff, wait_for_svcs,
)
from svcs.config import read_config, write_config, Config
from svcs.index import read_index
from svcs.exceptions import SVCSError

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SVCS",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Palette: 050505 / 004FFF / 31AFD4 / 902D41 / FF007F ──────────────────────
st.markdown("""
<style>
/* ── Base ── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main { background:#050505 !important; }

[data-testid="stSidebar"] { background:#0a0a0a !important; border-right:1px solid #1a1a2e; }

/* ── Typography ── */
html, body, * { color:#e8eaf6; font-family:'Segoe UI',sans-serif; }
h1,h2,h3 { color:#004FFF !important; }

/* ── Sidebar nav items ── */
.nav-item {
    display:flex; align-items:center; gap:10px;
    padding:10px 14px; border-radius:8px; margin-bottom:4px;
    cursor:pointer; font-size:14px; font-weight:500;
    color:#9ea3c0; transition:background .15s,color .15s;
    border:1px solid transparent;
}
.nav-item:hover { background:#0d1117; color:#e8eaf6; border-color:#1a1a2e; }
.nav-item.active {
    background:linear-gradient(135deg,#004FFF22,#31AFD422);
    color:#31AFD4; border-color:#004FFF55;
}
.nav-icon { font-size:16px; width:20px; text-align:center; }

/* ── Cards ── */
.card {
    background:#0d0d1a; border:1px solid #1a1a2e; border-radius:12px;
    padding:20px 24px; margin-bottom:16px;
}
.card-accent { border-left:3px solid #004FFF; }

/* ── Metric tiles ── */
.metric-row { display:flex; gap:16px; margin-bottom:24px; }
.metric {
    flex:1; background:#0d0d1a; border:1px solid #1a1a2e;
    border-radius:10px; padding:16px 20px;
}
.metric-label { font-size:11px; color:#6c7086; text-transform:uppercase;
                letter-spacing:.08em; margin-bottom:6px; }
.metric-value { font-size:28px; font-weight:700; }
.metric-blue  { color:#004FFF; }
.metric-teal  { color:#31AFD4; }
.metric-rose  { color:#902D41; }
.metric-pink  { color:#FF007F; }

/* ── Version table rows ── */
.vtable { width:100%; border-collapse:collapse; }
.vtable th {
    background:#0d0d1a; color:#6c7086; font-size:11px;
    text-transform:uppercase; letter-spacing:.06em;
    padding:10px 14px; border-bottom:1px solid #1a1a2e; text-align:left;
}
.vtable td { padding:12px 14px; border-bottom:1px solid #0d0d1a; font-size:13px; }
.vtable tr:hover td { background:#0d0d1a55; }
.badge {
    display:inline-block; padding:3px 10px; border-radius:20px;
    font-size:11px; font-weight:600; letter-spacing:.04em;
}
.badge-blue  { background:#004FFF22; color:#004FFF; border:1px solid #004FFF55; }
.badge-teal  { background:#31AFD422; color:#31AFD4; border:1px solid #31AFD455; }
.badge-rose  { background:#902D4122; color:#c0405a; border:1px solid #902D4155; }

/* ── Diff ── */
.diff-add    { background:#00400022; color:#a6e3a1; font-family:monospace;
               padding:2px 8px; display:block; border-left:3px solid #a6e3a1; }
.diff-remove { background:#40000022; color:#FF007F; font-family:monospace;
               padding:2px 8px; display:block; border-left:3px solid #FF007F; }
.diff-hunk   { background:#004FFF11; color:#31AFD4; font-family:monospace;
               padding:2px 8px; display:block; border-left:3px solid #31AFD4; }
.diff-ctx    { color:#4a4a6a; font-family:monospace; padding:2px 8px; display:block; }
.diff-file   { background:#0d0d1a; color:#004FFF; font-family:monospace; font-weight:700;
               padding:6px 10px; display:block; border-radius:6px; margin:10px 0 4px; }

/* ── Staged file chips ── */
.file-chip {
    display:inline-flex; align-items:center; gap:6px;
    background:#004FFF11; border:1px solid #004FFF33;
    border-radius:6px; padding:4px 10px; margin:3px;
    font-size:12px; color:#31AFD4; font-family:monospace;
}

/* ── Streamlit widget overrides ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] select {
    background:#0d0d1a !important; border:1px solid #1a1a2e !important;
    color:#e8eaf6 !important; border-radius:8px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color:#004FFF !important; box-shadow:0 0 0 2px #004FFF33 !important;
}
.stButton > button {
    background:#004FFF !important; color:#fff !important;
    border:none !important; border-radius:8px !important;
    font-weight:600 !important; padding:8px 20px !important;
    transition:opacity .15s !important;
}
.stButton > button:hover { opacity:.85 !important; }
.stButton > button[kind="secondary"] {
    background:#0d0d1a !important; border:1px solid #1a1a2e !important;
    color:#9ea3c0 !important;
}

/* alert overrides */
[data-testid="stAlert"] { border-radius:10px !important; }

div[data-testid="stHorizontalBlock"] > div { gap:12px; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "page"    not in st.session_state: st.session_state.page    = "dashboard"
if "msg"     not in st.session_state: st.session_state.msg     = None   # (type, text)
if "proj"    not in st.session_state: st.session_state.proj    = ""

def set_page(p): st.session_state.page = p
def flash(kind, text): st.session_state.msg = (kind, text)

# ── Helpers ───────────────────────────────────────────────────────────────────
def proj_path() -> Path | None:
    p = st.session_state.proj.strip()
    return Path(p) if p else None

def is_initialized() -> bool:
    p = proj_path()
    return bool(p and (p / ".svcs").exists())

def _safe(fn, *args, **kwargs):
    """Run fn, flash error on exception, return None on failure."""
    try:
        return fn(*args, **kwargs)
    except SVCSError as e:
        flash("error", str(e))
        return None
    except Exception as e:
        flash("error", f"Unexpected error: {e}")
        return None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='padding:18px 4px 8px'>"
                "<span style='color:#004FFF;font-size:20px;font-weight:800;'>⬡ SVCS</span>"
                "<span style='color:#6c7086;font-size:12px;margin-left:8px;'>v1.0</span>"
                "</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Project input
    st.markdown("<p style='color:#6c7086;font-size:11px;text-transform:uppercase;"
                "letter-spacing:.06em;margin-bottom:4px;'>Project Path</p>",
                unsafe_allow_html=True)
    st.session_state.proj = st.text_input(
        "proj", value=st.session_state.proj,
        placeholder="C:/my/project",
        label_visibility="collapsed"
    )

    p = proj_path()
    if p:
        if is_initialized():
            st.markdown(f"<div style='color:#31AFD4;font-size:12px;margin-bottom:12px;'>"
                        f"✔ {p.name}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='color:#902D41;font-size:12px;margin-bottom:12px;'>"
                        f"✗ not initialized</div>", unsafe_allow_html=True)

    st.markdown("---")

    nav_items = [
        ("dashboard", "◈",  "Dashboard"),
        ("stage",     "+",  "Stage Files"),
        ("commit",    "✔",  "Commit"),
        ("history",   "≡",  "History"),
        ("diff",      "⇄",  "Diff"),
        ("restore",   "↺",  "Restore"),
        ("settings",  "⚙",  "Settings"),
    ]
    for key, icon, label in nav_items:
        active = "active" if st.session_state.page == key else ""
        if st.button(f"{icon}  {label}", key=f"nav_{key}",
                     use_container_width=True):
            set_page(key)
        # inject active style via custom class — use JS trick via empty placeholder
    st.markdown("---")

    # User badge
    if is_initialized():
        try:
            svcs_dir = wait_for_svcs(proj_path())
            cfg = read_config(svcs_dir)
            st.markdown(f"<div style='color:#6c7086;font-size:12px;'>👤 {cfg.username}</div>",
                        unsafe_allow_html=True)
        except Exception:
            pass

# ── Flash message ─────────────────────────────────────────────────────────────
if st.session_state.msg:
    kind, text = st.session_state.msg
    if kind == "success": st.success(text)
    elif kind == "error":  st.error(text)
    elif kind == "warn":   st.warning(text)
    else:                  st.info(text)
    st.session_state.msg = None

page = st.session_state.page

# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if page == "dashboard":
    st.markdown("## Dashboard")

    if not proj_path():
        st.markdown("""
        <div class='card card-accent'>
          <h3 style='color:#31AFD4;margin-top:0'>Get started</h3>
          <p style='color:#9ea3c0'>Enter your project path in the sidebar, then initialize or open an existing SVCS project.</p>
        </div>""", unsafe_allow_html=True)
    else:
        p = proj_path()
        initialized = is_initialized()

        # Metrics row
        n_versions, n_staged, username = 0, 0, "—"
        if initialized:
            try:
                svcs_dir = wait_for_svcs(p)
                n_versions = len(list_versions(p))
                n_staged   = len(read_index(svcs_dir))
                username   = read_config(svcs_dir).username
            except Exception:
                pass

        st.markdown(f"""
        <div class='metric-row'>
          <div class='metric'>
            <div class='metric-label'>Versions</div>
            <div class='metric-value metric-blue'>{n_versions}</div>
          </div>
          <div class='metric'>
            <div class='metric-label'>Staged Files</div>
            <div class='metric-value metric-teal'>{n_staged}</div>
          </div>
          <div class='metric'>
            <div class='metric-label'>Project</div>
            <div class='metric-value' style='font-size:20px;color:#e8eaf6'>{p.name}</div>
          </div>
          <div class='metric'>
            <div class='metric-label'>User</div>
            <div class='metric-value' style='font-size:20px;color:#FF007F'>{username}</div>
          </div>
        </div>""", unsafe_allow_html=True)

        if not initialized:
            st.markdown("<div class='card card-accent'>"
                        "<p style='color:#9ea3c0;margin:0'>Project not initialized.</p></div>",
                        unsafe_allow_html=True)
            if st.button("⬡  Initialize Project"):
                result = _safe(initialize_project, p)
                if result is None and st.session_state.msg is None:
                    flash("success", f"Project initialized at {p}")
                elif result is not None:
                    flash("success", f"Project initialized at {p}")
                st.rerun()
        else:
            # Recent versions
            try:
                versions = list_versions(p)
                if versions:
                    st.markdown("### Recent Versions")
                    rows_html = ""
                    for v in reversed(versions[-5:]):
                        ts = v.timestamp[:19].replace("T", " ")
                        nf = len(v.files)
                        rows_html += (
                            f"<tr>"
                            f"<td><span class='badge badge-blue'>v{v.number}</span></td>"
                            f"<td>{v.message}</td>"
                            f"<td style='color:#6c7086'>{ts}</td>"
                            f"<td><span class='badge badge-teal'>{v.username}</span></td>"
                            f"<td style='color:#6c7086'>{nf} file{'s' if nf!=1 else ''}</td>"
                            f"</tr>"
                        )
                    st.markdown(f"""
                    <div class='card'>
                    <table class='vtable'>
                      <thead><tr>
                        <th>Version</th><th>Message</th><th>Date</th>
                        <th>Author</th><th>Files</th>
                      </tr></thead>
                      <tbody>{rows_html}</tbody>
                    </table></div>""", unsafe_allow_html=True)
            except Exception:
                pass

# ═══════════════════════════════════════════════════════════════════════════════
# STAGE FILES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "stage":
    st.markdown("## Stage Files")
    if not is_initialized():
        st.error("Initialize a project first.")
    else:
        p = proj_path()
        svcs_dir = wait_for_svcs(p)

        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("<div class='card card-accent'>", unsafe_allow_html=True)
            target = st.text_input("Path to stage", placeholder=". (all)  or  src/main.py  or  docs/")
            if st.button("＋  Stage", use_container_width=True):
                if not target.strip():
                    flash("warn", "Enter a path or '.' for everything.")
                else:
                    res = _safe(add_item, p, target.strip())
                    if st.session_state.msg is None:
                        flash("success", f"Staged: {target}")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            entries = read_index(svcs_dir)
            st.markdown(f"<div class='card'>"
                        f"<p style='color:#6c7086;font-size:11px;text-transform:uppercase;"
                        f"letter-spacing:.06em;margin-bottom:12px'>Staged — {len(entries)} file(s)</p>",
                        unsafe_allow_html=True)
            if entries:
                chips = "".join(
                    f"<div class='file-chip'>📄 {e.rel_path}</div>" for e in entries
                )
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.markdown("<p style='color:#4a4a6a;font-size:13px'>Nothing staged yet.</p>",
                            unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# COMMIT
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "commit":
    st.markdown("## Commit")
    if not is_initialized():
        st.error("Initialize a project first.")
    else:
        p = proj_path()
        svcs_dir = wait_for_svcs(p)
        entries = read_index(svcs_dir)

        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("<div class='card card-accent'>", unsafe_allow_html=True)
            msg = st.text_input("Commit message", placeholder="Describe what changed...")
            if st.button("✔  Create Version", use_container_width=True):
                v = _safe(create_version, p, msg)
                if v is not None:
                    flash("success", f"Version {v} created: {msg}")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown(f"<div class='card'>"
                        f"<p style='color:#6c7086;font-size:11px;text-transform:uppercase;"
                        f"letter-spacing:.06em;margin-bottom:12px'>Will commit {len(entries)} file(s)</p>",
                        unsafe_allow_html=True)
            for e in entries:
                st.markdown(f"<div class='file-chip'>📄 {e.rel_path}</div>",
                            unsafe_allow_html=True)
            if not entries:
                st.markdown("<p style='color:#902D41;font-size:13px'>⚠ Nothing staged.</p>",
                            unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "history":
    st.markdown("## Version History")
    if not is_initialized():
        st.error("Initialize a project first.")
    else:
        versions = _safe(list_versions, proj_path())
        if versions is not None:
            if not versions:
                st.info("No versions yet. Stage files and commit to create one.")
            else:
                rows_html = ""
                for v in reversed(versions):
                    ts = v.timestamp[:19].replace("T", " ")
                    nf = len(v.files)
                    rows_html += (
                        f"<tr>"
                        f"<td><span class='badge badge-blue'>v{v.number}</span></td>"
                        f"<td style='font-weight:500'>{v.message}</td>"
                        f"<td style='color:#6c7086;font-family:monospace;font-size:12px'>{ts}</td>"
                        f"<td><span class='badge badge-teal'>{v.username}</span></td>"
                        f"<td style='color:#6c7086'>{nf} file{'s' if nf!=1 else ''}</td>"
                        f"</tr>"
                    )
                st.markdown(f"""
                <div class='card'>
                <table class='vtable'>
                  <thead><tr>
                    <th>Version</th><th>Message</th><th>Timestamp</th>
                    <th>Author</th><th>Files</th>
                  </tr></thead>
                  <tbody>{rows_html}</tbody>
                </table></div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DIFF
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "diff":
    st.markdown("## Diff")
    if not is_initialized():
        st.error("Initialize a project first.")
    else:
        p = proj_path()
        versions = _safe(list_versions, p) or []
        nums = [v.number for v in versions]

        if len(nums) < 2:
            st.info("Need at least 2 versions to diff.")
        else:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                v1 = st.selectbox("Version A", nums, index=len(nums)-2,
                                  format_func=lambda n: f"v{n}")
            with col2:
                v2 = st.selectbox("Version B", nums, index=len(nums)-1,
                                  format_func=lambda n: f"v{n}")
            with col3:
                st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
                run_diff = st.button("⇄  Compare", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            if run_diff or True:
                diffs = _safe(show_diff, p, v1, v2)
                if diffs is not None:
                    if not diffs:
                        st.info(f"No differences between v{v1} and v{v2}.")
                    else:
                        for fd in diffs:
                            html = f"<span class='diff-file'>⊞ {fd.rel_path}</span>"
                            for line in fd.lines:
                                esc = (line.replace("&","&amp;")
                                           .replace("<","&lt;")
                                           .replace(">","&gt;"))
                                if line.startswith("+++") or line.startswith("---"):
                                    html += f"<span class='diff-hunk'>{esc}</span>"
                                elif line.startswith("@@"):
                                    html += f"<span class='diff-hunk'>{esc}</span>"
                                elif line.startswith("+"):
                                    html += f"<span class='diff-add'>{esc}</span>"
                                elif line.startswith("-"):
                                    html += f"<span class='diff-remove'>{esc}</span>"
                                else:
                                    html += f"<span class='diff-ctx'>{esc}</span>"
                        st.markdown(f"<div class='card' style='font-size:13px'>{html}</div>",
                                    unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# RESTORE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "restore":
    st.markdown("## Restore Version")
    if not is_initialized():
        st.error("Initialize a project first.")
    else:
        p = proj_path()
        versions = _safe(list_versions, p) or []

        if not versions:
            st.info("No versions to restore.")
        else:
            st.warning("⚠ Restoring will overwrite all current uncommitted files.")

            rows_html = ""
            for v in reversed(versions):
                ts = v.timestamp[:19].replace("T", " ")
                rows_html += (
                    f"<tr>"
                    f"<td><span class='badge badge-blue'>v{v.number}</span></td>"
                    f"<td>{v.message}</td>"
                    f"<td style='color:#6c7086'>{ts}</td>"
                    f"<td style='color:#6c7086'>{v.username}</td>"
                    f"</tr>"
                )
            st.markdown(f"""
            <div class='card' style='margin-bottom:20px'>
            <table class='vtable'>
              <thead><tr><th>Version</th><th>Message</th><th>Date</th><th>Author</th></tr></thead>
              <tbody>{rows_html}</tbody>
            </table></div>""", unsafe_allow_html=True)

            nums = [v.number for v in versions]
            col1, col2 = st.columns([1, 2])
            with col1:
                target_v = st.selectbox("Select version", nums,
                                        format_func=lambda n: f"v{n}")
            with col2:
                st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
                if st.button(f"↺  Restore v{target_v}", use_container_width=True):
                    res = _safe(restore_version, p, target_v)
                    if st.session_state.msg is None:
                        flash("success", f"Restored to v{target_v}")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "settings":
    st.markdown("## Settings")
    if not is_initialized():
        st.error("Initialize a project first.")
    else:
        svcs_dir = wait_for_svcs(proj_path())
        cfg = read_config(svcs_dir)

        with st.form("settings_form"):
            st.markdown("<div class='card card-accent'>", unsafe_allow_html=True)
            new_user = st.text_input("Username", value=cfg.username)
            new_ignored = st.text_area(
                "Ignored patterns (one per line)",
                value="\n".join(cfg.ignored),
                height=120
            )
            submitted = st.form_submit_button("💾  Save Settings", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if submitted:
            cfg.username = new_user.strip() or "default_user"
            cfg.ignored = [l.strip() for l in new_ignored.splitlines() if l.strip()]
            write_config(svcs_dir, cfg)
            flash("success", f"Settings saved. Username: {cfg.username}")
            st.rerun()
