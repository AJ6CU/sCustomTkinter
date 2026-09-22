## sCTkTableview

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Methods](#methods)
* [Editing and Selection](#editing-and-selection)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkTableview` is a theme-compliant, scrollable grid of labeled cells — a simple spreadsheet-like table, with optional zebra-striped rows, click and edit callbacks, and in-place cell editing. It's built by inheriting `sCTkScrollableFrame` directly, using its scrolling and label feature, then laying out its own header row and cell grid on top.

  ![sCTkTableview in dark mode](images/sCTkTableview_Dark.png)&emsp; &emsp; &emsp; &emsp;
 ![sCTkTableview in light mode](images/sCTkTableview_Light.png)

This widget inherits `sCTkScrollableFrame` directly — the same composition pattern used by `sCTkSelector` — and previously needed a fragile workaround for it: temporarily overwriting its own `self.__class__.__name__` during construction, to trick `sCTkScrollableFrame`'s internal `ThemeableWidget.__init__` call into reading a harmless theme block instead of corrupting this widget's own. That workaround has been removed entirely. `ThemeableWidget`'s run-once guard now prevents the double-init outright, and `sCTkScrollableFrame` itself filters its inbound kwargs down to only what native `CTkScrollableFrame` actually accepts — confirmed directly against CustomTkinter's source to have no `**kwargs` catch-all at all, so this filtering matters more here than for almost any other widget in this project.

---

### Constructor

```python
sCTkTableview(master, columns=None, width=500, height=300, grid_mode="zebra",
              header_line_width=2, outline_width=1.0, outline_radius=4,
              state="normal", num_columns=3, num_rows=1, show_headers=True,
              cell_bg_color=None, cell_alt_bg_color=None,
              editable_columns=None, edit_trigger="double", select_rows=False,
              column_choices=None, *args, **kwargs)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | — | Parent container. |
| `columns` | `list[str]` or `str` | `None` | Column header labels. Accepts `["Time", "Freq"]`, a bare comma-separated string, or a real list — see [List Properties](ListProperties.md). Setting this also sets `num_columns` to match. |
| `width` / `height` | `int` | `500` / `300` | The width fits the columns. The height fits the rows **up to this value**; a table with more rows than that scrolls. |
| `grid_mode` | `"zebra"` / `"grid"` / `"none"` | `"zebra"` | Row background styling. |
| `header_line_width` | `int` | `2` | Header row's bottom border thickness. |
| `outline_width` / `outline_radius` | `float` / `int` | `1.0` / `4` | Outer table border thickness and corner rounding. |
| `state` | `"normal"` / `"disabled"` | `"normal"` | Initial state. |
| `num_columns` / `num_rows` | `int` | `3` / `1` | Initial grid size when `columns` isn't given. |
| `show_headers` | `bool` | `True` | Whether the header row is shown. |
| `cell_bg_color` / `cell_alt_bg_color` | color | `None` | Overrides the theme's cell background colors for this instance specifically — see [Theming](#theming-sctkthemesjson) for how this interacts with the theme file. |
| `editable_columns` | `list[int]` or `str` | `None` | Which columns can be edited, by index — `[1, 2]` or `"1, 2"`. `None` means every column. See [Editing and Selection](#editing-and-selection). |
| `edit_trigger` | `"double"` / `"select"` | `"double"` | What opens a cell's editor. See [Editing and Selection](#editing-and-selection). |
| `select_rows` | `bool` | `False` | Highlight the row last clicked. Always on when `edit_trigger` is `"select"`. |
| `column_choices` | `dict` | `None` | `{column_index: [values]}` — columns edited by choosing from a list instead of typing. See [Choosing from a list](#choosing-from-a-list). |
| `**kwargs` | — | — | Any native `CTkScrollableFrame` argument, or an override for one of the other theme keys listed under [Theming](#theming-sctkthemesjson). |

```python
readings_table = sCTkTableview(control_panel, columns=["Time", "Frequency", "Signal"], num_rows=8)
readings_table.pack(expand=True, fill="both", padx=20, pady=20)
```

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `load_dataset(rows)` | — | Replaces every row, rebuilding the cells. `rows` is a list of lists; short rows are padded and long ones cut to the column count. |
| `set_row(index, values)` | — | Replaces one row's values in place, without rebuilding. Use it for a table that changes a row at a time — `load_dataset()` recreates every cell, which is slow and flickers. |
| `select_row(index)` | — | Selects a row from code, or clears the selection given `None`. Does **not** call the selection callback. |
| `get_selected_row()` | `int` or `None` | The selected row's index. |
| `clear_selection()` | — | Equivalent to `select_row(None)`. |
| `bind_selection_callback(fn)` | — | `fn(row_index, row_values)` on every click on a row. |
| `set_column_choices(index, choices)` | — | Makes a column edited from a list of `choices`, or typed again given `None`. |
| `bind_cell_editable_callback(fn)` | — | `fn(row_index, column_index) -> bool`, for cells whose editability depends on the row. See [Editing and Selection](#editing-and-selection). |
| `bind_activate_callback(fn)` | — | `fn(row_index, row_values)` on a double-click that does not open an editor. See [Editing and Selection](#editing-and-selection). |
| `bind_edit_callback(fn)` | — | `fn(row_index, column_index, value)` after an edit that changed the cell. |
| `bind_validation_callback(fn, with_row=False)` | — | Checks an edit before it is stored. See [Validating an edit](#validating-an-edit). |
| `state(mode=None)` / `get_state()` | `str` | Gets or sets `"normal"`/`"disabled"`. |
| `configure(**kwargs)` / `config(**kwargs)` | varies | Standard configuration, plus `state=...` triggers a full color/font re-application across every header and cell. `columns=...` rebuilds the header row and resizes the grid to match. |

---

<a name="editing-and-selection"></a>
### Editing and Selection

By default every cell can be edited by double-clicking it, and no row is highlighted — the table's original behaviour. Three options change that.

**`editable_columns`** limits editing to the columns listed. The rest are read-only, which a row number, a computed value or a note needs:

```python
table = sCTkTableview(panel, columns=["#", "Label", "Frequency", "Note"],
                      editable_columns=[1, 2])
```

**Some cells in an editable column may still need to be read-only** — a column that only some rows can hold. `bind_cell_editable_callback` decides cell by cell, and a cell it refuses never opens an editor. That matters: refusing the edit afterwards, in validation, would let someone type into the cell and then throw the typing away without a word.

```python
# Only the first nine rows carry a label.
table.bind_cell_editable_callback(lambda row, col: not (col == 1 and row >= 9))
```

It is consulted after `editable_columns`, so a column left out there stays read-only whatever the callback says.

**`edit_trigger="select"`** opens the editor when you click a cell in the row that is **already selected** — the spreadsheet and file-manager convention. That frees the double-click for something else, reported through `bind_activate_callback`:

```python
table = sCTkTableview(panel, columns=[...], editable_columns=[1, 2],
                      edit_trigger="select")
table.bind_activate_callback(lambda row, values: open_record(row))
```

A double-click starts with an ordinary click, so on the selected row that first click would open an editor just before the double-click arrived. To prevent it, a click on the selected row waits half a second (`EDIT_DELAY_MS`) before opening the editor, and a double-click arriving in the meantime cancels it — the same pause a file manager takes before renaming.

With `"double"`, a double-click on an editable column edits it, and one on a read-only column goes to the activate callback instead.

**`select_rows=True`** highlights the row last clicked. It is always on with `"select"`, which cannot work without a selection. `select_row()` sets the selection from code without calling the selection callback — the application already knows what it chose.

**In the editor**, Return or clicking away keeps the change, and **Escape cancels it**, leaving the cell as it was. One editor is open at a time. Reloading the table with `load_dataset()` cancels an open editor rather than saving it, since the data it was editing is being replaced.

<a name="choosing-from-a-list"></a>
#### Choosing from a list

A column whose values come from a fixed set is better chosen than typed — typing invites mistakes, and every value then needs checking. Give it choices, and its cells are edited with a dropdown instead:

```python
table = sCTkTableview(panel, columns=["Label", "Mode"], editable_columns=[0, 1],
                      column_choices={1: ["LSB", "USB", "CWL", "CWU"]})
```

The dropdown opens already showing its list, so choosing takes the same clicks as typing. **Only a choice is kept.** The menu has to show something when it opens — for a cell holding none of the choices, the first one — so closing it without choosing, whether by Escape or by clicking another cell, changes nothing. Otherwise an empty cell would quietly take the first value just from being looked at.

A chosen value goes through validation and the edit callback like a typed one.

<a name="validating-an-edit"></a>
#### Validating an edit

`bind_validation_callback(fn)` checks each edit before it is stored. The callback's answer decides what happens:

| Returns | Result |
|---|---|
| a string | Accepted — and **this** is stored instead of what was typed. Use it to tidy a value: a frequency typed `14.074` stored as `14.074.000`. |
| anything else truthy | Accepted as typed. |
| anything falsy | Rejected — the cell keeps its old value. |

By default the callback is `fn(column_index, value)`. Pass `with_row=True` to have it called as `fn(row_index, column_index, value)`, for checks that depend on the row — whether that row may hold a value at all, say. It is a separate switch, so existing two-argument callbacks keep working.

A rejected edit, or one that leaves the value unchanged, does not call the edit callback.

---

### Theming (`sCTkThemes.json`)

- **Applied once, at construction** — every key below, plus `cell_bg_color`/`cell_alt_bg_color` (which can also come from the constructor, see below).
- **Re-applied on every `state()` change.**

```json
{
    "sCTkTableview": {
        "header_bg_color": ["#E2E8F0", "#0F172A"],
        "header_text_color": ["#0F172A", "#F8FAFC"],
        "header_font": ["Arial", 14, "bold"],
        "cell_bg_color": ["#FFFFFF", "#111827"],
        "cell_alt_bg_color": ["#D1DCEE", "#222C3A"],
        "cell_text_color": ["#1E293B", "#E2E8F0"],
        "cell_font": ["Arial", 13, "normal"],
        "grid_line_color": ["#CBD5E1", "#334155"],
        "disabled_map": {
            "header_bg_color": ["#CBD5E1", "#1E293B"],
            "header_text_color": ["#94A3B8", "#64748B"],
            "cell_bg_color": ["#F1F5F9", "#1F2937"],
            "cell_alt_bg_color": ["#E2E8F0", "#263241"],
            "cell_text_color": ["#94A3B8", "#64748B"],
            "grid_line_color": ["#E2E8F0", "#293548"]
        }
    }
}
```

All six colors are required both at the top level and in `disabled_map` — missing any raises immediately at construction, naming the exact key.

**`cell_selected_color` is optional**, at the top level and in `disabled_map` — it colours the selected row. A theme written before rows could be selected has no such key, and requiring it would break every one of them, so when it is absent the header colour stands in. That is still a theme value, never a hardcoded one. `header_font`/`cell_font` are required only at the top level; no widget in this project uses a disabled-state font variant.

**`cell_bg_color`/`cell_alt_bg_color` are the two exceptions** — they can come from either the theme block *or* the constructor kwarg of the same name, so it's only a hard failure if *neither* provides a value. Whichever one this instance resolves to at construction is remembered and correctly restored on every return to `"normal"` — an earlier version always reverted to the theme's value on re-enable, silently discarding a constructor override after a disable/enable cycle.

Colors are passed through as raw `(light, dark)` tuples, letting CustomTkinter's native appearance-mode tracking handle repaints — an earlier version resolved disabled-state colors to a single fixed string while leaving enabled-state colors as tuples, meaning a disabled table would stop following light/dark mode changes while an enabled one kept working correctly. Both branches are now consistent.

---

### Example

```python
from scustomtkinter import sCTk, sCTkFrame, sCTkTableview, sCTkButtonPrimary

if __name__ == "__main__":
    root = sCTk()
    root.geometry("400x300")
    root.title("Tableview Example")

    base = sCTkFrame(root)
    base.pack(expand=True, fill="both", padx=20, pady=20)

    table = sCTkTableview(base, columns=["Time", "Frequency", "Signal"], num_rows=6)
    table.pack(expand=True, fill="both", pady=10)

    def toggle_disabled():
        target = "disabled" if table.get_state() == "normal" else "normal"
        table.configure(state=target)
        toggle_btn.configure(text="Enable Table" if target == "disabled" else "Disable Table")

    toggle_btn = sCTkButtonPrimary(base, text="Disable Table", command=toggle_disabled)
    toggle_btn.pack(pady=10)

    root.mainloop()
```

---

### Known Limitations

- **`columns` passed to the constructor sets the column count.** Earlier versions only did so through the Designer or `configure()`, so a table built in code with five column names showed three — the default — and dropped the rest.
- **A long table scrolls rather than growing.** Earlier versions sized the height to every row, so a table with many rows asked for enough room never to scroll and pushed its neighbours out of the window. The `height` given is now the most it will take.
- **Changing `columns` clears the table.** The rebuild reloads with empty rows, the same as changing `num_columns`. Expected at design time; reload your data afterwards at runtime.
- **Column choices are set in code.** The Designer's property panel has no way to hold a list per column, so `column_choices` is not offered there.
- **The edit callback fires only when a value actually changes.** Retyping the same value, or leaving an editor without altering anything, is silent — as is an edit the validation callback rejects. An earlier version compared the cell against the value it had just written to that same cell, a condition that was always true, so the callback fired on every save regardless.
- Missing a required theme key raises `KeyError` at construction, naming exactly which key and whether it's needed at the top level or in `disabled_map` — check the exact message if construction fails after a theme file change.
- Calling `configure("propname")` for most single-argument property queries falls through to the native widget's `configure()`, which doesn't support arbitrary single-argument queries — the same known gap as elsewhere in this project's Pygubu-query investigation.

[Return to Table of Contents](#contents)
