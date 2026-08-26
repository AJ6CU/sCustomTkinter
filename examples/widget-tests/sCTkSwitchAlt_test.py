#!/usr/bin/python3
"""
sCTkSwitchAlt - Piece 1 of 2

An advanced custom composite toggle switch component driven by a high-performance
ctk.CTkCanvas layout engine. Completely eliminates square bounding box artifacts
while providing perfect palette flexibility driven straight out of themes.json.
"""
import tkinter as tk
import customtkinter as ctk
from ThemeableWidget import ThemeableWidget


class sCTkSwitchAlt(ctk.CTkFrame, ThemeableWidget):
    def __init__(self, master=None, text="", command=None, variable=None,
                 textvariable=None, onvalue=1, offvalue=0, state="normal", font=None, **kw):

        # 1. Initialize our shared theme engine and load from the unified block
        ThemeableWidget.__init__(self, kw)
        theme_dict = ThemeableWidget._get_theme_dict(self) if hasattr(ThemeableWidget, "_get_theme_dict") else {}
        self._switch_theme_profile = dict(theme_dict.get("sCTkSwitch", {}))
        self._custom_disabled_map = self._switch_theme_profile.get("disabled_map", {})

        # 2. Scrub theme dictionaries clean before parent container initialization passes
        for pop_key in ["fg_color", "progress_color", "button_color", "button_hover_color",
                        "text_color", "font", "disabled_map"]:
            kw.pop(pop_key, None)

        # 3. Initialize our master layout background tracking panel frame
        super().__init__(master, fg_color="transparent", border_width=0, **kw)

        # 4. Hydrate internal configuration state arrays
        self._master_ref = master
        self._text_payload = text
        self._command_payload = command
        self._variable_payload = variable
        self._textvariable_payload = textvariable
        self._onvalue_payload = onvalue
        self._offvalue_payload = offvalue
        self._font_payload = font if font is not None else self._switch_theme_profile.get("font",
                                                                                          ("Arial", 14, "normal"))

        self._state = "normal" if str(state).lower() == "normal" else "disabled"
        self._is_toggled = False
        self._trace_name = None

        # 5. Instantiate a vector canvas to render pure geometry lines safely
        self.canvas_core = ctk.CTkCanvas(
            self, width=44, height=22, highlightthickness=0,
            bg=self._apply_parent_bg_handshake(master)
        )
        self.canvas_core.pack(side="left", padx=(0, 8))

        # 6. Mount the descriptive typography display label
        self.label_txt = ctk.CTkLabel(self, text=self._text_payload, font=self._font_payload)
        self.label_txt.pack(side="left")

        # 7. Bind mouse tracking triggers straight across the components
        for component in [self, self.canvas_core, self.label_txt]:
            component.bind("<Button-1>", self._handle_switch_click_gesture)

        self._initialize_variable_hooks()
        self._initialize_textvariable_hooks()
        self._apply_custom_theme_colors()

    def _apply_parent_bg_handshake(self, master) -> str:
        """🔑 FIXED COLOR PIPELINE: Unpacks parent frames and intercepts 'transparent' tokens safely."""
        dark_fallback, light_fallback = "#1C1C1C", "#F1F5F9"
        try:
            if hasattr(master, "cget"):
                color_tuple = master.cget("fg_color")
                if isinstance(color_tuple, (list, tuple)) and len(color_tuple) == 2:
                    val = str(color_tuple[0 if ctk.get_appearance_mode().lower() == "light" else 1]).strip()
                else:
                    val = str(color_tuple).strip()

                # Intercept un-renderable transparent canvas tokens forcefully
                if val.lower() == "transparent":
                    return light_fallback if ctk.get_appearance_mode().lower() == "light" else dark_fallback
                return val
        except Exception:
            pass
        return light_fallback if ctk.get_appearance_mode().lower() == "light" else dark_fallback

    def _initialize_variable_hooks(self):
        if self._variable_payload is not None:
            try:
                val = self._variable_payload.get()
                self._is_toggled = (val == self._onvalue_payload or str(val).lower() in ("true", "1", "yes", "on"))
            except Exception:
                pass

    def _initialize_textvariable_hooks(self):
        if self._trace_name and self._textvariable_payload:
            try:
                self._textvariable_payload.trace_remove("write", self._trace_name)
            except Exception:
                pass
        if self._textvariable_payload is not None:
            try:
                self.label_txt.configure(text=str(self._textvariable_payload.get()))
                self._trace_name = self._textvariable_payload.trace_add(
                    "write", lambda *a: self.label_txt.configure(text=str(self._textvariable_payload.get()))
                )
            except Exception:
                pass

    def _handle_switch_click_gesture(self, event):
        if self._state == "disabled": return "break"
        self._is_toggled = not self._is_toggled

        if self._variable_payload is not None:
            try:
                self._variable_payload.set(self._onvalue_payload if self._is_toggled else self._offvalue_payload)
            except Exception:
                pass

        self._apply_custom_theme_colors()

        if self._command_payload:
            active_val = self._onvalue_payload if self._is_toggled else self._offvalue_payload
            try:
                self._command_payload(active_val)
            except TypeError:
                self._command_payload()
        return "break"

    def _apply_custom_theme_colors(self):
        """🔑 THE VECTOR RENDERING CORE: Clears pixel lines and redraws clean geometry primitives dynamically."""
        if not hasattr(self, "canvas_core") or not self.canvas_core.winfo_exists(): return
        self.canvas_core.delete("all")

        is_disabled = self._state == "disabled"
        m = self._custom_disabled_map if is_disabled else self._switch_theme_profile
        dm = self._custom_disabled_map

        d_b_text = self._resolve_color(dm.get("text_color", ("#94A3B8", "gray50")))

        if is_disabled:
            resolved_txt = d_b_text
            resolved_knob = self._resolve_color(dm.get("button_color", ("#8A94A6", "#94A3B8")))
            resolved_track = self._resolve_color(dm.get("fg_color", ("#D8DEE9", "#4C566A")))
        else:
            resolved_txt = self._resolve_color(m.get("text_color", ("#1F2937", "#F9FAFB")))
            resolved_knob = self._resolve_color(m.get("button_color", ("#FFFFFF", "#CBD5E1")))
            resolved_track = self._resolve_color(
                m.get("progress_color" if self._is_toggled else "fg_color", ("#1A4375", "#1F6AA5")))

        self.label_txt.configure(text_color=resolved_txt)

        # 1. Draw the rounded capsule track geometry safely into the vector layer
        self.canvas_core.create_oval(2, 2, 22, 20, fill=resolved_track, outline=resolved_track)
        self.canvas_core.create_oval(22, 2, 42, 20, fill=resolved_track, outline=resolved_track)
        self.canvas_core.create_rectangle(12, 2, 32, 20, fill=resolved_track, outline=resolved_track)

        # 2. Calculate knob handle horizontal coordinates cleanly based on toggle states
        knob_x_start = 23 if self._is_toggled else 5

        # 3. 🔑 PROPORTIONAL SYMMETRY FIX: Expanded vertical diameter bounds to exactly 16 pixels.
        # This matches CustomTkinter's standard switch knob scale perfectly!
        self.canvas_core.create_oval(
            knob_x_start, 3, knob_x_start + 16, 19,
            fill=resolved_knob, outline=resolved_knob
        )

    def configure(self, require_redraw=None, **kwargs):
        if require_redraw is not None and not kwargs and isinstance(require_redraw, str):
            if require_redraw == "state": return ('state', 'state', 'State', 'normal',
                                                  str(getattr(self, "_state", "normal")))
            return super().configure(require_redraw)

        if isinstance(require_redraw, dict): kwargs = require_redraw | kwargs
        if "state" in kwargs: self._state = str(kwargs.pop("state")).lower()
        if "text" in kwargs: self._text_payload = kwargs.pop("text"); self.label_txt.configure(text=self._text_payload)
        if "font" in kwargs: self._font_payload = kwargs.pop("font"); self.label_txt.configure(font=self._font_payload)
        if "variable" in kwargs: self._variable_payload = kwargs.pop("variable"); self._initialize_variable_hooks()
        if "textvariable" in kwargs: self._textvariable_payload = kwargs.pop(
            "textvariable"); self._initialize_textvariable_hooks()

        if kwargs: super().configure(**kwargs)
        self._apply_custom_theme_colors()

    config = configure

    def cget(self, attribute_name: str):
        pname = str(attribute_name).lower()
        if pname == "state": return getattr(self, f"_{pname}")
        if pname == "text": return self._text_payload
        if pname == "font": return self._font_payload
        if pname == "variable": return self._variable_payload
        if pname == "textvariable": return self._textvariable_payload
        return super().cget(attribute_name)

    def _set_appearance_mode(self, mode_string: str):
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        if hasattr(self, "canvas_core") and self.canvas_core.winfo_exists():
            self.canvas_core.configure(bg=self._apply_parent_bg_handshake(self._master_ref))
        self._apply_custom_theme_colors()

    def state(self, mode: str = None) -> str:
        if mode is None: return str(getattr(self, "_state", "normal")).lower()
        self.configure(state=mode)
        return mode

    def get_state(self) -> str:
        return self.state()

    def get(self):
        return self._onvalue_payload if self._is_toggled else self._offvalue_payload

    def set(self, value):
        self._is_toggled = (value == self._onvalue_payload or str(value).lower() in ("true", "1", "yes", "on"))
        self._apply_custom_theme_colors()


