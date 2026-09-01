#!/usr/bin/env python3
import sys
import re
import os


filename = "../docs/README.md"


# Read and process file
with open(filename, 'r', encoding='utf-8') as f:
    content = f.read()

# Regex to find ![alt](path)
pattern = r'!\[([^]]*)\]\(([^)]*)\)'
replacement = r'<img src="\2" alt="\1" style="border: 1px solid #d3d3d3;">'
new_content = re.sub(pattern, replacement, content)

# Write back to file
with open(filename, 'w', encoding='utf-8') as f:
    f.write(new_content)
