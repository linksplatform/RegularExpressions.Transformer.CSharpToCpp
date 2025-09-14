#!/usr/bin/env python3
import re

# Read the file
with open('/tmp/gh-issue-solver-1757812256489/python/cs2cpp/cs2cpp.py', 'r') as f:
    content = f.read()

# Replace all \k<groupname> with (?P=groupname)
# This regex matches \k<groupname> patterns
pattern = r'\\k<([^>]+)>'
replacement = r'(?P=\1)'

new_content = re.sub(pattern, replacement, content)

# Write the fixed content back
with open('/tmp/gh-issue-solver-1757812256489/python/cs2cpp/cs2cpp.py', 'w') as f:
    f.write(new_content)

print("Fixed all \\k<> patterns in Python file")