# =====================================================================
# TESTING HARNESS IMPORTS & SETUP
# =====================================================================

# !/usr/bin/python3
"""
sCustomTkinter Dual Switch Validation Bench

A standalone real-time execution harness designed to test and compare the 
operational and visual look configurations of sCTkSwitch and sCTkSwitchAlt.
"""
import customtkinter as ctk
import sCTkThemes
from sCTkFrame import sCTkFrame
from sCTkLabelSecondary import sCTkLabelSecondary
from sCTkSwitch import sCTkSwitch
from sCTkSwitchAlt import sCTkSwitchAlt

if __name__ == "__main__":
    sCTkThemes.apply_sCTkThemes()

    root = ctk.CTk()
    root.geometry("520x460")
    root.title("sCustomTkinter Dual Switch Validation Bench")
    root.configure(fg_color=("#F1F5F9", "#1C1C1C"))

    base = sCTkFrame(root, border_width=2)
    base.pack(expand=True, fill="both", padx=30, pady=30)

    # Configure the internal panel weights cache grid system to force left alignment
    base.grid_columnconfigure(0, weight=1)

    # =====================================================================
    # 🎛️ MODULE 1: Standard Switch (Native Inheritance Variant)
    # =====================================================================
    # 🔑 LEFT REALIGNMENT PASS: Configured with sticky="w" to lock alignment flush left!
    lbl_std = sCTkLabelSecondary(base, text="[Standard ctk.CTkSwitch Subclass]", font=("Arial", 11, "bold"))
    lbl_std.grid(row=0, column=0, padx=40, pady=(15, 2), sticky="w")

    switch_std = sCTkSwitch(
        base,
        text="Standard Pre-Amp Link Channel",
        command=lambda val: print(f"Standard Pass -> State Value: {val}")
    )
    switch_std.grid(row=1, column=0, padx=40, pady=10, sticky="w")

    # =====================================================================
    # 🎛️ MODULE 2: Alternative Switch (Custom Composite Drawing Variant)
    # =====================================================================
    lbl_alt = sCTkLabelSecondary(base, text="[Alternative sCTkSwitchAlt Custom Draw]", font=("Arial", 11, "bold"))
    lbl_alt.grid(row=2, column=0, padx=40, pady=(25, 2), sticky="w")

    switch_alt = sCTkSwitchAlt(
        base,
        text="Advanced VFO Frequency Lock Link",
        command=lambda val: print(f"Alternative Pass -> State Value: {val}")
    )
    switch_alt.grid(row=3, column=0, padx=40, pady=10, sticky="w")


    # =====================================================================
    # 🛠️ INTERACTIVE BENCH LOOK CONTROLLERS
    # =====================================================================
    def toggle_framework_locks():
        """Toggles operational locked states across both components smoothly."""
        current_std = switch_std.get_state()
        target = "disabled" if current_std == "normal" else "normal"

        switch_std.configure(state=target)
        switch_alt.configure(state=target)

        btn_lock.configure(
            text="Unlock Panel (Set 'normal')" if target == "disabled" else "Lock Panel (Set 'disabled')")


    def toggle_skin_preference():
        """Toggles between Light and Dark application window appearances dynamically."""
        ctk.set_appearance_mode("Light" if ctk.get_appearance_mode() == "Dark" else "Dark")


    # Arrange execution buttons layout grids at the lower edge of the screen capsule
    btn_lock = ctk.CTkButton(root, text="Lock Panel (Set 'disabled')", command=toggle_framework_locks)
    btn_lock.pack(side="bottom", pady=5)

    btn_skin = ctk.CTkButton(root, text="Toggle UI Light/Dark Appearance", command=toggle_skin_preference)
    btn_skin.pack(side="bottom", pady=5)

    root.mainloop()

