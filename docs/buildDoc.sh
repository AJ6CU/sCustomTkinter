#!/bin/bash

echo -e "# Contents\n" > index.md

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

    echo "${indent}[$title](#$anchor)" >> index.md
  done
done < order.txt

echo -e "\n---\n" >> index.md

# 2. Append files in the specified order
while read -r file; do
  cat "$file" >> index.md && echo -e "\n\n" >> index.md
done < order.txt
