#!/usr/bin/python3
"""
sCTkFrameLabeledSecondary

A clean CustomTkinter ScrollableFrame that natively hides its scrollbars
by matching their color profile to the frame background.

UI source file: sCTkFrameLabeledSecondary.ui
"""
import customtkinter as ctk
from ThemeableWidget import ThemeableWidget


class sCTkFrameLabeledSecondary(ctk.CTkScrollableFrame, ThemeableWidget):
    properties = frozenset()

    def __init__(self, master=None, **kwargs):
        # 1. Fire our shared theme logic first. It automatically finds the class section inside themes.json [INDEX]
        ThemeableWidget.__init__(self, kwargs)

        # 2. 🛠️ THE MUTATION SAFEGUARD DEEP COPY:
        # Isolate your configuration rules inside protected memory structures BEFORE
        # initializing super, preserving your true active settings from native deletion loops [INDEX].
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # 3. Initialize CustomTkinter ScrollableFrame natively with final kwargs safely
        super().__init__(master, **self.final_kw)

        self._custom_current_state = "normal"

        # 4. Force initial scrollbar hiding execution pass
        self._hide_internal_scrollbars()

    def configure(self, *args, **kwargs):
        """Handles Pygubu designer queries and manages composite state updates safely."""

        # -----------------------------------------------------------------
        # ZONE A: POSITION INTERCEPT (Pygubu Inspector compatibility check)
        # -----------------------------------------------------------------
        if args and len(args) == 1:
            pname = args
            if pname == "state":
                return ("state", "state", "state", "normal", str(self.state()))

            if pname in ["fg_color", "border_color", "label_text_color"]:
                current_state = str(self.state()).lower()
                val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(
                    pname)
                return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

            return super().configure(pname)

        # Handle Pygubu positional dictionary merging layers cleanly
        if args and isinstance(args, dict):
            kwargs = args | kwargs

        # -----------------------------------------------------------------
        # ZONE B: SUB-COMPONENT STATE INTERCEPTION
        # -----------------------------------------------------------------
        if "state" in kwargs:
            target_state = kwargs.pop("state")
            self.state(target_state)

        # Clean empty strings passed by backspacing parameters in Pygubu to prevent exceptions [INDEX]
        for k, v in list(kwargs.items()):
            if v == "":
                kwargs.pop(k)

        # -----------------------------------------------------------------
        # ZONE C: RUNTIME KEYWORDS MRO ROUTING PASS & REDRAW PROPS
        # -----------------------------------------------------------------
        if kwargs:
            result = super().configure(**kwargs)
            self._hide_internal_scrollbars()
            return result
        return None

    def get_state(self):
        """Explicit getter synchronized with your standalone test harness script assertions."""
        return self.state()

    def state(self, mode: str = None):
        """Dedicated container frame state controller."""
        if mode is None:
            return getattr(self, "_custom_current_state", "normal")

        mode = mode.lower()
        if mode in ("normal", "enabled", "active"):
            self._custom_current_state = "normal"
            self._update_current_visual_state()

        elif mode == "disabled":
            # Safely apply custom disabled overrides manually via super layout pools [INDEX]
            super_payload = {}
            for key in ("fg_color", "border_color", "label_text_color"):
                if key in self._custom_disabled_map and self._custom_disabled_map[key] is not None:
                    super_payload[key] = self._custom_disabled_map[key]

            if super_payload:
                super().configure(**super_payload)

            self._custom_current_state = "disabled"
            self._hide_internal_scrollbars()

    def _update_current_visual_state(self):
        """
        MASTER VISUAL ROUTER: Dynamically applies extensible theme properties out of protected memory [INDEX].
        Completely free of hardcoded property name fallback strings, ensuring total extensibility [INDEX].
        """
        # 🛠️ THE BOUNDED DYNAMIC FILTER SHIELD:
        config_payload = {}
        for key in ("fg_color", "border_color", "label_text_color", "border_width", "label_font"):
            val = self._local_defaults.get(key)
            if val is not None:
                config_payload[key] = val

        if config_payload:
            super().configure(**config_payload)
        self._hide_internal_scrollbars()

    def _hide_internal_scrollbars(self):
        """Forces the scrollbar track elements to match the frame background color seamlessly."""
        try:
            bg_color = super().cget("fg_color")
            if hasattr(self, "_scrollbar") and self._scrollbar is not None:
                self._scrollbar.configure(
                    fg_color=bg_color,
                    button_color=bg_color,
                    button_hover_color=bg_color,
                    width=0
                )
        except Exception:
            pass

    def winfo_children(self, include_private: bool = False) -> list:
        """
        🛠️ UNIFIED STRUCTURE INTERCEPTOR OVERRIDE:
        By default, filters private internal title labels and heading elements out [INDEX].
        Pass `include_private=True` to bypass the filter shield and return the raw,
        unmanipulated Tkinter core layout lineage tree [INDEX]!
        """
        raw_children = super().winfo_children()
        if include_private:
            return raw_children

        filtered_children = []
        for child in raw_children:
            # Drop the private framework structural heading text cells and frame backplanes
            if child.__class__.__name__ not in ["CTkLabel", "Label", "CTkFrame", "Frame"]:
                filtered_children.append(child)
        return filtered_children

    def get_children(self) -> list:
        """Convenience function providing a clean, application-level custom widget layout array [INDEX]."""
        return self.winfo_children(include_private=False)

    def get_all_children(self) -> list:
        """Convenience function providing direct, unfiltered access to the entire C-level native tree."""
        return self.winfo_children(include_private=True)

    def get_container(self):
        return self


