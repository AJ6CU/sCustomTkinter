## sCTkPathChooser

### Table of Contents
* [API Property Reference](#api-property-reference)
* [Constructor](#constructor)
* [Convenience Functions](#convenience-functions)
* [Centralized Stylesheet Setup](#centralized-stylesheet-setup-sctkthemesjson)
* [Other Notes](#other-notes)
* [Implementation Example & Test Harness](#implementation-example--test-harness)

---

An advanced composite field-and-trigger widget pairing a fluid single-line text lane entry block directly alongside an integrated modal browser toggle button. It translates local paths, expands system tilde keys (`~`), and dynamically opens an embedded, theme-synchronized `sCTkFileExplorer` portal centered accurately over your parent layout dimensions without locking primary background execution threads.

### API Property Reference

| Property / Feature | Standard CustomTkinter | Your `sCustomTkinter` Setup |
| :--- | :--- | :--- |
| **Instantiation** | *Not Available Natively* | `sCTkPathChooser(master)` *(Compound Path Selector)* |
| **File Mapping** | No unified compound object natively synchronizes text cells with buttons. | Separated safely across `sCTkPathChooser.py` and `ThemeableWidget.py`. |
| **State Lock** | `self.configure(state="disabled")` | `chooser.state("disabled")`<br>**OR**<br>`chooser.configure(state="disabled")`<br><br>**Polymorphic State Control:** Simultaneously locks the entry string text buffer lane and freezes the browser launcher button out of centralized `disabled_map` guidelines. |
| `get_state()` | *Not Available Natively* | `Method -> str` explicit verification query matching system test assertions. |

---

### Constructor

Initialize a custom compound directory path or file selector instance. Offset parameters like `btn_width` or `entry_height` can be passed cleanly during instantiation to stretch internal sub-elements independently.

```python
sCTkPathChooser(master, type="directory", title="Select Path", filetypes=None, initialdir=None, initialfile=None, command=None, width=350, height=32, justify="left", entry_height=32, btn_width=110, btn_height=32, btn_text=None, browser_width=500, browser_height=450, **kwargs)
```

| Parameter Name | Data Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `master` | `any` | *Required* | Reference pointer tracking your root window, parent layout layer, or container frame capsule. |
| `type` | `str` | `"directory"` | Structural layout operation mode. Options: `"directory"` (renders folder browser options) or `"file"` (enforces file extension checks). |
| `title` | `str` | `"Select Path"` | Text heading string displayed inside the top title deck of the popup modal browser window. |
| `filetypes` | `list` / `str` | `None` | Filter array masking permitted file extensions. Formatted as an explicit python list or bracketed string array (e.g., `['.py', '.json']`). |
| `justify` | `str` | `"left"` | Text alignment profile string inside the input field lane. Accepts `"left"`, `"right"`, or `"center"`. |
| `entry_height` | `int` | *Matches height* | Manual vertical height footprint tracking restriction assigned to the text box lane measured in pixels. |
| `btn_width` | `int` | `110` | Manual horizontal width allocated to the macro click trigger browse button measured in pixels. |
| `btn_text` | `str` | `None` | Display string override assigned to the browse button. Automatically falls back to mode labels if left as `None`. |
| `command` | `callable` | `None` | Single-click method event callback executed whenever a file selection path is successfully submitted or confirmed. |
### Convenience Functions
```python
# Programmatically manipulate selector entries, fetch strings, or trigger modal windows on the fly
chooser.set("/Users/name/Documents") # Clears the current buffer and inserts an expanded absolute pathway
active_path = chooser.get()          # Returns the active character path string array currently displayed

# Evaluate current state configurations or apply absolute user interaction locks via dual-routing syntax
current_mode = chooser.get_state()   # Returns 'normal' or 'disabled'
chooser.state("disabled")            # Freezes button triggers and applies muted flat gray skins
```

### Centralized Stylesheet Setup (`sCTkThemes.json`)
```json
{
    "sCTkPathChooser": {
        "entry_fg": ["#FFFFFF", "#1E1E1E"],
        "entry_border_color": ["#CBD5E1", "#334155"],
        "entry_text_color": ["#1F2937", "#FFFFFF"],
        "entry_font": ["Arial", 12],
        "btn_fg": ["#1A4375", "#1F6AA5"],
        "btn_border_color": ["#94A3B8", "#4B5563"],
        "btn_text_color": ["#FFFFFF", "#FFFFFF"],
        "btn_hover": ["#112A4B", "#194A7A"],
        "btn_font": ["Arial", 11, "bold"],
        "disabled_map": {
            "entry_fg": ["#F9FAFB", "#1A1A1A"],
            "entry_border_color": ["#E5E7EB", "#222222"],
            "entry_text_color": ["#94A3B8", "#4B5563"],
            "btn_fg": ["#F3F4F6", "#111111"],
            "btn_border_color": ["#E5E7EB", "#222222"],
            "btn_text_color": ["#94A3B8", "#4B5563"]
        }
    }
}
```

---

### Other Notes
* **Inversion Blacklist & Mutation Shield:** To bypass CustomTkinter's private constructor sweeping arrays that destructively mutate configuration dictionary values, the constructor copies your data parameters into `self._local_defaults = dict(self.final_kw)` beforehand. This preserves your geometric variables safely.
* **Polymorphic Cascade Safety:** State changes automatically flow downward. Passing a `.state("disabled")` loop locks down both the interior text lane and the macro browse button, preventing unwanted modal triggers and hover events uniformly.
* **Automated Lifecycle Handshake:** Triggers `self._finalize_themeable_lifecycle()` at the absolute bottom of the initialization track to cleanly pass instance registration hooks straight back up to Pygubu layout trees out of the box.

---

### Implementation Example & Test Harness

Below is a complete, self-contained test execution script demonstrating how to embed an `sCTkPathChooser` within an isolated `sCTkFrame` chassis backplane while implementing runtime lock states and interactive selection feedback loops.

```python
#!/usr/bin/python3
"""
sCTkPathChooser - Standalone Interactive Testing Harness
"""
import customtkinter as ctk
import os

# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP
# =====================================================================
import sCTkThemes                      
from sCTkFrame import sCTkFrame        
from sCTkLabelSecondary import sCTkLabelSecondary
from sCTkPathChooser import sCTkPathChooser

if __name__ == "__main__":
    # Natively resolves your package assets and populates configurations cleanly
    sCTkThemes.apply_sCTkThemes()

    root = ctk.CTk()
    root.title("Compound Component Test Suite")
    root.geometry("700x260")

    # Swapped top container backplane over to theme-compliant chassis frame
    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    lbl_monitor = sCTkLabelSecondary(base, text="Active Telemetry Target: [None Selection]")
    lbl_monitor.pack(pady=10)

    def print_result(path):
        lbl_monitor.configure(text=f"Active Telemetry Target: {os.path.basename(path)}")
        print(f"MAIN CONSOLE PATH SELECTION -> {path}")

    # Instantiate your custom compound directory path chooser element
    chooser = sCTkPathChooser(
        base,
        type="file",
        title="Select Log Target",
        filetypes=[".py"],
        command=print_result,
        justify="right",
        width=550,
        height=50,
        state="normal",
        entry_height=40,
        btn_width=40,
        btn_height=40,
        btn_text="▶",
        browser_width=550,
        browser_height=500
    )
    chooser.pack(padx=20, pady=15)

    def toggle_chooser_lock():
        """Toggles the component state between normal active and dimmed profiles."""
        current_mode = chooser.get_state()
        target = "disabled" if current_mode == "normal" else "normal"
        chooser.configure(state=target)
        btn_lock.configure(text="Lock Chooser Deck" if target == "normal" else "Unlock Chooser Deck")
        print(f"Logged Verification Hook -> chooser.get_state() = {chooser.get_state()}")

    btn_lock = ctk.CTkButton(base, text="Lock Chooser Deck", command=toggle_chooser_lock)
    btn_lock.pack(side="bottom", pady=5)

    # Run the interactive boot tracking validation sequences
    print("--- BOOT INITIALIZATION PASSTHROUGH ---")
    chooser.state("disabled")
    print("state (Disabled Pass) =", chooser.get_state())  # Output: disabled
    chooser.state("normal")
    print("state (Normal Pass)   =", chooser.get_state())  # Output: normal
    print("========================================\n")

    root.mainloop()
```

[Return to Table of Contents](#contents)
