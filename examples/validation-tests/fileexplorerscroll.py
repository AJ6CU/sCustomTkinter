#!/usr/bin/python3
"""
Tests two specific things about sCTkFileExplorer's scroll-binding fix:

1. SCOPED, NOT GLOBAL: places an sCTkFileExplorer on the left and a plain
   sCTkScrollableFrame (with enough dummy rows to need scrolling) on the
   right. This is the part a single-widget test CANNOT catch -- with only
   one scrollable widget in the whole window, the old bind_all() bug and the
   new scoped bind() would behave identically, since there'd be nothing else
   competing for the global binding. With two independent scrollable things
   side by side: scroll while hovering over the LEFT panel -- only the file
   list should move. Scroll while hovering over the RIGHT panel -- only the
   dummy list should move. If scrolling over one ever moves the other, or if
   scrolling only ever affects whichever widget was bound most recently
   regardless of where the cursor is, that's the bind_all bug back.

2. RE-BINDING AFTER NAVIGATION: two buttons jump to two different folders
   (pick ones on your system likely to have enough files to actually need
   scrolling -- defaults below are reasonable guesses, change them if
   needed). Confirms scrolling still works on the SECOND folder shown, not
   just the first -- since navigating replaces every row widget, and each
   new set needs its own scroll bindings applied again.

Also exercises ordinary interaction while you're in here anyway: single-click
a file/folder row (should update the "Selected" label below), double-click a
folder (should navigate into it).
"""
import os
from scustomtkinter import sCTk, sCTkFrame, sCTkFileExplorer, sCTkScrollableFrame, sCTkLabelPrimary, sCTkButtonPrimary

root = sCTk()
root.geometry("820x520")
root.title("FileExplorer Scroll-Binding Test")

outer = sCTkFrame(root)
outer.pack(expand=True, fill="both", padx=15, pady=15)

sCTkLabelPrimary(
    outer,
    text="Scroll over LEFT panel -> only file list should move. Scroll over RIGHT -> only dummy list should move.",
    font=("Arial", 12, "bold"),
).pack(anchor="w", pady=(0, 8))

panels = sCTkFrame(outer, fg_color="transparent")
panels.pack(expand=True, fill="both")

# --- Left: the actual widget under test ---
left = sCTkFrame(panels, fg_color="transparent")
left.pack(side="left", expand=True, fill="both", padx=(0, 8))

selected_label = sCTkLabelPrimary(left, text="Selected: (none yet)")
selected_label.pack(anchor="w", pady=(0, 4))

# Change these two to folders on your system with a decent number of files.
FOLDER_A = os.path.expanduser("~")
FOLDER_B = os.path.expanduser("~/Documents") if os.path.isdir(os.path.expanduser("~/Documents")) else os.path.expanduser("~")

explorer = sCTkFileExplorer(
    left,
    initialdir=FOLDER_A,
    type="directory",
    width=350,
    height=380,
    command=lambda path: selected_label.configure(text=f"Selected: {path}"),
)
explorer.pack(fill="both", expand=True)
# Note: unlike sCTkScrollableFrame, sCTkFileExplorer already auto-schedules
# _finalize_split_bindings() itself via self.after(10, ...) inside __init__
# -- no manual call needed here.

nav_row = sCTkFrame(left, fg_color="transparent")
nav_row.pack(fill="x", pady=(8, 0))

def navigate_to(folder):
    # No public method exists for external navigation as of this writing --
    # path_to_show has no trace of its own (unlike selected_path), so the
    # caller must set it AND explicitly call _fill_explorer(), matching the
    # confirmed internal pattern used by _move_back(). Calling a private
    # method directly like this is a real gap in the widget's public API,
    # not something to treat as normal usage going forward.
    explorer.path_to_show.set(folder)
    explorer._fill_explorer()

sCTkButtonPrimary(nav_row, text=f"Go to: {os.path.basename(FOLDER_A) or FOLDER_A}",
                   command=lambda: navigate_to(FOLDER_A)).pack(side="left", padx=(0, 6))
sCTkButtonPrimary(nav_row, text=f"Go to: {os.path.basename(FOLDER_B) or FOLDER_B}",
                   command=lambda: navigate_to(FOLDER_B)).pack(side="left")

# --- Right: an independent scrollable widget, purely to prove scope ---
right = sCTkFrame(panels, fg_color="transparent")
right.pack(side="left", expand=True, fill="both", padx=(8, 0))

sCTkLabelPrimary(right, text="Unrelated scrollable list (control)").pack(anchor="w", pady=(0, 4))

dummy_scroll = sCTkScrollableFrame(right, width=350, height=380, label_text="Dummy Content")
dummy_scroll.pack(fill="both", expand=True)
for i in range(40):
    sCTkLabelPrimary(dummy_scroll, text=f"Dummy row {i + 1}").pack(anchor="w", pady=2)
dummy_scroll._finalize_split_bindings()

print(f"Folder A: {FOLDER_A}")
print(f"Folder B: {FOLDER_B}")
print("If either has too few files to need scrolling, edit FOLDER_A/FOLDER_B above.")
print("\nWatch for scroll SCOPE (does it stay on the panel under the cursor)")
print("and RE-BINDING (does scroll still work after clicking a 'Go to' button).\n")

root.mainloop()