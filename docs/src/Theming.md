# Theming

Every colour, font, and several structural values in this library come from a single file: `sCTkThemes.json`. No widget hardcodes a colour. If you don't like the palette — and you may not, the author is somewhat red/brown colour blind — you change one file and the whole application follows.

* [Where the file lives](#where-the-file-lives)
* [Block structure](#block-structure)
* [State maps](#state-maps)
* [Light and dark](#light-and-dark)
* [Changing values at runtime](#changing-values-at-runtime)
* [Things that will break your theme](#things-that-will-break-your-theme)
* [Adding a theme block for your own widget](#adding-a-theme-block-for-your-own-widget)

---

<a name="where-the-file-lives"></a>
## Where the file lives

Two locations are checked, in this order:

1. **`sCTkThemes.json` in your application's working directory** — your override.
2. **`scustomtkinter/assets/sCTkThemes.json`** — the one shipped with the library.

The first one found wins, completely. There is **no merging**: if a local file exists, the bundled one is not consulted at all, for any widget.

That matters more than it sounds. Copy the bundled file, delete the blocks you don't care about, and every widget whose block you removed will fail to construct — not fall back to the library defaults. **Copy the whole file and edit in place.**

```bash
cp .../scustomtkinter/assets/sCTkThemes.json ./sCTkThemes.json
```

The file is read once, at import time. Changes require a restart.

---

<a name="block-structure"></a>
## Block structure

One block per widget class, keyed by the exact class name:

```json
{
    "sCTkButtonPrimary": {
        "fg_color": ["#1A4375", "#1F6AA5"],
        "text_color": ["#FFFFFF", "#FFFFFF"],
        "font": ["Arial", 13, "bold"],
        "disabled_map": {
            "fg_color": ["#CBD5E1", "#334155"],
            "text_color": ["#94A3B8", "#64748B"]
        }
    }
}
```

The class name is the lookup key and it is **case-sensitive and exact**. A block named `sCTkButton` does nothing for a widget class named `sCTkButtonPrimary`. There is no inheritance between blocks — `sCTkDialSelector` does not inherit from a `sCTkDial` block, and each of the three dial variants carries its own full set of keys even where the values are identical.

Two kinds of key appear in a block:

- **Native CustomTkinter options** — `fg_color`, `corner_radius`, `border_width` and so on. These are passed through to the underlying widget.
- **Keys specific to this library** — `dial_color`, `led_on_color`, `scale_font`, `btn_hover`. These are read by the widget's own drawing code and never reach CustomTkinter.

You mostly don't need to know which is which. It matters in one place: see [adding a block for your own widget](#adding-a-theme-block-for-your-own-widget).

---

<a name="state-maps"></a>
## State maps

Nested inside a block, a state map overrides specific keys when the widget is in that state. Anything not listed keeps its normal value.

| Map | Applies when |
|---|---|
| `disabled_map` | The widget is disabled via `state("disabled")` or `configure(state="disabled")`. |
| `pressed_map` | A button is being held down. |
| `alarm_map` | A widget is in an alert condition. |
| `readonly_map` | An entry or spinbox is readonly — arrows still work, typing is blocked. |

Most widgets use only `disabled_map`. The button family uses `pressed_map` and `alarm_map`; `sCTkEntryPrimary`/`Secondary` and `sCTkSpinbox` use `readonly_map` to support a genuine three-state model rather than collapsing everything non-disabled into "normal".

**A state map is not a full block.** Only list the keys that actually change. Widgets deliberately leave `fg_color` out of `disabled_map` in most cases — the background stays put and the border, text, or face carries the signal.

Some keys exist *only* inside a state map, because they have no normal-state equivalent. `sCTkSegmentedButton`'s `selected_text_color` is one: a selected segment's normal text colour comes from `text_color`, and the separate key exists so the selection is still identifiable when the control is greyed out.

---

<a name="light-and-dark"></a>
## Light and dark

Colours are written as a two-element list: **`[light_mode, dark_mode]`**.

```json
"text_color": ["#1A4375", "#FF9100"]
```

Widgets pass these through as pairs rather than resolving them up front, so CustomTkinter's own appearance-mode tracking repaints them when the user switches. You don't need to do anything.

A single string is also accepted, and means the same colour in both modes. The literal `"transparent"` is a CustomTkinter pseudo-value meaning "show whatever is behind me". Note that `"transparent"` **cannot** be used for anything drawn on a raw `tkinter.Canvas` — that includes the dials, the S-meters, and `sCTkScrollArea`'s background, which need a real renderable colour.

Fonts are `[family, size]` or `[family, size, weight]`.

### One place appearance mode does not reach

If you call `ctk.set_appearance_mode("dark")` while the operating system is set to light, **dropdown menus follow the system, not your setting.** The main widget goes dark; the menu that drops out of it stays light. Switch the system to dark and the menu follows — proving it is tracking the OS rather than the application.

Affects `sCTkComboBox`, `sCTkOptionMenuPrimary` and `sCTkOptionMenuSecondary`.

This is **not** something the theme file can fix, and not specific to this library — plain `customtkinter.CTkComboBox` behaves identically, confirmed by direct testing. The dropdown is a native menu that the operating system draws itself, largely ignoring the colours a widget configures on it.

The only real fix would be replacing the native menu with a CustomTkinter-drawn one — a `CTkToplevel` holding themed buttons. That is a widget-level project, not a theme change, and it hasn't been done.

If your application sets an appearance mode explicitly rather than following the system, expect this mismatch on those three widgets.

---

<a name="changing-values-at-runtime"></a>
## Changing values at runtime

`configure()` accepts theme keys directly, and the override **sticks**:

```python
frame.configure(fg_color="red")
```

Two consequences worth understanding:

**A single colour replaces the light/dark pair.** Passing one value for a key means that property stops following appearance mode — which is what asking for one specific colour means. Pass a two-element tuple if you want it to keep tracking:

```python
frame.configure(fg_color=("#FFFFFF", "#111827"))
```

**State maps still win in their state.** Overriding `border_color` sets the *normal*-state colour. If the widget is disabled, or later becomes disabled, `disabled_map` supplies the border colour as usual. To change what a disabled widget looks like, change the theme file.

---

<a name="things-that-will-break-your-theme"></a>
## Things that will break your theme

This section is the important one. JSON is unforgiving and the failure modes are not always obvious.

### Syntax errors take out the entire file

A missing comma, a stray trailing comma before a `}`, an unclosed brace, or a smart quote pasted in from a document — any one of these makes the whole file unparseable. The library catches the error, prints a warning, and **continues with an empty theme registry**. Every widget then fails to construct.

The warning looks like this:

```
sCustomTkinter System Warning -> Could not parse theme layout tracking: ...
```

If you see that line, the problem is a syntax error in your file, not in any widget. Validate before running:

```bash
python -m json.tool sCTkThemes.json > /dev/null
```

Silence means it parsed. Any editor with JSON support will also flag these as you type — worth using one.

### Deleting a key is not the same as leaving it at default

There is no "default" to fall back to. Widgets validate their required keys at construction and raise immediately:

```
KeyError: "'sCTkTabview' theme block is missing 'text_color' at the top level of sCTkThemes.json."
```

That message names the exact key and whether it belongs at the top level or in a state map. This is deliberate. An earlier design substituted a plausible hardcoded colour when a key was missing, and the result was worse than a crash: five separate widgets shipped for a long time rendering in hardcoded colours while their configured theme values were silently ignored, and nobody noticed because the substituted colours *looked* fine. A loud failure that names the key is far better than a widget that quietly ignores you.

If you genuinely don't want a widget's block, don't delete it — you'll break that widget. Change its values instead.

### Misspelling a key is worse than deleting it

A misspelled key is not an error. It's an unrecognised key that gets ignored, while the *correct* key is now missing:

```json
"text_colour": ["#1A4375", "#FF9100"]
```

That produces a `KeyError` about `text_color` being missing — which is confusing until you spot that your line is right there, spelled British. Check the spelling in this library's own documentation for the widget; it uses American spellings throughout, following CustomTkinter.

A misspelling inside a state map is quieter still: state maps aren't validated as strictly, so a typo there usually means "that property just doesn't change when disabled," with no error at all.

### Renaming a block orphans it

Rename `sCTkSlider` to `sCTkSliders` and the block becomes dead data while every slider fails to construct. Block names must match class names exactly.

The reverse also happens: a block for a widget that no longer exists, or was renamed, sits in the file doing nothing. Harmless, but it accumulates.

### Adding a key that isn't read does nothing

Adding `"hover_glow_color"` to a block will not make anything glow. Widgets read a fixed set of keys; extra ones are ignored silently. If you want a new visual property, the widget's drawing code has to read it.

---

<a name="adding-a-theme-block-for-your-own-widget"></a>
## Adding a theme block for your own widget

If you subclass `ThemeableWidget`, your block is found automatically by class name. Three things to know:

**Custom keys must not reach the native constructor.** CustomTkinter widgets reject keyword arguments they don't recognise — `CTkToplevel` in particular raises on *any* unknown key. Filter your resolved keywords down to what the native class actually accepts before calling `super().__init__()`. Every widget in this library that adds custom keys does this; copy the pattern from one close to yours.

**Some custom keys are stripped for you.** `ThemeableWidget` maintains an internal list of names it removes from the resolved keywords for canvas-drawing widgets — `dial_color`, `text_color`, `pointer_color` and others. If your widget uses one of those names, it will not be in `final_kw`, and you must read it from the raw theme registry instead. This is not obvious and has caused real bugs: an entire widget family rendered in fallback colours for its whole existence because it looked for those keys in the wrong place. If a colour you configured isn't appearing, this is the first thing to check.

**Validate your required keys at construction.** Follow the pattern used throughout:

```python
_REQUIRED_THEME_KEYS = ("fg_color", "text_color")
_REQUIRED_DISABLED_KEYS = ("text_color",)
```

and raise `KeyError` naming the missing key. It costs a dozen lines and turns a class of silent visual bug into an immediate, self-explaining failure.
