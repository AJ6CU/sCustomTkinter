#!/usr/bin/env python3
import sys
import re
import os

filename = "../docs/README.md"

# Read and process file
with open(filename, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix: Handles leading tabs/spaces and works across multiple lines
pattern = r'^[ \t]*!\[([^]]*)\]\(\s*([^)\s]+)\s*\)'
replacement = r'<img src="\2" alt="\1" style="border: 2px solid #555555;">'
# replacement = r'<img src="\2" alt="\1" style="border: 2px solid #555555; max-width: 300px; ">'
new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

# Write back to file
with open(filename, 'w', encoding='utf-8') as f:
    f.write(new_content)
