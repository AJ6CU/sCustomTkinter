# Designer Hints

Things that are true across the library when working in Pygubu Designer. Widget-specific quirks stay on each widget's own page.

Rough notes for now — expect this to grow.

---

## Images resolve relative to the running directory

Set an image in the inspector and it appears on the canvas. Run the generated code from a different directory and it won't.

The image property editor stores only the **basename**. The full path lives in the designer's own registry for the length of the session and does not survive into generated code, which emits the bare name:

```python
self.img_logo = image_loader(master, "logo.png")
```

The generated `safe_image_loader` is an explicit stub — its docstring says "Setup image_loader in derived class file" — and does a plain `tk.PhotoImage(file=name)`. So the name resolves against the process's working directory.

**Put the image beside the script you run, or supply your own loader.** This is pygubu's design rather than a defect: the name is a key, and resolving it is the application's job.

Worth knowing that the two widget families fail differently when it isn't found. The tk stub wraps its load in `except tk.TclError: pass` and returns `None`, so `configure(image=None)` succeeds and you get no image and no message. The CustomTkinter path calls `Image.open()` unwrapped and raises `FileNotFoundError`. Same cause, opposite symptoms — a silent blank in one case, a traceback in the other.

### Images fail in "Preview in toplevel"

Separate from the above, and not a path problem. A widget with an image shows
correctly on the design canvas, then previewing it produces:

```
Failed to set property 'image' ... Error: image "pyimage60" does not exist
```

That is Tk saying there is no image by that name in **this** interpreter, not
that a file is missing. The preview builds a new root, and images created
against the designer's own interpreter do not exist in it.

Reproducible with a plain `customtkinter.CTkLabel`, so it is not something this
library introduces. CustomTkinter's designer plugin rebuilds its image cache
when a new root appears, for exactly this reason -- the widgets that go through
that path are fine, and others are not.

No workaround beyond checking images in the design view and in the generated
code rather than in the preview.

---

## Overriding a theme value in the inspector

Set a colour, a font or a size in the inspector and it **replaces** the theme's value for that widget, for as long as that widget exists. Leave the field blank and the theme applies.

**An override survives state changes.** Set `fg_color` red, disable the widget, re-enable it, and it is still red. That sounds obvious, and it was not true until recently: widgets repaint themselves from a snapshot of the theme taken at construction, and nothing wrote runtime changes into that snapshot — so any state change quietly restored the theme colour. In the Designer it happened immediately, because properties are applied in an order that sets `state` after the colours.

**Clearing a field returns to the theme, not to the last value.** Blanking a property does not blank the property — it reverts to what the theme says, which is what the generated code produces anyway, since the property is simply omitted and the constructor default applies. Clearing a button's `apply_text` shows "Apply" again rather than an empty button.

The default reported to the Designer comes from an untouched copy of the theme block, so clearing a field you have already overridden gives you the theme's value rather than the override you just replaced.

Properties the theme says nothing about keep their current value instead. A no-op is better than a guessed default, because the guess would be applied.

**One field means one thing.** A widget usually has two sets of colours — the normal ones and a `disabled_map` — but the inspector shows a single field per property. That field always edits the **normal** value, whatever state the widget is currently in. Setting a colour on a disabled widget therefore shows nothing until you re-enable it.

The one exception is `text_color_disabled`, which has its own field precisely because it names the disabled value directly. Setting it is equivalent to setting `disabled_map.text_color` in the theme, and the two are kept as a single value rather than fighting each other.

**A property the theme says nothing about is not overridden — it is just set.** Only keys present in a widget's theme block participate in any of this, because those are the only ones a repaint touches.

**Some properties are absent from `disabled_map` on purpose,** and keep their current value when the widget is disabled rather than changing. The labels are the clearest case: their `fg_color` is `transparent`, so a disabled fill would give them a solid background they do not otherwise have. If a property does not appear to change on disable, that is usually why.

---

## The Bindings tab is empty

Deliberately, and not by us — CustomTkinter's plugin disables it on twelve builder objects individually. Most CTk widgets are composites that draw on an internal canvas, and a binding attached to the outer widget frequently never fires; the canvas or a child receives the event instead. An enabled tab producing dead bindings would be worse than no tab.

