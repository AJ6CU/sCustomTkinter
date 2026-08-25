## sCTkThemes

The centralized asset discovery, package path resolution, and optional core theme injection engine for the `sCustomTkinter` framework. 

`sCTkThemes` functions as a unified controller. It dynamically scans and reads theme layouts from a single `sCTkThemes.json` master file, populates the application's global layout registries, and encapsulates CustomTkinter's system-level appearance hooks into a single import model.

### API Method Reference

| Method / Wrapper Hook | Parameters | Description |
| :--- | :--- | :--- |
| `apply_sCTkThemes()` | `custom_path=None`, `bootstrap_ctk=False`, `mapping_mode="primary"` | **Framework Entry Point:** Automatically locates, reads, and loads style settings into active memory. |
| `set_appearance_mode()` | `mode_string: str` | **Wrapper Hook:** Seamlessly shifts global interface states (`'System'`, `'Dark'`, `'Light'`). |
| `get_appearance_mode()` | *None* | **Wrapper Hook:** Queries and returns the active drawing environment string. |
| `set_default_color_theme()` | `theme_name_or_path: str`| **Wrapper Hook:** Loads a core native CTk layout JSON base map tracker. |

---

### Core Architectural Features

#### 1. Native Relative Package Discovery
Instead of assuming where a terminal session or external executable was opened, `apply_sCTkThemes()` uses Python's relative file inspection token (`__file__`). It calculates exactly where the framework module files are currently residing on the hard drive at that exact millisecond. 

This self-discovery mechanism ensures that properties register perfectly across three specific distribution horizons without breaking environment lookups:
1. **The Distributed Pip Module:** Looks inside the global virtual environment `site-packages` layout tree natively.
2. **The Project Source Download:** Automatically locates the internal `sCTkThemes.json` file sitting directly alongside your source widgets.
3. **The Pygubu Designer Track:** Resolves paths back to your active package module folders when executed out of an isolated designer directory tree, painting preview canvas layouts perfectly.

#### 2. The Flexible, Opt-In Theme Engine (`bootstrap_ctk=True`)
Forcing an absolute styling overwrite onto all components would violate modular design rules. By default (`bootstrap_ctk=False`), the registry isolates your rich color structures exclusively for your custom `sCTk*` class subclasses.

When a developer sets `bootstrap_ctk=True`, the engine translates your custom class keys into native tags (e.g., `sCTkButtonPrimary` -> `CTkButton`) and dynamically overlays them straight into CustomTkinter's core memory space (`ctk.ThemeManager.theme`). This allows **plain native CustomTkinter widgets to instantly inherit your custom branding configurations** without modifying a single line of their structural layout code.

#### 3. Order-Independent Variant Control (`mapping_mode`)
To prevent random array sorting loops inside your master JSON stylesheet from accidentally corrupting native defaults, the engine implements two distinct mapping behaviors:
* `mapping_mode="primary"` *(Default and Recommended)*: Only allows `"Primary"` variant blocks to overhaul native CustomTkinter defaults. Auxiliary styling adjustments (like `Secondary`, `Ghost`, or `Tertiary`) are cleanly bypassed, shielding your primary interface guidelines from code displacement updates.
* `mapping_mode="file_order"`: Actively treats the JSON structure as a raw pass-through loop where whichever block variant sits lowest down at the bottom of the document text tree wins the native namespace.

---

### Complete Method Execution Profiles & Path Resolution Examples

#### Example 1: Standard Standalone Initialization (Zero-Configuration Fallbacks)
```python
import sCTkThemes

# Fired with zero arguments right at your app boot frame loop
sCTkThemes.apply_sCTkThemes()
```
*   **What happens on Path Discovery:** The system immediately triggers its relative self-discovery engine. It uses `__file__` to look at the directory where `sCTkThemes.py` is resting on disk. 
    *   *If running your local source checkouts,* it loads the default `sCTkThemes.json` file sitting directly next to your widgets.
    *   *If running via an installed `pip` package,* it looks straight inside the virtual environment's `site-packages/scustomtkinter/` folder, ensuring a safe baseline floor is always found without throwing path exceptions.
