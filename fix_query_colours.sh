#!/bin/bash
# Colour queries must not str() a (light, dark) pair.
#
#   str(x)  ->  "('#1A4375', '#2471A3')"  ->  Tk: unknown color name
#
# _query_value() resolves a pair to the half in use and passes everything else
# through untouched -- including numbers, which str() would have corrupted into
# strings.

cd "$(dirname "$0")" || exit 1

echo "before:"
grep -n "return (pname, pname, pname, str(" scustomtkinter/sctk_*.py

for f in scustomtkinter/sctk_*.py; do
    grep -q "return (pname, pname, pname, str(" "$f" || continue
    sed -i '' -E \
        's/return \(pname, pname, pname, str\(([^)]*(\([^)]*\))?[^)]*)\), str\(([^)]*)\)\)/return (pname, pname, pname, self._query_value(\1), self._query_value(\3))/' \
        "$f"
    echo "patched $(basename "$f")"
done

echo
echo "after:"
grep -n "return (pname, pname, pname, str(" scustomtkinter/sctk_*.py || echo "  no str() colour queries remain"

echo
python3 -m compileall -q scustomtkinter/ && echo "all files compile"
