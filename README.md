# sCustomTkinter

A high-performance, theme-adaptive, and encapsulated widget framework engineered specifically for desktop transceiver control interfaces and radio telemetry logging decks. It wraps `customtkinter` with an architectural mixin engine, forcing full look parsing continuity out of a centralized JSON stylesheet system.

## 📌 Localized Table of Contents
* [Quick-Start Import Blueprint](#quick-start-import-blueprint)
* [Comprehensive Component Catalog](#comprehensive-component-catalog)
* [Repository Directory Structure](#repository-directory-structure)
* [Markdown Asset Consolidation](#markdown-asset-consolidation)

---

## 🚀 Quick-Start Import Blueprint

`sCustomTkinter` eliminates raw, brittle `customtkinter` imports in user space code, standardizing your interface application files into a unified namespace pipeline:

```python
import scustomtkinter as sctk

# 1. Initialize centralized framework look records natively on system boot
sctk.apply_sCTkThemes()

# 2. Instantiate primary window frame anchor and component widgets fluidly
app = sctk.sCTk()
app.geometry("600x450")
app.title("Station Command Console")

panel = sctk.sCTkFrame(app, border_width=2)
panel.pack(padx=20, pady=20, fill="both", expand=True)

btn = sctk.sCTkButtonPrimary(panel, text="Transmit Call", command=lambda: print("TX ACTIVE"))
btn.pack(pady=10)

app.mainloop()
```

---

## 🎛️ Comprehensive Component Catalog

The library packages the following theme-compliant and platform-synchronized workspace widgets out-of-the-box:

* **`sCTk`**: The core main window master shell container. A clean, direct pass-through wrapper for `customtkinter.CTk`.
* **`sCTkToplevel`**: An encapsulated top-level popup container used to drive modal configuration screens and popup alert logs cleanly.
* **`sCTkFrame`**: The baseline background docking card panel, matching layout palettes with centralized stylesheet metrics.
* **`sCTkButtonPrimary`**: A high-visibility, accented action button featuring integrated hover loops and dynamic panel lock desaturation states.
* **`sCTkLabelPrimary`**: A bold, heavy header text panel element mapping high-contrast foreground labels.
* **`sCTkLabelSecondary`**: A crisp, clean layout typography item engineered for tabular listings, lane statuses, and technical readouts.
* **`sCTkTableview`**: A dense, interactive telemetry data grid component. Features inline data validation filters, row double-click entry editing, and dynamic column property anchors.
* **`sCTkScrollbar` & `sCTkScrollArea`**: An unblocked viewport engine. Embedded with an **Inertial Micro-Delta Aggregator Loop**, it perfectly aggregates fine-grained macOS touchpad and Apple Magic Mouse gesture streams alongside standard notched scroll wheels with zero layout stutter or type error drifts.
* **`sCTkTabview`**: A multi-page layout container. Features cascading palette loops to cleanly desaturate unselected tabs and flatten backing frame blocks when frozen.


## 📂 Repository Directory Structure

```text
sCustomTkinter/              (The GitHub Repository Root)
├── README.md                (This Core Architecture Readme)
├── setup.py                 (Standard Python package deployment script)
├── requirements.txt
│
├── scustomtkinter/          (The Core Production Library Package)
│   ├── __init__.py          (Unified top-level sctk import map)
│   ├── sCTk.py
│   ├── sCTkTableview.py
│   └── assets/
│       └── themes.json      (Master stylesheet look definitions)
│
├── docs/                    (Pure Markdown Documentation Vault)
│   ├── index.md
│   ├── sCTkTableview.md
│   ├── sCTkScrollbar.md
│   └── images/              (Shared documentation screenshots)
│       ├── tableview_showcase.png
│       └── scrollbar_mac_demo.png
│
├── examples/                (Standalone Executable Verification Benches)
│   └── sCTkTableview_Validation_Bench.py
│
├── pygubu_integration/      (Visual Layout Studio Workspace Files)
│   ├── sCTkWidgets.xml
│   └── sCTkWidgets_plugin.py
│
└── tools/                   (Internal Repository Maintenance Scripts)
    └── build_docs.sh        (Documentation consolidation script)
```

### 🖼️ Asset Image Injection Rules
To maintain broken-link protection across both standalone local setups and online GitHub hosting pages, follow these path-binding guidelines:
* **Storage Location:** Save all workspace layout screenshots and visual display graphs inside the dedicated folder track `docs/images/`.
* **Path Injections:** Reference images using clean relative path mappings to ensure they render identically across your local IDE markdown previewer lanes and the GitHub web panel:
  `![Tableview Telemetry Interface Layout](docs/images/tableview_showcase.png)`

---

## 📋 Markdown Asset Consolidation

For offline indexing, printer exports, or single-file deployment passes, the repository houses an internal automation compiler shell script at `tools/build_docs.sh`. 

This script iterates through individual component markdown documentation sheets sequentially, stripping trailing notes, and combining them into a single file named `docs/sCustomTkinter_Comprehensive_Guide.md`.

#### Executing the Documentation Builder Script:
```bash
chmod +x tools/build_docs.sh
./tools/build_docs.sh
```

---

## 📥 Installation Frame

Install this library straight from your terminal drive path using pip:
```bash
pip install git+https://github.com/aj6cu/sCustomTkinter/ 

```
Or from the Pycharm Library manager, Select the Gear option, and click "Install from VCS" when asked for the URL, enter
```bash
https://github.com/aj6cu/sCustomTkinter/
```
