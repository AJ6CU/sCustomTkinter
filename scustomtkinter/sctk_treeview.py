import customtkinter as ctk
from typing import List, Optional

# Pull the unmodified base repository class layout
from ctktreeview import CTkTreeview

# Import your system's shared configuration architecture
from sCTkThemes import THEME_DEFAULTS
from ThemeableWidget import ThemeableWidget


class sCTkTreeview(CTkTreeview, ThemeableWidget):
    """
    Advanced themeable Treeview grid widget component.
    Subclasses CTkTreeview safely to provide centralized styling lookups
    while preserving 100% of the original package's native behavior.
    """

    def __init__(self,
                 master: any,
                 columns: List[str],
                 width: int = 500,
                 height: int = 25,
                 show: str = "headings",
                 *args, **kwargs):

        # 1. Initialize the ThemeableWidget engine using your dictionary assets
        # Fallbacks are intentionally omitted as failure causes a hard ValueError in ThemeableWidget.
        local_kwargs = {}
        ThemeableWidget.__init__(
            self,
            theme_defaults=THEME_DEFAULTS.get("sCTkTreeview", {}),
            kwargs=local_kwargs
        )

        # 2. Extract configuration properties from the stylesheet layout layer
        self._header_bg = self.final_kw.get("header_bg_color")
        self._header_fg = self.final_kw.get("header_text_color")
        self._header_font = self.final_kw.get("header_font")

        self._row_bg = self.final_kw.get("row_bg_color")
        self._row_alt_bg = self.final_kw.get("row_alt_bg_color")
        self._row_fg = self.final_kw.get("text_color")
        self._row_font = self.final_kw.get("font")
        self._grid_color = self.final_kw.get("grid_color")

        self._select_bg = self.final_kw.get("selected_bg_color")
        self._select_fg = self.final_kw.get("selected_text_color")

        # 3. Invoke the parent CTkTreeview initializer verbatim with unmodified signatures
        super().__init__(
            master=master,
            width=width,
            height=height,
            columns=columns,
            show=show,
            *args, **kwargs
        )

        # 4. Distribute theme parameters to the core panel frames
        self._apply_theme_to_tree()

    def _apply_theme_to_tree(self):
        """Maps structural palette tokens onto the underlying main widget frame and internal tree instance."""
        bg_resolved = self._apply_appearance_mode(self._row_bg)
        fg_resolved = self._apply_appearance_mode(self._row_fg)
        grid_resolved = self._apply_appearance_mode(self._grid_color)

        if hasattr(self, "configure"):
            self.configure(fg_color=bg_resolved)

        # Directly target the internal private tree instance instead of using a global ttk.Style manager.
        if hasattr(self, "_treeview") and self._treeview:
            try:
                self._treeview.configure(
                    show="headings",
                    background=bg_resolved,
                    foreground=fg_resolved,
                    fieldbackground=bg_resolved,
                    gridcolor=grid_resolved
                )
            except Exception:
                pass

    def _set_appearance_mode(self, mode_string):
        """Forces an appearance update pass whenever light/dark modes toggle."""
        super()._set_appearance_mode(mode_string)
        self._apply_theme_to_tree()


# ==========================================
#   MAIN RUNNER TESTING ENVIRONMENT
# ==========================================
if __name__ == "__main__":
    import customtkinter as ctk
    from sCTkThemes import THEME_DEFAULTS
    from sCTkTreeview import sCTkTreeview

    # Ensure stylesheet keys match the validation profiles if running completely isolated
    if "sCTkTreeview" not in THEME_DEFAULTS:
        THEME_DEFAULTS["sCTkTreeview"] = {
            "bg_color": "transparent",
            "header_bg_color": ("#E2E8F0", "#1E293B"),
            "header_text_color": ("#0F172A", "#F8FAFC"),
            "header_font": ("Arial", 11, "bold"),
            "row_bg_color": ("#FFFFFF", "#111827"),
            "row_alt_bg_color": ("#F1F5F9", "#1E293B"),
            "text_color": ("#1E293B", "#F1F5F9"),
            "font": ("Arial", 11),
            "grid_color": ("#CBD5E1", "#334155"),
            "selected_bg_color": ("#3B82F6", "#2563EB"),
            "selected_text_color": ("#FFFFFF", "#FFFFFF")
        }

    root = ctk.CTk()
    root.geometry("750x450")
    root.title("sCTkTreeview Vanilla Theme Integration Sandbox")

    cols = ["Channel Label", "Frequency (MHz)", "Mode", "Station Name"]

    # Instantiate the plain themeable wrapper
    tree = sCTkTreeview(root, columns=cols, width=550, height=300, show="headings")
    tree.pack(side="left", fill="both", expand=True, padx=20, pady=20)

    # Use native context manager heading mapping commands from the base library
    with tree.headings() as th:
        th.text("Channel Label", "Channel Label")
        th.text("Frequency (MHz)", "Frequency (MHz)")
        th.text("Mode", "Mode")
        th.text("Station Name", "Station Name")

    # Use native context manager column width adjustments from the base library
    with tree.columns() as tc:
        tc.minwidth("Channel Label", 110)
        tc.minwidth("Frequency (MHz)", 110)
        tc.minwidth("Mode", 60)
        tc.minwidth("Station Name", 220)
        tc.anchor("Frequency (MHz)", "center")
        tc.anchor("Mode", "center")

    # Call native un-mutated insert methods to load your ham station rows
    radio_stations = [
        ["160M-VOX", "1.8400", "LSB", "160m - Voice / Calling"],
        ["40M-LSB", "7.2000", "LSB", "40m - LSB Voice Calling"],
        ["40M-FT8", "7.0740", "USB", "40m - FT8 Digital Mode"],
        ["20M-FT8", "14.0740", "USB", "20m - FT8 Digital Mode"],
        ["17M-USB", "18.1300", "USB", "17m - USB Voice Calling"],
        ["15M-USB", "21.3000", "USB", "15m - USB Voice Calling"],
        ["12M-USB", "24.9500", "USB", "12m - USB Voice Calling"],
        ["10M-USB", "28.4000", "USB", "10m - Tech / General Voice"]
    ]

    for station in radio_stations:
        tree.insert("", "end", values=station)

    root.mainloop()
