"""
sCTkFrequencyDisplay never uses Windows' bitmap "Courier".

    python examples/validation-tests/test_frequency_display_font.py

On Windows "Courier" is installed as the old raster font, so the readout's
digits came out jagged (uBITX CEC Desktop, 2026-11-13). The platform and the
installed fonts are simulated here, so this runs anywhere.
"""
import sys
import tkinter.font as tkfont
import scustomtkinter as s
from scustomtkinter import sctk_frequency_display as fd

root = s.sCTk()
real_families, real_platform = tkfont.families, sys.platform
cases = [
    ("win32", ["Courier", "Consolas", "Courier New", "Arial"], "Consolas"),
    ("win32", ["Courier", "Courier New", "Arial"], "Courier New"),
    ("darwin", ["Courier", "Menlo"], "Courier"),
    ("linux", ["Courier", "DejaVu Sans Mono"], "Courier"),
]
results = []
for platform, installed, want in cases:
    fd.sys.platform = platform
    tkfont.families = lambda *a, _i=installed, **k: tuple(_i)
    fd.sCTkFrequencyDisplay._resolved_family = None
    display = s.sCTkFrequencyDisplay(root)
    got = display._available_family("Courier")
    display.destroy()
    ok = got == want
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {platform} with {installed}: {got} (want {want})")
fd.sys.platform, tkfont.families = real_platform, real_families
fd.sCTkFrequencyDisplay._resolved_family = None
root.destroy()
print(f"{sum(results)}/{len(results)} passed")
