#!/usr/bin/env python3
# Keep the LCG recurrence visible while every parameter is being entered.
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "MAD101_G3A_Project/src/main.c")
source = path.read_text(encoding="utf-8")

old = r'''        dtext(4, 34, C_BLACK, field);
        dtext(4, 56, C_BLACK, current);
        dtext(4, 78, C_BLACK, range);
        dtext(4, 100, C_BLACK, message);
        dtext(4, 132, C_BLACK, "Digits=input  F1=+/-  DEL=erase");
        dtext(4, 152, C_BLACK, "AC=clear  EXE=confirm  EXIT=back");
'''

new = r'''        if(strncmp(section, "LCG INPUT", 9) == 0) {
            dtext(4, 30, C_BLACK, "x[n+1]=(a*x[n]+c) mod m");
            dtext(4, 52, C_BLACK, field);
            dtext(4, 74, C_BLACK, current);
            dtext(4, 96, C_BLACK, range);
            dtext(4, 118, C_BLACK, message);
            dtext(4, 146, C_BLACK, "Digits=input F1=+/- DEL=erase");
            dtext(4, 166, C_BLACK, "AC=clear EXE=confirm EXIT=back");
        }
        else {
            dtext(4, 34, C_BLACK, field);
            dtext(4, 56, C_BLACK, current);
            dtext(4, 78, C_BLACK, range);
            dtext(4, 100, C_BLACK, message);
            dtext(4, 132, C_BLACK, "Digits=input  F1=+/-  DEL=erase");
            dtext(4, 152, C_BLACK, "AC=clear  EXE=confirm  EXIT=back");
        }
'''

if 'dtext(4, 30, C_BLACK, "x[n+1]=(a*x[n]+c) mod m")' in source:
    print("LCG formula is already visible during input")
elif old not in source:
    raise SystemExit("Could not find the numeric input layout to upgrade")
else:
    source = source.replace(old, new, 1)
    path.write_text(source, encoding="utf-8")
    print(f"Made the LCG formula visible on every input screen in {path}")
