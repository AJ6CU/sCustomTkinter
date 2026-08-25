#!/usr/bin/python3
"""
sCTkThemes

Centralized package asset discovery and core theme configuration engine.
Wraps CustomTkinter native parameters to provide a single, unified import model.
"""
import os
import json
import customtkinter as ctk
from ThemeableWidget import GLOBAL_THEME_REGISTRY


def apply_sCTkThemes(custom_path=None, bootstrap_ctk=False, mapping_mode="primary"):
    """
    Universal Package Asset Locator & Bootstrapper.
    Discovers style shapes from explicit paths, root workspaces, or internal
    defaults, then optionally injects them into CustomTkinter core memory arrays.
    """
    if custom_path:
        if os.path.isabs(custom_path):
            target_file = custom_path
        else:
            target_file = os.path.abspath(custom_path)
    else:
        project_root_override = os.path.abspath(os.path.join(os.getcwd(), "sCTkThemes.json"))
        if os.path.exists(project_root_override):
            target_file = project_root_override
        else:
            library_dir = os.path.dirname(os.path.abspath(__file__))
            target_file = os.path.join(library_dir, "sCTkThemes.json")

    if not os.path.exists(target_file):
        target_file = os.path.abspath("sCTkThemes.json")

    try:
        with open(target_file, "r") as f:
            data = json.load(f)
            GLOBAL_THEME_REGISTRY.clear()
            GLOBAL_THEME_REGISTRY.update(data)

            if bootstrap_ctk:
                mode = str(mapping_mode).strip().lower()
                for s_widget_key, style_dict in data.items():
                    if s_widget_key.startswith("sCTk"):
                        if mode == "primary":
                            is_primary = "Primary" in s_widget_key
                            is_secondary_variant = any(v in s_widget_key for v in ["Secondary", "Ghost", "Tertiary"])
                            if is_secondary_variant and not is_primary:
                                continue

                        native_key = s_widget_key[1:]
                        if mode == "primary" and "Primary" in native_key:
                            native_key = native_key.replace("Primary", "")
                        else:
                            for suffix in ["Primary", "Secondary", "Tertiary", "Ghost"]:
                                if suffix in native_key:
                                    native_key = native_key.replace(suffix, "")
                                    break

                        clean_native_props = {}
                        for prop_key, prop_val in style_dict.items():
                            if prop_key not in ("disabled_map", "pressed_map", "alarm_map"):
                                clean_native_props[prop_key] = prop_val

                        if native_key in ctk.ThemeManager.theme:
                            ctk.ThemeManager.theme[native_key].update(clean_native_props)
                        else:
                            ctk.ThemeManager.theme[native_key] = clean_native_props

                print(f"sCustomTkinter: Successfully applied styles and bootstrapped CTk memory via -> {target_file}")
            else:
                print(f"sCustomTkinter: Successfully applied styles via -> {target_file}")
    except Exception as e:
        print(f"sCustomTkinter Registry Warning: Could not parse theme layout file ({e})")


# =====================================================================
# 🛠️ NATIVE CUSTOMTKINTER WRAPPER ROUTINES
# =====================================================================

def set_appearance_mode(mode_string: str):
    """
    Wraps ctk.set_appearance_mode natively.
    Options: "System" (OS-tracked preference), "Dark", or "Light".
    """
    ctk.set_appearance_mode(mode_string)


def set_default_color_theme(theme_name_or_path: str):
    """
    Wraps ctk.set_default_color_theme natively.
    Allows passing standard built-in themes ("blue", "green", "dark-blue")
    or explicit relative/absolute paths to standalone CTk .json theme files.
    """
    ctk.set_default_color_theme(theme_name_or_path)


def get_appearance_mode() -> str:
    """
    Wraps ctk.get_appearance_mode natively.
    Returns the currently active interface mode string (e.g. "Light" or "Dark").
    """
    return str(ctk.get_appearance_mode())


# !/usr/bin/python3
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