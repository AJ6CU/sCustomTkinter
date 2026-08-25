## sCTkSpinbox

The `sCTkSpinbox` is a highly configurable, theme-compliant custom spinbox wrapper widget. It extends `ctk.CTkFrame` and aggregates an internal `sCTkEntryPrimary` alongside two flanking or stacked directional button controls. The component dynamically supports two operational tracking modes: standard numerical incrementation step ranges, and discrete string text array index navigation. Like all sCTk widgets, it is fully theme-adaptive.

<a name="contents"></a>
### 📍 Table of Contents
* [API Constructor Reference](#constructor)
* [Custom Keyword Extensions (**kw)](#extensions)
* [Global Object Instance Methods](#methods)
* [Centralized Stylesheet Integration](#stylesheet)
* [Implementation Reference Template](#template)

---

<a name="constructor"></a>
### 📋 API Constructor Reference

```python
sCTkSpinbox(master=None, from_=0.0, to=100.0, step_size=1.0, command=None, state="normal", wrap=False, justify="left", show=None, placeholder_text=None, exportselection=True, width=140, height=32, **kw)
```

| Parameter Name | Data Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `master` | `any` | `None` | Reference pointer tracking your root window or parent layout layer capsule container. |
| `from_` | `float` | `0.0` | The lower numerical limit boundary representing the floor of your adjustment range. |
| `to` | `float` | `100.0` | The upper numerical limit boundary representing the ceiling of your adjustment range. |
| `step_size` | `float` | `1.0` | The exact mathematical offset added or subtracted from your tracking float on every button click. |
| `command` | `callable` | `None` | Optional event logging callback function executed instantly on text shifts, passing the active value. |
| `state` | `str` | `"normal"` | Execution state controller. Toggling to `"disabled"` dampens and locks out all inputs and arrows. |
| `wrap` | `bool` | `False` | Mechanical boundary iteration loop flag. When `True`, stepping past limits wraps around to alternative poles. |
| `justify` | `str` | `"left"` | Content text arrangement alignment tracking mask within the entry area. Options: `"left"`, `"center"`, `"right"`. |
| `show` | `str` | `None` | Character masking input indicator string sequence (e.g. `show="*"` for password entries). |
| `placeholder_text` | `str` | `None` | Faded background prompt text block displayed natively whenever the input cell field is completely empty. |
| `exportselection` | `bool` | `True` | Standard Tkinter selection clipboard persistence state identifier switch. |
| `width` | `int` | `140` | Manual hardware panel horizontal width layout footprint dimension measured in pixels. |
| `height` | `int` | `32` | Manual hardware panel vertical height layout footprint dimension measured in pixels. |

---

<a name="extensions"></a>
### 🛠️ Custom Keyword Extensions (`**kw`)
These exclusive configuration parameters override default geometry behaviors, resolve theme definitions, and style proportions dynamically:

| Extension Parameter | Data Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `button_width` | `int` | `22` | The horizontal width tracking measurement assigned to increment/decrement button frames in pixels. |
| `button_height` | `int` | `None` | The vertical button height. If `None`, scales automatically based on active grid parameters. |
| `button_side` | `str` | `"right"` | Hardware control grid positioning side anchor layout. Options: `"right"`, `"left"`, `"split"`. |
| `orientation` | `str` | `"vertical"` | Structural grid layout arrangement axis profile track. Options: `"vertical"`, `"horizontal"`. |
| `arrow_font_size` | `int` | `11` | Typography scaling rule explicitly defining point sizes for the raw directional glyph markings inside Pygubu. |
| `format` | `str` | `""` | Numerical formatting mask specifier string rule (supports C percent styles `%.3f` or bracket masks `{:.3f}`). |
| `values` | `str` / `list` | `None` | Literal input values array string loader. Setting choices converts your widget into Discrete Text List Mode. |

---

<a name="methods"></a>
### ⚡ Global Object Instance Methods

#### Programmatically Set Value Elements
```python
# Insert a distinct float, integer, or matching list mode text option string natively
spinbox.set(12.5)
```

#### Fetch Active Value Strings
```python
# Reaches into the data entry track, pulling back the active string layout contents
current_selection = spinbox.get()
```

#### Discrete Values Array Loader Shortcut
```python
# Programmatically inject custom space-separated lines or list records on the fly
spinbox.set_values('Slow Normal Fast "Turbo Speed" Max')
```

#### Layout Parameter Configuration Modifier
```python
# Updates interactive structural layouts or boundaries cleanly without layout recreation overhead
spinbox.configure(orientation="horizontal", button_side="split", arrow_font_size=14, wrap=True)
```

#### Advanced Sub-Component Style Targeting
If an explicit overrides requirement arises at runtime that bypasses the compiled stylesheet definitions, you can directly interact with the isolated increment/decrement components safely without initialization crashes:
```python
# Manually altering internal button typography fonts or text strings at runtime safely
spinbox.up_button.configure(font=("Arial", 10, "normal"))   # Increment button control instance
spinbox.down_button.configure(font=("Arial", 10, "normal")) # Decrement button control instance
```

---

<a name="stylesheet"></a>
### 🎨 Centralized Stylesheet Integration (`sCTkThemes.json`)

The widget relies heavily on direct index key lookups within your central styling map profile matrix. The component automatically feeds state updates down to your nested `sCTkEntryPrimary` instance, cascading text dimming transitions natively.

```json
{
    "sCTkSpinbox": {
        "font": ["Arial", 15, "normal"],
        "arrow_font_size": 11,
        "arrow_up_char": "▲",
        "arrow_down_char": "▼",
        "arrow_right_char": "▶",
        "arrow_left_char": "◀",
        "format": "%.2f",
        "border_width": 1.5,
        "corner_radius": 6,
        
        "entry_color": ["#FFFFFF", "#111827"],
        "border_color": ["#1A4375", "#64748B"],
        "text_color": ["#1F2937", "#F9FAFB"],
        "placeholder_text_color": ["#5A6E7F", "#526071"],
        "button_color": ["#9E9E9E", "#2A2F3D"],
        "button_hover_color": ["#7D7D7D", "#374151"],

        "disabled_map": {
            "entry_color": ["#F3F4F6", "#1F2937"],
            "border_color": ["#CBD5E1", "#475569"],
            "text_color": ["#94A3B8", "#64748B"],
            "button_color": ["#CBD5E1", "#334155"]
        }
    }
}
```

---

<a name="template"></a>
### 💻 Implementation Reference Template

```python
import customtkinter as ctk
import sCTkThemes
from sCTkFrame import sCTkFrame
from sCTkSpinbox import sCTkSpinbox
from sCTkLabelSecondary import sCTkLabelSecondary

# 1. Initialize centralized framework look records natively out of themes.json
sCTkThemes.apply_sCTkThemes()

root = ctk.CTk()
root.geometry("450x250")
root.title("Transceiver VFO Calibration Deck")

# 2. Mount custom master dashboard backplane frame
dashboard = sCTkFrame(root)
dashboard.pack(expand=True, fill="both", padx=20, pady=20)

# 3. Initialize dynamic monitoring readout label
status_lbl = sCTkLabelSecondary(dashboard, text="VFO Offset: 5.00 kHz", font=("Courier New", 14, "bold"))
status_lbl.pack(pady=10)

# 4. Instantiate custom pattern-perfect spinbox controller
vfo_step_ctrl = sCTkSpinbox(
    dashboard, 
    from_=0.0, 
    to=50.0, 
    step_size=0.5, 
    justify="center",
    format="%.2f kHz",
    command=lambda val: status_lbl.configure(text=f"VFO Offset: {val}")
)
vfo_step_ctrl.pack(pady=15)

# Seed boot parameter baseline coordinate safely
vfo_step_ctrl.set(5.0)

root.mainloop()
```

[Return to Table of Contents](#contents)
