# List Properties

Several widgets take a list of strings — column headings, selectable items, dial labels, file extensions. All of them accept the same formats and parse them through one shared function, so the format you learn for one works everywhere.

* [Accepted formats](#accepted-formats)
* [Which properties](#which-properties)
* [In Pygubu Designer](#in-pygubu-designer)
* [In Python code](#in-python-code)
* [Why this is shared](#why-this-is-shared)

---

<a name="accepted-formats"></a>
## Accepted formats

Three forms, all equivalent:

```python
["Name", "Freq", "Mode"]      # bracketed list -- preferred
'Name, Freq, Mode'            # bare comma-separated
["Name", "Freq", "Mode"]      # a real Python list, in code
```

Details that hold across all of them:

- **Either quote style**, and mixing them is fine: `['A', "B"]` parses correctly.
- **Whitespace is stripped** from every value, so `AM, FM, LSB` gives `["AM", "FM", "LSB"]` with no leading spaces.
- **Quotes are optional** in the bracketed form: `[A, B]` works, even though it isn't valid Python.
- **Empty values are dropped**, so `a,,b` gives two items, not three.
- **Empty input** gives an empty list — or the property's own default where it has one — never `None`.

**Use the bracketed form when a value contains a comma.** That's the one thing the bare form can't express:

```python
["Smith, John", "Doe, Jane"]   # two values
'Smith, John, Doe, Jane'       # four values
```

Space is **not** a separator. `Meat Loaf` is one value.

---

<a name="which-properties"></a>
## Which properties

| Widget | Property |
|---|---|
| [`sCTkTableview`](sCTkTableview.md) | `columns` |
| [`sCTkSelector`](sCTkSelector.md) | `items` |
| [`sCTkDialSelector`](sCTkDialSelector.md) | `labels` |
| [`sCTkSpinbox`](sCTkSpinbox.md) | `values` |
| [`sCTkFileExplorer`](sCTkFileExplorer.md) | `filetypes` |
| [`sCTkPathChooser`](sCTkPathChooser.md) | `filetypes` |

All are settable at construction and through `configure()`, and both paths parse identically.

---

<a name="in-pygubu-designer"></a>
## In Pygubu Designer

Type the bracketed form into the property field:

```
["AM", "FM", "LSB"]
```

The bare comma-separated form also works and is quicker to type, but the bracketed form is what the inspector's defaults and help text show, for two reasons: it can express a value containing a comma, and it matches what the generated Python code will contain.

Generated code always emits a real Python list regardless of which form you typed.

---

<a name="in-python-code"></a>
## In Python code

Pass a real list. There's no reason to pass a string:

```python
table = sCTkTableview(parent, columns=["Channel", "Frequency", "Mode"])
selector = sCTkSelector(parent, items=["Ch 1", "Ch 2", "Ch 3"])
mode = sCTkDialSelector(parent, labels=["AM", "FM", "LSB", "USB", "CW"])
```

Tuples work too, and are returned as lists.

---

<a name="why-this-is-shared"></a>
## Why this is shared

These properties previously had **seven different parsers** and no two behaved alike:

| Widget | Old behaviour |
|---|---|
| `sCTkTableview.columns` | comma split, stripped |
| `sCTkSelector.items` | `ast.literal_eval` only — the bare form failed |
| `sCTkDialSelector.labels` | `literal_eval` at construction, but a plain comma split with **no quote stripping** in `configure()` — the same value parsed differently depending on when it was set |
| `sCTkFileExplorer.filetypes` | three separate implementations, in one file |
| `sCTkPathChooser.filetypes` | `literal_eval` only |
| `sCTkSpinbox.values` | `shlex.split` when no comma was present, making **space** a separator there and nowhere else |

The user-visible result was that each widget wanted a different format for the same kind of property, with nothing in the inspector to say which. Entering `AM, FM, LSB` into a dial produced labels with leading spaces; the identical string in a Tableview worked correctly. Entering `["A", "B"]` into a dial produced two garbage values.

They now all call `parse_list_property()` in `themeable_widget.py`. Space separation was dropped rather than propagated — `Meat Loaf` being two values in a spinbox and one value everywhere else was more surprising than useful.

**If you add a widget with a list property, use that function.** It's the difference between a format users can learn once and a format they have to look up per widget.
