## sCTkToplevel

The `sCTkToplevel` is the secondary window container class wrapper for the `sCustomTkinter` workstation library ecosystem. It acts as a clean, direct pass-through equivalent to its foundational parent window layout class, `customtkinter.CTkToplevel`.

### 📌 Localized Table of Contents
* [Core Architectural Purpose](#core-architectural-purpose)
* [Constructor Reference](#constructor-reference)

---

### Core Architectural Purpose

The secondary window container serves as an independent, modal, or auxiliary pop-up anchor for your interface tree:
1. **Decoupled User Space:** It eliminates the architectural requirement to maintain raw `import customtkinter` bindings inside your sub-window or dialog code.
2. **Framework Alignment:** It standardizes auxiliary window initialization sequences to match the repository's native object naming conventions (`sCTkFrame`, `sCTkButtonPrimary`, etc.).

---

### Constructor Reference

It maps perfectly onto all native top-level window properties, modal behaviors, grab events, lifecycle handlers, and geometry configurations out-of-the-box.

```python
from sCTk import sCTk
from sCTkToplevel import sCTkToplevel
from sCTkThemes import apply_sCTkThemes

# 1. Initialize centralized framework look records natively on system boot
apply_sCTkThemes()

# 2. Instantiate your primary root application backplane directly
app = sCTk()
app.geometry("800x600")
app.title("Main Control Rig Backplane")

# 3. Spawn a secondary, decoupled window surface overhead
dialog = sCTkToplevel(master=app)
dialog.geometry("400x300")
dialog.title("Auxiliary Operational Panel")

app.mainloop()
```


[Return to Table of Contents](#contents)
