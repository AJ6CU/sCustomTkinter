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

If your widget has a repaint routine that re-pushes colours from stored defaults — most do, for appearance-mode switches and state changes — then `configure()` must write overrides into those defaults *before* repainting, or the repaint reverts them on the next line:

```python
_THEME_TRACKED_KEYS = frozenset({"fg_color", "border_color"})

for key in self._THEME_TRACKED_KEYS:
    if key in kwargs:
        self._local_defaults[key] = kwargs[key]
if kwargs:
    super().configure(**kwargs)
    self._update_current_visual_state()
```

### Subclasses and theme block names

`ThemeableWidget` resolves a block by `self.__class__.__name__`, with `_THEME_BLOCK_NAME` as an override. A subclass whose name has no theme block gets an empty one — and any widget with fail-loud validation then raises. Preview subclasses in the Designer plugin all set it.

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

### What the Designer cannot do

Tab pages cannot be selected by clicking them in the design canvas — `CTkTabview` stacks every page in one grid cell with only the active one mapped, so a click cannot be attributed. CustomTkinter's own plugin contains a commented-out attempt at the same fix. Select tabs from the widget tree.

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
