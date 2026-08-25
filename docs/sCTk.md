## sCTk

The `sCTk` is the primary main window container class wrapper for the `sCustomTkinter` workstation library ecosystem. It acts as a clean, direct pass-through equivalent to its foundational parent container layout class, `customtkinter.CTk`.

### 📌 Localized Table of Contents
* [Core Architectural Purpose](#core-architectural-purpose)
* [Constructor Reference](#constructor-reference)

---

### Core Architectural Purpose

The application base frame serves as the core master anchor for your interface tree:
1. **Decoupled User Space:** It eliminates the architectural requirement to maintain raw `import customtkinter` bindings inside your station cockpit panel code.
2. **Framework Alignment:** It standardizes the root initialization sequence pass to match the repository's native object naming conventions (`sCTkFrame`, `sCTkButtonPrimary`, etc.).

---

### Constructor Reference

It maps perfectly onto all native window properties, event loop callbacks, lifecycle handlers, and geometries tracking parameters out-of-the-box.

```python
from sCTk import sCTk
from sCTkThemes import apply_sCTkThemes

# 1. Initialize centralized framework look records natively on system boot
apply_sCTkThemes()

# 2. Instantiate your primary root application backplane directly
app = sCTk()
app.geometry("800x600")
app.title("Main Control Rig Backplane")

app.mainloop()
```
