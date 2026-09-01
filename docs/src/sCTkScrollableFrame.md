## sCTkScrollableFrame

### Table of Contents
* [Overview](#overview)
* [Constructor](#constructor)
* [Scrolling and State](#scrolling-and-state)
* [Methods](#methods)
* [Theming (sCTkThemes.json)](#theming-sctkthemesjson)
* [Example](#example)
* [Known Limitations](#known-limitations)

---

### Overview

`sCTkScrollableFrame` is a themeable subclass of `customtkinter.CTkScrollableFrame`. It adds automatic light/dark theme resolution from `sCTkThemes.json`, plus carefully-tuned cross-platform mouse wheel and macOS trackpad scroll handling that native CustomTkinter doesn't reliably provide on its own.

Dark Mode:  ![sCTkScrollableFrame in dark mode](images/sCTkScrollableFrame_Dark.png)&emsp; &emsp; &emsp; &emsp;
Light Mode: ![sCTkScrollableFrame in light mode](images/sCTkScrollableFrame_Light.png)

Unlike `sCTkFrame`, this widget **does** have a disabled state. That's justified here where it isn't for a plain frame: this widget owns real behavior to disable, not just colors. Disabling dims the border and scrollbar and stops all scrolling — wheel, trackpad, and scrollbar drag alike.

Disabling does **not** cascade to child widgets. That remains the caller's responsibility, exactly as with the labeled frame variants — loop over `get_children()` and call `.configure(state=...)` on each one.

---

### Constructor

```python
sCTkScrollableFrame(master=None, **kwargs)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `master` | widget | `None` | Parent container. |
| `state` | `str` | `"normal"` | `"normal"` or `"disabled"`. See [Scrolling and State](#scrolling-and-state). |
| `scroll_enabled` | `bool` | `True` | Whether this frame should respond to scroll input at all. |
| `**kwargs` | — | — | Any native `CTkScrollableFrame` argument (e.g. `label_text`, `orientation`), or an override for one of the theme keys listed under [Theming](#theming-sctkthemesjson). |

```python
log_viewport = sCTkScrollableFrame(dashboard, width=380, height=250, label_text="Telemetry Log")
log_viewport.pack(padx=20, pady=20, fill="both", expand=True)
# Scrolling works immediately -- no activation call needed.
```

---

### Scrolling and State

Scroll bindings are **automatic**. The constructor binds `<Map>`, so scroll handling activates by itself the first time the widget becomes visible via `pack()`/`grid()`/`place()`, and again on any later remap (so content added while the frame was hidden is picked up when it reappears).

`<Map>` is used rather than binding directly in the constructor because the binding logic inspects the widget's real parent hierarchy via `winfo_parent()`, which isn't fully realized at construction time. `<Map>` is the earliest point at which it is.

**`state` and `scroll_enabled` are two independent axes**, deliberately not collapsed into one. `state` is the user-facing enabled/disabled presentation; `scroll_enabled` is the developer's own intent about whether this frame should scroll at all. Effective scrolling is the AND of the two:

| `scroll_enabled` | `state` | Scrolls? |
|---|---|---|
| `True` | `"normal"` | yes |
| `True` | `"disabled"` | no |
| `False` | `"normal"` | no |
| `False` | `"disabled"` | no |

Because state changes never write to `scroll_enabled`, intent survives a round trip. A frame explicitly set non-scrolling stays non-scrolling after `state="disabled"` → `state="normal"`, rather than being silently switched on by the state change.

This is also why `cget("scroll_enabled")` reports stored **intent** while `is_scrolling()` reports the live **effective** result. A frame with `scroll_enabled=True` that has been disabled returns `True` from the former and `False` from the latter.

**Temporarily suspending scroll** is a supported pattern, useful during bulk content updates where rebinding on every widget added would be wasted work:

```python
frame = sCTkScrollableFrame(master)
frame.disable_scroll()
frame.pack(fill="both", expand=True)
for item in many_items:
    sCTkLabelSecondary(frame, text=item).pack()
frame.enable_scroll()
```

Calling `disable_scroll()` before placement correctly suppresses the automatic `<Map>` activation rather than being overridden by it. Passing `scroll_enabled=False` to the constructor achieves the same starting state without the separate call.

---

### Methods

| Method | Returns | Description |
|---|---|---|
| `configure(**kwargs)` / `config(**kwargs)` | `None` | Standard configuration. Accepts `state` and `scroll_enabled` alongside any native option. Both are this library's own properties and are removed before reaching native `CTkScrollableFrame.configure()`, which rejects unrecognized keywords. |
| `configure(name)` | `tuple` | Pygubu-style single-argument query for `fg_color`, `label_fg_color`, `scrollbar_button_color`, `border_color`, `state`, and `scroll_enabled`. For the color keys the `default` and `current` positions are identical; for `state` and `scroll_enabled` they can differ, since those carry live runtime values. |
| `cget(name)` | `Any` | Extended to know about `state` and `scroll_enabled`; everything else passes through to the native widget. |
| `enable_scroll()` | `None` | Turns scroll handling back on. Equivalent to `configure(scroll_enabled=True)`. Safe to call repeatedly. |
| `disable_scroll()` | `None` | Turns scroll handling off — wheel, trackpad, and scrollbar drag. Equivalent to `configure(scroll_enabled=False)`. |
| `is_scrolling()` | `bool` | The live effective scroll state — the AND of `scroll_enabled` and `state`. Distinct from `cget("scroll_enabled")`; see above. |
| `get_state()` | `str` | Current state, `"normal"` or `"disabled"`. Mirrors the same accessor on `sCTkFrameLabeledPrimary`/`Secondary`. |
| `winfo_children(include_private=False)` | `list` | By default, filters out children whose exact class name is `"CTkScrollbar"`, `"CTkCanvas"`, or `"Canvas"` — internal furniture this widget creates for its own scrolling machinery. **Confirmed correct by direct, live testing** — printing `get_children()` alongside the widget's internal `_parent_frame.winfo_children()` confirmed the real content widgets are found correctly by this method, and are *not* reachable via `_parent_frame` at all (they're nested deeper, inside the internal scrolling canvas). Pass `include_private=True` for the raw, unfiltered list. |
| `get_children()` | `list` | Equivalent to `winfo_children(include_private=False)`. |
| `get_all_children()` | `list` | Equivalent to `winfo_children(include_private=True)`. |
| `_finalize_split_bindings()` | `None` | **Retained for compatibility; no longer required.** Calling this after placement was once mandatory. Existing callers are harmless — the underlying toggle is idempotent — but new code shouldn't need it. Composite widgets that rebuild their content dynamically (`sCTkFileExplorer`, `sCTkTableview`) do still call it deliberately, to bind rows created after the initial `<Map>`. It respects the current state rather than forcing scrolling on. |

**On the scroll-handling itself:** the platform-specific event processing is maintainer-verified, hard-won working code, left untouched during this project's audit. It binds standard wheel and platform-specific touchpad events across multiple layers (this widget, its parent canvas if one exists, that canvas's own parent in turn, the scrollbar, and every content descendant at every depth) using regular, scoped `.bind()` calls — never `bind_all()`. It handles three genuinely different platform behaviors: Windows' `/120`-scaled `<MouseWheel>` delta, Linux's discrete `<Button-4>`/`<Button-5>` events (no continuous delta at all on Linux), and macOS's own `<MouseWheel>` scaling plus a separate, higher-precision `<TouchpadScroll>` synthetic event — which packs a two-axis scroll delta into a single 32-bit integer, decoded via bit-shifting into signed 16-bit X and Y components.

**Nested scrollable frames are handled.** The descendant walk stops at any nested `CTkScrollableFrame` boundary, so an inner scrollable frame (including anything built on this class, such as `sCTkSelector` or `sCTkTableview`) keeps its own bindings and isn't double-bound by the outer frame. Without this, both handlers would fire on the same event and scroll both frames at once. Native CustomTkinter guards the same boundary in its own `_check_if_valid_scroll`.

**How disabling actually works** (relevant if you're extending this widget). Two separate mechanisms are involved, because neither one alone is sufficient:

- *Wheel and trackpad events.* Unbinding is not enough — native `CTkScrollableFrame.__init__` installs its own application-global `bind_all("<MouseWheel>")` handler that survives any `unbind()` here. Calling `unbind_all()` would disable scrolling for every other scrollable frame in the application. Instead, a handler returning `"break"` is installed on each layer. Tk dispatches bindings by bindtag in order — widget, class, toplevel, then `all` — and `bind_all` lands on that final tag, so a widget-level `"break"` halts the chain before native's handler is ever reached. **Confirmed by live testing**: with two independent scrollable frames side by side, disabling one left the other scrolling normally with both a mouse wheel and a trackpad.
- *Scrollbar dragging.* `unbind()` is actively dangerous here — Tk's `unbind()` removes *every* binding for an event on a widget, so calling it on the scrollbar's `<Button-1>` would destroy CustomTkinter's own drag handler permanently, with no way to restore it. Binding a blocker with `add="+"` doesn't work either, since handlers fire in the order added and CustomTkinter's was added during its own construction — returning `"break"` at that point is too late. A private, per-instance bindtag is inserted at the *front* of the scrollbar's tag list instead, so the blocker runs before any of CustomTkinter's bindings. Re-enabling simply removes the tag; CustomTkinter's own bindings are never touched.

---

### Theming (`sCTkThemes.json`)

```json
{
    "sCTkScrollableFrame": {
        "border_width": 1.5,
        "border_color": ["#64748B", "#94A3B8"],
        "corner_radius": 8,
        "fg_color": ["#FFFFFF", "#111827"],
        "label_fg_color": "transparent",
        "scrollbar_fg_color": ["#FFFFFF", "#111827"],
        "scrollbar_button_color": ["#64748B", "#4B5563"],
        "scrollbar_button_hover_color": ["#1A4375", "#2471A3"],
        "disabled_map": {
            "border_color": ["#CBD5E1", "#374151"],
            "scrollbar_button_color": ["#CBD5E1", "#1F2937"],
            "scrollbar_button_hover_color": ["#CBD5E1", "#1F2937"]
        }
    }
}
```

`label_fg_color` is deliberately `"transparent"`, so the internal title-row label blends with the frame's own `fg_color` via CustomTkinter's native parent-to-child color propagation, rather than showing its own distinct background.

**`disabled_map` is required, not optional.** Construction raises `KeyError` immediately if `border_color`, `scrollbar_button_color`, or `scrollbar_button_hover_color` is missing from either the top-level block or `disabled_map`. This is the same fail-loud principle used across this project — a theme gap surfaces at construction with a message naming exactly what's missing, rather than being papered over with a guessed color.

The hover color needs a disabled entry because a disabled scrollbar is inert (dragging is blocked), and one that still lit up on hover would falsely advertise itself as draggable. Setting it to the same value as the disabled `scrollbar_button_color`, as above, means it simply doesn't react.

Only the keys that genuinely change when disabled are required in `disabled_map`. `fg_color` is deliberately **not** among them: the content background stays put when disabled, and the border and the now-inert scrollbar carry the visual signal on their own.

**Validation is scoped to direct construction.** A subclass inheriting this class (such as `sCTkTableview`) reaches this constructor with `final_kw` built from *its own* theme block — `ThemeableWidget`'s run-once guard means the parent never rebuilds it. Validating this widget's keys against a subclass's block would demand scrollbar colors from, say, the `sCTkTableview` block and raise on every construction. Subclasses own their own theme contract and validate it themselves, so this check runs only for the concrete class.

Colors are stored and passed through as raw `(light, dark)` tuples rather than resolved to a single value ahead of time, so they should correctly follow system/app appearance-mode changes automatically — the same approach validated on `sCTkComboBox`, `sCTkSegmentedButton`, and the button family, though not separately re-confirmed for this specific widget.

**Safe to use as a base class for your own composite widgets.** If you build a composite widget by inheriting `sCTkScrollableFrame` directly, construction is protected on two fronts: a run-once guard in `ThemeableWidget.__init__` stops your composite's own `final_kw` from being silently overwritten if your widget explicitly calls `ThemeableWidget.__init__` before `super().__init__()`; and this widget's own constructor only forwards the specific keys native `CTkScrollableFrame` actually accepts (confirmed directly against CustomTkinter's source, which has no fallback `**kwargs` at all — every parameter is explicitly named, so this matters more here than for most widgets).

---

### Example

```python
from scustomtkinter import sCTk, sCTkButtonPrimary, sCTkEntryPrimary, sCTkScrollableFrame

if __name__ == "__main__":
    root = sCTk()
    root.title("ScrollableFrame Example")
    root.geometry("450x420")

    log_viewport = sCTkScrollableFrame(root, width=380, height=250, label_text="Telemetry Log")
    log_viewport.pack(padx=20, pady=20, fill="both", expand=True)

    for i in range(12):
        entry = sCTkEntryPrimary(log_viewport, placeholder_text=f"Channel {i + 1}")
        entry.pack(padx=10, pady=5, fill="x")

    # No activation call needed -- scrolling is live as soon as the widget
    # is placed.

    def toggle_lock():
        target = "disabled" if log_viewport.get_state() == "normal" else "normal"
        log_viewport.configure(state=target)
        toggle_btn.configure(text="Enable All" if target == "disabled" else "Disable All")

        # Disabling the frame dims it and stops its scrolling, but does NOT
        # cascade to children -- do that explicitly.
        for child in log_viewport.get_children():
            if hasattr(child, "configure"):
                try:
                    child.configure(state=target)
                except Exception:
                    pass

    toggle_btn = sCTkButtonPrimary(root, text="Disable All", command=toggle_lock)
    toggle_btn.pack(side="bottom", pady=15)

    root.mainloop()
```

---

### Known Limitations

- **Disabling does not cascade to children.** The frame dims and stops scrolling, but child widgets are unaffected — disabling their content is the caller's responsibility, as shown in the example above.
- **The scrollbar is made inert, not hidden.** When disabled it can't be dragged and doesn't respond to hover, but it stays visible. CustomTkinter's scrollbar has no native disabled state to lock, so there's no greyed-out appearance to switch to either. Hiding it entirely is a separate technique, used elsewhere in this project (`sCTkFrameLabeledPrimary`/`Secondary`) via color-matching and zero width.
- **`winfo_children()`'s default filtering is a class-name check, not an identity check** — a plain, un-themed `customtkinter.CTkCanvas`/`CTkScrollbar`/`Canvas` added directly as a real child (not internal furniture) would be incorrectly filtered out too, since its class name matches. Themed `sCTk`-prefixed widgets are unaffected.
- **`_parent_frame`'s `width`/`height` don't reflect the real configured size** — confirmed by direct testing: reading `width`/`height` through the outer widget correctly returns the real value, but the same properties read through the internal `_parent_frame` attribute always report `0`, regardless of the widget's actual size. `fg_color`, `border_color`, and `border_width` are reliable through either path; `width`/`height` are not. There's no current code path in this widget that relies on `_parent_frame` for sizing, so this is a trap for future changes, not an active bug.
- **The nested-frame boundary guard is reasoned, not yet live-tested.** The logic mirrors native CustomTkinter's own guard and is straightforward, but an actual nested scrollable frame (or an `sCTkSelector`/`sCTkTableview` placed inside another scrollable frame) hasn't been exercised against it yet.
- **A separate `Canvas` + scrollbar placed inside this frame is not guarded.** The nested-frame boundary check keys on `CTkScrollableFrame` specifically. An independent scrolling region built directly on a plain `Canvas` would still be walked into and bound to this frame's handler, stacking an unwanted scroll behavior on top of its own. Guarding this would need an explicit opt-out convention, since a plain `Canvas` has no generic way to declare itself an independent scroll region.
- **Single-argument color queries return `str(value)`**, where `value` may itself be a `(light, dark)` tuple rather than a single resolved color. A known gap shared with the wider Pygubu single-argument query investigation set aside elsewhere in this project.

[Return to Table of Contents](#contents)
