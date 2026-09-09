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

## Clearing a field restores the theme value

Blanking a property in the inspector doesn't blank the property. It reverts to what the theme says, which is what the generated code produces anyway — the property is omitted and the constructor default applies.

So clearing a button's `apply_text` shows "Apply" again rather than an empty button, and clearing a colour returns it to the theme's colour rather than to nothing.

Properties the theme says nothing about keep their current value instead. A no-op is better than a guessed default, because the guess would be applied.

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

Tab pages are the one remaining case. Segmented buttons and dials were in this
list until recently and are now selectable.

Tabview **tabs** cannot be selected by clicking them. `CTkTabview` stacks every page in one grid cell with only the active one mapped, so a click cannot be attributed to the page you aimed at. CustomTkinter's own designer plugin contains a commented-out attempt at the same fix.

Select the tab in the widget tree to edit its `label`.

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

## Dropdowns ignore an explicitly set appearance mode

If your application calls `ctk.set_appearance_mode("dark")` while the operating system is in light mode, the dropdown lists on `sCTkComboBox`, `sCTkOptionMenuPrimary` and `sCTkOptionMenuSecondary` stay light. They are native menus the OS draws itself.

Reproducible with plain `customtkinter.CTkComboBox`, so it is not something this library introduces, and it cannot be fixed from the theme file. See [Theming](Theming.md#light-and-dark).
