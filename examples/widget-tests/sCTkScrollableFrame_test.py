#!/usr/bin/python3
"""
sCTkScrollableFrame - Piece 1 of 3

A clean, theme-compliant scrollable viewport container frame.
Inherits cleanly and directly from ctk.CTkScrollableFrame to preserve 100% of native
CustomTkinter feature loops, fully unblocking macOS high-precision theme switches [1.1, 1.2].
"""
import sys
import platform
import customtkinter as ctk
from ThemeableWidget import ThemeableWidget

class sCTkScrollableFrame(ctk.CTkScrollableFrame, ThemeableWidget):
    properties = frozenset()

    def __init__(self, master=None, **kwargs):
        # 1. Fire our shared theme logic first. It automatically finds "sCTkScrollableFrame" in themes.json
        ThemeableWidget.__init__(self, kwargs)

        # 2. Store your custom maps safely onto instance memory channels
        self._local_defaults = dict(self.final_kw)

        # 3. Initialize CustomTkinter natively as a pure programmatic scrollable frame asset
        super().__init__(master, **self.final_kw)

        # Execute a baseline visual update loop right on boot
        self._update_current_visual_state()

        # 4. REGISTER LIFECYCLE HANDSHAKE HOOK:
        # Pushes tracking notifications reachably up to Pygubu systems cleanly.
        self._finalize_themeable_lifecycle()

    def _set_appearance_mode(self, mode_string: str):
        """Native look catcher ensuring all internal layers repaint fluidly on theme shifts [1.1, 1.2]."""
        if hasattr(super(), "_set_appearance_mode"):
            try:
                super()._set_appearance_mode(mode_string)
            except Exception:
                pass
        self._update_current_visual_state()
    def configure(self, *args, **kwargs):
        """Handles standard keyword configurations and Pygubu designer inspector queries cleanly [1.1]."""
        if args and len(args) == 1:
            pname = args if isinstance(args, (list, tuple)) else args

            if pname in ["fg_color", "label_fg_color", "scrollbar_button_color", "border_color"]:
                return (pname, pname, pname, str(self._local_defaults.get(pname)), str(self._local_defaults.get(pname)))

            return super().configure(*args, **kwargs)

        if args and isinstance(args, dict):
            kwargs = args | kwargs

        if kwargs:
            super().configure(**kwargs)
            self._update_current_visual_state()

    def cget(self, attribute_name: str) -> any:
        """Safely intercept configuration property queries cleanly [1.1]."""
        return super().cget(attribute_name)

    def _update_current_visual_state(self):
        """MASTER VISUAL ROUTER: Restores theme colors directly out of local stylesheet directories [1.1, 1.2]."""
        config_payload = {}
        for key in ("fg_color", "border_color", "label_fg_color"):
            val = self._local_defaults.get(key)
            if val is not None:
                config_payload[key] = self._resolve_color(val) if "color" in key or "fg" in key else val

        if config_payload:
            super().configure(**config_payload)

        # FORCE-REPAINT HIGH-CONTRAST SCROLLBAR TOKENS:
        if hasattr(self, "_scrollbar") and self._scrollbar:
            try:
                normal_bar = self._resolve_color(self._local_defaults.get("scrollbar_button_color", ["#94A3B8", "#475569"]))
                normal_hover = self._resolve_color(self._local_defaults.get("scrollbar_button_hover_color", ["#64748B", "#334155"]))
                self._scrollbar.configure(button_color=normal_bar, button_hover_color=normal_hover)

                if hasattr(self._scrollbar, "_draw"):
                    self._scrollbar._draw()
            except Exception:
                pass
    def _toggle_scroll_bindings(self, bind=True):
        """The parent canvas intercept engine routing mouse wheels and touchpad events [1.1]."""
        SCROLL_EVENTS = ["<MouseWheel>", "<TouchpadScroll>", "<Button-4>", "<Button-5>"]
        layers_to_bind = [self]
        try:
            parent_path = self.winfo_parent()
            parent_widget = self.nametowidget(parent_path)
            if parent_widget and parent_widget.__class__.__name__ == "Canvas":
                layers_to_bind.append(parent_widget)
                grandparent_path = parent_widget.winfo_parent()
                grandparent_widget = self.nametowidget(grandparent_path)
                if grandparent_widget: layers_to_bind.append(grandparent_widget)
        except Exception:
            pass

        for child in self.get_children():
            if child not in layers_to_bind: layers_to_bind.append(child)

        for target_layer in layers_to_bind:
            for event_str in SCROLL_EVENTS:
                try: target_layer.unbind(event_str)
                except Exception: pass

                if bind:
                    if "Touchpad" in event_str:
                        if sys.platform == "darwin":
                            target_layer.bind("<TouchpadScroll>", self._process_mac_touchpad_scroll, add="+")
                    else:
                        target_layer.bind(event_str, self._process_scroll_wheel, add="+")

    def _process_mac_touchpad_scroll(self, event):
        """Processes Apple high-precision touch masks on the true master canvas [1.1]."""
        try:
            parent_widget = self.nametowidget(self.winfo_parent())
            if parent_widget and hasattr(parent_widget, "yview_scroll"):
                delta_x, delta_y = self._decode_mac_touchpad_delta(event.delta)
                if delta_y != 0:
                    MAC_SCROLL_SENSITIVITY = 3
                    scaled_scroll = -MAC_SCROLL_SENSITIVITY if delta_y > 0 else MAC_SCROLL_SENSITIVITY
                    parent_widget.yview_scroll(scaled_scroll, "units")
        except Exception:
            pass

    def _process_scroll_wheel(self, event):
        """Processes cross-platform standard mouse wheels and physical tuning knobs [1.1]."""
        try:
            parent_widget = self.nametowidget(self.winfo_parent())
            if parent_widget and hasattr(parent_widget, "yview_scroll"):
                sys_platform = platform.system()
                if sys_platform == "Darwin":
                    delta = event.delta
                    MAC_SCROLL_SENSITIVITY = 3
                    scaled_scroll = int(-MAC_SCROLL_SENSITIVITY * delta) if abs(delta) >= 1 else (
                        -MAC_SCROLL_SENSITIVITY if delta > 0 else MAC_SCROLL_SENSITIVITY)
                    parent_widget.yview_scroll(scaled_scroll, "units")
                elif sys_platform == "Linux":
                    if event.num == 4: parent_widget.yview_scroll(-1, "units")
                    elif event.num == 5: parent_widget.yview_scroll(1, "units")
                else:
                    parent_widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    def _decode_mac_touchpad_delta(self, raw_delta):
        """🛠️ DIAL-VERIFIED PHYSICS MASK: Decodes macOS touchpad bitmasks [1.1]."""
        raw = raw_delta & 0xFFFFFFFF
        delta_x = (raw >> 16) & 0xFFFF
        if delta_x >= 0x8000: delta_x -= 0x10000
        delta_y = raw & 0xFFFF
        if delta_y >= 0x8000: delta_y -= 0x10000
        return delta_x, delta_y

    def _finalize_split_bindings(self):
        """Standard layout binding connection pass [1.1]."""
        self._toggle_scroll_bindings(bind=True)

    def winfo_children(self, include_private: bool = False) -> list:
        """Filters background sub-elements out by default to preserve clean loops [1.1]."""
        raw_children = super().winfo_children()
        if include_private:
            return raw_children

        filtered_children = []
        for child in raw_children:
            if child.__class__.__name__ not in ["CTkScrollbar", "CTkCanvas", "Canvas"]:
                filtered_children.append(child)
        return filtered_children

    def get_children(self) -> list:
        return self.winfo_children(include_private=False)

    def get_all_children(self) -> list:
        return self.winfo_children(include_private=True)


