## sCTkFileExplorer

### Table of Contents
* [API Property Reference](#api-property-reference)
* [Constructor](#constructor)
* [Convenience Functions](#convenience-functions)
* [Execution Event Callbacks](#execution-event-callbacks-command--double_click_command)
* [Centralized Stylesheet Setup](#centralized-stylesheet-setup-sctkthemesjson)
* [Other Notes](#other-notes)
* [Implementation Example & Test Harness](#implementation-example--test-harness)

---

A theme-compliant, highly configurable custom file and folder navigation panel embedded directly within user layout cards. Designed to list paths and filter extensions dynamically without forcing external platform dialog boxes, it unbinds hover highlights and locks canvas scroll mechanisms seamlessly when interaction states toggle.

---
![FileExplorer.png](images/FileExplorer.png)

### API Property Reference

| Property / Feature | Standard CustomTkinter | Your `sCustomTkinter` Setup |
| :--- | :--- | :--- |
| **Instantiation** | *Not Available Natively* | `sCTkFileExplorer(master)` *(Embedded Local File Navigator)* |
| **File Mapping** | No native component layout handles inline folder index matrices. | Streamlined and compiled programmatically across `sCTkFileExplorer.py` and `ThemeableWidget.py`. |
| **State Lock** | *Not Supported Natively* | `explorer.state("disabled")`<br>**OR**<br>`explorer.configure(state="disabled")`<br><br>**Dual-Routing State Pipeline:** Natively handles both syntaxes. Freezes canvas item scrolling, strips active button double-clicks, and dims rows using centralized `disabled_map` presets. |
| `get_state()` | *Not Supported Natively* | `Method -> str` explicit verification query matching system test assertions. |

---

### Constructor

Initialize a custom embedded directory explorer window panel. Specific configuration metrics like `filetypes` can be parsed straight out of layout inspectors without generating order-of-operation runtime exceptions. High-level custom configuration parameters from Pygubu (like `translator`, `on_first_object_cb`, `image_loader`, and `data_pool`) are automatically intercepted, processed, and purged early by the `ThemeableWidget` mixin layer before the native constructor fires.

```python
sCTkFileExplorer(master, type="directory", filetypes=None, initialdir=None, initialfile=None, command=None, double_click_command=None, width=400, height=300, corner_radius=None, border_width=None, bg_color="transparent", fg_color=None, border_color=None, background_corner_colors=None, overwrite_preferred_drawing_method=None, **kwargs)
```

| Parameter Name | Data Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `master` | `any` | *Required* | Reference pointer tracking your root window, parent layout layer, or container frame capsule. |
| `type` | `str` | `"directory"` | Structural layout operation mode. Options: `"directory"` (renders folders only) or `"file"` (renders folders and compatible files). |
| `filetypes` | `list` / `str` | `None` | Filter array masking permitted file extensions. Formatted as an explicit python list or bracketed string array (e.g., `['.py', '.txt']`). Defers to unfiltered mode when `None`. |
| `initialdir` | `str` | `None` | Starting navigation folder pathway string. Supports tilde user expansion (`~`) and forces normalization to absolute paths at instantiation. Defaults to `os.getcwd()` if omitted. |
| `initialfile` | `str` | `None` | Default starting highlight target file path string. Highlights and selects the specified file asset row automatically on boot. |
| `command` | `callable` | `None` | Single-click method event callback triggered instantly whenever a valid, active list row is highlighted. Requires a strict **two-argument footprint**. |
| `double_click_command` | `callable` | `None` | Double-click selection method callback executed when an active row file is confirmed or executed. Requires a strict **two-argument footprint**. |
| `width` | `int` | `400` | Manual horizontal width constraint boundary dimension allocated to the explorer component measured in pixels. |
| `height` | `int` | `300` | Manual vertical height constraint boundary dimension allocated to the explorer component measured in pixels. |
### Convenience Functions
```python
# Programmatically manipulate selection items, change views, or filter parameters dynamically
explorer.set_mode("directory")               # Options: "file" or "directory"
explorer.set_initial_dir("/path/to/folder") # Forces the navigation frame to jump to a specific directory
explorer.set_initial_file("/path/file.py")   # Forces the text buffer lane to highlight a specific default file path
explorer.set_filetypes([".py", ".json"])     # Updates the active file type visibility extension arrays

# Evaluate current state configurations or apply absolute user interaction locks via dual-routing syntax
current_mode = explorer.get_state()          # Returns 'normal' or 'disabled'
explorer.state("disabled")                   # Freezes directory lines and dims row font components
```

---

### ⚡ Execution Event Callbacks (`command` & `double_click_command`)

Both callback functions execute dynamically when rows are manipulated by the user. To prevent application layer traceback drops, **any method mapped to these commands must accept exactly two mandatory arguments**:

```python
def my_explorer_callback(widget_instance, selected_path):
    """
    Mandatory Callback Signature Requirement
    
    1. widget_instance: The sCTkFileExplorer object triggering the method loop.
    2. selected_path:   The absolute string file path matching the row just clicked.
    """
    print(f"Action detected from {widget_instance}: Processing path -> {selected_path}")
```

* **`command`**: Triggers when a folder or file row is highlighted on a single click. Passes the explorer instance pointer and the updated absolute string path of the row item.
* **`double_click_command`**: Triggers when an active item row is double-clicked. If the targeted row is a subdirectory, the explorer automatically expands and steps *into* that directory. If the item is a valid file asset, it hands structural control back to the callback method, passing the explorer instance pointer and the absolute file location path.

---

### 🎨 Centralized Stylesheet Setup (`sCTkThemes.json`)

The file explorer queries your repository styling map profile matrix using standard `self._resolve_color()` lookup routines. This decoupling ensures that layout shapes, font styles, and path row aesthetics repaint smoothly during real-time theme profile adjustments.

To satisfy the framework configuration guidelines, ensure your theme matrix includes this structured asset block:

```json
{
    "sCTkFileExplorer": {
        "fg_color": "transparent",
        "btn_fg": ["#1A4375", "#1F6AA5"],
        "btn_border_color": ["#94A3B8", "#4B5563"],
        "btn_text_color": ["#FFFFFF", "#FFFFFF"],
        "btn_hover": ["#112A4B", "#194A7A"],
        "entry_fg": ["#FFFFFF", "#1E1E1E"],
        "entry_border_color": ["#CBD5E1", "#334155"],
        "entry_text_color": ["#1F2937", "#FFFFFF"],
        "row_active_text": ["#111827", "#F9FAFB"],
        "row_dimmed_text": ["#94A3B8", "gray50"],
        "button_color": ["#64748B", "#475569"],
        "disabled_map": {
            "btn_fg": ["#F3F4F6", "#111111"],
            "btn_border_color": ["#E5E7EB", "#222222"],
            "btn_text_color": ["#94A3B8", "#4B5563"],
            "entry_fg": ["#F9FAFB", "#1A1A1A"],
            "entry_border_color": ["#E5E7EB", "#222222"],
            "entry_text_color": ["#94A3B8", "#4B5563"],
            "button_color": ["#CBD5E1", "#334155"]
        }
    }
}
```

---

### Other Notes
* **Standalone Embed Mechanics:** Instead of blocking main loops via operational platform modal windows (`filedialog`), this component behaves as a standard frame block that can pack or grid comfortably anywhere inside your primary interface layouts.
* **Automated Lifecycle Handshake:** Fires `self._finalize_themeable_lifecycle()` at the absolute end of the constructor initialization track to cleanly pass instance registration hooks straight back up to Pygubu parent controllers.
* **Deep-Copy Dictionary Isolation Shield:** Because CustomTkinter's native container initialization loops mutate and delete attributes directly out of raw dictionary data footprints during its boot pass, the constructor clones your configurations into `self._local_defaults = dict(self.final_kw)` beforehand. This preserves your color mappings safely.

---

### Implementation Example & Test Harness

Below is a complete, self-contained test execution script demonstrating how to properly embed an `sCTkFileExplorer` workspace card alongside pure, composite companion input tools and entry lanes to drive runtime changes dynamically.

```python

#!/usr/bin/python3
# =====================================================================
# 🛠️ TESTING HARNESS SETUP
# =====================================================================
if __name__ == "__main__":
    import os
    import customtkinter as ctk
    import sCTkThemes
    from sCTkFrame import sCTkFrame
    from sCTkEntryPrimary import sCTkEntryPrimary
    from sCTkButtonPrimary import sCTkButtonPrimary
    from sCTkOptionMenuPrimary import sCTkOptionMenuPrimary
    from sCTkLabelSecondary import sCTkLabelSecondary
    from sCTkFileExplorer import sCTkFileExplorer

    sCTkThemes.apply_sCTkThemes()
    root = ctk.CTk()
    root.title("Standalone Embedded sCTkFileExplorer Panel View")
    root.geometry("600x720")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    lbl_monitor = sCTkLabelSecondary(base, text="Active Highlight Track: [None Selection]")
    lbl_monitor.pack(pady=10)

    def track_selection(explorer_instance):
        path = explorer_instance.selected_path.get()
        lbl_monitor.configure(text=f"Active Highlight Track: {os.path.basename(path)}")
        print(f"SINGLE-CLICK HIGHLIGHT: {path}")

    def execute_file(explorer_instance, path):
        print(f"DOUBLE-CLICK CONFIRMED! Launching: {path}")

    user_home_dir = os.path.expanduser("~")
    explorer = sCTkFileExplorer(base, type="file", initialdir=user_home_dir, filetypes=[".py", ".md", ".json"], command=track_selection, double_click_command=execute_file, width=540, height=350)
    explorer.pack(fill="both", expand=True, padx=15, pady=10)

    control_deck = sCTkFrame(base, border_width=1, corner_radius=6)
    control_deck.pack(fill="x", padx=15, pady=10)

    row1 = sCTkFrame(control_deck)
    row1.pack(fill="x", padx=10, pady=5)
    sCTkLabelSecondary(row1, text="Explorer Mode:", width=100, anchor="w").pack(side="left", padx=5)

    def on_mode_menu_changed(choice):
        mode_type = "file" if "File" in choice else "directory"
        explorer.set_mode(mode_type)
        entry_filter.configure(state="disabled" if mode_type == "directory" else "normal")

    opt_mode = sCTkOptionMenuPrimary(row1, values=["File Mode (Show Items)", "Directory Mode (Folders Only)"], command=on_mode_menu_changed, width=250)
    opt_mode.pack(side="left", padx=5)
    opt_mode.set("File Mode (Show Items)")

    row2 = sCTkFrame(control_deck)
    row2.pack(fill="x", padx=10, pady=5)
    sCTkLabelSecondary(row2, text="File Filter List:", width=100, anchor="w").pack(side="left", padx=5)

    entry_filter = sCTkEntryPrimary(row2, placeholder_text="['.py', '.md', '.json', '.txt']")
    entry_filter.pack(side="left", fill="x", expand=True, padx=5)
    entry_filter.bind("<Return>", lambda e: explorer.set_filetypes(entry_filter.get().strip()))

    row3 = sCTkFrame(control_deck)
    row3.pack(fill="x", padx=10, pady=5)
    sCTkLabelSecondary(row3, text="Jump to Path:", width=100, anchor="w").pack(side="left", padx=5)

    entry_path = sCTkEntryPrimary(row3, placeholder_text="Enter absolute directory path...")
    entry_path.insert(0, user_home_dir)
    entry_path.pack(side="left", fill="x", expand=True, padx=5)
    entry_path.bind("<Return>", lambda e: explorer.set_initial_dir(entry_path.get().strip()))

    def toggle_explorer_lock():
        target = "disabled" if explorer.get_state() == "normal" else "normal"
        explorer.configure(state=target)
        opt_mode.configure(state=target)
        entry_filter.configure(state=target)
        entry_path.configure(state=target)
        btn_lock.configure(text="Lock Explorer Deck" if target == "normal" else "Unlock Explorer Deck")

    btn_lock = sCTkButtonPrimary(base, text="Lock Explorer Deck", command=toggle_explorer_lock)
    btn_lock.pack(side="bottom", pady=10)
    root.mainloop()
```

[Return to Table of Contents](#contents)
