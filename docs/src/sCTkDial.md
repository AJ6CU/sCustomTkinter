## sCTKDialBase

Abstract base class for the rotary dial family. It owns the canvas rendering, the mouse and scroll interaction model, the theme contract, and the state machine shared by [`sCTkDialContinuous`](sCTkDialContinuous.md), [`sCTkDialSelector`](sCTkDialSelector.md), and [`sCTkDialRange`](sCTkDialRange.md).

![sCTkDial_All_Dark.png](images/sCTkDial_All_Dark.png)

This page is the reference for how dials are drawn and themed. The three variant pages describe only what differs.

Note the spelling: the class is `sCTKDialBase` with a capital K. It is never instantiated directly and has no theme block of its own — each concrete subclass resolves its own block by class name.

### Table of Contents
* [Knob rendering](#knob-rendering)
* [Theme contract](#theme-contract)
* [Reading theme colours](#reading-theme-colours)
* [Shared API](#shared-api)
* [Redraw model](#redraw-model)
* [Known limitations](#known-limitations)

---

<a name="knob-rendering"></a>
### Knob rendering

The knob is drawn as a stack of concentric ovals stepping from `dial_shadow_color` at the rim to `dial_highlight_color` off-centre, each ring shifted toward a light source in the upper left. Tk's canvas has no gradient primitive and **no alpha channel**, so this is the only way to get a domed surface — every colour is a solid fill computed by interpolation, never a translucent overlay.

Two arcs finish it: `dial_rim_light_color` across the upper-left edge and `dial_rim_shadow_color` across the lower-right.

**The rim light does most of the work on dark knobs.** A black knob's shading range is clamped at the bottom — you cannot go darker than black at the edge — so it has roughly half the dynamic range of a light one. Remove the bright rim arc and a dark knob collapses back to a flat disc. This is why the highlight and shadow colours are explicit theme keys rather than derived from `dial_color` by a fixed lighten/darken: a percentage that produces a visible rim on black blows out on aluminium, and vice versa.

Tuning constants live on the base class, so they can be overridden per subclass or per instance:

| Constant | Default | Meaning |
|---|---|---|
| `KNOB_SHADE_STEPS` | `18` | Ring count. Below ~12 the steps read as contour bands; above ~24 costs more than it shows. |
| `KNOB_SHADE_SHRINK` | `0.55` | How far the stack shrinks from rim to centre, as a fraction of radius. |
| `KNOB_LIGHT_OFFSET` | `0.55` | How far each ring drifts toward the light. |
| `DIMPLE_RADIUS_FRAC` | `0.36` | Finger dimple radius, as a fraction of knob radius. |
| `DIMPLE_RIM_CLEARANCE_FRAC` | `0.06` | Gap between dimple edge and rim, same units. |
| `POINTER_WIDTH` | `3.0` | Pointer line width in pixels. |
| `POINTER_RIM_INSET` | `3` | How far short of the rim the pointer stops. |

The dimple and clearance are **fractions, not pixels**. An earlier version used a fixed 14px inset with a fixed 14.5px radius, so the dimple was lost on a large dial and swallowed a small one.

**Recesses shade opposite to domes.** The knob body is a dome, lit on the upper left. The dimple is a hole, so its shading inverts — shadowed on the upper-left interior wall, lit on the lower right. Drawn with the body's light direction it reads as a raised bump instead of something you can put a finger in.

---

<a name="theme-contract"></a>
### Theme contract

Every concrete dial requires these at the **top level** of its theme block:

`fg_color`, `text_color`, `shadow_color`, `dial_color`, `dial_highlight_color`, `dial_shadow_color`, `dial_rim_light_color`, `dial_rim_shadow_color`

and these inside **`disabled_map`**:

`text_color`, `dial_color`

Plus one variant-specific key each — see the individual pages.

**Construction raises `KeyError`** naming the missing key and where it belongs. This replaced a pattern of `.get(key) or ("#hex", "#hex")` throughout the draw routine, which silently substituted a plausible guess and made an incomplete theme block look merely slightly-off rather than broken.

`fg_color` is deliberately **not** required in `disabled_map`: the background does not dim when disabled, the knob face and text carry the signal. This also fixes a latent bug — the old code read `fg_color` from `disabled_map` for *both* the dial face and the background, so once that key existed the knob would have rendered the same colour as the surface behind it and vanished. The two only looked different because the map was empty and their hardcoded fallbacks happened to differ.

The flat `disabled_text_color` / `disabled_dial_color` / `disabled_dimple_glow` keys used by earlier theme files are **retired**. They now live in `disabled_map` under their normal names, matching every other widget in the library.

---

<a name="reading-theme-colours"></a>
### Reading theme colours

> **Custom drawing colours must be read from the raw theme registry, not from `final_kw`.** This is a trap that produces plausible-looking wrong colours rather than an error, and it went unnoticed in this widget family for its entire existence.

`ThemeableWidget` maintains a `CUSTOM_VECTOR_KEYS` set — `dial_color`, `shadow_color`, `text_color`, `pointer_color`, `pointer_glow_color`, `diameter` and others — which it strips out of `final_kw` for vector widgets, so they never reach the native `CTkFrame` constructor and raise `ValueError`. That stripping is correct and necessary.

What was wrong was reading those colours back out of `final_kw` afterwards. They were never in there. Every fallback in the old draw code was therefore *always* taken, and the configured values for `dial_color`, `shadow_color`, `text_color` and `pointer_glow_color` were decorative — the dials rendered in hardcoded colours regardless of what the theme said. Applying fail-loud validation is what surfaced it.

The base class now builds `_local_defaults` from the raw registry block, with `final_kw` layered on top so non-vector keys and constructor overrides keep their precedence:

```python
raw_block = _tw.GLOBAL_THEME_REGISTRY.get(self.__class__.__name__) or {}
raw_colors = {k: v for k, v in raw_block.items() if not isinstance(v, dict)}
self._local_defaults = ThemeableWidget._convert_lists_to_tuples(raw_colors)
self._local_defaults.update(self.final_kw)
```

The registry is reached as a **module attribute**, not a direct name import, because `load_initial_framework_themes()` rebinds that global on load — `from ... import GLOBAL_THEME_REGISTRY` captures the empty dict that exists at import time.

---

<a name="shared-api"></a>
### Shared API

| Member | Type | Description |
| :--- | :--- | :--- |
| `state(mode=None)` | method | Getter with no argument; setter with `"normal"` or `"disabled"`. Unbinds clicks, wheel and trackpad input, and repaints from `disabled_map`. |
| `get_state()` | method | Equivalent to `state()` with no argument. |
| `configure(state=...)` | method | Same effect as `state()`. Both routes are supported. |
| `configure(name)` | method | Pygubu-style single-argument query. |
| `config` | alias | Bound to `configure` **on every class in the family**. |
| `diameter` | `int` | Square bounding size; sets canvas width and height together. |
| `divisions` | `int` | Tick count drawn around the outer ring. |

**`config = configure` is declared separately on each class, and must be.** Tkinter binds `.config` to `.configure` as its own class attribute — it does not track whichever `configure()` a subclass defines. Without a per-class line, `.config(...)` skips every override and lands on the native widget, bypassing divisions/command/diameter handling and the theme repaint entirely. This was missing from all four dial classes; the same bug was confirmed on `sCTkSegmentedButton` earlier in this project's audit. An inherited alias would not help — it would point at the *parent's* `configure()`.

---

<a name="redraw-model"></a>
### Redraw model

Two entry points, deliberately separate:

- **`_draw_dial_base()`** rebuilds everything. Call on geometry, theme or state change.
- **`_redraw_indicator()`** redraws only the dimple or pointer line, leaving the knob body, ticks and labels alone. Call on a **value** change.

The body is now roughly twenty shaded ovals plus ticks and labels, none of which changes as the dial turns. Rebuilding all of it per detent would make the shading cost real; the split makes it free while tuning. Same pattern as `sCTkSMeter._execute_needle_draw()`, which redraws its needle against a static face.

`_redraw_indicator()` falls back to a full pass if the body isn't on the canvas — first paint, or after a resize wiped it — so a partial update can't leave the dial blank.

---

<a name="known-limitations"></a>
### Known limitations

- **Constructor overrides don't work for vector-guarded colours.** `sCTkDialContinuous(master, dial_color="#FF0000")` is silently ignored, because `ThemeableWidget` strips those names from its `kwargs` loop as well as from the theme block. Changing this means touching `themeable_widget.py`.
- **The five shading keys aren't in `CUSTOM_VECTOR_KEYS`,** so they do land in `final_kw`. Harmless here — the dial's own `FRAME_VALID_KEYS` whitelist filters them before the native constructor — but a widget that forwarded `final_kw` wholesale would raise.
- **Knurling teeth and the canvas background fallback remain hardcoded.** The teeth are a shadow effect rather than a palette choice; the background fallback is the "a raw canvas needs a renderable colour" case accepted elsewhere in this library.
- **Ticks and labels are not affected by the body shading** — they sit outside the knob radius and draw flat in `text_color`.
- **Scroll handling is duplicated across the three subclasses.** `_process_mac_touchpad_scroll` and `_process_scroll_wheel` are near-identical in each, differing only in the line that applies the step. This is not a candidate for `ScrollBindingMixin`: a dial steps discretely with a cooldown and has no `yview_scroll` target. It belongs in this base class with one overridable step method.
