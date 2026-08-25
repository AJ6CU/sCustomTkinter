## sCTkMessage

### Table of Contents
* [System Architecture Overview](#system-architecture-overview)
* [API Constructor Reference](#api-constructor-reference)
* [Global Shortcut Function Handlers](#global-shortcut-function-handlers)
* [Centralized Stylesheet Setup](#centralized-stylesheet-setup-sctkthemesjson)
* [Layout & Text Wrapping Integration Rules](#layout--text-wrapping-integration-rules)

---

The `sCTkMessage` is an advanced, themeable dialog window system subclassed from `ctk.CTkToplevel` and integrated with `ThemeableWidget`. It replaces standard OS message alerts with modular, center-positioned dialogue boxes featuring dynamic text-wrapping, automated parent window tracking calculations, custom asset handling, and support for dual high-contrast action selection layouts that return boolean runtime parameters.

### System Architecture Overview

The subsystem operates dynamically at runtime through execution logic chains. Because modal dialog boxes are instantiated procedurally within code event callbacks rather than being statically placed, **this component does not require a Pygubu Builder Object (BO) file.**

The architecture is divided into the following layout segments:
1. **`sCTkMessage.py`**: Contains the top-level window manager tracking rules, uniform grid button size distributions, and global functional shortcut wrappers.
2. **`images/` Subdirectory**: A localized storage assets folder matching your component layout containing custom graphic files.
   * `info.png`, `warning.png`, `error.png` *(Standard Light Mode Assets)*
   * `info_dark.png`, `warning_dark.png`, `error_dark.png` *(High-Contrast Dark Mode Overrides)*

---

### API Constructor Reference

```python
sCTkMessage(title, message, typ, master=None, buttons="ok", ok_text="Ok", yes_text="Yes", no_text="No", width=400)
```

| Parameter Name | Data Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `title` | `str` | *Required* | Text displayed inside the top operating window header bar title deck. |
| `message` | `str` | *Required* | Body text string message container paragraph to display inside the prompt panel. |
| `typ` | `str` | *Required* | Alert asset track type classification identifier. Accepts `"info"`, `"warning"`, or `"error"`. |
| `master` | `any` | `None` | Reference pointer tracking your root window or parent `sCTkFrame` to calculate centering bounds. |
| `buttons` | `str` | `"ok"` | Layout selection control mapping. Accepts `"ok"` (single center prompt) or `"yes_no"` (twin balanced selections). |
| `ok_text` | `str` | `"Ok"` | Custom display string label mapped to the single button layout option track. |
| `yes_text` | `str` | `"Yes"` | Display string assigned to the primary confirmation button choice track. |
| `no_text` | `str` | `"No"` | Display string assigned to the secondary dismissal button choice track. |
| `width` | `int` | `400` | Manual window width boundary tracking restriction limit measured in pixels. |

---

### Global Shortcut Function Handlers

To launch modal dialog blocks quickly inside callback triggers without handling complete class instantiations manually, utilize these pre-wired functional shortcuts:

#### Standard Alert Prompts (Returns `True` upon closure)
```python
showinfo(title, message, ok_text="Ok", width=400, master=root)
showwarning(title, message, ok_text="Ok", width=400, master=root)
showerror(title, message, ok_text="Ok", width=400, master=root)
```

#### Confirmation Prompt Shortcuts (Returns primitive Python `True` or `False` boolean states)
```python
askyesno(title, message, yes_text="Yes", no_text="No", width=400, master=root)
askwarningyesno(title, message, yes_text="Yes", no_text="No", width=400, master=root)
askerroryesno(title, message, yes_text="Yes", no_text="No", width=400, master=root)
```
### Centralized Stylesheet Setup (`sCTkThemes.json`)

The component relies heavily on your centralized style dictionary system. To prevent the mixin parser tracking structures from raising runtime validation faults, verify your shared stylesheet contains this asset entry:

```json
{
    "sCTkMessage": {
        "font": ["Arial", 14],
        "text_color": ["#1A1A1A", "#E5E5E5"]
    }
}
```

---

### Layout & Text Wrapping Integration Rules

To completely bypass CustomTkinter's internal multi-line font calculation limitations, this widget uses Python's native `textwrap` module to inject hard newline coordinates before passing layout parameters to your primary text components.

Observe these implementation traits:
* **Horizontal Capsule Brackets**: When `buttons="yes_no"` is active, Column 0 and Column 1 utilize an interlocking `uniform="dialog_buttons"` constraint map. This completely locks both buttons to an identical layout grid pixel width, regardless of text length mismatches.
* **Vertical Safety Gutter**: Text layout nodes use `padx=(10, 35)` paired alongside a calculated character width subtraction map. This forces word bounds to drop downwards well before interacting with the physical window frame margin boundary.
* **Autonomous Resizing**: The `_center_window` geometry calculations lock your custom manual `width` pixel profile constraint, but query the active required widget layout height parameters dynamically via `winfo_reqheight()`. This allows window frames to expand or shrink vertically based on your text content volume requirements automatically.

[Return to Table of Contents](#contents)

---

### Implementation Example & Test Harness

Below is a complete, self-contained test execution script demonstrating how to properly map shortcut handlers, custom text boundaries, and dynamic boolean feedback out of an interactive transceiver dashboard setup.

```python
#!/usr/bin/python3
"""
sCTkMessage - Standalone Interactive Testing Harness
"""
import customtkinter as ctk

# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP
# =====================================================================
import sCTkThemes                
from sCTkButtonPrimary import sCTkButtonPrimary
from sCTkMessage import showinfo, showwarning, showerror, askyesno, askwarningyesno, askerroryesno

if __name__ == "__main__":
    sCTkThemes.apply_sCTkThemes()

    root = ctk.CTk()
    root.geometry("300x520")
    root.title("Message Example")

    long_msg = (
        "Warning: The VFO phase lock loop has lost lock synchronization with the master synthesizer. "
        "Continuous operation may contaminate adjacent radio channels. Do you wish to override?"
    )

    def trigger_info_ask():
        ans = askyesno("Info Query", "Do you wish to log parameter data strings?", yes_text="Log Data", no_text="Skip", master=root)
        print(f"Info Yes/No Feedback evaluated to: {ans}")

    def trigger_warning_ask():
        ans = askwarningyesno("Band Switch Warning", long_msg, yes_text="Override", no_text="Disconnect", width=450, master=root)
        print(f"Warning Yes/No Feedback evaluated to: {ans}")

    def trigger_error_ask():
        ans = askerroryesno("Fatal Overload Error", "VFO buffer cascade encountered. Attempt cold reset?", yes_text="Reset Buffer", no_text="Terminate", master=root)
        print(f"Error Yes/No Feedback evaluated to: {ans}")

    # ----------------------------------------------------
    #   1. INFO ALERT SECTION (Testing custom ok_text text!)
    # ----------------------------------------------------
    sCTkButtonPrimary(root, text="Test Info (OK)", width=200,
                      command=lambda: showinfo("Message Example", "Short statement info alert box.", ok_text="Acknowledge", master=root)).pack(pady=8)
    sCTkButtonPrimary(root, text="Test Info (Yes/No)", width=200,
                      command=trigger_info_ask).pack(pady=(8, 25))

    # ----------------------------------------------------
    #   2. WARNING ALERT SECTION
    # ----------------------------------------------------
    sCTkButtonPrimary(root, text="Test Warning (OK)", width=200,
                      command=lambda: showwarning("Warning", "Listen carefully", ok_text="Proceed", master=root)).pack(pady=8)
    sCTkButtonPrimary(root, text="Test Warning (Yes/No)", width=200,
                      command=trigger_warning_ask).pack(pady=(8, 25))

    # ----------------------------------------------------
    #   3. ERROR ALERT SECTION
    # ----------------------------------------------------
    sCTkButtonPrimary(root, text="Test Error (OK)", width=200,
                      command=lambda: showerror("Error", "Dead meat", ok_text="Close", master=root)).pack(pady=8)
    sCTkButtonPrimary(root, text="Test Error (Yes/No)", width=200,
                      command=trigger_error_ask).pack(pady=8)

    root.mainloop()
```

[Return to Table of Contents](#contents)
