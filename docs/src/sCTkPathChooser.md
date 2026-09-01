## sCTkPathChooser

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkPathChooser` is a theme-compliant single-line path entry paired with a "Browse..." button that opens an `sCTkFileExplorer` in a modal popup. It inherits `ctk.CTkFrame` directly, composing an internal `sCTkEntryPrimary` and `sCTkButtonPrimary`.

Dark Mode:  ![sCTkPathChooser in dark mode](images/sCTkPathChooser_Dark.png)&emsp; &emsp; &emsp; &emsp;
Light Mode: ![sCTkPathChooser in light mode](images/sCTkPathChooser_Light.png)

Every property this widget forwards to its internal entry (`justify`, `width`, `height`) has been confirmed valid against CustomTkinter's own real `CTkEntry` source, the same verification done for `sCTkSpinbox`. There's no risk of this widget sending an unrecognized property to its own entry.

---

### Constructor

```python
sCTkPathChooser(master=None, initialdir=None, initialfile=None, type="file",
                 filetypes=None, title=None, defaultextension=None,
                 justify="left", entry_height=None, browser_width=None,
                 browser_height=None, btn_text="Browse...", **kwargs)
```

| Parameter | Type | Description |
|---|---|---|
| `master` | widget | Parent container. |
| `initialdir` / `initialfile` | `str` | Starting directory/filename for the browser popup. |
| `type` | `"file"` / `"directory"` | Whether individual files are selectable, or only directories. |
| `filetypes` | `list[str]` | File extension filter. |
| `justify` | `str` | Text alignment inside the entry. |
| `btn_text` | `str` | The browse button's label. |
| `**kwargs` | — | Any native `CTkFrame` argument, or a theme-key override (see [Theming](#theming-sctkthemesjson)). |

```python
save_path = sCTkPathChooser(control_panel, type="directory", initialdir="/Users/you/Documents")
save_path.pack(fill="x", padx=20, pady=10)
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `get()` | `str` | Current path text. |
| `set(path)` | `None` | Sets the displayed path, normalizing and expanding it. |
| `state(mode=None)` / `get_state()` | `str` | Gets or sets `"normal"`/`"disabled"`, dimming both the entry and the browse button. |
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard configuration, accepting `state`, `type`, `title`, `justify`, `btn_text`, `entry_height`, `btn_width` and `btn_height` as first-class properties. |
| `configure(name)` | `tuple` | Pygubu-style single-argument query for any of the eight properties above. **Previously broken:** the implementation read `pname = args` rather than `args[0]`, so every comparison tested a tuple against a string and failed — all eight queries fell through to the native widget and Pygubu could read none of them. The dict form of `configure()` was dead for the same reason (`isinstance(args, dict)` on a tuple is never true). |

Clicking "Browse..." opens an `sCTkFileExplorer` in a modal popup; selecting a path there calls `self.set(...)` on this widget automatically.

---

### Theming (`sCTkThemes.json`)

```json
{
    "sCTkPathChooser": {
        "entry_font": ["Arial", 13],
        "entry_fg": ["#F9F9FA", "#343638"],
        "entry_border_color": ["#979DA2", "#565B5E"],
        "entry_text_color": ["#000000", "#FFFFFF"],
        "btn_font": ["Arial", 13, "bold"],
        "btn_fg": ["#3B8ED0", "#1F6AA5"],
        "btn_hover": ["#2C74B3", "#144E75"],
        "btn_text_color": ["#DCE4EE", "#F9F9FA"],
        "btn_border_color": ["#3B8ED0", "#1F6AA5"],
        "disabled_map": {
            "entry_fg": ["#EAEAEA", "#2B2B2C"],
            "entry_border_color": ["#D3D3D3", "#3A3A3C"],
            "entry_text_color": ["#A0A0A0", "#7C7C7C"],
            "btn_fg": ["#D3D3D3", "#2D2F31"],
            "btn_border_color": ["#D3D3D3", "#2D2F31"],
            "btn_text_color": ["#A0A0A0", "#5A5C5E"]
        }
    }
}
```

Every key the code references is present in both the top-level block and `disabled_map` — confirmed by direct cross-check against the actual source, nothing missing.

Every top-level key is now required and validated at construction, matching `sCTkFileExplorer`/`sCTkTableview`/`sCTkSpinbox`/`sCTkSelector` — missing any raises immediately, naming the exact key. `disabled_map` entries deliberately keep their original, more lenient behavior: gracefully falling back to the top-level/normal value if not overridden, rather than hard-failing, since that's intentional and already correct.

---

### Example

```python
from scustomtkinter import sCTk, sCTkFrame, sCTkPathChooser, sCTkButtonPrimary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("450x200")
    root.title("PathChooser Example")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    chooser = sCTkPathChooser(base, type="directory")
    chooser.pack(fill="x", pady=10)

    def toggle_disabled():
        target = "disabled" if chooser.get_state() == "normal" else "normal"
        chooser.state(target)
        toggle_btn.configure(text="Enable" if target == "disabled" else "Disable")

    toggle_btn = sCTkButtonPrimary(base, text="Disable", command=toggle_disabled)
    toggle_btn.pack(pady=10)

    root.mainloop()
```

---

### Known Limitations

- **No readonly support** — unlike `sCTkSpinbox`, this widget only has `"normal"`/`"disabled"`, even though the same design opportunity applies (the entry could be readonly-locked while "Browse..." stays clickable, since it's the intended alternative way to set the value). Identified as a genuine future enhancement, not implemented yet.

[Return to Table of Contents](#contents)
