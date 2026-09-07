#!/bin/bash
# Replaces the broken fall-through in every widget that still has it.
#
#   return super().configure(pname)          -> return self._configure_query(pname)
#   return super().configure(require_redraw) -> return self._configure_query(require_redraw)
#
# Only matches whole lines, so the FIX comments quoting the old code in
# already-corrected files are left alone.

cd "$(dirname "$0")" || exit 1

for f in scustomtkinter/sctk_*.py; do
    before=$(grep -cE '^\s+return super\(\)\.configure\((pname|require_redraw)\)\s*$' "$f")
    [ "$before" -eq 0 ] && continue
    sed -i '' -E \
        's/^([[:space:]]+)return super\(\)\.configure\((pname|require_redraw)\)[[:space:]]*$/\1return self._configure_query(\2)/' \
        "$f"
    after=$(grep -cE '^\s+return super\(\)\.configure\((pname|require_redraw)\)\s*$' "$f")
    echo "$(basename "$f"): $before site(s), $after remaining"
done

echo
echo "verifying every file still compiles:"
python3 -m compileall -q scustomtkinter/ && echo "  all OK"
