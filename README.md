# sCustomTkinter

A high-performance, theme-adaptive, and encapsulated widget framework engineered to support user interfaces with multiple designs for each widget. Not all Buttons (or for that matter Labels, Menus, etc.) should look the same in a well thought out UX. Important ones should catch your attention, while the less important fade into the background until needed. For example, `sCustomTkinter` starts you off with 3 different level of Buttons, that you can individually tailor to your design theme to help create consistency across your whole UX. 

This project is a set of subclasses (hence the "s" prefix) of Tom Schimansky's [CustomTkinter](https://customtkinter.tomschimansky.com/) that he has generously made available This widget to the community under the MIT License. Without his work, this would not have been made possible.

The vast majority of the widgets provided by `sCustomTkinter` are based on the ones originally provided with `CustomTkinter`. However, there are several additions including knobs, analog meter displays, file choosers, table, selectors, and spinboxes that have been added primarily because I needed them for my own project and decided to share. In addition, the library has been designed from the start to integrated with Alejandro Autalan wonderful GUI Builder for python, [Pygubu-Designer](https://github.com/alejandroautalan/pygubu-designer). I have used his software extensively in other projects (visit other areas in my Github) and it has saved me a lot of time and effort.

However, this design has been architected to allow you to add your own widgets, or subclass mine for your purposes. The key to the themes is sCTkThemes.json. Don't like my color choices (understandable as I am a little red/brown color blind...) , copy this file from Github, modify it and put it in your applications directory. It will be found before the common one in scustomtkinter/assets.  The format of this file, is very similar to the original Themes definition file of `CustomTkinter` (it has additions that would give the standard `CustomTkinter` theme processor problems in addition to the new widgets that might cause a few runtime exceptions). 

Want to add a widget, create it, add ThemeableWidget as a second inheritance of your class, look at the existing code for Init and Configure to avoid properties being pushed down into the underlying `CustomTkinter` library, and get coding! 



## 📌 Localized Table of Contents
* [Quick-Start](#quick-start)
* [Comprehensive Component Catalog](#comprehensive-component-catalog)
* [Repository Directory Structure](#repository-directory-structure)

---

## 🚀 Quick-Start

### sCustomTkinter Installation

Install this library straight from your terminal drive path using pip:


```bash
pip install git+https://github.com/aj6cu/sCustomTkinter/ 

```

Or from the Pycharm Library manager, Select the Gear option, and click "Install from VCS" when asked for the URL, enter


```bash
https://github.com/aj6cu/sCustomTkinter/
```


### Library Test Script


You can use the following simple program to test that the installation worked:

```python
from scustomtkinter import sCTk, sCTkFrame, sCTkButtonPrimary

root = sctk.sCTk()
root.geometry("600x450")
root.title("Station Command Console")

panel = sCTkFrame(root, border_width=2)
panel.pack(padx=20, pady=20, fill="both", expand=True)

btn = CTkButtonPrimary(panel, text="Transmit Call", command=lambda: print("TX ACTIVE"))
btn.pack(pady=10)

root.mainloop()
```

### Pygubu-Designer Installation

    1. Download the Pygubu-Designer plugin from [sCTkWidgetSetForPygubuDesigner] (https://github.com/AJ6CU/sCustomTkinter/blob/main/pygubu-designer-integration/sCTkWidgetSetForPygubuDesigner.py).  Store it someplace convenient so that you can reference it from multiple Pygubu-Designer sessions.
    2. Start Pygubu-Designer, add any widget (you will probably delete and replace this later)
    3. Create a new project and save it. 
    4. in the Project->Settings->Custom Widgets, hit the "+", naviagate where you stored  `sCTkWidgetSetForPygubuDesigner.py` and select it.
    5. Return to Design mode. You should see a new set of widgets on the palette under 'sCustomTkinter'.



## Comprehensive Component Catalog

The reference manual for this library is provided [here](https://github.com/AJ6CU/sCustomTkinter/tree/main/docs/Readme.md) THe following is a summary of the library:


### Standard CustomTkinter Widgets


#### Containers
* sCTk`: The core main window master shell container. A clean, direct pass-through wrapper for `customtkinter.CTk`.
* `sCTkToplevel`: An encapsulated top-level popup container used to drive modal configuration screens and popup alert logs cleanly.
* sCTkFrame`: The baseline background docking card panel, matching layout palettes with centralized stylesheet metrics.
* `ssCTkScrollableFrame` A

#### Controls and Display
* `sCTkButtons` There are three levels of buttons included in the library. 

    * `sCTkButttonPrimary`** provides high-visibility, accented action button featuring integrated hover loops and dynamic panel lock desaturation states. Use this for the action the user should take. 
    * `sCTkButtonSecondary`**:  A toned down button used for less likely options or end points. You might use this for the Cancel button.
    * `sCTkButtonTertiary`**: Known in the industry as a `Ghost Button`, this button is almost invisible. Use this for low probability selections.
* `sCTkCheckBox`: A
* `sCTkComboBox`: A
* `Entry Fields`
  * `sCTkEntryPrimary` A
  * `ssCTkEntrySecondary`: A
* `Labels`
  * `sCTkLabelPrimary` A bold, heavy header text panel element mapping high-contrast foreground labels.
  * `ssCTkLabelSecondary`: A crisp, clean layout typography item engineered for tabular listings, lane statuses, and technical readouts.
  * `sCTkLabelTertiray`:
* `sCTkProgressBar`: A
* `sCTkRadioButton`: A
* `sCTkScrollbar` & `sCTkScrollArea`: An unblocked viewport engine. Embedded with an **Inertial Micro-Delta Aggregator Loop**, it perfectly aggregates fine-grained macOS touchpad and Apple Magic Mouse gesture streams alongside standard notched scroll wheels with zero layout stutter or type error drifts.

* `sCTkSegmentedButton`: A
* `sCTkSlider`: A
* `sCTkSwitch`: A
* `sCTkTabview`: A multi-page layout container. Features cascading palette loops to cleanly desaturate unselected tabs and flatten backing frame blocks when frozen.
*  `Textboxes`
  * `sCTkTextboxPrimary`: A
  * `sCTkTextboxSecondary`: A



#### Menus
* `sCTkOptionMenuPrimary`: A
* `sCTkOptionMenuSecondary`: A



### Additional Widgets provided by `sCustomTkinter`
* `sCTkDial`: A
* `sCTkDialog`: A
* `sCTkFileExplorer`: A
* `sCTkFrameLabeledPrimary`: A
* `ssCTkFrameLabeledSecondary`: A
* `sCTkFrameOutlined`: A
* `sCTkPathChooser`: A
* `sCTkSelector`: A
* `sCTkSeparator`: A
* `sCTkSMeter`: A
* `sCTkSMeterBar`: A
* `sCTkSpinbox`: A
* `sCTkSwitchAlt`: A
* `sCTkTableview`: A dense, interactive telemetry data grid component. Features inline data validation filters, row double-click entry editing, and dynamic column property anchors.











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



