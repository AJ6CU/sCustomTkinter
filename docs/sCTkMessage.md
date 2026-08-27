## sCTkMessage

### Table of Contents
* [System Architecture Overview](#system-architecture-overview)
* [API Constructor Reference](#api-constructor-reference)
* [Global Shortcut Function Handlers](#global-shortcut-function-handlers)
* [Simple Syntax Quick-Reference Guide](#simple-syntax-quick-reference-guide)
* [Centralized Stylesheet Setup](#centralized-stylesheet-setup-sctkthemesjson)
* [Layout & Text Wrapping Integration Rules](#layout--text-wrapping-integration-rules)
* [Implementation Example & Test Harness](#implementation-example--test-harness)

---

The `sCTkMessage` is an advanced, themeable dialog window system subclassed from `ctk.CTkToplevel` and integrated with `ThemeableWidget`. It replaces standard OS message alerts with modular, center-positioned dialogue boxes featuring dynamic text-wrapping, automated parent window tracking calculations, custom asset handling, and support for dual high-contrast action selection layouts that return boolean runtime parameters.

### System Architecture Overview

The subsystem operates dynamically at runtime through execution logic chains. Because modal dialog boxes are instantiated procedurally within code event callbacks rather than being statically placed, **this component does not require a Pygubu Builder Object (BO) file.**

The architecture is divided into the following layout segments:
1. **`sctk_message.py`**: Contains the top-level window manager tracking rules, uniform grid button size distributions, and the virtual `messagebox` object attribute bindings.
2. **`assets/images/` Subdirectory**: A centralized storage assets folder containing your custom graphic files:
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

To launch modal dialog blocks quickly inside callback triggers without handling complete class instantiations manually, utilize these pre-wired shortcuts via the **`messagebox`** namespace proxy:

#### Standard Alert Prompts (Returns `True` upon closure)
```python
messagebox.showinfo(title, message, ok_text="Ok", width=400, master=root)
messagebox.showwarning(title, message, ok_text="Ok", width=400, master=root)
messagebox.showerror(title, message, ok_text="Ok", width=400, master=root)
```

#### Confirmation Prompt Shortcuts (Returns primitive Python `True` or `False` boolean states)
```python
messagebox.askyesno(title, message, yes_text="Yes", no_text="No", width=400, master=root)
messagebox.askwarningyesno(title, message, yes_text="Yes", no_text="No", width=400, master=root)
messagebox.askerroryesno(title, message, yes_text="Yes", no_text="No", width=400, master=root)
```

---

### Simple Syntax Quick-Reference Guide

Below are clean, minimal use-cases showcasing how to call each convenience shortcut using the standardized `messagebox` proxy engine.

#### 1. `messagebox.showinfo`
Used for general application notifications, status confirmations, and completions.
```python
from scustomtkinter import messagebox

# Displays a standard informative dialog popup
messagebox.showinfo("System Init", "Satellite link successfully established.", master=root)
```

#### 2. `messagebox.showwarning`
Used to display alert parameters, non-fatal operational boundary breaches, or layout cautions.
```python
from scustomtkinter import messagebox

# Displays a warning alert box with a custom approval button text
messagebox.showwarning("Battery Low", "Backup power source dropped below 15%.", ok_text="Acknowledge", master=root)
```

#### 3. `messagebox.showerror`
Used to halt operations when a severe terminal failure or unhandled exception block is triggered.
```python
from scustomtkinter import messagebox

# Displays a fatal critical error box
messagebox.showerror("TX Failure", "Transmitter hardware thermal overload detected.", master=root)
```

#### 4. `messagebox.askyesno`
Launches a standard query dialogue window, returning a boolean flag based on the user's action.
```python
from scustomtkinter import messagebox

# Captures true/false verification states
if messagebox.askyesno("Log Session", "Do you wish to save the active telemetry log files?", master=root):
    print("User clicked YES: Executing write loop...")
else:
    print("User clicked NO: Dropping record data...")
```

#### 5. `messagebox.askwarningyesno`
Launches a critical query box carrying high-visibility alert graphics for destructive actions.
```python
from scustomtkinter import messagebox

# Captures permission states for hazardous overrides
override_allowed = messagebox.askwarningyesno(
    "Frequency Sync", 
    "VFO phase lock is currently unstable. Force manual override?", 
    yes_text="Force Override", 
    no_text="Abort Scan", 
    master=root
)
```

#### 6. `messagebox.askerroryesno`
Launches an error-status confirmation panel, typical for prompt actions following a hard code drop.
```python
from scustomtkinter import messagebox

# Captures choice states to run system self-healing scripts
if messagebox.askerroryesno("Cascade Failure", "Buffer buffer overflow hit. Attempt a cold reset?", master=root):
    # Execute recovery sequence...
    pass
```

---

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

---

### Implementation Example & Test Harness

Below is a complete, self-contained test execution script demonstrating how to properly map shortcut handlers, custom text boundaries, and dynamic boolean feedback out of an interactive transceiver dashboard setup.

```python
#!/usr/bin/python3
# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP for Messagebox
# =====================================================================

import customtkinter as ctk
from scustomtkinter import sCTkFrame, sCTkButtonPrimary,sCTk

if __name__ == "__main__":
    root = sCTk()
    root.geometry("300x520")
    root.title("Message Example")

    long_msg = "Warning: The VFO phase lock loop has lost lock synchronization with the master synthesizer. Override?"

    # 🚀 Clean functional callbacks using the messagebox namespace!
    def trigger_info_ask():
        print(f"Feedback: {messagebox.askyesno('Info Query', 'Log parameter data?', yes_text='Log', no_text='Skip', master=root)}")

    def trigger_warning_ask():
        print(f"Feedback: {messagebox.askwarningyesno('Band Switch', long_msg, yes_text='Override', no_text='Drop', width=450, master=root)}")

    def trigger_error_ask():
        print(f"Feedback: {messagebox.askerroryesno('Fatal Error', 'Attempt buffer cold reset?', yes_text='Reset', no_text='Quit', master=root)}")

    # 🚀 Native drop-in style execution pass!
    sCTkButtonPrimary(root, text="Test Info (OK)", width=200, command=lambda: messagebox.showinfo("Message Example", "Short statement alert.", ok_text="Acknowledge", master=root)).pack(pady=8)
    sCTkButtonPrimary(root, text="Test Info (Yes/No)", width=200, command=trigger_info_ask).pack(pady=(8, 25))
    sCTkButtonPrimary(root, text="Test Warning (OK)", width=200, command=lambda: messagebox.showwarning("Warning", "Listen carefully", ok_text="Proceed", master=root)).pack(pady=8)
    sCTkButtonPrimary(root, text="Test Warning (Yes/No)", width=200, command=trigger_warning_ask).pack(pady=(8, 25))
    sCTkButtonPrimary(root, text="Test Error (OK)", width=200, command=lambda: messagebox.showerror("Error", "Dead meat", ok_text="Close", master=root)).pack(pady=8)
    sCTkButtonPrimary(root, text="Test Error (Yes/No)", width=200, command=trigger_error_ask).pack(pady=8)

    root.mainloop()
```