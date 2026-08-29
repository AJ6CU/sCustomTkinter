#!/usr/bin/python3
"""
sCTkOptionMenuSecondary

subclass of ctk.CTkFrame acting as a cleanly bordered composite OptionMenu
(Secondary / Helper Selection Controller Variant)

UI source file: sCTkOptionMenuSecondary.ui
"""
import customtkinter as ctk
from ThemeableWidget import ThemeableWidget


# 🛠️ THE INHERITANCE CORRECTION:
# Inherit directly from ctk.CTkFrame instead of your custom sCTkFrame.
# This permanently blocks the dual-mixin collision loop from corrupting your dictionary!
class sCTkOptionMenuSecondary(ctk.CTkFrame, ThemeableWidget):

    def __init__(self, master=None, width=160, height=28, **kw):
        # 1. PARAMETER POPPING: Capture menu-specific operational attributes early
        values = kw.pop("values", [""])
        command = kw.pop("command", None)
        variable = kw.pop("variable", None)

        # 2. INJECT SIGNATURE DEFAULTS: Guarantees parameters clear standalone math loops
        if "width" not in kw: kw["width"] = width
        if "height" not in kw: kw["height"] = height

        # 3. Fire our shared theme logic first to resolve global configurations safely
        ThemeableWidget.__init__(self, kw)

        # 4. THE MUTATION SAFEGUARD DEEP COPY
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)

        # 5. 🛠️ THE SYSTEM FILTER SHIELD: Exclude all menu keys from reaching the frame constructor
        FRAME_VALID_KEYS = {"width", "height", "fg_color", "border_color", "border_width", "corner_radius", "bg_color"}
        frame_kwargs = {}
        for key in FRAME_VALID_KEYS:
            # We use a safe .get() track so it gracefully skips keys instead of dropping KeyErrors!
            val = self._local_defaults.get(key)
            if val is not None:
                frame_kwargs[key] = val

        # 6. Initialize the native ctk.CTkFrame container using ONLY valid frame properties
        super().__init__(master, **frame_kwargs)

        # 7. Initialize inner CustomTkinter option menu using cleanly popped parameters
        self._menu = ctk.CTkOptionMenu(
            self,
            values=values,
            command=command,
            variable=variable
        )
        self._menu.pack(expand=True, fill="both", padx=2, pady=2)

        # 8. Execute your custom visual layout matching tracks smoothly
        self._update_current_visual_state()
        self._custom_current_state = "normal"

    def _update_current_visual_state(self):
        """
        MASTER VISUAL ROUTER: Dynamically maps all available theme attributes.
        Completely free of hardcoded property name fallbacks, ensuring total
        extensibility if new options are introduced to the stylesheet in the future.
        """
        # 1. Dynamically sync the outer frame properties if they exist in your theme configuration
        frame_config = {}
        for key in ("border_color", "fg_color", "border_width", "corner_radius"):
            if self._local_defaults.get(key) is not None:
                frame_config[key] = self._local_defaults[key]
        if frame_config:
            super().configure(**frame_config)

        # 2. 🛠️ THE FUTURE-PROOF DYNAMIC ROUTER:
        # We loop directly through whatever properties exist inside your theme file block!
        # If it is a frame-specific layout key, we skip it. Everything else gets packed
        # dynamically into a payload dictionary and handed straight down to the inner menu.
        FRAME_SPECIFIC_KEYS = {"border_width", "border_color", "corner_radius", "width", "height"}
        menu_payload = {}

        for key, value in self._local_defaults.items():
            if key not in FRAME_SPECIFIC_KEYS and value is not None:
                menu_payload[key] = value

        # 3. Handle your transparent composite blend properties cleanly
        # If fg_color isn't assigned yet, we let it slide so it picks up the native framework values
        if "fg_color" in frame_config:
            menu_payload["fg_color"] = frame_config["fg_color"]
            menu_payload["button_color"] = frame_config["fg_color"]
            if "button_hover_color" not in menu_payload:
                menu_payload["button_hover_color"] = frame_config["fg_color"]

        # 4. Dispatch the compiled styling payload directly into the inner component
        if menu_payload:
            self._menu.configure(**menu_payload)

        # Clear base canvas borders to enforce true flat alignment if supported
        try:
            if hasattr(self._menu, "_canvas") and self._menu._canvas:
                self._menu._canvas.configure(background="")
        except Exception:
            pass

    def configure(self, *args, **kwargs):
        """Handles Pygubu designer queries and manages composite state updates safely."""
        if args and len(args) == 1:
            pname = args
            if pname == "state":
                return ("state", "state", "state", "normal", str(self.state()))

            if pname in ["fg_color", "border_color", "text_color", "width", "height"]:
                current_state = str(self.state()).lower()
                val = self._custom_disabled_map.get(pname) if current_state == "disabled" else self._local_defaults.get(
                    pname)
                return (pname, pname, pname, str(self._local_defaults.get(pname)), str(val))

            return super().configure(pname)

        if args and isinstance(args, dict):
            kwargs = args | kwargs

        # Sub-Component Routing
        if "values" in kwargs:
            self._menu.configure(values=kwargs.pop("values"))
        if "command" in kwargs:
            self._menu.configure(command=kwargs.pop("command"))
        if "variable" in kwargs:
            self._menu.configure(variable=kwargs.pop("variable"))

        if "state" in kwargs:
            target_state = str(kwargs.pop("state")).lower()
            self.state(target_state)

        if kwargs:
            # Clean out empty strings passed by backspacing parameters in Pygubu to prevent exceptions
            for k, v in list(kwargs.items()):
                if v == "":
                    kwargs.pop(k)
            if kwargs:
                super().configure(**kwargs)

    def get_state(self):
        """Explicit getter to return the current composite state string safely."""
        return str(self.state()).lower()

    def state(self, mode=None):
        """Dedicated option menu composite state controller."""
        if mode is not None:
            mode = mode.lower()
            if mode in ("normal", "enabled", "active"):
                self._menu.configure(state="normal")
                self._update_current_visual_state()
                self._custom_current_state = "normal"
            elif mode == "disabled":
                self._menu.configure(state="disabled")

                super().configure(
                    border_color=self._custom_disabled_map.get("border_color"),
                    fg_color=self._custom_disabled_map.get("fg_color")
                )
                self._menu.configure(
                    fg_color=self._custom_disabled_map.get("fg_color"),
                    button_color=self._custom_disabled_map.get("fg_color"),
                    text_color=self._custom_disabled_map.get("text_color"),
                    button_hover_color=self._custom_disabled_map.get("fg_color")
                )
                self._custom_current_state = "disabled"

        return self._menu.cget("state")



    def update_list(self, new_values: list, default_index: int = 0):
        """Safely updates the items list and resets the visible value."""
        if not new_values:
            self._menu.configure(values=[""])
            self._menu.set("")
            return

        self._menu.configure(values=new_values)

        if default_index < len(new_values):
            self._menu.set(new_values[default_index])
        else:
            self._menu.set(new_values)

    def set(self, value: str):
        self._menu.set(value)

    def get(self) -> str:
        return self._menu.get()


# =====================================================================
# 🛠️ INTEGRATED REPOSITORY COMPLIANT INLINE TESTING HARNESS
# =====================================================================
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("400x200")

    from sCTkFrame import sCTkFrame

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    widget = sCTkOptionMenuSecondary(base, values=["Helper Option A", "Helper Option B"])
    widget.pack(expand=True, fill="x", padx=40, pady=10)

    print("Populating secondary parameters track values list...")
    widget.update_list(["Filter: Narrow", "Filter: Medium", "Filter: Wide"], default_index=0)

    # Verify our custom cascading state system locks down the composite selector!
    widget.state("disabled")
    print("--- DISABLED PASS ---")
    print("state (Disabled Sequence) =", widget.get_state())  # Output: disabled

    # Verify the cascade pipeline unlocks everything smoothly right back to normal
    widget.state("normal")
    print("\n--- NORMAL PASS ---")
    print("state (Normal Sequence)   =", widget.get_state())  # Output: normal

    root.mainloop()