*   **What happens to your Widgets:** The master layout configuration mappings are safely stored inside `GLOBAL_THEME_REGISTRY` in memory. Your custom `sCTk*` components load your precise design guidelines perfectly, but plain native `ctk.*` widgets are left completely untouched, rendering in their factory default blue/gray aesthetics.

#### Example 2: The Explicit Custom Location Overrides (Local Customizations)
```python
import sCTkThemes

# A developer provides a distinct relative file tracker location path string
sCTkThemes.apply_sCTkThemes(custom_path="assets/branding/rig_neon_theme.json")
```
*   **What happens on Path Discovery:** The locator engine intercepts the path parameter. It checks if the string is absolute (`os.path.isabs`). Because it is relative, it dynamically converts it against the user's active execution workspace directory (`os.path.abspath`), pointing the stream straight to `/Users/username/project_folder/assets/branding/rig_neon_theme.json`.
*   **What happens to your Widgets:** The package bypasses its own built-in fallback files completely. It pulls the developer's unique, modified theme variables into memory instead, giving the end-user total power to change or maintain separate file configs inside dedicated app asset folders.

#### Example 3: Automatic Project Workspace Detection (Zero-Config Overrides)
```python
import sCTkThemes

# Fired with no arguments, but a modified sCTkThemes.json sits in your project root
sCTkThemes.apply_sCTkThemes()
```
*   **What happens on Path Discovery:** The asset engine reads your active **working directory** (`os.getcwd()`). Before falling back to look inside its own internal installation folders, it proactively checks if a custom file named `sCTkThemes.json` is sitting directly in the developer's project root workspace directory. If a modified file is discovered there, the path engine locks onto it automatically.
*   **What happens to your Widgets:** This gives developers a true zero-config customization lane. They can tweak or entirely rewrite theme hex parameters inside this local file, and the framework natively favors their local workspace rules over the global `site-packages` defaults, keeping production code clean of hardcoded path text.

#### Example 4: Full Global Application Overhaul (Pygubu & Bootstrap Track)
```python
import sCTkThemes

# Fired with full opt-in injection straps and protected primary matching rules
sCTkThemes.apply_sCTkThemes(bootstrap_ctk=True, mapping_mode="primary")
```
*   **What happens on Path Discovery:** If this file is being loaded by **Pygubu Designer** at interface layout design-time out of an isolated execution directory, the self-discovery path traces back to where your registered module library resides on disk. It loads the style registries seamlessly, allowing Pygubu's canvas preview manager to paint your ghost border layouts cleanly with no environment path faults.
*   **What happens to your Widgets:** The memory injector loops through your theme data, drops the leading "s" character, and layers your custom hex files directly into CustomTkinter's live master `ctk.ThemeManager.theme` dictionary array. Because `mapping_mode="primary"` is active, only your principal `"Primary"` data blocks are allowed to overhaul the global namespace. Any auxiliary design entries (like `Secondary`, `Ghost`, or `Tertiary`) are cleanly bypassed, guaranteeing that plain, native `ctk.CTkButton` or `ctk.CTkEntry` elements automatically absorb your primary branding lines without corrupting your composite custom widgets!

#### Example 5: Runtime Dynamic Multi-Theme Profile Loading
```python
import sCTkThemes

# Dynamically swap the entire user interface canvas styling map at runtime
def change_application_profile(profile_type="stealth"):
    if profile_type == "stealth":
        # Load a heavily muted tactical theme file
        sCTkThemes.apply_sCTkThemes(custom_path="themes/stealth_tactical.json", bootstrap_ctk=True)
    else:
        # Revert back to the bright desktop profile file layout
        sCTkThemes.apply_sCTkThemes(custom_path="themes/field_day_bright.json", bootstrap_ctk=True)
```
*   **What happens on Path Discovery:** When the toggle event triggers, the asset engine bypasses package fallback lookups and clears out the old `GLOBAL_THEME_REGISTRY`. It cleanly charts straight to the absolute computed coordinates of the selected custom profile JSON file. 
*   **What happens to your Widgets:** Because `bootstrap_ctk=True` is enabled, the code translates the custom keys, strips variant names, and live-injects the new style updates right over the existing values in CustomTkinter's master `ThemeManager` dictionary cache. The entire interface—both custom `sCTk*` variants and standard native `ctk.*` elements—instantly repaints itself with the new styles without requiring an application restart.

