import customtkinter as ctk
import time
from sCTkTableview import sCTkTableview

# 🚀 SYSTEM ARCHITECTURE IMPORTS: Your specialized component blocks
from sCTkFrame import sCTkFrame
from sCTkLabelPrimary import sCTkLabelPrimary
from sCTkLabelSecondary import sCTkLabelSecondary
from sCTkButtonPrimary import sCTkButtonPrimary
from sCTkButtonSecondary import sCTkButtonSecondary


class sCTkTableviewEdgeTester(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("sCTkTableview Specialized Ecosystem Harness")
        self.geometry("820x760")
        ctk.set_appearance_mode("dark")

        # 📐 Upper telemetry readout panel built via custom sCTk layout blocks
        self.status_panel = sCTkFrame(self, height=50)
        self.status_panel.pack(fill="x", padx=15, pady=10)

        self.status_label = sCTkLabelPrimary(
            self.status_panel,
            text="Ecosystem Initialized. Click an Edge-Case, Grid Mode, or Theme track below...",
            font=("Arial", 13, "bold")
        )
        self.status_label.pack(pady=10)

        # 📊 INITIAL CONFIGURATION STATE: 4 Columns x 4 Rows
        self.table = sCTkTableview(
            master=self,
            num_columns=4,
            num_rows=4,
            columns=["Callsign", "Frequency", "Mode", "Power"],
            grid_mode="grid",
            width=680,
            height=320
        )
        self.table.pack(padx=15, pady=15, expand=True, fill="both")

        # Master dashboard console layout panel
        self.controls_panel = sCTkFrame(self)
        self.controls_panel.pack(fill="x", padx=15, pady=15)

        # ---------------------------------------------------------------------
        # 📦 SECTION 1: DATA EDGE CASES (Using your sCTkButtonPrimary styling)
        # ---------------------------------------------------------------------
        self.data_label = sCTkLabelPrimary(self.controls_panel, text="📊 DATA VECTOR BOUNDARY TESTS",
                                           font=("Arial", 12, "bold"))
        self.data_label.pack(anchor="w", padx=15, pady=(8, 2))

        # Inner arrangement bracket container
        self.data_grid = sCTkFrame(self.controls_panel)
        self.data_grid.pack(fill="x", padx=10, pady=5)
        self.data_grid.configure(fg_color="transparent", border_width=0)  # Make container seamless
        self.data_grid.columnconfigure((0, 1), weight=1)

        sCTkButtonPrimary(
            self.data_grid, text="Test 1: Row Overflow (6 rows of data)",
            command=self.run_row_overflow
        ).grid(row=0, column=0, padx=10, pady=6, sticky="ew")

        sCTkButtonPrimary(
            self.data_grid, text="Test 2: Row Underflow (2 rows of data)",
            command=self.run_row_underflow
        ).grid(row=0, column=1, padx=10, pady=6, sticky="ew")

        sCTkButtonPrimary(
            self.data_grid, text="Test 3: Column Overflow (5 wide data cells)",
            command=self.run_column_overflow
        ).grid(row=1, column=0, padx=10, pady=6, sticky="ew")

        sCTkButtonPrimary(
            self.data_grid, text="Test 4: Column Underflow (2 wide data cells)",
            command=self.run_column_underflow
        ).grid(row=1, column=1, padx=10, pady=6, sticky="ew")

        # ---------------------------------------------------------------------
        # 🎨 SECTION 2: DYNAMIC GRID MODE SWITCHING (Using your sCTkButtonSecondary styling)
        # ---------------------------------------------------------------------
        self.grid_label = sCTkLabelPrimary(self.controls_panel, text="🎨 VISUAL GRID ARCHITECTURE SWITCHING",
                                           font=("Arial", 12, "bold"))
        self.grid_label.pack(anchor="w", padx=15, pady=(12, 2))

        self.grid_box = sCTkFrame(self.controls_panel)
        self.grid_box.pack(fill="x", padx=10, pady=5)
        self.grid_box.configure(fg_color="transparent", border_width=0)  # Make container seamless
        self.grid_box.columnconfigure((0, 1, 2), weight=1)

        sCTkButtonSecondary(
            self.grid_box, text="Set Mode: ZEBRA",
            command=lambda: self.switch_grid_mode("zebra")
        ).grid(row=0, column=0, padx=10, pady=6, sticky="ew")

        sCTkButtonSecondary(
            self.grid_box, text="Set Mode: GRID",
            command=lambda: self.switch_grid_mode("grid")
        ).grid(row=0, column=1, padx=10, pady=6, sticky="ew")

        sCTkButtonSecondary(
            self.grid_box, text="Set Mode: NONE (Borderless)",
            command=lambda: self.switch_grid_mode("none")
        ).grid(row=0, column=2, padx=10, pady=6, sticky="ew")

        # 🌗 SECTION 3: SYSTEM APPEARANCE CONSOLE CONTROL
        self.theme_label = sCTkLabelPrimary(self.controls_panel, text="🌗 COCKPIT STATION APPEARANCE SYSTEM",
                                            font=("Arial", 12, "bold"))
        self.theme_label.pack(anchor="w", padx=15, pady=(12, 2))

        self.theme_box = sCTkFrame(self.controls_panel)
        self.theme_box.pack(fill="x", padx=10, pady=5)
        self.theme_box.configure(fg_color="transparent", border_width=0)
        self.theme_box.columnconfigure(0, weight=1)

        # 👑 Public Toggle Switch Integration (FIXED: Swapped 'fill' for 'sticky')
        sCTkButtonSecondary(
            self.theme_box, text="Toggle Theme: LIGHT / DARK Mode",
            command=self.toggle_appearance_mode
        ).grid(row=0, column=0, padx=10, pady=6, sticky="ew")

    def log_status(self, test_name, message):
        self.status_label.configure(text=f"[{test_name}] -> {message}")
        print(f"[{test_name}] {message}")

    def toggle_appearance_mode(self):
        """🚀 LIVE REPAINT MATRIX SWITCH: Alternates the frame look between dark/light environments."""
        current_mode = ctk.get_appearance_mode().lower()
        target_mode = "light" if current_mode == "dark" else "dark"

        ctk.set_appearance_mode(target_mode)
        self.log_status("THEME CONSOLE",
                        f"Ecosystem presentation shifted successfully to '{target_mode.upper()}' Mode.")

    def switch_grid_mode(self, mode):
        self.log_status("GRID SWITCH", f"Changing layout render matrix rule to: '{mode}'...")
        header_line = 0 if mode == "none" else 4
        self.table.configure(grid_mode=mode, header_line_width=header_line)

        active_rows = self.table.get_num_rows()
        active_cols = self.table.get_num_columns()
        self.log_status("GRID SWITCH",
                        f"Success! Redrawn with '{mode}' layout. Current matrix: {active_rows}x{active_cols}")

    def run_row_overflow(self):
        self.log_status("ROW OVERFLOW", "Streaming 6 data records into 4 layout slots...")
        overflow_dataset = [
            ["W6EL", "14.074 MHz", "FT8", "50W"],
            ["K6K7", "7.047 MHz", "CW", "100W"],
            ["N6RE", "21.285 MHz", "SSB", "100W"],
            ["AI6IR", "144.200 MHz", "FM", "25W"],
            ["AJ6CU", "3.573 MHz", "FT8", "10W"],
            ["W1AW", "14.020 MHz", "CW", "1500W"]
        ]
        self.table.load_dataset(overflow_dataset)
        active_rows = self.table.get_num_rows()
        active_cols = self.table.get_num_columns()
        self.log_status("ROW OVERFLOW",
                        f"Success! Grid Matrix size expanded to: {active_rows} Rows x {active_cols} Cols.")

    def run_row_underflow(self):
        self.log_status("ROW UNDERFLOW", "Streaming 2 data records into 4 layout slots...")
        underflow_dataset = [
            ["G3TPW", "28.074 MHz", "FT8", "100W"],
            ["VK3IL", "14.230 MHz", "SSTV", "50W"]
        ]
        self.table.load_dataset(underflow_dataset)
        active_rows = self.table.get_num_rows()
        active_cols = self.table.get_num_columns()
        self.log_status("ROW UNDERFLOW",
                        f"Success! Grid Matrix size preserved at: {active_rows} Rows x {active_cols} Cols.")

    def run_column_overflow(self):
        self.log_status("COL OVERFLOW", "Streaming 5 wide cell vectors into 4 column headings...")
        wide_dataset = [
            ["W6EL", "14.074", "FT8", "50W", "GRID-DM14"],
            ["K6K7", "7.047", "CW", "100W", "GRID-CM87"],
            ["N6RE", "21.285", "SSB", "100W", "GRID-DM13"],
            ["AI6IR", "144.200", "FM", "25W", "GRID-DM12"]
        ]
        self.table.load_dataset(wide_dataset)
        active_rows = self.table.get_num_rows()
        active_cols = self.table.get_num_columns()
        self.log_status("COL OVERFLOW",
                        f"Success! Extra items truncated. Active size: {active_rows} Rows x {active_cols} Cols.")

    def run_column_underflow(self):
        self.log_status("COL UNDERFLOW", "Streaming 2 wide cell vectors into 4 column headings...")
        narrow_dataset = [
            ["W6EL", "14.074"],
            ["K6K7", "7.047"],
            ["N6RE", "21.285"],
            ["AI6IR", "144.200"]
        ]
        self.table.load_dataset(narrow_dataset)
        active_rows = self.table.get_num_rows()
        active_cols = self.table.get_num_columns()
        self.log_status("COL UNDERFLOW",
                        f"Success! Missing data padded. Active size: {active_rows} Rows x {active_cols} Cols.")


if __name__ == "__main__":
    app = sCTkTableviewEdgeTester()
    app.mainloop()
