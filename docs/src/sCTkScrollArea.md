## sCTkScrollArea

`sCTkScrollArea` is a scrollable viewport container built on a raw `tkinter.Canvas`, offered as an alternative to `ctk.CTkScrollableFrame` for cases where you want to supply your own external scrollbar and control child event binding explicitly. It inherits `ctk.CTkFrame` and `ScrollBindingMixin`.


Its companion is [`sCTkScrollbar`](sCTkScrollbar.md). Scroll handling comes from [`ScrollBindingMixin`](ScrollBindingMixin.md), which is the reference for how scrolling works across this library.

<a name="contents"></a>
### Table of Contents
* [Constructor](#constructor)
* [Attributes](#attributes)
* [Methods](#methods)
* [Wiring it up](#wiring)
* [Theming](#theming)
* [Example](#example)
* [Known Limitations](#limitations)

---

<a name="constructor"></a>
### Constructor

```python
scroll_area = sCTkScrollArea(master=None, **kwargs)
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `master` | widget | Parent container. |
| `**kwargs` | — | Passed to `ctk.CTkFrame`. Note `fg_color="transparent"` and `border_width=0` are set internally and can't be overridden. |

---

<a name="attributes"></a>
### Attributes

| Attribute | What it is |
| :--- | :--- |
| `scroll_content` | The frame your content goes into. A raw `tkinter.Frame`, not a themed widget. |
| `canvas` | The raw `tkinter.Canvas` providing the scrolling viewport. |

---

<a name="methods"></a>
### Methods

| Method | Description |
| :--- | :--- |
| `hook_scrollbar(scrollbar_widget)` | Connects a scrollbar to the canvas in both directions, and registers it as a scroll layer so the wheel keeps working while the pointer is over the bar itself. |
| `propagate_scroll_events(target_widget)` | Registers a widget outside `scroll_content` to receive scroll events, along with its descendants. **Rarely needed now** — see below. |
| `process_incoming_scroll(event)` | Compatibility shim. Scroll events are dispatched by the mixin directly; this remains only for external callers that bound this method themselves. |

**`propagate_scroll_events()` is no longer required for ordinary content.** Anything placed inside `scroll_content` is bound automatically and re-bound whenever it changes, so the per-item call shown in older examples is redundant. It's still useful for widgets that sit *outside* that tree.

Its behavior also changed: registered widgets are now **remembered** and re-bound on every subsequent pass. The previous implementation bound once and forgot, so any later rebind lost them.

---

<a name="wiring"></a>
### Wiring it up

```python
scroll_view = sCTkScrollArea(container)
scroll_view.pack(fill="both", expand=True)

scrollbar = sCTkScrollbar(container, orientation="vertical")
scrollbar.pack(side="right", fill="y")

scroll_view.hook_scrollbar(scrollbar)

for i in range(25):
    sCTkLabelSecondary(scroll_view.scroll_content, text=f"Row {i}").pack(anchor="w")
```

No `propagate_scroll_events()` call is needed — the rows are inside `scroll_content`, so the content rebind picks them up.

---

<a name="theming"></a>
### Theming

**This widget is not part of the theme system.** It doesn't inherit `ThemeableWidget`, doesn't read `sCTkThemes.json`, and has no theme block. An earlier version of this page showed an `sCTkScrollArea` JSON block — nothing reads it, and adding it has no effect.

The canvas and content-frame backgrounds are hardcoded: `#FAFAFA` in light mode, `#1A1A1A` in dark, switched by the widget's own `_set_appearance_mode()` hook. `scroll_content` is a raw `tkinter.Frame`, which cannot render CustomTkinter's transparent pseudo-value or `(light, dark)` tuples, so it needs a literal color.

Bringing this widget into the theme system is an open item, tied to the Pygubu Designer integration work.

---

<a name="example"></a>
### Example

```python
#!/usr/bin/python3
import customtkinter as ctk
from scustomtkinter import (sCTk, sCTkFrame, sCTkButtonPrimary, sCTkLabelSecondary,
                            sCTkScrollbar, sCTkScrollArea)

if __name__ == "__main__":
    root = sCTk()
    root.geometry("480x480")
    root.title("sCTkScrollArea Validation Bench")
    root.configure(fg_color=("#F1F5F9", "#1C1C1C"))

    lower_tray = sCTkFrame(root, fg_color="transparent")
    lower_tray.pack(side="bottom", fill="x", padx=15, pady=(0, 15))

    main_layout = sCTkFrame(root, border_width=2)
    main_layout.pack(expand=True, fill="both", padx=15, pady=15)

    status_monitor = sCTkLabelSecondary(main_layout, text="STATUS: viewport online")
    status_monitor.pack(fill="x", padx=10, pady=(5, 10))

    def toggle_appearance_skin():
        ctk.set_appearance_mode("Light" if ctk.get_appearance_mode() == "Dark" else "Dark")

    btn_theme = sCTkButtonPrimary(lower_tray, text="Toggle Light/Dark", command=toggle_appearance_skin)
    btn_theme.pack(fill="x", expand=True, padx=5)

    scrollbar = sCTkScrollbar(main_layout, orientation="vertical")
    scrollbar.pack(side="right", fill="y", padx=(5, 10), pady=10)

    content_chassis = sCTkFrame(main_layout, border_width=0, fg_color="transparent")
    content_chassis.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)

    scroll_view = sCTkScrollArea(content_chassis)
    scroll_view.pack(fill="both", expand=True)

    for i in range(25):
        sCTkLabelSecondary(
            scroll_view.scroll_content,
            text=f"Transceiver channel {100 + i} [OK]"
        ).pack(anchor="w", padx=10, pady=4)

    scroll_view.hook_scrollbar(scrollbar)

    root.mainloop()
```

---

<a name="limitations"></a>
### Known Limitations

- **Outside the theme system entirely** — see [Theming](#theming). It's the only widget in this library in that position.
- **No `_finalize_themeable_lifecycle()` handshake,** so Pygubu Designer gets no registration signal from it.
- **No disabled state.** Unlike `sCTkScrollableFrame` and `sCTkFileExplorer`, there's no `state()` here and no way to make it inert.
- **`scroll_content` is a raw `tkinter.Frame`,** so widgets placed in it don't inherit CustomTkinter background propagation. Themed `sCTk` children render correctly; plain `tk` children may need their `bg` set to match.
- **The debounced rebind also runs on genuine resizes** — see the [mixin page](ScrollBindingMixin.md#activation-and-rebinding).

**Behavior changed when this widget adopted the shared mixin.** Three corrections, all bringing it in line with the rest of the library: Windows wheel travel halved (it previously doubled the `/120` delta), the two's-complement boundary at exactly 32768 was fixed, and the packed touchpad delta is now decoded by bit-shifting rather than reading `event.delta_y`. It also gained the nested-frame boundary guard and the automatic content rebind.

[Return to Table of Contents](#contents)
