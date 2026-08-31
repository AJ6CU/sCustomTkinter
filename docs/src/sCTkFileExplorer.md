## sCTkFileExplorer

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkFileExplorer` is a theme-compliant, scrollable file/folder browser — a back button, an editable current-path entry, and a scrollable list of clickable file/folder rows. It inherits `ctk.CTkFrame` directly and builds its own scrolling machinery internally (a raw `tkinter.Canvas` plus a `CTkScrollbar`), rather than composing `sCTkScrollableFrame`.

Dark Mode:  ![sCTkFileExplorer in dark mode](images/sCTkFileExplorer_Dark.png)&emsp; &emsp; &emsp; &emsp;
Light Mode: ![sCTkFileExplorer in light mode](images/sCTkFileExplorer_Light.png)

**Scroll handling is cross-platform and properly scoped.** An earlier version used a global `bind_all("<MouseWheel>", ...)` — affecting mouse wheel scrolling for the *entire application*, not just this widget, and only handling macOS and a generic Windows-style delta, with no Linux support at all. It's since been replaced with the same proven, scoped, three-platform scroll-handling logic used by `sCTkScrollableFrame`, adapted to target this widget's own internal canvas directly. Scroll bindings are re-applied automatically every time you navigate to a new folder, since navigating replaces every row widget.

---

### Constructor

```python
sCTkFileExplorer(master=None, initialdir=None, type="file", filetypes=None, ...)
```

| Parameter | Type | Description |
|---|---|---|
| `master` | widget | Parent container. |
| `initialdir` | `str` | Starting directory. |
| `type` | `"file"` / `"directory"` | Whether individual files are selectable, or only directories. |
| `filetypes` | `list[str]` | File extension filter (only meaningful when `type="file"`). |
| `command` | `callable` | Called with the clicked path (a string) on a single click. |
| `double_click_command` | `callable` | Called with `(self, path)` on a double click. |
| `width` / `height` | `int` | Overall widget dimensions. |
| `**kwargs` | — | Any native `CTkFrame` argument, or a theme-key override (see [Theming](#theming-sctkthemesjson)). |

```python
explorer = sCTkFileExplorer(control_panel, initialdir="/Users/you/Documents", type="directory", width=350, height=380)
explorer.pack(fill="both", expand=True)
```

**`command` receives a path, not the widget.** An earlier version passed `self` (the widget instance) instead of the clicked path — confirmed and fixed, since the only real-world caller (`sCTkPathChooser`) expected a path string and would have received garbage.

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `_finalize_split_bindings()` | `None` | Sets up scroll bindings and wires the back button/path entry. Auto-scheduled via `self.after(10, ...)` inside `__init__` — unlike `sCTkScrollableFrame`, you don't need to call this yourself. |
| `state(mode=None)` / `get_state()` | `str` | Gets or sets `"normal"`/`"disabled"`, dimming the back button, path entry, scrollbar, and all rows. |
| `configure(**kwargs)` | varies | Standard configuration. |

There's currently no public method for programmatic navigation from outside the widget — `path_to_show` (a `StringVar`) has no automatic refresh trace of its own (unlike `selected_path`), so navigating externally means setting it *and* explicitly calling the private `_fill_explorer()` afterward, matching the pattern used internally by the back button. This is a real API gap, not a documented feature.

---

### Theming (`sCTkThemes.json`)

```json
{
    "sCTkFileExplorer": {
        "btn_font": ["Arial", 11, "bold"],
        "entry_font": ["Arial", 12, "normal"],
        "btn_fg": ["#3B82F6", "#1D4ED8"],
        "btn_hover": ["#2563EB", "#1E40AF"],
        "btn_text_color": ["#FFFFFF", "#F9FAFB"],
        "btn_border_color": ["#1E3A8A", "#1E3A8A"],
        "entry_fg": ["#FFFFFF", "#111827"],
        "entry_text_color": ["#1F2937", "#F9FAFB"],
        "entry_border_color": ["#CBD5E1", "#475569"],
        "row_active_text": ["#1F2937", "#F9FAFB"],
        "row_dimmed_text": ["#94A3B8", "#64748B"],
        "button_color": ["#64748B", "#4B5563"],
        "disabled_map": {
            "btn_fg": ["#CBD5E1", "#334155"],
            "btn_border_color": ["#CBD5E1", "#334155"],
            "btn_text_color": ["#94A3B8", "#64748B"],
            "entry_fg": ["#F3F4F6", "#1F2937"],
            "entry_border_color": ["#CBD5E1", "#475569"],
            "entry_text_color": ["#94A3B8", "#64748B"],
            "row_dimmed_text": ["#5A6672", "#3A4552"],
            "button_color": ["#CBD5E1", "#334155"]
        }
    }
}
```

**`button_color` is not currently in your theme file at all — top-level or `disabled_map`.** This is a confirmed, more urgent gap than `row_dimmed_text`: `_process_live_theme_repaint()` is bound to `<Visibility>`, so it fires essentially every time a FileExplorer widget is actually displayed, not only when explicitly disabled. Against your real, current theme file, that means displaying this widget at all would currently raise `KeyError` immediately. The values shown above (`["#64748B", "#4B5563"]` normal, `["#CBD5E1", "#334155"]` disabled) are a proposal, not something already confirmed to exist — add both before testing this widget.

`button_color` controls the internal scrollbar's color, distinct from `btn_fg` (the back button).

`row_active_text`/`row_dimmed_text` control file/folder row text color — `row_active_text` for a normal, selectable row; `row_dimmed_text` for either a row excluded by the current filter, or every row when the whole widget is disabled. Both required at the top level; `row_dimmed_text` is also hard-required in `disabled_map` for the whole-widget-disabled case.

**Only `button_color` and `row_dimmed_text` genuinely hard-fail if missing from `disabled_map`.** The other six disabled-state keys (`btn_fg`, `btn_border_color`, `btn_text_color`, `entry_fg`, `entry_border_color`, `entry_text_color`) gracefully fall back to their top-level/normal value if `disabled_map` doesn't override them — not a crash risk, just means that specific property simply won't visually change when disabled unless you give it a distinct value.

The internal raw `Canvas`'s background color isn't part of this theme block at all — it's derived from this widget's own `fg_color`, falling back to a fixed neutral pair (`#1C1C1C` dark / `#F3F4F6` light) if `fg_color` is `"transparent"`, since a raw Canvas can't render CTk's transparent pseudo-value. This is a different kind of fallback than the ones above — not a theme gap, but a genuine "needs an actual renderable color" situation, the same accepted pattern used in `sCTkFrameLabeledPrimary`'s scrollbar hiding.

---

### Example

```python
from scustomtkinter import sCTk, sCTkFrame, sCTkFileExplorer, sCTkLabelPrimary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("420x480")
    root.title("FileExplorer Example")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    status = sCTkLabelPrimary(base, text="Selected: (none yet)")
    status.pack(anchor="w", pady=(0, 8))

    explorer = sCTkFileExplorer(
        base, type="directory",
        command=lambda path: status.configure(text=f"Selected: {path}"),
    )
    explorer.pack(expand=True, fill="both")

    root.mainloop()
```

---

### Known Limitations

- No public method for programmatic navigation — see [Methods](#methods) above.
- Missing a required theme key raises `KeyError` at first use, naming exactly which key and whether it's needed at the top level or in `disabled_map`.

[Return to Table of Contents](#contents)
