#!/bin/bash

cat  ../docs/src/introduction.md > ../docs/README.md
echo -e "# Contents\n" >> ../docs/README.md

# 1. Generate TOC using order.txt
while read -r file; do
  # Removed the buggy file check completely to prevent skipping

  # awk tracks if it is inside a code block and only processes actual markdown headings
  awk '
    /^```/ { in_block = !in_block; next }
    !in_block && /^#{1,2} / { print }
  ' "$file" | while read -r line; do

    title=$(echo "$line" | sed 's/^#\{1,2\} *//')
    anchor=$(echo "$title" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g')

    case "$line" in
      "### "*) indent="    * " ;;
      "## "*)  indent="  * " ;;
      "# "*)   indent="* " ;;
    esac

    echo "${indent}[$title](#$anchor)" >> ../docs/README.md
  done
done < order.txt

echo -e "\n---\n" >> ../docs/README.md

# 2. Append files in the specified order
while read -r file; do
  cat "$file" >> ../docs/README.md && echo -e "\n\n" >> ../docs/README.md
done < order.txt

# =====================================================================
# 3. Correct the image paths for the root README.md
# =====================================================================
# Works perfectly on both macOS and Linux:
perl -pi -e 's|\(images/|\(src/images/|g' ../docs/README.md

# =====================================================================
# 4. Add a border around the images
# =====================================================================
# Works perfectly on both macOS and Linux:
python3 highlightMD.py