Bind in your derived class instead:

```python
class MyApp(baseui.MyAppUI):
    def __init__(self, master=None):
        super().__init__(master)
        self.my_entry.bind("<KeyRelease>", self.on_key)
```

---

## Some widgets are not in the palette, deliberately

`sCTkMessagebox` is raised at runtime in response to an error or an
informational event, not placed on a form — there is nothing to design.

`sCTkDialogToplevel` is created by `sCTkDialog`, never placed by a user. The
class ships; only its Designer registration does not.

Both are omissions by choice, not oversights.

---

## Some widgets are selected from the tree, not the canvas

Most widgets can be selected by clicking them on the canvas. Two cannot:
**tabview tabs**, and the three scrolling frames -- `sCTkScrollableFrame`,
`sCTkFrameLabeledPrimary` and `sCTkFrameLabeledSecondary`.

Clicking a tab switches the page but leaves the inspector showing whatever was
selected before; clicking a widget inside the new page corrects it. Clicking
one of the three frames does nothing at all.

**Select them in the widget tree.** Selecting a tab there switches the canvas
to it, and selecting a widget inside a tab switches to whichever tab holds it.
A widget dropped *inside* any of these is selectable by clicking as normal, so
this affects only the container itself.

Both are dead ends rather than outstanding bugs, for reasons in how
CustomTkinter builds those two widgets. If you are curious, or tempted to fix
it, `dev/docs/Developing.md` records the mechanism and the three approaches
that were tried and failed.

Segmented buttons, dials and the file explorer were on this list until
recently and are now selectable.

---

## sCTkTabview does not grow with its contents

A tabview is a fixed size. Drop widgets into a tab and the tabview stays as it
was, clipping anything that does not fit -- it does not expand the way a frame
does, and no amount of packing or `expand=True` on the children changes that.

Set `width` and `height` on the tabview itself.

This is native `CTkTabview` behaviour rather than something this library adds:
the widget takes explicit dimensions and does not propagate its children's
requested size. Its theme block sets neither, so the size you get without
asking is CustomTkinter's own default.

If a tab's contents look cut off, that is why. Reach for `width` and `height`
before suspecting the layout.

---

## Transparent widgets look wrong on the canvas

A widget whose theme sets `"transparent"` shows whatever is behind it. At runtime that's a themed parent, so it follows light and dark correctly. The design canvas does not participate in appearance mode — it is a fixed light grey — so in dark mode a transparent widget keeps a light background while its text follows the dark palette, and the text can become almost unreadable.

Several widgets in this library carry a concrete background on their preview class for exactly this reason. If you meet it on one that doesn't, that's why.

The **light green** you sometimes see is pygubu's own preview background, showing through where a widget doesn't fill the space the canvas allotted it. Not your theme, and not a fault.

---

## Widgets that build their own contents are not containers

You cannot drop children into `sCTkSelector`, `sCTkPathChooser`, `sCTkFileExplorer` or the dials. Each builds and manages what it holds, and a child dropped in would land in an unmanaged position and be destroyed by the next rebuild.

`sCTkDialog` is the exception that looks like one of these but isn't: widgets dropped onto it land in its content area automatically, which is the point.

---

## Dropdown colours are ignored on macOS

The dropdown lists on `sCTkComboBox`, `sCTkOptionMenuPrimary` and `sCTkOptionMenuSecondary` are native menus the operating system draws itself. On macOS that means the OS decides how they look, and the theme keys that describe them have no effect:

- `dropdown_fg_color`
- `dropdown_text_color`
- `dropdown_hover_color`

The same applies to appearance mode: call `ctk.set_appearance_mode("dark")` while the system is in light mode and the dropdown stays light, whatever the rest of the application does.

All of it is reproducible with plain `customtkinter.CTkComboBox`, so it is not something this library introduces and it cannot be fixed from the theme file.

**Platform-specific, not dead.** These keys are expected to work where Tk draws the menu itself rather than handing it to the OS. Do not remove them from your theme because they do nothing on a Mac.

See [Theming](Theming.md#light-and-dark).