---

### Centralized Stylesheet Setup Reference (`sCTkThemes.json`)

Your primary configuration files structure their dual-color mode list metrics `["LightModeHex", "DarkModeHex"]` like this:

```json
{
    "sCTkButtonPrimary": {
        "fg_color": ["#1A4375", "#1F6AA5"],
        "text_color": ["#FFFFFF", "#FFFFFF"],
        "hover_color": ["#112A4B", "#194A7A"],
        "border_width": 0,
        "corner_radius": 6
    },
    "sCTkOptionMenuSecondary": {
        "fg_color": "transparent",
        "border_color": ["#CBD5E1", "#44403C"],
        "text_color": ["#334155", "#E7E5E4"],
        "border_width": 1,
        "corner_radius": 4
    }
}
```

### Other notes
* **Unmapped Widget Safety Guards:** If a user instantiates a native CustomTkinter widget that has no custom `sCTk` equivalent configured inside your JSON schema, the bootstrapping framework handles it safely by dropping into a passive bypass loop. The unmapped native component cleanly falls back to using CustomTkinter's factory default gray, blue, or dark styles with zero console errors or warnings.
* **Encapsulated API Surface Area:** Providing pass-through wrapper functions inside `sCTkThemes.py` allows your application scripts to execute complete interface mode adjustments through a single file connection, completely removing the requirement to type `import customtkinter as ctk` inside your project view lanes.

---

### Implementation Example & Test Harness

Below is a complete, self-contained test execution script demonstrating how to properly initialize the centralized theme utility engine and manipulate appearance states natively through your wrapped API layer.

```python
#!/usr/bin/python3
"""
sCTkThemes - Standalone Automated Initialization Testing Harness
"""
import customtkinter as ctk
import sCTkThemes  # 🛠️ THE UNIFIED SINGLE ENGINE IMPORT MODEL

if __name__ == "__main__":
    # 1. Fire your centralized asset discovery and loading utility engine.
    # We turn on bootstrap_ctk to force plain native CTk widgets to absorb our designs,
    # and lock mapping_mode to primary to protect our baseline application layout rules.
    sCTkThemes.apply_sCTkThemes(bootstrap_ctk=True, mapping_mode="primary")

    # 2. 🛠️ THE ENCAPSULATION PASS-THROUGH IN ACTION:
    # We alter global operating window appearance states directly via your utility module.
    # This completely eliminates the need to cross-reference or type the 'ctk' namespace!
    sCTkThemes.set_appearance_mode("Dark")

    root = ctk.CTk()
    root.geometry("450x250")
    root.title("sCTkThemes Global Controller Validation Deck")

    # Layout a clean base application container card
    from sCTkFrame import sCTkFrame
    base_card = sCTkFrame(root)
    base_card.pack(expand=True, fill="both", padx=25, pady=25)

    from sCTkLabelPrimary import sCTkLabelPrimary
    lbl_title = sCTkLabelPrimary(base_card, text="CORE FREQUENCY ENGINE OPERATIONAL")
    lbl_title.pack(pady=15)

    # Standard interactive toggle button hook to verify wrapped runtime state changes
    def cycle_display_themes():
        current_env = sCTkThemes.get_appearance_mode().lower()
        target_env = "Light" if current_env == "dark" else "Dark"
        
        sCTkThemes.set_appearance_mode(target_env)
        print(f"Logged Verification Hook -> sCTkThemes.get_appearance_mode() = {sCTkThemes.get_appearance_mode()}")

    btn_mode_shift = ctk.CTkButton(
        base_card, 
        text="Flip UI Theme Mode", 
        command=cycle_display_themes
    )
    btn_mode_shift.pack(pady=10)

    print("--- BOOT INITIALIZATION SEAMLESS PASSTHROUGH ---")
    print(f"Active Runtime Theme Capture Mode = {sCTkThemes.get_appearance_mode().upper()}")
    print("=================================================\n")

    root.mainloop()
```