# =====================================================================
# 🛠️ TESTING HARNESS MODIFIED: Demonstrates clean external cascade loop pass
# =====================================================================
if __name__ == "__main__":
    import sCTkThemes
    from sCTkButtonPrimary import sCTkButtonPrimary
    from sCTkEntryPrimary import sCTkEntryPrimary

    root = ctk.CTk()
    root.title("ScrollableFrame Pure Baseline Verification")
    root.geometry("450x420")

    sCTkThemes.apply_sCTkThemes()

    test_frame = sCTkScrollableFrame(root, width=380, height=250, label_text="Telemetry Viewport Container")
    test_frame.pack(padx=20, pady=20, fill="both", expand=True)

    for i in range(12):
        mock_entry = sCTkEntryPrimary(test_frame, placeholder_text=f"Active Transceiver Channel {i + 1}")
        mock_entry.pack(padx=10, pady=5, fill="x")

    _is_locked = False
    def toggle_cascade_lockout():
        global _is_locked
        _is_locked = not _is_locked
        target = "disabled" if _is_locked else "normal"

        toggle_btn.configure(text="Enforce State: NORMAL" if _is_locked else "Enforce State: DISABLED")

        # 🔑 CLEAN APPLICATION-LEVEL LOOKOUT LOOP CASCADE:
        # The external control logic explicitly dictates when and how to update nested elements!
        for entry_widget in test_frame.get_children():
            if hasattr(entry_widget, "configure"):
                try:
                    entry_widget.configure(state=target)
                except Exception:
                    pass

    toggle_btn = sCTkButtonPrimary(root, text="Enforce State: DISABLED", command=toggle_cascade_lockout)
    toggle_btn.pack(side="bottom", pady=15)

    btn_theme = ctk.CTkButton(root, text="Toggle Theme Skin", command=lambda: ctk.set_appearance_mode(
        "Dark" if ctk.get_appearance_mode() == "Light" else "Light"))
    btn_theme.pack(side="bottom", pady=5)

    test_frame._toggle_scroll_bindings(bind=True)
    root.mainloop()
