#!/usr/bin/python3
"""
sCTkTabview - Piece 1 of 2

A theme-compliant custom multi-page tab container layout.
Inherits from sCTkTabviewUI and ThemeableWidget to manage dense cockpit dashboard
panels safely with full live theme repaint loops out of themes.json.
"""
import tkinter as tk
import customtkinter as ctk
import sCTkTabviewui as baseui
from ThemeableWidget import ThemeableWidget

class sCTkTabview(baseui.sCTkTabviewUI, ThemeableWidget):
    def __init__(self, master=None, **kw):

        # 1. Run shared mixin logic first to parse master themes.json safely
        ThemeableWidget.__init__(self, kw)

        # 2. Store your custom memory deep-copy maps cleanly onto instance structures
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = self._local_defaults.get("disabled_map", {})
        self._custom_current_state = "normal"

        # 3. Intercept the non-standard font key locally before initialization pass
        target_font = self.final_kw.pop("font", self._local_defaults.get("font", ("Arial", 13, "normal")))

        # 4. Initialize parent class natively with clean frame-compliant attributes safely
        super().__init__(master, **self.final_kw)

        # 5. Forward the extracted font parameter down to the native layout bar safely
        if hasattr(self, "_segmented_button") and self._segmented_button:
            try:
                self._segmented_button.configure(font=target_font)
            except Exception:
                pass

        # 6. Apply styles and complete lifecycle
        self._apply_custom_theme_colors()
        self._finalize_themeable_lifecycle()

    def _apply_custom_theme_colors(self):
        """Cascades structural look profiles directly out of your centralized stylesheet json."""
        if not hasattr(self, "_segmented_button") or not self._segmented_button:
            return

        is_disabled = (self._custom_current_state == "disabled")
        m = self._custom_disabled_map if is_disabled else self._local_defaults

        # Resolve light/dark text colors cleanly from the parsed theme dictionaries
        resolved_txt = self._resolve_color(m.get("text_color", ("#1F2937", "#F9FAFB")))

        if is_disabled:
            # Re-compile clean keyword payloads to flatten background tracks safely when locked
            updates = {
                "fg_color": self._resolve_color(m.get("segmented_button_fg_color", ("#E5E7EB", "#334155"))),
                "selected_color": self._resolve_color(m.get("segmented_button_selected_color", ("#CBD5E1", "#475569"))),
                "selected_hover_color": self._resolve_color(m.get("segmented_button_selected_color", ("#CBD5E1", "#475569"))),
                "unselected_color": self._resolve_color(m.get("segmented_button_unselected_color", ("#F1F5F9", "#1F2937"))),
                "unselected_hover_color": self._resolve_color(m.get("segmented_button_unselected_color", ("#F1F5F9", "#1F2937")))
            }
        else:
            updates = {
                "fg_color": self._resolve_color(m.get("segmented_button_fg_color", ("#E2E8F0", "#1E293B"))),
                "selected_color": self._resolve_color(m.get("segmented_button_selected_color", ("#1A4375", "#1F6AA5"))),
                "selected_hover_color": self._resolve_color(m.get("segmented_button_selected_hover_color", ("#15375B", "#1A5885"))),
                "unselected_color": self._resolve_color(m.get("segmented_button_unselected_color", ("#F8FAFC", "#334155"))),
                "unselected_hover_color": self._resolve_color(m.get("segmented_button_unselected_hover_color", ("#E2E8F0", "#475569")))
            }

        try:
            self._segmented_button.configure(**updates)
        except Exception:
            pass

        # Intercept child buttons array dictionary to forcefully assign text color mappings cleanly
        if hasattr(self._segmented_button, "_buttons_dict") and self._segmented_button._buttons_dict:
            for button in self._segmented_button._buttons_dict.values():
                try:
                    button.configure(text_color=resolved_txt)
                except Exception:
                    pass
    def state(self, mode: str = None) -> str:
        """🔑 THE CORE DESIGN PATTERN GATEWAY: Aligns fully with all other repository widgets!"""
        if mode is None:
            return str(getattr(self, "_custom_current_state", "normal")).lower()

        target_mode = str(mode).lower()
        if target_mode in ("normal", "enabled", "active"):
            self._custom_current_state = "normal"
            if hasattr(self, "_segmented_button") and self._segmented_button:
                try: self._segmented_button.configure(state="normal")
                except Exception: pass
        elif target_mode == "disabled":
            self._custom_current_state = "disabled"
            if hasattr(self, "_segmented_button") and self._segmented_button:
                try: self._segmented_button.configure(state="disabled")
                except Exception: pass

        self._apply_custom_theme_colors()
        return self._custom_current_state

    # 🔑 API CONTINUITY PASS-THROUGHS
    def get_state(self) -> str:
        return self.state()

    def bind(self, sequence=None, func=None, add=None):
        """Intercepts designer click loops to prevent unexpected NotImplementedError crashes."""
        try:
            return tk.Frame.bind(self, sequence, func, add)
        except Exception:
            return ""

    def _set_appearance_mode(self, mode_string: str):
        if hasattr(super(), "_set_appearance_mode"):
            try: super()._set_appearance_mode(mode_string)
            except Exception: pass
        self._apply_custom_theme_colors()


