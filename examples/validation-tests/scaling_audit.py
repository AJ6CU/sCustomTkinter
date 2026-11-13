"""
Every sCustomTkinter widget, made at scaling 1.0, then the scaling doubled:
does it ask for about twice the room, and does it draw within that room?

    python examples/validation-tests/scaling_audit.py

"CHECK" rows are worth a look, not all faults: a frame holding a CTkLabel with
short text stays the same width (CustomTkinter's label quirk), and a few
widgets draw outline strokes a few px past their canvas at every scale.
"""
import time, tkinter as tk
import customtkinter as ctk
import scustomtkinter as s

root = s.sCTk(); root.geometry("+0+0")
def pump(ms=150):
    end = time.monotonic() + ms / 1000
    while time.monotonic() < end: root.update(); time.sleep(0.005)

def build(name):
    host = s.sCTkFrame(root); host.pack()
    W = getattr(s, name, None)
    if W is None:
        from scustomtkinter.sctk_dial import sCTkDialSelector as W
    kw = {}
    if name in ("sCTkButtonPrimary", "sCTkButtonSecondary", "sCTkButtonTertiary", "sCTkCheckBox",
                "sCTkRadioButton", "sCTkSwitch", "sCTkLabelPrimary", "sCTkLabelSecondary", "sCTkLabelTertiary"):
        kw = {"text": "Sample text"}
    if name in ("sCTkComboBox", "sCTkOptionMenuPrimary", "sCTkOptionMenuSecondary", "sCTkSegmentedButton"):
        kw = {"values": ["One", "Two", "Three"]}
    if name in ("sCTkFrameLabeledPrimary", "sCTkFrameLabeledSecondary"):
        kw = {"label_text": "Group"}
    if name == "sCTkTableview":
        kw = {"columns": ["a", "b"], "num_rows": 3}
    if name == "sCTkDialRange":
        kw = {}
    w = W(host, **kw)
    w.pack(padx=4, pady=4)
    if name in ("sCTkFrameLabeledPrimary", "sCTkFrameLabeledSecondary", "sCTkFrame", "sCTkScrollableFrame"):
        ctk.CTkLabel(w, text="inside").pack()
    if name == "sCTkFrequencyDisplay":
        w.set(14032000)
    if name == "sCTkNotebook":
        w.add("First"); w.add("Second")
    if name == "sCTkTabview":
        w.add("First"); w.add("Second")
    return host, w

def canvases(widget):
    out = []
    def walk(x):
        if isinstance(x, tk.Canvas): out.append(x)
        for c in x.winfo_children(): walk(c)
    walk(widget); return out

def overflow(widget):
    """Canvas items drawn outside their canvas (px), the worst case."""
    worst = 0
    for c in canvases(widget):
        cw, ch = c.winfo_width(), c.winfo_height()
        if cw <= 1 or ch <= 1: continue
        box = c.bbox("all")
        if not box: continue
        x0, y0, x1, y1 = box
        worst = max(worst, -x0, -y0, x1 - cw, y1 - ch)
    return worst

SKIP = {"sCTk", "sCTkToplevel", "sCTkDialog", "sCTkMessagebox", "sCTkFileExplorer", "sCTkScrollArea", "sCTkPathChooser"}
import re
names = [n for n in re.findall(r"import (\w+)", open(s.__file__).read()) if n.startswith("sCTk") and n not in SKIP]
names = sorted(set(names) | {"sCTkDialSelector"})
rows = []
for name in names:
    ctk.set_widget_scaling(1.0); pump()
    try:
        host, w = build(name); pump(300)
    except Exception as err:
        rows.append((name, "BUILD FAILED", f"{type(err).__name__}: {err}")); continue
    w1, h1 = w.winfo_reqwidth(), w.winfo_reqheight()
    ctk.set_widget_scaling(2.0)
    # CustomTkinter locks a window's size on a scaling change (see uBITX CEC
    # Desktop, _release_size_lock): released, and the window left to follow
    # its content, so a clipped drawing means the widget, not the test window.
    tk.Tk.wm_maxsize(root, 4000, 4000); tk.Tk.wm_minsize(root, 1, 1); tk.Tk.wm_geometry(root, "")
    pump(500)
    w2, h2 = w.winfo_reqwidth(), w.winfo_reqheight()
    over = overflow(w)
    rw, rh = w2 / max(w1, 1), h2 / max(h1, 1)
    ok = 1.7 <= rw <= 2.3 and 1.7 <= rh <= 2.3 and over <= 2
    rows.append((name, "ok" if ok else "CHECK", f"{w1}x{h1} -> {w2}x{h2} (x{rw:.2f}, x{rh:.2f}), drawn outside its canvas by {over}px"))
    host.destroy(); ctk.set_widget_scaling(1.0); pump()
for name, verdict, info in rows:
    print(f"{verdict:13s} {name:28s} {info}")
root.destroy()
