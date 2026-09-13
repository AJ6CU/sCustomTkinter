# Developing sCustomTkinter

Notes for extending this library: adding a widget, writing a Pygubu Designer builder object, or changing shared machinery. **Not needed to use the library** — for that, see the [reference manual](../../docs/README.md).

Most of what follows was learned the expensive way. Where a section explains a bug, it is because that bug cost real time to find and the code alone does not explain itself.

* [Conventions](#conventions)
* [Writing a widget](#writing-a-widget)
* [Theme mechanics](#theme-mechanics)
* [Recurring bug patterns](#recurring-bug-patterns)
* [Pygubu Designer plugin requirements](#pygubu-designer-plugin-requirements)
* [Testing](#testing)

---

<a name="conventions"></a>
## Conventions

**File naming.** `sctk_<widgetname>.py` in `scustomtkinter/`, `sCTk<WidgetName>bo.py` in `scustomtkinter_pygubu/`. One deliberate exception: the root window class `sCTk` lives in `sctk_core.py`, not `sctk_sctk.py`, and its builder object is `sCTkCorebo.py`. Both sides break the convention together.

**Class naming.** Match CustomTkinter's capitalisation exactly — `sCTkToplevel`, lowercase `l`, mirroring `CTkToplevel`. A mismatch here propagates into generated code as an import of a name that does not exist.

**`config = configure`.** Every class that overrides `configure()` needs this line, declared on that class. Tkinter binds `.config` to `.configure` as a separate class attribute and does **not** track a subclass's override, so without it `.config(...)` silently skips your code and lands on the native widget. Inheriting the alias does not help — it would point at the parent's `configure()`.

**List properties** go through `parse_list_property()` in `themeable_widget.py`. See [List Properties](../../docs/src/ListProperties.md) for the accepted formats and why seven separate parsers were consolidated into one.

**Scroll handling** goes through `ScrollBindingMixin`. Do not write a fourth copy.

**Fonts from the Designer** go through `parse_font_property()` in
`themeable_widget.py`. Pygubu's `fontentry` editor emits a Tk font
specification rather than a tuple, and for *no style selected* it emits Tk's
empty-list literal:

    {American Typewriter} 12 {}

Passed through as a style, that reaches a canvas item as
`TclError: unknown font style ""`. Two builder objects had their own copy of
this parser and both got it wrong the same way, which is why there is now one.

**Documentation style.** H2 title, H3 sections, no emoji, no marketing language, dark and light mode images, "Return to Table of Contents" link at the end.

---

<a name="writing-a-widget"></a>
## Writing a widget

The minimum shape:

```python
class sCTkMyWidget(ctk.CTkSomething, ThemeableWidget):
    _REQUIRED_THEME_KEYS = ("fg_color", "text_color")
    _REQUIRED_DISABLED_KEYS = ("text_color",)

    def __init__(self, master=None, **kw):
        ThemeableWidget.__init__(self, kw)
        self._local_defaults = dict(self.final_kw)
        self._custom_disabled_map = dict(self._widget_disabled_map)
        self._validate_theme_keys()

        native_kwargs = {k: v for k, v in self.final_kw.items()
                         if k in self._NATIVE_KWARGS}
        super().__init__(master, **native_kwargs)
        self._finalize_themeable_lifecycle()
```

Four things that matter:

**Base class order.** The native CTk class comes first, `ThemeableWidget` second. Every `super()` call in your file then resolves to the native widget rather than the mixin — which is why `ThemeableWidget` has no `configure()`/`cget()` overrides. They would be unreachable.

**Whitelist your kwargs.** CustomTkinter widgets reject keywords they do not recognise, and `CTkToplevel` and `CTkScrollableFrame` name every parameter explicitly with no `**kwargs` catch-all — so *any* stray key raises. Filter `final_kw` down to what the native class actually accepts before calling `super().__init__()`.

**Validate required theme keys.** See [Theme mechanics](#theme-mechanics).

**Call `_finalize_themeable_lifecycle()` last.** It notifies Pygubu that construction finished.

### A CTkFrame with an explicit size ignores its children

`CTkFrame` defaults to 200x200, and a frame given an explicit width or height
requests THAT size regardless of what is inside it. Setting one dimension and
leaving the other at its default silently imposes 200px:

```python
self.contentFrame.configure(width=500)            # height still demands 200
self.contentFrame.configure(width=500, height=1)  # collapses to its children
```

`sCTkDialog` carried an unexplained 120px of empty space above its button row
for exactly this reason. If a container is meant to size to its contents,
collapse the dimension you are not setting.

### Composing an sCTk widget as a base class

If your widget inherits another sCTk widget rather than a native one — `sCTkTableview` inherits `sCTkScrollableFrame`, `sCTkSelector` inherits `sCTkFrame` — the parent's `__init__` runs with `self.final_kw` built from **your** theme block, not its own. `ThemeableWidget`'s run-once guard prevents it being rebuilt.

Two consequences:

- The parent's theme validation would demand *its* keys from *your* block. Scope validation with `if type(self) is MyClass:` so subclasses are exempt and validate their own contract.
- Anything the parent sets in `__init__` may overwrite what you set before calling `super().__init__()`. Guard with `if not hasattr(self, "_state"):` in the parent.

Both patterns are in `sctk_scrollable_frame.py`.

---

<a name="theme-mechanics"></a>
## Theme mechanics

The user-facing rules are in [Theming](../../docs/src/Theming.md). These are the parts only a widget author hits.

### Vector-guarded keys are not in `final_kw`

`ThemeableWidget` maintains a `CUSTOM_VECTOR_KEYS` set — `dial_color`, `shadow_color`, `text_color`, `pointer_color`, `pointer_glow_color`, `diameter` and others — which it strips from `final_kw` for canvas-drawing widgets so they never reach a native constructor that would reject them.

That stripping is correct. Reading those colours back out of `final_kw` afterwards is not, because they were never there.

**This produced a real bug that survived for the entire life of a widget family.** The dials read their colours from `self._local_defaults`, which is `dict(self.final_kw)`, with `.get(key) or ("#hex", "#hex")` fallbacks. Every fallback was therefore *always* taken. The configured `dial_color`, `shadow_color`, `text_color` and `pointer_glow_color` were decorative — the dials rendered in hardcoded colours regardless of the theme file, and nobody noticed because the hardcoded colours looked reasonable.

If your widget uses one of those key names, read the raw registry instead:

```python
from . import themeable_widget as _tw

raw_block = _tw.GLOBAL_THEME_REGISTRY.get(self.__class__.__name__) or {}
raw_colors = {k: v for k, v in raw_block.items() if not isinstance(v, dict)}
self._local_defaults = ThemeableWidget._convert_lists_to_tuples(raw_colors)
self._local_defaults.update(self.final_kw)
```

Access it as a **module attribute**, not a direct name import: `load_initial_framework_themes()` rebinds that global on load, so `from ... import GLOBAL_THEME_REGISTRY` captures the empty dict that existed at import time.

### Fail loud, never fall back

Validate required keys at construction and raise `KeyError` naming the missing key and where it belongs:

```python
raise KeyError(
    f"'{name}' theme block is missing '{key}' in disabled_map."
)
```

**Do not write `.get(key, ("#hex", "#hex"))`.** Five separate widgets shipped rendering in hardcoded colours while their configured values were silently ignored, by five *different* mechanisms:

| Mechanism | Widgets |
|---|---|
| `disabled_map` read from `final_kw`, which excludes it — always an empty dict | Switch, Spinbox, Tabview, Tableview |
| Vector-guarded keys read from `final_kw` | the dial family |
| Key popped in `__init__`, then read back from the dict it was removed from | both S-meters |
| No `disabled_map` in the theme block at all | Separator |
| Fallbacks reachable only if a key is deleted | SegmentedButton |

Every one was invisible because the substituted colour looked plausible. A loud failure naming the key is far cheaper.

### Reading a state map

Read from `self._widget_disabled_map`, **not** from `final_kw` or `_local_defaults` — `ThemeableWidget` excludes `disabled_map` from `final_kw` deliberately, so reading it there yields `{}` and every disabled lookup silently falls through.

### Runtime overrides must survive the repaint

If your widget has a repaint routine that re-pushes colours from stored defaults — most do, for appearance-mode switches and state changes — then a value set through `configure()` has to be written into those defaults, or the repaint reverts it on the next line.

Call the shared helper near the top of `configure()`, before the values are consumed or forwarded:

```python
def configure(self, *args, **kwargs):
    ...
    self._record_theme_overrides(kwargs)

    if "state" in kwargs:
        self.state(kwargs.pop("state"))
    ...
```

That is the whole contract. `ThemeableWidget._record_theme_overrides()` handles five things a hand-written loop tends to miss:

| It does | Because |
| :--- | :--- |
| Records only keys the theme block defines | That is exactly the set a repaint reapplies. No per-widget key list to maintain, and native options the theme says nothing about are left alone. |
| Normalises the value into theme shape | The Designer supplies a plain string. Several widgets call `tuple()` on a colour, and `tuple("red")` is `('r','e','d')` — which CustomTkinter rejects. A string becomes `(value, value)` when the map holds a pair. |
| Snapshots the theme before the first override | Otherwise `_local_defaults` no longer holds the theme's value, and a query reports the override as its own default — so clearing a field in the Designer restores the override instead of the theme. |
| Triggers a repaint | Derived values are the reason. `sCTkOptionMenuSecondary` computes `button_color` from `fg_color`; those are worked out in the repaint, not in `configure()`. Without this, clearing `fg_color` restored the background and left the arrow on the override. |
| Maps `text_color_disabled` onto `disabled_map.text_color` | They are one value under two names — CustomTkinter's native option and this library's theme key. Recorded separately, a repaint would overwrite whichever was set last. |

**Report the pristine value as a query default.** If your widget has its own branch in the single-argument query form, take the default from `_theme_default(pname)`, not from `_local_defaults`:

```python
return (pname, pname, pname,
        self._query_value(self._theme_default(pname)),
        self._query_value(val))
```

Four widgets were missed on this because their query never reached `_configure_query` — `sCTkSwitch`, `sCTkSpinbox`, `sCTkTableview` and `sCTkSlider` each had a private branch with its own default table. A shared fix does not reach a private path.

**Fall back to the current value when the theme has nothing.** `_theme_default()` returns `None` for a key the block does not define, and pygubu hands that `None` straight back to the widget:

```
color is None, for transparency set color='transparent'
```

**Canvas-drawing widgets need their key list consulted too.** If your widget reads theme keys that are not native options — the dials, the S-meters — `configure()` must consume them before forwarding, or `CTkFrame` raises `['text_color'] are not supported arguments`. Popping any key present in `_local_defaults` covers it without a second list to maintain.

### Subclasses and theme block names

`ThemeableWidget` resolves a block by `self.__class__.__name__`, with `_THEME_BLOCK_NAME` as an override. A subclass whose name has no theme block gets an empty one — and any widget with fail-loud validation then raises. Preview subclasses in the Designer plugin all set it, and so does any widget meant to be subclassed by users.

Two failures follow from this, both under [Recurring bug patterns](#recurring-bug-patterns): a widget built for subclassing needs to declare the attribute, and validation messages must report the resolved block rather than the class.

---

<a name="recurring-bug-patterns"></a>
## Recurring bug patterns

These appeared in nearly every file audited. Check for them in anything new.

### `pname = args`

```python
def configure(self, *args, **kwargs):
    if args and len(args) == 1:
        pname = args          # WRONG -- a tuple
        if pname == "state":  # never true
```

`args` is a tuple; `args[0]` is the value. Found in three widgets, where it silently killed every single-argument property query and left Pygubu unable to read any of them.

### `isinstance(args, dict)`

```python
if args and isinstance(args, dict):   # never true
```

Same cause. `args` is always a tuple. Found in six files, where it made the dict form of `configure()` dead code.

### `try` wrapping a whole loop

```python
try:
    for pname in Something.properties:
        copy_custom_property(...)
except RuntimeError:
    pass
```

The first failure aborts the entire loop and everything after it is skipped. Put the `try` **inside**, so one failure affects one iteration. The same applies to several copies grouped under one `try`: widgets listed later receive fewer properties than those listed first, with no error.

### Bare `except:`

```python
except:
    pass
```

Catches `NameError` too. A misspelled variable — `CTkScrollableFrame_builder_id` where `sCTkScrollableFrame_builder_id` was meant — became a silent no-op that surfaced days later as a wrong default in the Designer inspector. Use `except RuntimeError:` or whatever you actually expect.

### `configure()` must handle the single-argument query form

Four widgets failed the same way in one evening. Pygubu calls `configure(name)`
to read a property's default whenever a field is blanked in the Designer
inspector, and expects a Tkinter-style five-element tuple back:

```python
(name, name, name, default, current)
```

Forwarding the name to a native `configure()` does not do that. CustomTkinter
declares `configure(self, require_redraw=False, **kwargs)`, so the property NAME
arrives as `require_redraw` and the call returns `None`. Pygubu then hands that
`None` straight to `_set_property()`:

```
Failed to set property 'height' ... float() argument must be a string or a
real number, not 'NoneType'
```

Handle the query explicitly and build the tuple from `cget()`:

```python
try:
    current = self.cget(pname)
except Exception:
    current = None
default = self._NATIVE_QUERY_DEFAULTS.get(pname, current)
return (pname, pname, pname, default, current)
```

**Only state a default you can point at.** `sCTkSpinbox` and `sCTkTableview`
declare theirs from their own constructor signatures; `sCTkSwitch`'s table is
empty because it forwards width and height to native `CTkSwitch` and has none of
its own. A property with no stated default reports its current value, making a
blank a no-op — guessing would be worse, because the guess gets applied.

Note this is separate from the `*args` version of the same problem: a
`configure(self, cnf=None, **kwargs)` signature receives the query as `cnf`, and
`{**cnf}` raises `TypeError: 'str' object is not a mapping`. Both shapes need a
query branch.

### Theme errors must name the resolved block, not the class

```python
raise KeyError(f"'{self.__class__.__name__}' theme block is missing ...")
```

For a subclass that reports the SUBCLASS's name — which is not the block the
widget reads when `_THEME_BLOCK_NAME` is set. The Designer showed:

```
KeyError: "'sCTkDialogForPreview' theme block is missing 'heading_font' ..."
```

There is no such block and there never was. The lookup was correct; only the
message was wrong. But in a fail-loud design a misleading error costs more than
a vague one, because naming the exact problem is the whole justification for
raising instead of falling back. Resolve it the same way `ThemeableWidget` does:

```python
name = getattr(self, '_THEME_BLOCK_NAME', None) or self.__class__.__name__
```

Twenty-one sites across seven widgets had this.

### A widget meant to be subclassed needs `_THEME_BLOCK_NAME`

Theme blocks resolve from the class name, which is right for widgets nobody
subclasses. It is wrong for one that exists to be subclassed — `sCTkDialog`,
where the Designer generates `class SettingsDialog(sCTkDialog)` and every user
does the same. Validation demanded a `SettingsDialog` block nobody would think
to write.

Declare the block on the base class so subclasses inherit it:

```python
class sCTkDialog(sCTkFrame):
    _THEME_BLOCK_NAME = "sCTkDialog"
```

A subclass wanting its own styling overrides it. A better general rule would be
for `ThemeableWidget` to walk the MRO and use the first class name with a block,
so any subclass inherits its parent's theme — not done, but worth considering.

### Native signatures differ

`CTkFrame.configure(require_redraw=False, **kwargs)` accepts a positional argument and silently swallows it. `CTkScrollableFrame.configure(**kwargs)` does not, and raises. Code that appears to work on most widgets can fail on one.

### `unbind()` is destructive

Tk's `unbind(sequence)` with no `funcid` removes **every** binding for that sequence on that widget, including ones you never installed. Never call it on a widget whose own handlers you need to keep — CustomTkinter's scrollbar drag handler cannot be restored once destroyed. To suppress an event, insert a bindtag ahead of the widget's own and return `"break"` from it.

---

<a name="pygubu-designer-plugin-requirements"></a>
## Pygubu Designer plugin requirements

### A custom root widget needs `is_toplevel_widget()`

`IDesignerPlugin.is_toplevel_widget()` returns `False` by default. `pygubudesigner/codegen/scriptgenerator.py` decides which code template to use from:

```python
toplevel_uids = ("tk.Tk", "tk.Toplevel", "customtkinter.CTk",
                 "customtkinter.CTkToplevel", "tkmt.ThemedTKinterFrame")
if target_class in toplevel_uids or \
   PluginManager.is_toplevel_widget(target_class):
    main_widget_is_toplevel = True
```

That tuple is hardcoded. Without the plugin method, a custom root falls to the **widget** template, whose `__main__` block reads:

```python
root = tk.Tk()
app = MyApp(root)
```

Since `sCTk` creates its own Tcl interpreter, that produced a **second** one — and the failure mode was nothing like the cause. A `tk.StringVar()` built without an explicit master attaches to whichever root Tkinter considers default, so a variable bound to a widget in one interpreter was read from the other. The widget worked, the command callback fired with the right value, and `variable.get()` returned empty forever. Every variable-bound widget in generated code was affected.

pygubu's own source carries a `FIXME` beside that tuple asking plugins to implement the method rather than the tuple being extended:

```python
def is_toplevel_widget(self, builder_uid: str) -> bool:
    return builder_uid in (sCTk_builder_id, sCTkToplevel_builder_id)
```

`group=GROOT` on `register_widget()` is a **different** thing — palette placement only. It does not affect code generation.

### Properties need registering twice

`properties` on the builder object decides which properties the inspector **shows**. `copy_custom_property()` or `register_custom_property()` supplies the **editor definition** for each name. Both are required: copying alone leaves the property invisible, listing alone leaves it with no editor and a misleading default.

To inherit a native widget's property set:

```python
from pygubu.plugins.customtkinter.widgets import CTkFrameBO
properties = CTkFrameBO.properties + OPTIONS_CUSTOM
```

and add the builder id to the matching copy loop in `designer/properties.py`.

### A new widget needs registering in FOUR places

Three of them fail loudly. The fourth does not, which is why it is the one that gets forgotten.

| File | What it does | How it fails |
| :--- | :--- | :--- |
| `scustomtkinter/__init__.py` | Exports the class | ImportError, immediately |
| `scustomtkinter_pygubu/<Widget>bo.py` | Builder object and properties | Absent from the palette |
| `scustomtkinter_pygubu/designer/plugin.py` | Preview class and Designer hooks | Odd behaviour while designing |
| `scustomtkinter_pygubu/sCTkWidgetSetForPygubuDesigner.py` | **Runtime** registration | Designer fine, generated code crashes |

The last one is a plain list of imports, and it is what registers the builder objects when an **application** loads a `.ui` file. The Designer never uses it — it imports the builder objects directly through `plugin.py` — so a widget missing from that list works perfectly throughout design and fails the moment the generated code runs:

```
AttributeError: 'list' object has no attribute 'startswith'
```

raised from `importlib`, several frames deep, naming nothing useful.

**Where that message comes from.** Pygubu falls back to `get_module_for()` for a class it has no registration for, and hands the result to `importlib`, which calls `name.startswith(".")`. That method must return a **string**; `get_all_modules()` beside it returns a **list**, and the two had been confused. Every widget was registered by the imports at the top of the file, so the fallback never ran and the mistake sat there unnoticed until the first widget missing from the list reached it.

`sCTkNotebook`, `sCTkDialog` and `sCTkFileExplorer` were all in that state at once. The latter two were commented out with reasons that had stopped being true — one said "missing bo file" about a file that exists.

**Check the two lists agree** after adding anything:

```bash
grep -o "scustomtkinter_pygubu\.sCTk[A-Za-z]*bo" scustomtkinter_pygubu/designer/plugin.py |
    sed 's/.*\.//' | sort -u > /tmp/designer.txt
grep -o "^import scustomtkinter_pygubu\.sCTk[A-Za-z]*bo" \
    scustomtkinter_pygubu/sCTkWidgetSetForPygubuDesigner.py |
    sed 's/.*\.//' | sort -u > /tmp/runtime.txt
comm -23 /tmp/designer.txt /tmp/runtime.txt
```

Anything printed works in the Designer and breaks when run.

### Registration order matters

`copy_custom_property()` **overwrites** whatever definition is already registered for that name. So a deliberate override in a builder-object module is silently undone if a copy loop runs afterwards.

This bit us on `appearance_mode`. `sCTkCorebo.py` registered it as a three-value choice including `System`:

```python
register_custom_property(
    builder_id, "appearance_mode", "choice",
    values=("System", "Light", "Dark"), state="readonly",
)
```

but `designer/properties.py` then copied `CTkBO.properties` onto the same id, replacing it with CustomTkinter's own definition — blank, Light, Dark, no `System`. The inspector showed two values and no error was raised anywhere.

An intentional override has to be registered **after** the copy loop, which in practice means putting it in `designer/properties.py` rather than in the builder-object module:

```python
for pname in CTkBO.properties:
    try:
        copy_custom_property(nsctk.CTk, pname, sCTk_builder_id)
    except RuntimeError:
        pass

# AFTER the copy above, which would otherwise overwrite it.
register_custom_property(
    sCTk_builder_id, "appearance_mode", "choice",
    values=("System", "Light", "Dark"), state="readonly",
)
```

If a property in the inspector does not match what you registered, this is the first thing to check.

### `add_allowed_child()` takes a builder id string

Not a class. Passing a class silently matches nothing.

### `allowed_parents` uses builder ids

Generic pygubu category names like `'frame'` or `'toplevel'` will not match `scustomtkinter.sCTkFrame`, so the constraint rejects every valid parent while restricting nothing. Usually the right answer is to omit it.

### Preview subclasses need `_THEME_BLOCK_NAME`

A preview class named `sCTkTableviewForPreview` has no theme block, so validation raises and the preview dies. Set the attribute to the real widget's name.

### `container = True` means children can be dropped in

Set it `False` on widgets that build and manage their own contents — Selector, PathChooser, the dials. A child dropped into one lands in an unmanaged position and is destroyed by the next rebuild.

### Transparent widgets look wrong in the design canvas

The Designer canvas is a fixed light grey that ignores appearance mode, so a widget whose theme sets `"transparent"` renders light while its text follows the dark palette. Use the `preview_opaque()` decorator in `designer/plugin.py` to stamp a concrete background on the preview class only.

### The Bindings tab is empty, deliberately

CustomTkinter's plugin sets `allow_bindings = False` on twelve builder objects individually — not on a shared base class, so it is a considered decision per widget rather than a blanket policy. Our builder objects inherit theirs, so the tab is empty for sCTk widgets too.

The reason is sound. Most CTk widgets are composites that draw on an internal canvas, and a binding attached to the *outer* widget frequently never fires — the canvas or a child receives the event instead. An enabled tab that silently produced dead bindings would be worse than no tab.

**We keep them off.** A few of our widgets could probably support bindings — `sCTkSeparator` and `sCTkTabview` both override `bind()` to route events to something that actually receives them, and plain frames are likely fine — but enabling the flag is only worth doing per widget, after confirming that a binding attached in the Designer really fires in generated code. Setting `allow_bindings = True` in a builder object overrides the inherited `False` if you want to try.

Binding in the derived class works regardless, and is the normal answer:

```python
class MyApp(baseui.MyAppUI):
    def __init__(self, master=None):
        super().__init__(master)
        self.my_entry.bind("<KeyRelease>", self.on_key)
```

### A widget that rebinds in `state()` undoes the preview setup

`configure_for_preview()` runs **once**, at construction. Anything the widget does to its own bindings afterwards replaces what the plugin installed.

The dials are the worked example, and they broke it twice over. `state()` rebinds `<Button-1>`, `<Button-2>`, `<Button-3>` and the scroll sequences every time it returns to normal, so a dial stopped being selectable the moment its state was touched and did not recover when set back. And `_inject_private_layer_bindings()` is scheduled 50ms after construction with `add="+"`, so it runs after the plugin has finished and *appends* to the no-ops rather than being displaced by them — which is why a dial still turned under a trackpad in the design canvas.

Two rules follow. If a widget rebinds on a state change, its preview subclass must override `state()` and re-apply the plugin's bindings afterwards, deferred to idle so it runs after the widget's own rebinding. If a widget schedules a deferred binding pass, the preview subclass should override that method to do nothing.

Worth checking for any widget you add: `grep -n "\.bind(" ` your widget, and ask whether any of those calls can run more than once.

### Neutralize the right canvas

A widget that draws on its own canvas has **two**: `_canvas`, which `CTkFrame` draws its background on, and whatever the widget created for itself. `CTkFrame.bind()` routes the Designer's click handler to `_canvas`, so neutralizing `<Button-1>` there removes the selection binding itself and the widget cannot be selected at all.

Neutralize the widget's own canvas, and **forward** `<Button-1>` from it to `_canvas` rather than swallowing it — a no-op stops the click before it reaches the handler:

```python
face = getattr(widget, "canvas", None)
sequences = tuple(s for s in (_HOVER_CLICK + _SCROLL) if s != "<Button-1>")
_neutralize(face, sequences)
face.bind("<Button-1>", _select_dial)   # generates on widget._canvas
```

### What the Designer cannot do

Two widgets cannot be selected by clicking them on the canvas, and both are dead ends rather than open bugs. The user-facing consequence is in `DesignerHints.md`; this is the mechanism, so nobody spends an afternoon rediscovering it.

**Tab pages.** The page is a frame `sCTkTabview.add()` creates at runtime, not something the builder made, so it is absent from the builder's widget map and `get_widget_id()` returns `None` for it. Binding the tab buttons with `add=True` and forwarding a click to the revealed page was tried: the tab switched, the handler fired, the page was found — and selecting it did nothing, because of that same absence. CustomTkinter's own plugin carries a commented-out attempt at the same problem.

**The three scrolling frames** — `sCTkScrollableFrame` and both labelled variants. `CTkScrollableFrame` inverts the usual arrangement: the widget IS the inner frame, created inside a canvas owned by a separate outer frame. So the visible surface is the widget's *parent*, and `winfo_children()` returns an empty list.

Three routes, each closed by something specific:

| Approach | What closes it |
| :--- | :--- |
| Forward the click to the widget | The Designer resolves a click by walking *up* the tree. The frame is a **descendant** of the canvas, so the walk never reaches it. |
| Bind the canvas directly | `CTkScrollableFrame.bind()` routes the Designer's own handler to `_parent_canvas`. Binding it replaces that handler, so nothing is selected at all — worse than before. |
| A transparent overlay parented to the frame | Tk refuses: `place(in_=...)` requires its target to be the widget's own parent or a descendant of it, and the canvas is the overlay's **grandparent**. |

The one route not tried is rebuilding the labelled frames as `sCTkFrame` composites — they use `CTkScrollableFrame` only for its built-in label, and an ordinary frame is selectable. That means owning `label_text`, `label_font`, `label_text_color` and `label_fg_color` yourself, and returning the inner frame from `get_children()` so dropped widgets land below the label rather than beside it — the same arrangement `sCTkDialog` uses with `contentFrame`. `sCTkScrollableFrame` itself cannot be rebuilt that way, since the scrolling is the point.

**Preview classes are still worth having for all four**, selectable or not: they set `_THEME_BLOCK_NAME`, which is what makes a validation error name the real theme block instead of `sCTkScrollableFrameForPreview`.

---

<a name="testing"></a>
## Testing

There is no automated test suite. Each widget has a harness under `examples/` that exercises its states, callbacks and appearance-mode switching interactively.

Things worth exercising in a new harness, because they have each hidden a real bug:

- **Every state transition, in both directions.** Several bugs only appeared on the return to `"normal"`.
- **Appearance-mode toggle while in a non-normal state.** A disabled widget that stops following light/dark is a common failure.
- **Runtime `configure()` of theme colours**, then an appearance-mode toggle, to confirm the override survived the repaint.
- **Blanking a property in the Designer inspector**, which calls `configure(pname)` and reaches code paths normal use never touches.
- **Two instances side by side**, to confirm an effect is local. A scroll fix that looked correct with one scrollable frame turned out to affect the whole application.
- **A real wheel mouse as well as a trackpad**, on macOS. They report wildly different delta magnitudes and one bug only appeared with the wheel.