# !/usr/bin/python3
"""
sCTkTabview - Interactive Functional Verification Bench

A standalone real-time execution harness designed to validate page additions,
live look changes, tab layout nesting, and composite state locking loops.
"""
import customtkinter as ctk
import sCTkThemes
from sCTkFrame import sCTkFrame
from sCTkLabelPrimary import sCTkLabelPrimary
from sCTkTabview import sCTkTabview

if __name__ == "__main__":
    # 1. Initialize centralized framework look records natively out of themes.json
    sCTkThemes.apply_sCTkThemes()

    root = ctk.CTk()
    root.geometry("560x420")
    root.title("sCTkTabview Container Validation Bench")
    root.configure(fg_color=("#F1F5F9", "#1C1C1C"))

    # 2. Mount custom master backplane frame capsule container
    base = sCTkFrame(root, border_width=2)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    # 3. Instantiate our custom multi-page tab container widget cleanly
    widget = sCTkTabview(base)
    widget.pack(expand=True, fill="both", padx=10, pady=10)

    # Define our targeted operational dashboard page labels string array
    tab_pages = ["Transceiver Settings", "Audio Filters", "System Logs"]

    # 4. 🔑 NESTED TAB FRAME GENERATION PASS:
    # Loops through the strings, adds the tabs, and nests an sCTkFrame containing
    # an sCTkLabelPrimary placeholder inside every viewport page cleanly!
    for page_name in tab_pages:
        # Add the structural landing track tab layer to the widget chassis
        widget.add(page_name)

        # Grab the native container reference object assigned to this specific tab page
        page_viewport = widget.tab(page_name)

        # Mount an inner sCTkFrame container capsule to pad out the sub-tab view workspace
        inner_frame = sCTkFrame(page_viewport, border_width=1, corner_radius=8)
        inner_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Drop a high-visibility sCTkLabelPrimary component right in the center slot of the sub-frame
        test_label = sCTkLabelPrimary(inner_frame, text=f"Test Contents — {page_name}")
        test_label.pack(expand=True, fill="none", padx=20, pady=20)


    # =====================================================================
    # 🛠️ INTERACTIVE BENCH OPERATION CONTROLLERS
    # =====================================================================
    def toggle_tab_lock():
        """Toggles active data page switches and flattens tab button fills."""
        current = widget.state()
        target = "disabled" if current == "normal" else "normal"
        widget.state(target)
        btn_lock.configure(
            text="Unlock Tabview Navigation" if target == "disabled" else "Lock Tabview (Set 'disabled')")
        print(f"Logged State Verification Hook -> widget.state() = {widget.state()}")


    def toggle_skin_preference():
        """Toggles between Light and Dark interface appearance preferences."""
        ctk.set_appearance_mode("Light" if ctk.get_appearance_mode() == "Dark" else "Dark")


    # Arrange test interaction buttons horizontally across the lower tray tray area
    control_tray = ctk.CTkFrame(root, fg_color="transparent")
    control_tray.pack(side="bottom", fill="x", padx=20, pady=(0, 15))

    btn_lock = ctk.CTkButton(control_tray, text="Lock Tabview (Set 'disabled')", command=toggle_tab_lock)
    btn_lock.pack(side="left", expand=True, padx=5)

    btn_skin = ctk.CTkButton(control_tray, text="Toggle UI Light/Dark Appearance", command=toggle_skin_preference)
    btn_skin.pack(side="right", expand=True, padx=5)

    root.mainloop()
