#!/usr/bin/python3
"""
ThemeableWidget

Shared __init__-time theme resolution and color-utility mixin for sCustomTkinter widgets.

Scope note: earlier versions of this class also defined configure()/cget()/_set_appearance_mode()
overrides, intended as shared runtime color-swapping logic used by every widget. Those methods are
removed here because they were structurally unreachable. Every sCTk* widget declares its native CTk
base class before ThemeableWidget (e.g. `class sCTkComboBox(ctk.CTkComboBox, ThemeableWidget)`), so
Python's MRO always resolves super().configure()/cget() calls to the native CTk widget -- and beneath
it, tkinter.Misc -- first. Both terminate the call chain without ever reaching ThemeableWidget. This
holds even for a hypothetical widget that defines neither configure() nor cget() itself, since
tkinter.Misc (an ancestor of every CTk widget) already implements both ahead of ThemeableWidget in
the MRO. Verified empirically against the real widget files during the docs/coding audit, not just
inferred from the class layout.

What this class DOES provide, and is genuinely used by every widget:
  - __init__: resolves this widget's block from sCTkThemes.json, merges it with any keyword
    overrides passed to the constructor, and builds self.final_kw plus the disabled/pressed/alarm/
    readonly color maps (self._widget_disabled_map / _widget_pressed_map / _widget_alarm_map /
    _widget_readonly_map).
  - _resolve_color / _convert_lists_to_tuples / _sanitize_value: color-normalization helpers,
    called directly (via self.) by each widget's own visual-state logic.
  - _finalize_themeable_lifecycle: Pygubu lifecycle hook, called directly by each widget's __init__.
  - apply_theme: convenience method that re-applies self.final_kw via self.configure(). Because this
    calls self.configure() (not super().configure()), it correctly dispatches to whichever configure()
    the actual widget instance defines -- unlike the removed methods, this one isn't dead code.

Each widget's own configure()/cget()/_set_appearance_mode() override is responsible for its own
runtime color-swapping, because each widget needs a different set of properties (and, for buttons,
a different state model -- normal/disabled/pressed/alarm) than any single shared method could know
about without hardcoding every widget's valid property list in one place. See the docs audit notes
for the reasoning behind not trying to re-centralize this.

RUN-ONCE GUARD: __init__ now sets self._themeable_widget_initialized = True on its first call per
instance, and returns immediately on any subsequent call. This matters specifically for widgets that
compose an already-themed sCTk widget as their own base class (e.g. sCTkSelector(sCTkFrame,
ThemeableWidget), sCTkTableview(sCTkScrollableFrame, ThemeableWidget)) -- without it, the base
widget's own internal ThemeableWidget.__init__ call (triggered when the composite widget's
super().__init__() cascades into it) would run a second time on the same instance, silently
overwriting self.final_kw. See __init__'s own docstring for the full reasoning.
"""
import os
import json
import tkinter as tk
import customtkinter as ctk


# GLOBAL THEME REGISTRY POOL
GLOBAL_THEME_REGISTRY = {}


def load_initial_framework_themes():
    """Idempotent startup hook to pull themes.json safely without dropping imports."""
    global GLOBAL_THEME_REGISTRY
    if GLOBAL_THEME_REGISTRY:
        return

    local_user_workspace = os.path.normpath(os.path.join(os.getcwd(), "sCTkThemes.json"))

    # FIXED DIRECTORY COORDINATES: Look inside your actual bundled assets folder
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    bundled_library_default = os.path.normpath(os.path.join(current_script_dir, "assets", "sCTkThemes.json"))

    theme_target = local_user_workspace if os.path.exists(local_user_workspace) else bundled_library_default

    try:
        if os.path.exists(theme_target):
            with open(theme_target, "r", encoding="utf-8") as file:
                GLOBAL_THEME_REGISTRY = json.load(file)
        else:
            # Fallback empty profile dictionary so your widget protections don't crash if files vanish
            GLOBAL_THEME_REGISTRY = {}
    except Exception as err:
        print(f"sCustomTkinter System Warning -> Could not parse theme layout tracking: {err}")
        GLOBAL_THEME_REGISTRY = {}


