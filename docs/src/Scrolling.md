# Scrolling

Scrolling in this library is handled in one place. Whichever widget you use, the wheel and trackpad behaviour comes from a single shared implementation — `ScrollBindingMixin` — so it feels the same everywhere and a fix applies everywhere.

* [Which widget to use](#which-widget-to-use)
* [How scroll input is handled](#how-scroll-input-is-handled)
* [Tuning scroll speed](#tuning-scroll-speed)
* [Disabling scrolling](#disabling-scrolling)
* [Nested scrolling regions](#nested-scrolling-regions)

---

<a name="which-widget-to-use"></a>
### Which widget to use

| Widget | Use when |
|---|---|
| [`sCTkScrollableFrame`](sCTkScrollableFrame.md) | You want a scrolling container and don't care where the scrollbar lives. This is the default choice. |
| [`sCTkScrollArea`](sCTkScrollArea.md) + [`sCTkScrollbar`](sCTkScrollbar.md) | You need the scrollbar somewhere the built-in one can't go, or you want to control child event binding explicitly. |
| [`sCTkFileExplorer`](sCTkFileExplorer.md), [`sCTkTableview`](sCTkTableview.md), [`sCTkSelector`](sCTkSelector.md) | These scroll internally. You don't wire anything up. |

`sCTkScrollableFrame` builds and manages its own scrollbar. `sCTkScrollArea` deliberately doesn't — you create an `sCTkScrollbar` separately and connect the two with `hook_scrollbar()`. That's the whole reason the pair exists: it lets the bar sit outside the scrolling region, share space with other widgets, or be styled independently.

```python
scroll_view = sCTkScrollArea(container)
scroll_view.pack(side="left", fill="both", expand=True)

scrollbar = sCTkScrollbar(container, orientation="vertical")
scrollbar.pack(side="right", fill="y")

scroll_view.hook_scrollbar(scrollbar)

# Content goes into scroll_content, not into the area itself.
for row in data:
    sCTkLabelSecondary(scroll_view.scroll_content, text=row).pack(anchor="w")
```

Content added to `scroll_content` is bound for scrolling automatically, including anything added later. You do not need to call `propagate_scroll_events()` on each item — that method now exists only for widgets placed *outside* the content tree.

---

<a name="how-scroll-input-is-handled"></a>
### How scroll input is handled

Three platforms behave differently, and all three are handled:

| Platform | Mechanism |
|---|---|
| Windows | `<MouseWheel>` with a delta scaled in units of 120 |
| Linux | Discrete `<Button-4>` / `<Button-5>` events — there is no continuous delta |
| macOS | Its own `<MouseWheel>` scaling, **plus** a separate higher-precision `<TouchpadScroll>` event |

macOS trackpads deliver far more events, with far finer values, than a wheel does. Acting on each one is unusably fast, so trackpad deltas accumulate and move the view only once a threshold is crossed. The accumulator resets when you reverse direction, so a change of direction responds immediately rather than having to cancel out what built up going the other way.

Bindings activate on their own and maintain themselves. You never call an activation method, and content added after a widget is placed — the normal case, since you construct, place, then populate — is picked up automatically.

Full detail, including why this takes four separate mechanisms, is on the [`ScrollBindingMixin`](ScrollBindingMixin.md) page.

---

<a name="tuning-scroll-speed"></a>
### Tuning scroll speed

Three constants control the feel. They live on `ScrollBindingMixin` as class attributes, so they can be changed globally, per widget class, or per instance.

| Constant | Default | Effect |
|---|---|---|
| `MAC_SCROLL_SENSITIVITY` | `3` | Amplification for macOS wheel deltas, which are much smaller than Windows' steps. |
| `MAC_SCROLL_MAX_STEP` | `5` | Ceiling on rows travelled per macOS wheel event. |
| `TOUCHPAD_ACCUMULATION_THRESHOLD` | `12.0` | Accumulated trackpad movement required before the view moves. |

**`MAC_SCROLL_MAX_STEP` is the one you're most likely to want to change.** macOS reports wildly different delta magnitudes depending on hardware: an Apple Magic Mouse sends fine values near 1, while a conventional wheel mouse sends a large value per detent — around 38 in testing. Without a ceiling, the amplification turns one wheel click into 114 rows of travel, which throws a hundred-row list end to end. The clamp lets small deltas scale normally and saturates large ones.

Set it to `3` for the conventional three-rows-per-notch that matches macOS defaults and most applications. Values below `3` also slow the Magic Mouse, since its fine deltas already scale to 3 before the clamp applies.

To change it everywhere, set it once at startup:

```python
from scustomtkinter.sctk_scroll_mixin import ScrollBindingMixin
ScrollBindingMixin.MAC_SCROLL_MAX_STEP = 3
```

Or per instance, if one widget wants a different feel:

```python
log_view = sCTkScrollableFrame(root)
log_view.MAC_SCROLL_MAX_STEP = 8
```

**These values are tuned on macOS.** If you're shipping to Windows or Linux and the feel is wrong, these are the knobs.

---

<a name="disabling-scrolling"></a>
### Disabling scrolling

`sCTkScrollableFrame` and `sCTkFileExplorer` both stop scrolling entirely when disabled — wheel, trackpad, and scrollbar dragging. The bar stays visible but inert; CustomTkinter's scrollbar has no greyed-out appearance to switch to.

`sCTkScrollableFrame` additionally separates two ideas that are easy to confuse:

- **`state`** is the user-facing enabled/disabled presentation.
- **`scroll_enabled`** is your own intent about whether this frame should scroll at all.

Scrolling happens only when both allow it, and neither overwrites the other. A frame you deliberately set non-scrolling stays non-scrolling after a disable/enable round trip:

```python
frame = sCTkScrollableFrame(master, scroll_enabled=False)
frame.configure(state="disabled")
frame.configure(state="normal")
frame.is_scrolling()          # still False -- your intent survived
```

`disable_scroll()` and `enable_scroll()` are the runtime equivalents, useful when adding a lot of content at once:

```python
frame.disable_scroll()
for item in many_items:
    sCTkLabelSecondary(frame, text=item).pack()
frame.enable_scroll()
```

`sCTkScrollArea` has no disabled state.

---

<a name="nested-scrolling-regions"></a>
### Nested scrolling regions

Putting one scrolling widget inside another works: the inner one keeps its own bindings and the outer one stops at its boundary, so the wheel scrolls whichever region the pointer is actually over rather than both at once.

The guard recognises `CTkScrollableFrame` and anything built on it — `sCTkScrollableFrame`, `sCTkTableview`, `sCTkSelector`. A scrolling region you build yourself directly on a plain `tkinter.Canvas` is **not** recognised, and would get bound to the outer widget as well as your own handler. If you need that, put it in an `sCTkScrollArea` instead.
