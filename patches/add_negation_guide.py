#!/usr/bin/env python3
"""Add an exam-oriented negation guide to the Logic menu."""
from pathlib import Path
import re
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "MAD101_G3A_Project/src/main.c")
source = path.read_text(encoding="utf-8")

if "NEGATION RULES - EXAM NOTE" in source:
    print("Negation guide already enabled")
    raise SystemExit(0)

menu_signature = "static void menu_logic(void)"
menu_start = source.find(menu_signature)
if menu_start < 0:
    raise SystemExit("Could not find menu_logic(void)")

# Locate the complete menu_logic function with brace matching.
open_brace = source.find("{", menu_start)
if open_brace < 0:
    raise SystemExit("Could not find opening brace of menu_logic")

depth = 0
menu_end = -1
for index in range(open_brace, len(source)):
    char = source[index]
    if char == "{":
        depth += 1
    elif char == "}":
        depth -= 1
        if depth == 0:
            menu_end = index + 1
            break
if menu_end < 0:
    raise SystemExit("Could not find closing brace of menu_logic")

function_code = r'''static void logic_negation_guide(void)
{
    TextPage p;
    page_init(&p);
    page_add(&p, "NEGATION RULES - EXAM NOTE");
    page_add(&p, "");
    page_add(&p, "MAIN METHOD: work from outside inward.");
    page_add(&p, "1) Switch every quantifier.");
    page_add(&p, "2) Keep the variable order unchanged.");
    page_add(&p, "3) Push NOT into the proposition.");
    page_add(&p, "");
    page_add(&p, "QUANTIFIERS");
    page_add(&p, "NOT (FOR ALL x P) = EXISTS x (NOT P)");
    page_add(&p, "NOT (EXISTS x P) = FOR ALL x (NOT P)");
    page_add(&p, "");
    page_add(&p, "CONNECTIVES");
    page_add(&p, "NOT (P AND Q) = (NOT P) OR (NOT Q)");
    page_add(&p, "NOT (P OR Q) = (NOT P) AND (NOT Q)");
    page_add(&p, "NOT (P -> Q) = P AND (NOT Q)");
    page_add(&p, "NOT (P <-> Q) = P XOR Q");
    page_add(&p, "NOT (P XOR Q) = P <-> Q");
    page_add(&p, "NOT (NOT P) = P");
    page_add(&p, "");
    page_add(&p, "CALCULATOR-SAFE KEYS");
    page_add(&p, "N=NOT A=AND O=OR X=XOR");
    page_add(&p, "I=implication B=biconditional");
    page_add(&p, "Example: N(P B Q) = P X Q");
    page_add(&p, "");
    page_add(&p, "EXAM EXAMPLE FROM REVIEW");
    page_add(&p, "Negate:");
    page_add(&p, "EXISTS x FOR ALL y");
    page_add(&p, "[P(x,y) <-> NOT Q(x,y)]");
    page_add(&p, "");
    page_add(&p, "Step 1: switch quantifiers");
    page_add(&p, "FOR ALL x EXISTS y");
    page_add(&p, "NOT [P(x,y) <-> NOT Q(x,y)]");
    page_add(&p, "");
    page_add(&p, "Step 2: NOT biconditional = XOR");
    page_add(&p, "FOR ALL x EXISTS y");
    page_add(&p, "[P(x,y) XOR NOT Q(x,y)]");
    page_add(&p, "");
    page_add(&p, "Correct answer: (iii)");
    page_add(&p, "");
    page_add(&p, "COMMON TRAPS");
    page_add(&p, "Do not reverse x,y order.");
    page_add(&p, "Do not only switch quantifiers;");
    page_add(&p, "the inside proposition must be negated too.");
    page_add(&p, "For <->, negation becomes XOR.");
    show_page("Negation rules", &p);
}

'''

source = source[:menu_start] + function_code + source[menu_start:]
menu_start += len(function_code)
menu_end += len(function_code)
menu_text = source[menu_start:menu_end]

# Add the new menu label to the existing items array.
items_match = re.search(
    r"const\s+char\s*\*\s*items\s*\[\s*\]\s*=\s*\{(?P<body>.*?)\}\s*;",
    menu_text,
    re.S,
)
if not items_match:
    raise SystemExit("Could not find items array in menu_logic")

items_body = items_match.group("body")
old_items = re.findall(r'"(?:\\.|[^"\\])*"', items_body)
old_count = len(old_items)
if old_count < 1:
    raise SystemExit("Logic menu has no items")

new_body = items_body.rstrip()
if new_body and not new_body.rstrip().endswith(","):
    new_body += ","
new_body += '"Negation rules & example"'
menu_text = (
    menu_text[:items_match.start("body")]
    + new_body
    + menu_text[items_match.end("body"):]
)

# Find the menu choice variable and increase the item count.
select_match = re.search(
    r"int\s+(?P<var>[A-Za-z_]\w*)\s*=\s*menu_select\((?P<args>[^;]*?\bitems\b\s*,\s*)(?P<count>\d+)\s*\)",
    menu_text,
    re.S,
)
if not select_match:
    raise SystemExit("Could not find menu_select call in menu_logic")
choice_var = select_match.group("var")
menu_count = int(select_match.group("count"))
if menu_count != old_count:
    raise SystemExit(f"Logic menu item count mismatch: array={old_count}, call={menu_count}")
menu_text = (
    menu_text[:select_match.start("count")]
    + str(old_count + 1)
    + menu_text[select_match.end("count"):]
)

# The original compact menu uses a final plain 'else old_last_function();'.
# Preserve that old last item and route only the new final index to the guide.
plain_else_pattern = re.compile(
    r"\belse\s+(?!if\b)(?P<call>[A-Za-z_]\w*\s*\([^;{}]*\)\s*;)"
)
plain_else_matches = list(plain_else_pattern.finditer(menu_text))
if not plain_else_matches:
    raise SystemExit("Could not find final dispatch else in menu_logic")
last_else = plain_else_matches[-1]
old_last_call = last_else.group("call")
replacement = (
    f"else if({choice_var}=={old_count - 1}){old_last_call}"
    f"else logic_negation_guide();"
)
menu_text = menu_text[:last_else.start()] + replacement + menu_text[last_else.end():]

source = source[:menu_start] + menu_text + source[menu_end:]
path.write_text(source, encoding="utf-8")
print(f"Added negation guide to {path}")
