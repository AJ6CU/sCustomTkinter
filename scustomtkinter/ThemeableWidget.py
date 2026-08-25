#!/usr/bin/python3
"""
ThemeableWidget - Piece 1 of 2

Centralized Theme Management and Global Structural Enforcement.
Natively structures color definitions into true 2-element dark/light tracking payloads
while safely intercepting and sanitizing Pygubu Designer parameters before compilation.
"""
import os
import json
import tkinter as tk
import customtkinter as ctk

# 🛠️ GLOBAL JSON LOADER (Runs only once when the application boots)
THEME_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sCTkThemes.json")

try:
    with open(THEME_FILE_PATH, "r", encoding="utf-8") as file:
        GLOBAL_THEME_REGISTRY = json.load(file)
except Exception as err:
    raise FileNotFoundError(
        f"CRITICAL SYSTEM BREAKDOWN: Centralized theme file '{THEME_FILE_PATH}' "
        f"could not be parsed. Error: {err}."
    )

def default_i18n_translator(value):
    return value

def default_fo_callback(widget):
    pass

def default_image_loader(master, image_name: str, size=None):
    if not image_name: return None
    try:
        if isinstance(image_name, ctk.CTkImage): return image_name
        img_size = size if size else (24, 24)
        from PIL import Image
        pil_img = Image.open(image_name)
        return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=img_size)
    except Exception:
        return None

