#!/usr/bin/env python3
"""Add file-scope prototypes required by patches inserted before helper definitions."""
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "MAD101_G3A_Project/src/main.c")
source = path.read_text(encoding="utf-8")

prototype = "static int base_prompt_int(const char *title, int minimum, int maximum, int *out);\n"
definition = "static int base_prompt_int(const char *title, int minimum, int maximum, int *out)"

use_pos = source.find("base_prompt_int(")
def_pos = source.find(definition)
proto_pos = source.find(prototype)

if def_pos < 0:
    raise SystemExit("Could not find base_prompt_int definition")

if proto_pos >= 0 and proto_pos < def_pos:
    print("Forward declaration already present")
    raise SystemExit(0)

# A patched tool calls base_prompt_int before its later static definition.
# Insert a file-scope prototype immediately before the first static function.
if use_pos >= 0 and use_pos < def_pos:
    insert_pos = source.find("\nstatic ")
    if insert_pos < 0:
        raise SystemExit("Could not find a safe file-scope insertion point")
    insert_pos += 1
    source = source[:insert_pos] + prototype + source[insert_pos:]
    path.write_text(source, encoding="utf-8")
    print("Added base_prompt_int forward declaration")
else:
    print("No forward declaration required")
