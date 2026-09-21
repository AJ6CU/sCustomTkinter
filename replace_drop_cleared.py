#!/usr/bin/python3
"""
Replaces the hand-written empty-string filter in every sCTk widget with a call
to ThemeableWidget._drop_cleared().

WHAT IT CHANGES

Each widget's configure() carried its own copy of

    for k, v in list(kwargs.items()):
        if v == "":
            kwargs.pop(k)

in one of two shapes (the pop on its own line, or on the same line as the
test). Every copy dropped `text=""` along with cleared theme values, so a
label or button could not be blanked. This swaps each copy for

    self._drop_cleared(kwargs)

which keeps content keys and drops everything else exactly as before.

WHAT IT WILL NOT DO

  * Touch a file whose class does not inherit ThemeableWidget -- the helper
    would not exist there, and the call would raise.
  * Rewrite anything that is not one of the two exact shapes above. Anything
    unusual is REPORTED, not guessed at.
  * Leave a file that no longer compiles. Each is compiled after editing,
    and restored from its backup if it fails.

Every edited file is backed up alongside itself as <name>.py.bak first.

Usage:
    python3 replace_drop_cleared.py scustomtkinter/
    python3 replace_drop_cleared.py scustomtkinter/ --dry-run
"""
import pathlib
import py_compile
import re
import shutil
import sys

# The loop in either shape, at any indentation, with any names for the dict
# and the two loop variables. The pop must use the same names as the loop, so
# an unrelated `if v == ""` elsewhere cannot match by accident.
LOOP = re.compile(
    r'^(?P<ind>[ \t]*)for (?P<k>\w+), (?P<v>\w+) in list\((?P<d>\w+)\.items\(\)\):\n'
    r'(?P=ind)[ \t]+if (?P=v) == "":'
    r'(?:[ \t]*(?P=d)\.pop\((?P=k)\)\n'                    # pop on the same line
    r'|\n(?P=ind)[ \t]+(?P=d)\.pop\((?P=k)\)\n)',          # or on the next
    re.MULTILINE)


def process(path, dry_run):
    src = path.read_text()
    if "ThemeableWidget" not in src:
        return "SKIPPED -- does not use ThemeableWidget"
    if 'if ' not in src or '== "":' not in src:
        return "nothing to change"

    new, count = LOOP.subn(lambda m: f'{m["ind"]}self._drop_cleared({m["d"]})\n', src)

    leftover = len(re.findall(r'if \w+ == "":', new))
    notes = []
    if leftover:
        notes.append(f"{leftover} other `== \"\"` test(s) left for a person to look at")
    if count == 0:
        return "no matching loop -- " + (notes[0] if notes else "check by hand")

    if dry_run:
        return f"would replace {count}" + (f"; {notes[0]}" if notes else "")

    backup = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, backup)
    path.write_text(new)
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError as err:
        shutil.copy2(backup, path)
        return f"RESTORED -- would not compile after the edit: {err.msg.splitlines()[-1]}"

    return f"replaced {count}" + (f"; {notes[0]}" if notes else "")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry_run = "--dry-run" in sys.argv
    folder = pathlib.Path(args[0] if args else "scustomtkinter")

    files = sorted(p for p in folder.glob("sctk_*.py"))
    if not files:
        print(f"no sctk_*.py files in {folder}")
        return

    print("DRY RUN -- nothing will be written\n" if dry_run else "")
    width = max(len(p.name) for p in files)
    for path in files:
        print(f"  {path.name:{width}}  {process(path, dry_run)}")

    if not dry_run:
        print("\nBackups are alongside each edited file as *.py.bak.")
        print("Delete them once you are happy:  rm scustomtkinter/*.py.bak")


if __name__ == "__main__":
    main()