# NATIVE INITIALIZATION PASS: Safe, unblocked startup invocation
load_initial_framework_themes()


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


def parse_list_property(value, default=None):
    """
    Parse a list-valued widget property from any of the formats this library
    and Pygubu Designer produce, returning a clean list of stripped strings.

    WHY THIS EXISTS. Before this function, seven widgets each parsed their own
    list property and no two agreed:

        sCTkTableview.columns     comma split, stripped
        sCTkSelector.items        ast.literal_eval only
        sCTkDialSelector.labels   literal_eval in __init__, but a plain
                                  comma split with NO quote stripping in
                                  configure() -- so the same value parsed
                                  differently depending on when it was set
        sCTkFileExplorer.filetypes   three different implementations, in one file
        sCTkPathChooser.filetypes    literal_eval
        sCTkSpinbox.values           shlex.split when no comma is present

    The user-visible consequence was that every widget wanted a different
    format for the same kind of property, and the Designer's inspector gave no
    hint which. Entering "AM, FM, LSB" into a dial produced labels with leading
    spaces; the same string in a Tableview worked correctly.

    Accepts, in order of preference:
      - an actual list or tuple, returned with each element stripped
      - a Python literal: "['A', 'B']" or "('A', 'B')"
      - a bare comma-separated string: "A, B, C"

    Empty input returns `default` (or an empty list), never None, so callers
    can iterate the result unconditionally.

    Deliberately does NOT accept space separation. sCTkSpinbox alone supported
    it via shlex, which means "Meat Loaf" was two values there and one value
    everywhere else -- surprising enough to be worth dropping rather than
    spreading. Quote a value containing a comma if you need one.

    Args:
        value: The raw property value, in any of the forms above.
        default: Returned when value is empty or unparseable. Defaults to [].

    Returns:
        A list of stripped strings.
    """
    if default is None:
        default = []

    if value is None:
        return list(default)

    if isinstance(value, (list, tuple)):
        cleaned = [str(item).strip() for item in value]
        return [item for item in cleaned if item] or list(default)

    text = str(value).strip()
    if not text:
        return list(default)

    # Python literal form, as written by older .ui files and by the Selector's
    # own inspector default of "['Item 1', 'Item 2']".
    if text[0] in "[(":
        try:
            import ast
            parsed = ast.literal_eval(text)
            if isinstance(parsed, (list, tuple)):
                cleaned = [str(item).strip() for item in parsed]
                return [item for item in cleaned if item] or list(default)
        except (ValueError, SyntaxError):
            # Malformed literal -- fall through to the comma split below, which
            # handles "[A, B]" (unquoted, not valid Python) correctly.
            pass

    # Bare comma-separated form. Brackets and quotes are stripped so a
    # half-formed literal still parses the way the user obviously intended.
    text = text.strip("[]()")
    return [item.strip().strip("\"'") for item in text.split(",")
            if item.strip().strip("\"'")] or list(default)


