# sCustomTkinter — changes from this session

Everything here is library work. The application files are separate.

    widgets/    go in the scustomtkinter package, beside their siblings
    docs/       go with the other widget pages
    tests/      standalone; run them from anywhere the library imports
    sCTkThemes.json   replaces the one in the library

---

## Widgets

**`sctk_frame_labeled_primary.py`**, **`sctk_frame_labeled_secondary.py`** —
*the panel is now as tall as what is in it.*

A `ttk.LabelFrame` is as tall as its contents, and these are modelled on one,
but they are built on `CTkScrollableFrame`, which is 200 points high whatever
it holds. A panel of two rows stood half empty. Worse, a `height` passed in
was recorded and then overridden, because the widget you hold is the INNER
frame of three — `master` is the canvas — and the height has to go on
`_parent_frame` with propagation off. No caller could reasonably work that
out, which is why it belongs here rather than in each caller.

* No `height` given: the panel follows its contents, measuring again whenever
  they change.
* A `height` given: honoured exactly, and content past it is clipped — this
  panel does not scroll by design.
* `fit_to_content()` is public, for rows added long after construction.

The chrome — title bar, padding, border — is MEASURED once, not calculated;
it came to 56 points on a Mac, against the 34 the arithmetic predicted, which
drew every panel one row short.

**`sctk_button_secondary.py`**, **`sctk_button_tertiary.py`** —
*the alarm state, which only Primary had.*

`set_alarm_state()`, `is_alarm`, and the precedence **disabled > alarm >
pressed > normal**, matching Primary exactly. Anything needing to raise an
alarm had to be a Primary before, whatever its place in the hierarchy, or be
hand-coloured by the caller.

Secondary fills red; Tertiary colours its border and text only, for the same
reason its `disabled_map` has no `fg_color` — a fill would turn an outline
button into a filled one just because it is raising an alarm.

**`sctk_smeter_bar.py`** — *the reading, in words.*

`set(sig_text="-63 dBFS")` draws the value at the right end of the S row's
caption line, level with "SIG". The bar shows roughly where a signal is; this
says exactly. The widget does not interpret the text, so the caller chooses
the units. Runtime state like the readings, so the Designer is unaffected.

---

## sCTkThemes.json

**Engaged states now move one way across the library** — see
`docs/Theming-engaged-states.md`, which is written to be pasted into
`Theming.md`.

* `sCTkButtonPrimary` takes the segmented button's palette exactly, so a
  latched button and a selected segment look alike. **Its resting fill
  changes**, from `#1A4375` to `#4F75A2`: nothing may rest on the colour that
  means engaged. Every primary button in an application gets lighter at rest.
* `sCTkButtonSecondary` and `sCTkButtonTertiary` step the same DIRECTION from
  their own colours — darker in light mode, lighter in dark. Secondary went
  the wrong way in dark mode; Tertiary's engaged fill was exactly its hover
  colour, so a button under the pointer looked identical to a latched one.
* `alarm_map` added for Secondary and Tertiary.

---

## Tests

**`test_frame_labeled_sizing.py`** — five panels: two rows, five rows, a
primary, one that grows when you add a row, and one given `height=90` with six
rows to clip. Prints drawn height, content height, and the room the contents
actually got. Every panel should say `yes` except the one meant to clip.

**`test_button_alarm.py`** — all three tiers: alarm on and off, alarm over
pressed, alarm on a disabled button. Watch that Tertiary stays unfilled.

---

## Not done, and known

* **`Theming.md` itself is not edited** — the file was not to hand. The
  section to paste is `docs/Theming-engaged-states.md`.
* **`sCTkSegmentedButton.md` is not updated.** Its colours do not change, but
  its page should point at the engaged-state rule now that Primary shares its
  palette.
* **`pressed` is a poor name** for what it means. `set_pressed()` is not click
  feedback — CustomTkinter has no press colour at all; what you see while
  clicking is the hover colour. It is a latch the application turns on and
  leaves on. Renaming it would touch every widget and every theme block, so
  the documentation explains it instead.
