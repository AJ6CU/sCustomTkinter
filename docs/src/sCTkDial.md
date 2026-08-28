## sCTKDialBase

Abstract foundational base class for theme-adaptive mechanical rotary encoder components. It coordinates vector canvas layouts, mouse interaction loops, and cross-platform OS theme repainting rules.

![sCTkDial_All_Dark.png](images/sCTkDial_All_Dark.png)

### Universal Dial Architecture

Every custom rotary knob in the ecosystem inherits its vector mechanics directly out of this core layout module. It establishes several universal features:

* **Centralized Theme Mapping:** Resolves raw colors and styles out of `themes.json` using the specific runtime class name, automatically generating fallback properties if individual blocks are unconfigured.
* **Cascading Interaction Blocks:** Toggling a component into a disabled state dynamically unbinds mouse clicks, trackpad sweeps, and scrolling event loops simultaneously to protect the live interface deck from input leaks.
* **Translucency Shield Protection Engine:** Natively catches instances where a parent widget background resolves to `"transparent"`. It programmatically climbs up the window hierarchy tree to resolve the canvas background to a valid parent hex value string, completely eliminating Light Mode Tcl color crashes.
* **Sequential Re-Binding Engine:** Forces real-time theme repaint sweeps to complete and settle background color layers *before* executing low-level pointer attachments, keeping Apple trackpad touch momentum and standard wheel clicks perfectly responsive upon coming back from a disabled state lockout.

### API Property Reference (Shared Properties)

| Property / Feature | Value Format | Description |
| :--- | :--- | :--- |
| `state(mode)` | `Method (str)` | Main state manager handling map transformations (`'normal'`, `'disabled'`). |
| `get_state()` | `Method -> str` | Direct verification query returning the current operational lock status. |
| `diameter` | `int` | Square bounding container metric enforcing canvas height and width equality. |
| `divisions` | `int` | Total tick scale markings drawn symmetrically around the outer chassis ring track. |

---

### Centralized Stylesheet Setup Reference (`themes.json`)

All concrete sub-classes read from this structural arrangement format inside your centralized style registries:

```json
{
    "sCTkDialContinuous": {
        "fg_color": ["#E2E8F0", "#262626"],
        "shadow_color": ["#CBD5E1", "#02040A"],
        "text_color": ["#1A4375", "#FF9100"],
        "dial_color": ["#1E293B", "#181E2B"],
        "pointer_glow_color": ["#CBD5E1", "#3A455C"],
        "disabled_map": {
            "fg_color": ["#E2E8F0", "#1A1D24"],
            "text_color": ["#94A3B8", "#4B5563"]
        }
    }
}
```

### Other notes
* **Keyword Isolation Guard:** The framework handles deep property filtering inside the master mixin initialization phase, stripping custom draw elements out before they can collide with native CustomTkinter frame assertions.
* **Cross-Platform Auto Sensing:** Automatically pairs mousewheel and touchpad scroll tracks across macOS, Windows, and Linux operating systems cleanly out of the box.
