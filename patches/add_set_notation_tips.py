#!/usr/bin/env python3
# Add a compact exam guide for membership, subsets, empty sets, and Cartesian products.
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "MAD101_G3A_Project/src/main.c")
source = path.read_text(encoding="utf-8")

function_marker = "static void ux_bitstring_tool(void)\n"
function_code = r'''static void ux_set_notation_guide(void)
{
    TextPage page;
    page_init(&page);
    page_add(&page, "SET NOTATION: IN VS SUBSET");
    page_add(&page, "");
    page_add(&page, "in: the LEFT side is one element.");
    page_add(&page, "subseteq: the LEFT side is a set.");
    page_add(&page, "Braces { } change an element into a set.");
    page_add(&page, "");
    page_add(&page, "Exam example: determine true statements");
    page_add(&page, "1) a in {a}                 TRUE");
    page_add(&page, "   a is an element of {a}.");
    page_add(&page, "");
    page_add(&page, "2) {a} in {a}               FALSE");
    page_add(&page, "   {a} contains a, not the set {a}.");
    page_add(&page, "");
    page_add(&page, "3) a subseteq {a,b}          FALSE");
    page_add(&page, "   a is an element, not a set.");
    page_add(&page, "");
    page_add(&page, "4) {a,b} in {a,b,c,d}        FALSE");
    page_add(&page, "   RHS contains a,b,c,d separately.");
    page_add(&page, "");
    page_add(&page, "5) empty subseteq {empty}    TRUE");
    page_add(&page, "   Empty set is a subset of every set.");
    page_add(&page, "");
    page_add(&page, "6) empty x {a} = empty       TRUE");
    page_add(&page, "   No first element means no ordered pair.");
    page_add(&page, "");
    page_add(&page, "Correct group: 1, 5, 6");
    page_add(&page, "");
    page_add(&page, "FAST CHECK");
    page_add(&page, "x in A: ask 'Is x listed in A?'");
    page_add(&page, "X subseteq A: ask 'Are all elements");
    page_add(&page, "of X also elements of A?'");
    page_add(&page, "Do not confuse empty with {empty}.");
    page_add(&page, "empty has 0 elements; {empty} has 1.");
    show_page("Set notation guide", &page);
}

'''

if "static void ux_set_notation_guide(void)" not in source:
    if function_marker not in source:
        raise SystemExit("Could not find bit-string tool marker")
    source = source.replace(function_marker, function_code + function_marker, 1)

old_items = '''        "Bit string -> subset",
        "Subset -> bit string",
        "Guide / exam example"
    };'''
new_items = '''        "Bit string -> subset",
        "Subset -> bit string",
        "Guide / exam example",
        "Set notation: in vs subset"
    };'''
if old_items in source:
    source = source.replace(old_items, new_items, 1)
elif "Set notation: in vs subset" not in source:
    raise SystemExit("Could not update bit-string menu items")

source = source.replace(
    'menu_select("Bit string / subset", items, 3);',
    'menu_select("Bit string / subset", items, 4);',
    1,
)
source = source.replace(
    '        else ux_bitstring_guide();',
    '        else if(choice == 2) ux_bitstring_guide();\n        else ux_set_notation_guide();',
    1,
)

path.write_text(source, encoding="utf-8")
print("Added set notation guide")