class ThemeableWidget:
    def __init__(self, kwargs: dict):
        """
        Shared base mixin that resolves global theme lookups via introspection,
        extracts styling options, handles nested map sanitization, and filters
        custom layout properties to prevent native framework validation failures.

        RUN-ONCE GUARD: if a widget composes an already-themed sCTk widget as its
        own base class (e.g. sCTkSelector(sCTkFrame, ThemeableWidget)), that base
        widget's own __init__ calls ThemeableWidget.__init__ again internally when
        super().__init__() cascades into it. Without a guard, this second call
        would run in full -- looking up the theme block again via
        self.__class__.__name__ (which is always the OUTERMOST class, e.g.
        "sCTkSelector", regardless of which base class's code is currently
        executing) and completely overwriting self.final_kw from scratch. For a
        widget that forwards its full final_kw to super().__init__() (like
        sCTkSelector), this second call happens to be a harmless no-op today,
        since it's re-merging already-merged data onto itself -- but that's
        incidental, not guaranteed, and fragile against future changes. For a
        widget that only forwards a few explicit constructor arguments (like
        sCTkTableview passing just master/width/height), the second call is
        actively destructive: it replaces the correctly-built final_kw with a far
        sparser one, silently discarding whatever the first call correctly
        resolved. This guard makes ThemeableWidget.__init__ idempotent per
        instance, the same way a C header's #ifndef/#define guard prevents a
        header's contents from being processed twice -- the first call does the
        real work and marks itself done; every subsequent call on the same
        instance returns immediately.
        """
        if getattr(self, "_themeable_widget_initialized", False):
            return
        self._themeable_widget_initialized = True

        # 1. PYGUBU UTILITY PARAMETER INTERCEPTION & EXTRIPATION:
        # We pop these completely out of the incoming kwargs pass before running any
        # dictionary loops. This guarantees CustomTkinter never encounters them!
        self.translator = kwargs.pop("translator", default_i18n_translator)
        self.on_first_object_cb = kwargs.pop("on_first_object_cb", default_fo_callback)
        self.image_loader = kwargs.pop("image_loader", default_image_loader)
        self.data_pool = kwargs.pop("data_pool", None)

        # _THEME_BLOCK_NAME lets a subclass declare which theme block it reads,
        # instead of the lookup always using its own class name.
        #
        # Needed by the Pygubu Designer preview subclasses: sCTkTableviewForPreview,
        # sCTkSelectorForPreview and friends exist only to expose internals so the
        # Designer can select them, but their class names have no theme block --
        # so the lookup found nothing, final_kw came back empty, and any widget
        # with fail-loud key validation raised KeyError instead of rendering.
        #
        # Also useful outside the Designer: a subclass of sCTkButtonPrimary can
        # now inherit its parent's theme rather than silently losing it.
        class_name = getattr(self, "_THEME_BLOCK_NAME", None) or self.__class__.__name__
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
        # readonly_map: added to support a genuine three-state model (normal/
        # readonly/disabled) on sCTkEntryPrimary/Secondary, for widgets like
        # sCTkSpinbox that need ttk.Spinbox's real readonly semantics (arrows
        # stay clickable, typing is blocked) rather than collapsing everything
        # non-disabled into "normal". Added here, not as an Entry-specific
        # hack, so any future widget can use the same pattern.
        self._widget_readonly_map = ThemeableWidget._convert_lists_to_tuples(theme_defaults.get("readonly_map") or {})

        forbidden_keys = {"disabled_map", "pressed_map", "alarm_map", "readonly_map"}
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

        # 2. AUTOMATED STRING TRANSLATION PASSTHROUGH:
        if "text" in self.final_kw:
            self.final_kw["text"] = self.translator(self.final_kw["text"])
        if "placeholder_text" in self.final_kw:
            self.final_kw["placeholder_text"] = self.translator(self.final_kw["placeholder_text"])
        if "label_text" in self.final_kw:
            self.final_kw["label_text"] = self.translator(self.final_kw["label_text"])

        # 3. MODERN HIGH-DPI ICON VECTOR UPGRADE PASS:
        if "image" in self.final_kw and isinstance(self.final_kw["image"], str):
            self.final_kw["image"] = self.image_loader(None, self.final_kw["image"])

        # NOTE: self._state is set here for backward compatibility, but as of this audit
        # no reviewed widget reads it correctly via a reachable code path (the one that
        # did -- sCTkSegmentedButton -- was doing so by mistake; see its own fix notes).
        # Left in place rather than removed until the remaining widgets are audited.
        self._state = "normal"

    def apply_theme(self):
        """
        Re-applies self.final_kw via self.configure(). This calls self.configure(), not
        super().configure(), so it correctly dispatches to whichever configure() the
        actual widget instance defines -- this method is NOT dead code like the removed
        configure()/cget() overrides were.
        """
        if hasattr(self, "configure"):
            self.configure(**self.final_kw)

    def _finalize_themeable_lifecycle(self):
        """POST-COMPILATION LIFECYCLE HOOK PASS: Dispatches object triggers cleanly up to Pygubu."""
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

    def _resolve_color(self, color_value):
        if color_value == "transparent": return "transparent"
        if isinstance(color_value, (tuple, list)):
            current_mode = str(ctk.get_appearance_mode()).lower()
            mode_idx = 1 if current_mode == "dark" else 0
            return color_value[mode_idx]
        return color_value