class ThemeableWidget:
    def __init__(self, kwargs: dict):
        """
        Shared base mixin that resolves global theme lookups via introspection,
        extracts styling options, handles nested map sanitization, and filters
        custom layout properties to prevent native framework validation failures.
        """
        # 🔑 1. PYGUBU UTILITY PARAMETER INTERCEPTION & EXTRIPATION:
        # We pop these completely out of the incoming kwargs pass before running any
        # dictionary loops. This guarantees CustomTkinter never encounters them!
        self.translator = kwargs.pop("translator", default_i18n_translator)
        self.on_first_object_cb = kwargs.pop("on_first_object_cb", default_fo_callback)
        self.image_loader = kwargs.pop("image_loader", default_image_loader)
        self.data_pool = kwargs.pop("data_pool", None)

        class_name = self.__class__.__name__
        theme_defaults = GLOBAL_THEME_REGISTRY.get(class_name) or {}

        if not isinstance(theme_defaults, dict):
            raise KeyError(f"CRITICAL STYLING EXCEPTION: Registry corrupted for type: '{class_name}'...")

        # Global unresolved null traffic check
        for style_key, style_value in theme_defaults.items():
            if isinstance(style_value, dict):
                for sub_key, sub_value in style_value.items():
                    if sub_value is None:
                        raise ValueError(f"Null theme parameter encountered at ['{class_name}']['{style_key}']['{sub_key}']")
            elif style_value is None:
                raise ValueError(f"Null theme parameter encountered at ['{class_name}']['{style_key}']")

        # Nested color map extractions
        self._widget_disabled_map = ThemeableWidget._convert_lists_to_tuples(theme_defaults.get("disabled_map") or {})
        self._widget_pressed_map = ThemeableWidget._convert_lists_to_tuples(theme_defaults.get("pressed_map") or {})
        self._widget_alarm_map = ThemeableWidget._convert_lists_to_tuples(theme_defaults.get("alarm_map") or {})

        forbidden_keys = {"disabled_map", "pressed_map", "alarm_map"}
        CUSTOM_VECTOR_KEYS = {
            "dial_color", "shadow_color", "text_color", "pointer_color",
            "pointer_glow_color", "disabled_text_color", "disabled_dial_color",
            "disabled_dimple_glow", "diameter"
        }

        self.final_kw = {}
        is_vector_widget = any(v_key in theme_defaults for v_key in ["dial_color", "pointer_color", "diameter"])

        active_vector_guards = set(CUSTOM_VECTOR_KEYS)
        if not is_vector_widget:
            active_vector_guards.discard("text_color")

        for key, value in theme_defaults.items():
            if key not in forbidden_keys and key not in active_vector_guards:
                self.final_kw[key] = ThemeableWidget._sanitize_value(key, value)

        for key, value in kwargs.items():
            if value is not None and key not in forbidden_keys and key not in active_vector_guards:
                self.final_kw[key] = ThemeableWidget._sanitize_value(key, value)

        # 🔑 2. AUTOMATED STRING TRANSLATION PASSTHROUGH:
        if "text" in self.final_kw:
            self.final_kw["text"] = self.translator(self.final_kw["text"])
        if "placeholder_text" in self.final_kw:
            self.final_kw["placeholder_text"] = self.translator(self.final_kw["placeholder_text"])
        if "label_text" in self.final_kw:
            self.final_kw["label_text"] = self.translator(self.final_kw["label_text"])

        # 🔑 3. MODERN HIGH-DPI ICON VECTOR UPGRADE PASS:
        if "image" in self.final_kw and isinstance(self.final_kw["image"], str):
            self.final_kw["image"] = self.image_loader(None, self.final_kw["image"])

        self._state = "normal"
    def cget(self, attribute_name: str) -> any:
        """Global Introspective Getter Interceptor."""
        attr_lower = str(attribute_name).lower()
        if attr_lower == "state":
            return getattr(self, "_state", "normal")

        current_lock = str(getattr(self, "_state", "normal")).lower()

        if current_lock == "disabled" and hasattr(self, "_widget_disabled_map"):
            if attr_lower in ("fg_color", "fgcolor"):
                val = self._widget_disabled_map.get("fg_color")
                if val is not None: return self._resolve_color(val)
            if attr_lower in ("text_color", "textcolor"):
                val = self._widget_disabled_map.get("text_color")
                if val is not None: return self._resolve_color(val)
            if attr_lower in ("border_color", "bordercolor"):
                val = self._widget_disabled_map.get("border_color")
                if val is not None: return self._resolve_color(val)

        elif current_lock == "normal" and hasattr(self, "final_kw"):
            if attr_lower in ("fg_color", "fgcolor"):
                val = self.final_kw.get("fg_color")
                if val is not None: return self._resolve_color(val)
            if attr_lower in ("text_color", "textcolor"):
                val = self.final_kw.get("text_color")
                if val is not None: return self._resolve_color(val)
            if attr_lower in ("border_color", "bordercolor"):
                val = self.final_kw.get("border_color")
                if val is not None: return self._resolve_color(val)

        if hasattr(super(), "cget"):
            return super().cget(attribute_name)
        return None

    def _set_appearance_mode(self, mode_string: str):
        """REAL-TIME LIFEHOOK FORWARDER."""
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass

        current_state = str(getattr(self, "_state", "normal")).lower()
        if current_state == "disabled":
            self.configure(state="disabled")
        else:
            self.configure(state="normal")

        if hasattr(self, "_on_theme_changed"):
            try:
                self._on_theme_changed()
            except Exception:
                pass

    def apply_theme(self):
        if hasattr(self, "configure"):
            self.configure(**self.final_kw)

    def _finalize_themeable_lifecycle(self):
        """🔑 POST-COMPILATION LIFECYCLE HOOK PASS: Dispatches object triggers cleanly up to Pygubu."""
        if hasattr(self, "on_first_object_cb") and self.on_first_object_cb:
            try: self.on_first_object_cb(self)
            except Exception: pass

    @classmethod
    def _convert_lists_to_tuples(cls, target_dict: dict) -> dict:
        output = {}
        for k, v in target_dict.items():
            if isinstance(v, list) and len(v) == 2:
                if "transparent" in v: output[k] = "transparent"
                else: output[k] = tuple(v)
            elif isinstance(v, str) and k in ("fg_color", "text_color", "border_color"):
                if v == "transparent": output[k] = "transparent"
                else: output[k] = (v, v)
            else:
                output[k] = v
        return output

    @classmethod
    def _sanitize_value(cls, key, value):
        if key in ("fg_color", "text_color", "border_color", "button_color", "button_hover_color"):
            if isinstance(value, list) and len(value) == 2:
                if "transparent" in value: return "transparent"
                return tuple(value)
            if isinstance(value, tuple) and len(value) == 2:
                if "transparent" in value: return "transparent"
                return value
            if isinstance(value, str):
                if value == "transparent": return "transparent"
                return (value, value)
        if isinstance(value, list):
            return tuple(value)
        return value

    def configure(self, require_redraw=False, **kwargs):
        """Global Framework Interceptor."""
        class_name = self.__class__.__name__

        # 🔑 Clean up Pygubu's incoming keywords dynamically if passed on live runtime updates
        kwargs.pop("translator", None)
        kwargs.pop("on_first_object_cb", None)
        kwargs.pop("image_loader", None)
        kwargs.pop("data_pool", None)

        if "state" in kwargs:
            self._state = str(kwargs.pop("state")).lower()
            if class_name in ("sCTkFrame", "sCTkScrollableFrame", "ThemeAdaptiveTestChassis"):
                actual_state = "normal"
            else:
                actual_state = self._state

            target_map = self._widget_disabled_map if actual_state == "disabled" else self.final_kw
            disabled_txt = target_map.get("text_color")
            disabled_fg = target_map.get("fg_color")
            disabled_border = target_map.get("border_color")

            if disabled_txt is not None: kwargs["text_color"] = self._resolve_color(disabled_txt)
            if disabled_fg is not None: kwargs["fg_color"] = self._resolve_color(disabled_fg)
            if disabled_border is not None: kwargs["border_color"] = self._resolve_color(disabled_border)
            require_redraw = True

        for k, v in list(kwargs.items()):
            if k in ("fg_color", "text_color", "border_color", "button_color", "button_hover_color"):
                if isinstance(v, str) and v != "transparent":
                    kwargs[k] = (v, v)

        if hasattr(super(), "configure"):
            if class_name in ("sCTkFrame", "sCTkScrollableFrame", "ThemeAdaptiveTestChassis"):
                kwargs.pop("state", None)
            else:
                if getattr(self, "_state", "normal") == "disabled":
                    kwargs["state"] = "disabled"

            try:
                import inspect
                sig = inspect.signature(super().configure)
                if "require_redraw" in sig.parameters:
                    return super().configure(require_redraw=require_redraw, **kwargs)
            except Exception:
                pass

            return super().configure(**kwargs)
        return None

    def _resolve_color(self, color_value):
        if color_value == "transparent": return "transparent"
        if isinstance(color_value, (tuple, list)):
            current_mode = str(ctk.get_appearance_mode()).lower()
            mode_idx = 1 if current_mode == "dark" else 0
            return color_value[mode_idx]
        return color_value
