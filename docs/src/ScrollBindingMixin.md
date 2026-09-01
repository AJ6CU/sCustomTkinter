## ScrollBindingMixin

The single shared implementation of cross-platform mouse wheel and macOS trackpad scroll handling for this library. Used by `sCTkScrollableFrame` (and therefore `sCTkTableview`), `sCTkFileExplorer`, and `sCTkScrollArea`.

This page is the reference for how scrolling works. The individual widget pages describe only their own hooks and link here.

### Table of Contents
* [Why it exists](#why-it-exists)
* [Platform behavior](#platform-behavior)
* [Tuning constants](#tuning-constants)
* [Activation and rebinding](#activation-and-rebinding)
* [Disabling scroll](#disabling-scroll)
* [Nested scrollable frames](#nested-scrollable-frames)
* [Host contract](#host-contract)

---

<a name="why-it-exists"></a>
### Why it exists

This logic previously existed as three independent copies, each adapted by hand from the first. They drifted, as duplicated code does:

- **The two's-complement sign correction disagreed.** `sCTkScrollableFrame` used `>= 0x8000`; `sCTkScrollArea` used `> 32768`. Those differ at exactly 32768 — the smallest *negative* value in a signed 16-bit field — which one read as −32768 and the other as +32768, inverting direction at that value.
- **`sCTkScrollArea` decoded the packed touchpad delta differently again**, reading `event.delta_y` when present and applying a 16-bit correction to what may be a 32-bit packed value, rather than bit-shifting out the signed components.
- **Windows wheel scaling disagreed:** `/120` unscaled in `sCTkScrollableFrame`, `/120 * 2` in `sCTkScrollArea` — twice the travel per notch.
- **`sCTkFileExplorer` had no touchpad accumulator at all**, scrolling on every raw event instead of gating on an accumulated threshold. Trackpad scrolling there was markedly faster and coarser than everywhere else.
- **`sCTkFileExplorer` walked only one level** into its row frame, so a row's label or icon was never bound and the wheel did nothing over them.
- **The nested-scrollable boundary guard existed in exactly one of the three.**

Every fix had to be made three times, and none of them were. Where the copies disagreed, `sCTkScrollableFrame`'s version — the maintainer-verified reference, confirmed smooth in live testing on macOS with both an Apple mouse and a trackpad — is the one that won.

---

<a name="platform-behavior"></a>
### Platform behavior

Three genuinely different platform models are handled:

| Platform | Mechanism |
|---|---|
| Windows | `<MouseWheel>` with a `/120`-scaled delta |
| Linux | Discrete `<Button-4>`/`<Button-5>` events — no continuous delta exists |
| macOS | Its own `<MouseWheel>` scaling, **plus** a separate higher-precision `<TouchpadScroll>` synthetic event |

macOS `<TouchpadScroll>` packs a two-axis delta into a single 32-bit integer — X in the high 16 bits, Y in the low 16 — each an *unsigned* field that must be converted back to signed, or every upward scroll reads as a large positive number.

Trackpad events arrive far more frequently and with far finer deltas than wheel notches, so scrolling on each one is unusably fast. Deltas accumulate and move the view only once a threshold is crossed. The accumulator resets on a direction reversal, so reversing responds immediately instead of first cancelling out what had built up.

---

<a name="tuning-constants"></a>
### Tuning constants

Class attributes on the mixin, so they can be overridden per subclass or per instance without any additional machinery. **These are macOS-tuned**; other platforms may want different values.

| Constant | Default | Meaning |
|---|---|---|
| `MAC_SCROLL_SENSITIVITY` | `3` | Amplification for macOS wheel deltas, which are much smaller than Windows' `/120` steps |
| `MAC_SCROLL_MAX_STEP` | `5` | Ceiling on units travelled per macOS wheel event |
| `TOUCHPAD_ACCUMULATION_THRESHOLD` | `12.0` | Accumulated trackpad delta required before the view moves |

**`MAC_SCROLL_MAX_STEP` exists because macOS reports wildly different delta magnitudes depending on hardware.** An Apple Magic Mouse sends fine-grained values near 1; a conventional wheel mouse sends a large value per detent — around 38 in live testing. Multiplying that by the sensitivity gave 114 units from a single wheel click, jumping a 100-row list end to end. The amplification is still correct for fine-grained hardware, so rather than dropping it, the result is clamped: small deltas scale normally, large ones saturate.

Resulting travel per event:

| `event.delta` | Hardware | Units |
|---|---|---|
| 0.4 | Magic Mouse | 3 |
| 1 | Magic Mouse | 3 |
| 2 | Magic Mouse | 5 (clamped) |
| 38 | Wheel detent | 5 (clamped) |

Setting `MAC_SCROLL_MAX_STEP` to 3 gives the conventional three-lines-per-notch that matches macOS defaults. Values below 3 slow the Magic Mouse too, since its fine deltas already scale to 3 before the clamp applies.

Whether these should move somewhere more discoverable than class attributes is an open question.

---

<a name="activation-and-rebinding"></a>
### Activation and rebinding

Bindings are automatic and self-maintaining. No activation call is needed, and content added after a widget is placed is picked up on its own.

That reliability takes four mechanisms, each covering a gap the others don't. All are idempotent — bindings are always torn down before being rebuilt — so overlapping coverage costs nothing.

| Mechanism | Covers |
|---|---|
| `<Map>` on the host | Later remaps, e.g. `pack_forget()` then re-placement |
| `<Map>` on `extra_map_widget` | The widget the geometry manager actually sees |
| `after_idle()` at construction | Initial activation, independent of mapping semantics |
| `<Configure>` on `content_widget`, debounced | Content added *after* activation |

**Why `<Map>` alone isn't enough.** `CTkScrollableFrame` is not the widget that gets placed: it builds an internal `_parent_frame` plus a canvas, inserts *itself* into that canvas via `create_window()`, and overrides `pack()`/`grid()`/`place()` to operate on `_parent_frame`. The widget is therefore a canvas-window child and may never receive `<Map>` the way an ordinarily-managed widget does. `after_idle()` is what actually establishes bindings in practice.

**Why the content rebind is needed.** Activation happens once, at a moment when the container is usually still empty — callers construct, place, and *then* populate. Confirmed by live testing: an `sCTkTableview` bound at activation time collected 16 layers (frame, canvas, header cells) because `load_dataset()` hadn't run yet; the 32 data cells created afterwards were never bound, so it scrolled beside its rows but not over them.

`<Configure>` fires when children change the container's layout, so it catches every content-adding path. It's debounced through `after_idle` because building a table fires it once per cell — one rebind instead of 32, run after the burst rather than during it, so it sees the finished tree.

`<Configure>` can't distinguish "children were added" from "the window was dragged", so **resizing rebinds too**. Coalesced, but not free on a very large content tree.

> **Do not replace `tk.Misc.bind(self, ...)` with `self.bind(...)`.** CustomTkinter overrides `CTkScrollableFrame.bind()` to forward every binding to `self._parent_canvas` instead of attaching it to the widget. An earlier version used `self.bind()`, and bindings never landed on the frame — scroll handling was silently never installed, and widgets only appeared to scroll where native CustomTkinter's own global `bind_all` handler happened to cover for it. `tk.Misc.bind` called unbound reaches the real Tkinter implementation. This looks like a needless complication and is not.

---

<a name="disabling-scroll"></a>
### Disabling scroll

When a host's `_scroll_permitted()` returns `False`, the mixin doesn't merely unbind — it installs **blocking** handlers. Two separate mechanisms are involved, because neither alone is sufficient.

**Wheel and trackpad events.** Unbinding is not enough: native `CTkScrollableFrame.__init__` installs its own application-global `bind_all("<MouseWheel>")` handler that survives any `unbind()`. Calling `unbind_all()` would disable scrolling for *every other* scrollable widget in the application. Instead a handler returning `"break"` is installed on each layer. Tk dispatches bindings by bindtag in order — widget, class, toplevel, then `all` — and `bind_all` lands on that final tag, so a widget-level `"break"` halts the chain before the global handler is reached. Confirmed by live testing: with two independent scrollable frames side by side, disabling one left the other scrolling normally with both a mouse wheel and a trackpad.

**Scrollbar dragging.** `unbind()` is actively dangerous here — Tk's `unbind()` removes *every* binding for an event on a widget, so calling it on a scrollbar's `<Button-1>` would destroy CustomTkinter's own drag handler permanently, with no way to restore it. Binding a blocker with `add="+"` doesn't work either: handlers fire in the order added, and CustomTkinter's was added during its own construction, so `"break"` at that point is too late. A private, per-instance bindtag is inserted at the **front** of the widget's tag list instead, so the blocker runs before CustomTkinter's bindings. Re-enabling removes the tag; CustomTkinter's bindings are never modified.

The tag name embeds `id(self)`, so disabling one host has no effect on any other in the same application.

**The scrollbar stays visible when blocked, just inert.** CustomTkinter's scrollbar has no native disabled state to lock, so there's no greyed-out appearance to switch to.

---

<a name="nested-scrollable-frames"></a>
### Nested scrollable frames

The descendant walk stops at any nested `CTkScrollableFrame` boundary — covering `sCTkScrollableFrame` and anything built on it, such as `sCTkSelector` and `sCTkTableview`. Without this, an inner scrollable frame placed inside an outer one would have its canvas, scrollbar, and entire content tree bound to the *outer* host's handler as well as its own, and since bindings use `add="+"`, both fire on the same event and scroll both at once. Native CustomTkinter guards the same boundary in its own `_check_if_valid_scroll`.

The guard applies to descendants only, so a scrollable host still binds its own layers.

**Not yet live-tested.** The logic mirrors CustomTkinter's own guard and is straightforward, but an actual nested case hasn't been exercised against it.

A separate scrolling region built directly on a plain `Canvas` is **not** guarded — the check keys on `CTkScrollableFrame` specifically. Guarding that would need an explicit opt-out convention, since a plain `Canvas` has no way to declare itself an independent scroll region.

---

<a name="host-contract"></a>
### Host contract

A host class must implement two methods and may override two more:

| Method | Required | Returns |
|---|---|---|
| `_scroll_target()` | yes | The widget to call `yview_scroll()` on, or `None` if scrolling isn't currently possible |
| `_scroll_layers()` | yes | The ordered, deduplicated list of widgets to bind |
| `_scroll_permitted()` | no | `False` to install blocking handlers instead of scroll handlers. Default `True` |
| `_scroll_drag_targets()` | no | Widgets whose click-drag should also be blocked when not permitted. Default none |

Hosts call two setup methods from `__init__`:

```python
self._init_scroll_state()                       # must run before any binding
self._install_scroll_activation(
    extra_map_widget=...,                       # optional
    content_widget=...,                         # optional
)
```

**`content_widget` matters.** It defaults to `self`, which is correct only when content is added directly to the host. A host that puts content in a separate inner frame **must** pass that frame — adding rows to an inner frame doesn't resize the outer widget, so `<Configure>` on `self` would never fire and the content rebind would silently never happen.

Hosts may also define `_USE_CUSTOM_SCROLL_BINDING = False` as a kill switch, falling back to whatever native CustomTkinter provides. It's checked inside `_toggle_scroll_bindings()` rather than at the call sites, so it can't be bypassed by reaching that method through a different entry point — the exact bug that made the toggle ineffective in an earlier revision.

#### Host implementations

| Host | `_scroll_target()` | Notes |
|---|---|---|
| `sCTkScrollableFrame` | Parent canvas via `winfo_parent()` | Wrapped by a native `CTkScrollableFrame` that owns the canvas. Passes `_parent_frame` as `extra_map_widget`. Disabling stops scrolling. |
| `sCTkFileExplorer` | `self.canvas` | Builds its own canvas, so no lookup needed. Passes `explorer_frame` as `content_widget`. Disabling stops scrolling. |
| `sCTkScrollArea` | `self.canvas` | Builds its own canvas. Passes `scroll_content` as `content_widget`. No disabled state. |

[Return to Table of Contents](#table-of-contents)
