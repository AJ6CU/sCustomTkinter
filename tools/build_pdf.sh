#!/bin/bash
# Builds the reference manual PDF from docs/README.md.
#
# Run from anywhere -- the script finds the repository root from its own
# location. The intermediate HTML is written into docs/ so that the images/
# paths inside the markdown resolve relative to it.
#
# Requires: pandoc, weasyprint
#     brew install pandoc pango
#     pip install weasyprint
#
# WeasyPrint looks for its graphics libraries under Windows-style names
# ("libgobject-2.0-0"), while Homebrew installs libgobject-2.0.dylib -- and
# Homebrew's lib directory is not on the dynamic loader's search path. The
# export below is what makes it findable:
#
#     OSError: cannot load library 'libgobject-2.0-0'
#
# Harmless on a machine that does not need it, and on Intel Macs the path is
# /usr/local/lib instead, so both are listed.

set -e
cd "$(dirname "$0")/.."          # repository root

export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib:/usr/local/lib:${DYLD_FALLBACK_LIBRARY_PATH}"
DOCS="docs"
CSS="tools/manual.css"
HTML="$DOCS/.manual.html"
OUT="$DOCS/sCustomTkinterReferenceManual.pdf"

command -v pandoc     >/dev/null || { echo "pandoc not found -- brew install pandoc"; exit 1; }
command -v weasyprint >/dev/null || { echo "weasyprint not found -- pip install weasyprint"; exit 1; }

echo "Converting markdown to HTML..."
pandoc "$DOCS/README.md" \
    -f gfm -t html5 \
    --standalone \
    --metadata title="sCustomTkinter Reference Manual" \
    -o "$HTML"

# Each widget page carries its own #contents, #overview and so on, which
# collide once merged -- WeasyPrint warns "Anchor defined twice" and every
# internal link jumps to the first occurrence in the document rather than the
# local one.
echo "Namespacing anchors..."
python3 tools/namespace_anchors.py "$HTML"

echo "Rendering PDF..."
# The stylesheet is passed on the command line rather than linked from the
# HTML, so the intermediate needs no knowledge of where it lives.
# Page size, margins, page numbers and the running header all come from
# @page rules in the CSS.
weasyprint --stylesheet "$CSS" "$HTML" "$OUT"

rm -f "$HTML"

echo "Written: $OUT"
