# sCustomTkinter


A high-performance, theme-adaptive, and encapsulated widget framework engineered to support user interfaces with multiple designs for each widget. Not all Buttons (or for that matter Labels, Menus, etc.) should look the same in a well thought out UX. Important ones should catch your attention, while the less important fade into the background until needed. For example, `sCustomTkinter` starts you off with 3 different level of Buttons, that you can individually tailor to your design theme to help create consistency across your whole UX. 

This project is a set of subclasses (hence the "s" prefix) of Tom Schimansky's [CustomTkinter](https://customtkinter.tomschimansky.com/) which he has generously made available to the community under the MIT License. Without his work, this would not have been made possible.

The vast majority of the widgets provided by `sCustomTkinter` are based on the ones originally provided with `CustomTkinter`. However, there are several additions including knobs, analog meter displays, file choosers, table, selectors, and spinboxes that have been added primarily because I needed them for my own project and decided to share. In addition, the library has been designed from the start to integrated with Alejandro Autalan wonderful GUI Builder for python, [Pygubu-Designer](https://github.com/alejandroautalan/pygubu-designer). I have used his software extensively in other projects (visit other areas in my Github) and it has saved me a lot of time and effort.

However, this design has been architected to allow you to add your own widgets, or subclass mine for your purposes. The key to the themes is sCTkThemes.json. Don't like my color choices (understandable as I am a little red/brown color blind...) , copy this file from Github, modify it and put it in your applications directory. It will be found before the common one in scustomtkinter/assets.  The format of this file, is very similar to the original Themes definition file of `CustomTkinter` (it has additions that would give the standard `CustomTkinter` theme processor problems in addition to the new widgets that might cause a few runtime exceptions). 

Want to add a widget? Create it, add `ThemeableWidget` as a second base class, and see [dev/docs/Developing.md](dev/docs/Developing.md) — it covers the theme contract, the traps in forwarding properties to the underlying `CustomTkinter` widget, and the bugs that have turned up repeatedly in this library so you can avoid repeating them.



## Table of Contents
* [Quick-Start](#quick-start)
* [Theming](#theming)
* [Scrolling](#scrolling)
* [List Properties](#list-properties)
* [Designer Hints](#designer-hints)
* [Comprehensive Component Catalog](#comprehensive-component-catalog)
* [Repository Directory Structure](#repository-directory-structure)
* [License](#license)

---

## Quick-Start

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

root = sCTk()
root.geometry("600x450")
root.title("Station Command Console")

panel = sCTkFrame(root, border_width=2)
panel.pack(padx=20, pady=20, fill="both", expand=True)

btn = sCTkButtonPrimary(panel, text="Transmit Call", command=lambda: print("TX ACTIVE"))
btn.pack(pady=10)

root.mainloop()
```

### Pygubu-Designer Installation

    1. Install Pygubu-Designer into your virtual environment after installing sCustomTkinter. It is "pygubu-designer" and can be installed using the same tools as sCustomTkinter above.
    2. Start Pygubu-Designer, you will see the sCustomTkinter widgets at the bottom of the Components on the left.
	3. Add a sCTK root or a sCTkToplevel and go!

## Theming

Every colour and font in this library comes from one file, `sCTkThemes.json`. No widget hardcodes a colour. To change the palette, copy that file into your application's directory and edit it — the local copy is found before the bundled one.

**Copy the whole file.** The local file replaces the bundled one entirely; there is no merging. A block you delete is not filled in from the library defaults — the widget will fail to construct instead. That's deliberate: widgets validate their required keys and raise a `KeyError` naming exactly what's missing, because the alternative (silently substituting a plausible colour) hid real bugs for a long time.

The format extends CustomTkinter's own theme file with per-state colour maps and additional widget blocks. Colours are `[light_mode, dark_mode]` pairs and follow appearance-mode switches automatically.

**See [Theming](docs/Theming.md)** for the full reference, including state maps, runtime overrides, and the several ways a hand-edited JSON file can break.

---

## Scrolling

Wheel and trackpad handling is shared by every scrolling widget, so it behaves consistently and is tuned in one place. Windows, Linux, and macOS are each handled natively, including macOS's separate high-precision trackpad event stream.

For most cases use `sCTkScrollableFrame`, which manages its own scrollbar. Use `sCTkScrollArea` with a separate `sCTkScrollbar` when you need the bar somewhere the built-in one can't go.

Scroll speed is controlled by three constants that can be changed globally or per widget. If a wheel click moves too far or too little — particularly on macOS, where a wheel mouse and a Magic Mouse report wildly different values — that's what to adjust.

**See [Scrolling](docs/Scrolling.md)** for the widget comparison, the tuning constants, and how disabling interacts with scroll state.

---

## List Properties

Several widgets take a list of strings — a table's column headings, a menu's items, a dial's labels. They all accept the same three forms: a bracketed list `["A", "B", "C"]`, a bare comma-separated string, or a real Python list.

The bracketed form is the one to prefer, and the only one that can hold a value containing a comma.

**See [List Properties](docs/src/ListProperties.md)** for which properties use it and why seven separate parsers became one.

---

## Designer Hints

Notes for working in Pygubu Designer: how images resolve at runtime, what clearing a field does, which widgets can only be selected from the widget tree, and what the light green background means.

**See [Designer Hints](docs/src/DesignerHints.md).** Skip it if you build your interfaces in code.

---

## Comprehensive Component Catalog

The reference manual for this library is provided [here](docs/README.md) and the [pdf](docs/sCustomTkinterReferenceManual.pdf) The following is a summary of the library:


### Standard CustomTkinter Widgets

All of the following are subclassed from their respective CTk. For example, sCTkCheckBox is a subclass of CTkCheckBox that includes the theming engine of `sCustomTkinter`


#### Containers
* <u>`sCTk`</u>: The core main window master shell container. A clean, direct pass-through wrapper for `customtkinter.CTk`.


* <u>`sCTkToplevel`</u>: Often used for modal configuration screens and popup alert logs cleanly.


* <u>`sCTkFrame`</u>: Commonly used to group and organized a set of widgets that internally need to be placed relative to each other.


* <u>`sCTkScrollableFrame`</u>: Provides a Frame with scrollbars. Very convenient widget as it avoids the complexity of adding a sCTkSCrollbar to a frame.


#### Controls and Display
* <u>sCTkButtons</u>: There are three levels of buttons included in the library.
    - `sCTkButtonPrimary` - Provides high-visibility, accented action button featuring integrated hover loops and dynamic panel lock desaturation states. Use this for the action the user should take. 
    - `sCTkButtonSecondary` - A toned down button used for less likely options or end points. You might use this for the Cancel button.
    - `sCTkButtonTertiary` - Known in the industry as a `Ghost Button`, this button is almost invisible. Use this for low probability selections.


* <u>`sCTkCheckBox`</u>: Used to enable/disable a feature function. 


* <u>Entry Fields</u>: There are two levels of Entry Fields included in this library.

	- `sCTkEntryPrimary` - It is recommended that you use this one for key or required input.
	- `sCTkEntrySecondary` - This one might be more appropriate for optional input.


* <u>Labels</u>: Used to describe options or communicate information to the end user.

	- `sCTkLabelPrimary` A bold, larger font size element used for high-contrast foreground labels. This one is typically used for Headers/Titles/Sections.
    - `sCTkLabelSecondary`: A crisp typography item engineered for tabular listings, lane statuses, and technical readouts.
	- `sCTkLabelTertiary`: Much smaller font. You would probably use this one for informational notices.


* <u>`sCTkProgressBar`</u>: Often used in a popup window to communicate progress on a lengthly task.


* <u>`sCTkRadioButton`</u>: Typically a set of 2 or more would be parented in a Frame. Pushing one button, automatically "unpushes" the currently pushed button. This widget gets its name for old car radios where each button was attached to a different radio station.


* <u>`sCTkScrollbar`</u>: An independent widget that can be attached to a Frame, Canvas or other scrollable object. See `sCTkScrollArea` for additional flexibility.


* <u>`sCTkSegmentedButton`</u>: Imagine 3 buttons smashed together. Click one of the buttons to fire a callback. Tho actions of the buttons are mutually exclusive. Selecting one unselects the others just like a RadioButton.


* <u>`sCTkSlider`</u>:: Used to adjust a value. Slide the handle one way or another. Both Horizontal and Vertical positioning are supported.


* <u>`sCTkSwitch`</u>: Simple slide switch for values that are on or off. Its disabled appearance has been retuned so the handle and track stay distinguishable in both light and dark modes.


* <u>`sCTkTabview`</u>: A multi-page layout container. Select the page by click the tab. Useful to minimize footprint and organize common operations while isolating those that are either irrelevant or conflicting.


* <u>Textboxes</u>: Two levels of text boxes are supported for different needs of your users.
	- `sCTkTextboxPrimary` - The standard textbox that you will probably use most of the time.
	- `sCTkTextboxSecondary` - Smaller font that you might find useful for other purposes.



#### Menus

* <u>`sCTkComboBox`</u>: Drop down menu of choices. But more importantly, can accept user input.



* <u>OptionMenus</u>: Two levels of optionsMenus (basically da rop down list that the user selects an item from) are provided.

	- `sCTkOptionMenuPrimary`: Larger font with stronger colors. Probably the one you will use for your main options
	- `sCTkOptionMenuSecondary`: Smaller font, less obvious colors. Use for less common options.


### Additional Widgets provided by `sCustomTkinter`
* <u>sCTkDial</u>: A set of 3 Dials/Knobs.

	- `sCTkDialContinuous` - This dial can turn forever clockwise or counterclockwise. Think of a knob to rune in a radio station.
    - `sCTkDialRange` - Has a stop/end point with user setable "ticks" A volume knob would be a good use for this widget.
    - `sCTkDialSelector` - Provide a fixed number of selections. For example, "AM", "FM", "HF", etc.


* <u>`sCTkDialog`</u>: A popup dialog with a heading, a content area you fill, and a row of Apply / Cancel / Reset buttons. It creates its own window, so you do not build a `Toplevel` around it.


* <u>`sCTkFileExplorer`</u>: Allows for browsing and selection of files or directories. You provide the infrastructure on when this is popped up and what are the selection criteria.


* <u>Labeled Frames</u>: Just a Frame with a build in Label. Built on a ScrollableFrame with the scrollbar disabled.

	- `sCTkFrameLabeledPrimary` - Larger font for Label. You would probably use this as an outer frame.
	- `sCTkFrameLabeledSecondary` -  Smaller fonts and border. Useful to group similar settings that you want to identify by a name.


* <u>Messagebox</u>: Used to communicate immediate and perhaps actionable information to the user. There are three types, Info, Warning and Error. And each can be configured for a customized single or two button response.
	- `sCTkMessagebox.showinfo`
    - `sCTkMessagebox.showwarning`
	- `sCTkMessagebox.showerror`
    - `sCTkMessagebox.askyesno`
    - `sCTkMessagebox.askwarningyesno`
	- `sCTkMessagebox.askerroryesno`

* <u>`sCTkPathChooser`</u>: Preconfigured file/directory selection widget.


* <u>`sCTkScrollArea`</u>: Addon to `sCTkScrollbar` that allows you to identify what scrolls when the cursor is within the widget.


* <u>`sCTkSelector`</u>: Allows the single or multiselection of properties. Also optionally includes a search bar.


* <u>`sCTkSeparator`</u>: Used to place a line between different widgets. Lines can be solid, dashed and include text.


* <u>`sCTkSMeter`</u>: Classical analog sweep meter for displaying signal strength.


* <u>`sCTkSMeterBar`</u>: Similar to the SMeter, the information is displayed as "bars". Natively supports S, SWR and PWR.


* <u>`sCTkSpinbox`</u>: Classical widget where different values can be selected by clicking the up/down arrows. Both numbers and text are supports.



* <u>`sCTkTableview`</u>: Supports the display of data in a table like format. Includes in place editing as well as different styles of display ("grid, "zebra", "none")



## Repository Directory Structure

```text
sCustomTkinter/                   (The GitHub repository root)
├── README.md                     (This file)
├── setup.py
├── requirements.txt
│
├── scustomtkinter/               (The library package)
│   ├── __init__.py               (Top-level import map)
│   ├── themeable_widget.py       (Theme resolution, shared helpers)
│   ├── sctk_core.py              (sCTk, the root window)
│   ├── sctk_<widget>.py          (One module per widget)
│   └── assets/
│       └── sCTkThemes.json       (Master stylesheet)
│
├── scustomtkinter_pygubu/        (Pygubu Designer integration)
│   ├── sCTk<Widget>bo.py         (One builder object per widget)
│   └── designer/
│       ├── plugin.py             (Preview classes and Designer hooks)
│       └── properties.py         (Property registration)
│
├── docs/
│   ├── README.md                 (The built manual, one file)
│   ├── src/                      (Per-widget and shared source pages)
│   └── images/                   (Light and dark screenshots)
│
├── dev/docs/
│   └── Developing.md             (Notes for extending the library)
│
├── examples/                     (Runnable test harnesses)
│
└── tools/
    └── build_docs.sh             (Concatenates docs/src into docs/README.md)
```
---

## License

`sCustomTkinter` is released under the MIT License. See [LICENSE](LICENSE) for the full text.

This project builds on [CustomTkinter](https://customtkinter.tomschimansky.com/) by Tom Schimansky, also MIT licensed. Individual widgets derived from other MIT-licensed community work carry their attribution in the source file's module docstring.

You may use, modify, and distribute this library, including in commercial and closed-source products. The only requirement is that the copyright notice and licence text travel with any substantial portion of the code you redistribute.
