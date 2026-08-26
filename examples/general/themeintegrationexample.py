#!/usr/bin/python3
import os
import json
import customtkinter as ctk
from ThemeableWidget import ThemeableWidget

# =====================================================================
# 1. CENTRALIZED BASE MIXIN (ThemeableWidget) & JSON FILE READER
# =====================================================================
THEME_FILE_PATH =  "../sCustomTkinter/sCTKThemes.json"

try:
    with open(THEME_FILE_PATH, "r", encoding="utf-8") as file:
        GLOBAL_THEME_REGISTRY = json.load(file)
except Exception as err:
    raise FileNotFoundError(f"CRITICAL SYSTEM BREAKDOWN: Could not find 'themes.json' -> {err}")


def bootstrap_application_theme():
    """
    Bypasses standard JSON file parsing by injecting native configurations
    directly into CustomTkinter's live memory manager, while leaving custom
    subclasses free to query their configurations independently.
    """
    # Map your custom theme blocks to their core target native component structures
    native_inheritance_map = {
        "sCTkButtonSecondary": "CTkButton"
    }

    forbidden_keys = {"disabled_map", "pressed_map", "alarm_map"}

    for custom_key, configurations in GLOBAL_THEME_REGISTRY.items():
        if custom_key in native_inheritance_map:
            target_native_class = native_inheritance_map[custom_key]

            # Clean out custom nested maps so standard CustomTkinter doesn't reject them
            sanitized_config = {
                k: list(v) if isinstance(v, tuple) else v
                for k, v in configurations.items()
                if k not in forbidden_keys
            }

            # Memory Injection Pass
            if target_native_class in ctk.ThemeManager.theme:
                ctk.ThemeManager.theme[target_native_class].update(sanitized_config)
            else:
                ctk.ThemeManager.theme[target_native_class] = sanitized_config

    print("Success: Live theme memory injection complete!")





# =====================================================================
# 2. CONCRETE CUSTOM CHILD SUBCLASSES
# =====================================================================
class sCTkFrame(ctk.CTkFrame, ThemeableWidget):
    def __init__(self, master=None, **kw):
        ThemeableWidget.__init__(self, kw)
        self._local_defaults = self.final_kw
        super().__init__(master, **self.final_kw)


class sCTkButtonSecondary(ctk.CTkButton, ThemeableWidget):
    def __init__(self, master=None, **kw):
        ThemeableWidget.__init__(self, kw)

        self._local_defaults = self.final_kw
        self._custom_disabled_map = self._widget_disabled_map
        self._custom_pressed_map = self._widget_pressed_map

        super().__init__(master, **self.final_kw)
        self.is_pressed = False

    def set_pressed(self, pressed: bool):
        self.is_pressed = pressed
        self._update_current_visual_state()

    def _update_current_visual_state(self):
        if getattr(self, "is_pressed", False):
            self.configure(
                fg_color=self._custom_pressed_map.get("fg_color"),
                border_color=self._custom_pressed_map.get("border_color"),
                hover_color=self._custom_pressed_map.get("hover_color", self._local_defaults.get("hover_color")),
                text_color=self._custom_pressed_map.get("text_color"),
                hover=False
            )
        else:
            self.configure(
                fg_color=self.final_kw.get("fg_color", self._local_defaults.get("fg_color")),
                border_color=self.final_kw.get("border_color", self._local_defaults.get("border_color")),
                hover_color=self.final_kw.get("hover_color", self._local_defaults.get("hover_color")),
                text_color=self.final_kw.get("text_color", self._local_defaults.get("text_color")),
                hover=True
            )


# =====================================================================
# 3. INTERACTIVE RUNTIME APP EXECUTION
# =====================================================================
if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")  # Set standard base default look first

    # Run our bootstrap injector script to update CustomTkinter's live theme memory
    bootstrap_application_theme()

    root = ctk.CTk()
    root.geometry("500x350")
    root.title("Theme Pipeline Cross-Verification Harness")

    container = sCTkFrame(root)
    container.pack(expand=True, fill="both", padx=20, pady=20)

    # 1. Your Custom Button (Uses custom maps)
    custom_widget = sCTkButtonSecondary(container, text="Custom Button Variant")
    custom_widget.configure(command=lambda: custom_widget.set_pressed(not custom_widget.is_pressed))
    custom_widget.pack(expand=True, padx=40, pady=10)

    # 2. A Standard, Native CustomTkinter Button
    # Notice it has NO access to ThemeableWidget mixins or click tracking codes.
    native_widget = ctk.CTkButton(container, text="Standard Native CTkButton")
    native_widget.pack(expand=True, padx=40, pady=10)

    root.mainloop()