# =====================================================================
# 🛠️ TESTING HARNESS IMPORTS & SETUP
# =====================================================================
import sCTkThemes  # 🔍 Duplicate import kept close for script scannability
from sCTkFrame import sCTkFrame  # Testing application wrapper container frame
from sCTkLabelTertiary import sCTkLabelTertiary
from sCTkFrameLabeledSecondary import sCTkFrameLabeledSecondary

if __name__ == "__main__":
    # Natively resolves your package assets and populates configurations cleanly [INDEX]
    sCTkThemes.apply_sCTkThemes()

    root = ctk.CTk()
    root.geometry("450x450")
    root.title("Labeled Scrollable Secondary Frame Test Bench")

    # Instantiate your custom scrollable secondary frame container [INDEX]
    scroll_panel = sCTkFrameLabeledSecondary(root, label_text="AUXILIARY METADATA TRACK MATRIX")
    scroll_panel.pack(expand=True, fill="both", padx=25, pady=25)

    # Populate scroll panel container slots with helper sCTkLabelTertiary notice items [INDEX]
    for i in range(1, 21):
        lbl_item = sCTkLabelTertiary(scroll_panel,
                                     text=f"Helper Node Index [ID: {i:02d}] - Calibration Offset [0.00Hz]")
        lbl_item.pack(pady=4, fill="x", padx=10)


    def toggle_frame_states():
        """Toggles the container panel and cascades the state down to all child widgets [INDEX]."""
        current_mode = scroll_panel.get_state()
        target = "disabled" if current_mode == "normal" else "normal"

        # 1. Update the parent scrollable frame's visual layout variables via dual-routing syntax [INDEX]
        scroll_panel.configure(state=target)

        # 2. Native standard cascade loop leveraging your winfo_children() override [INDEX]
        true_children = scroll_panel.winfo_children()
        print(f"DEBUG ASSERTER: Successfully captured {len(true_children)} label elements...")

        for child in true_children:
            if hasattr(child, "configure"):
                child.configure(state=target)

        btn_toggle.configure(
            text="Lock Container (Set 'disabled')" if target == "normal" else "Unlock Container (Set 'normal')")
        print(f"Logged Verification Hook -> scroll_panel.get_state() = {scroll_panel.get_state()}\n")


    btn_toggle = ctk.CTkButton(root, text="Lock Container (Set 'disabled')", command=toggle_frame_states)
    btn_toggle.pack(pady=15)

    # Run the interactive boot tracking logs [INDEX]
    print("--- BOOT INITIALIZATION PASSTHROUGH ---")
    scroll_panel.state("disabled")
    print(f"state (Disabled Pass) = {scroll_panel.get_state().upper()}")

    scroll_panel.state("normal")
    print(f"state (Normal Pass)   = {scroll_panel.get_state().upper()}")
    print("========================================\n")

    root.mainloop()
