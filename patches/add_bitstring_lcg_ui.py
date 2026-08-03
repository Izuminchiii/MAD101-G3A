#!/usr/bin/env python3
# Add a clear bit-string/subset utility and a step-by-step LCG solver.
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "MAD101_G3A_Project/src/main.c")
source = path.read_text(encoding="utf-8")

marker = "static void menu_algorithms(void)\n"

functions = r'''static int ux_digit_from_key(int key)
{
    if(key == KEY_0) return 0;
    if(key == KEY_1) return 1;
    if(key == KEY_2) return 2;
    if(key == KEY_3) return 3;
    if(key == KEY_4) return 4;
    if(key == KEY_5) return 5;
    if(key == KEY_6) return 6;
    if(key == KEY_7) return 7;
    if(key == KEY_8) return 8;
    if(key == KEY_9) return 9;
    return -1;
}

static int ux_prompt_int(
    const char *section, const char *field, const char *hint,
    int minimum, int maximum, int *out)
{
    char buffer[16] = "";
    int length = 0;
    int negative = 0;
    int invalid = 0;

    while(1) {
        char current[40];
        char range[48];
        char message[64];

        if(length == 0)
            snprintf(current, sizeof(current), "Current: %s_", negative ? "-" : "");
        else
            snprintf(current, sizeof(current), "Current: %s%s_", negative ? "-" : "", buffer);
        snprintf(range, sizeof(range), "Allowed: %d to %d", minimum, maximum);
        snprintf(message, sizeof(message), "%s", invalid ? "Value outside allowed range" : hint);

        dclear(C_WHITE);
        dtext(4, 4, C_BLACK, section);
        dline(0, 22, DWIDTH - 1, 22, C_BLACK);
        dtext(4, 34, C_BLACK, field);
        dtext(4, 56, C_BLACK, current);
        dtext(4, 78, C_BLACK, range);
        dtext(4, 100, C_BLACK, message);
        dtext(4, 132, C_BLACK, "Digits=input  F1=+/-  DEL=erase");
        dtext(4, 152, C_BLACK, "AC=clear  EXE=confirm  EXIT=back");
        dupdate();

        int key = getkey().key;
        int digit = ux_digit_from_key(key);
        invalid = 0;

        if(digit >= 0 && length < (int)sizeof(buffer) - 1) {
            buffer[length++] = (char)('0' + digit);
            buffer[length] = '\0';
        }
        else if(key == KEY_F1 && minimum < 0) negative = !negative;
        else if(key == KEY_DEL && length > 0) buffer[--length] = '\0';
        else if(key == KEY_ACON) {
            length = 0;
            negative = 0;
            buffer[0] = '\0';
        }
        else if(key == KEY_EXE && length > 0) {
            long long value = 0;
            for(int i = 0; i < length; i++) value = value * 10 + (buffer[i] - '0');
            if(negative) value = -value;
            if(value < minimum || value > maximum) invalid = 1;
            else {
                *out = (int)value;
                return 1;
            }
        }
        else if(key == KEY_EXIT || key == KEY_MENU) return 0;
    }
}

static int ux_prompt_bits(char *bits, int expected)
{
    int length = 0;
    bits[0] = '\0';

    while(1) {
        char progress[40];
        char display[48];
        snprintf(progress, sizeof(progress), "Position: %d / %d", length + 1, expected);
        snprintf(display, sizeof(display), "%s_", bits);

        dclear(C_WHITE);
        dtext(4, 4, C_BLACK, "BIT STRING INPUT");
        dline(0, 22, DWIDTH - 1, 22, C_BLACK);
        dtext(4, 36, C_BLACK, progress);
        dtext(4, 62, C_BLACK, display);
        dtext(4, 96, C_BLACK, "Press only 0 or 1");
        dtext(4, 118, C_BLACK, "DEL=erase  AC=clear");
        dtext(4, 140, C_BLACK, "EXE=confirm when complete");
        dtext(4, 162, C_BLACK, "EXIT=cancel");
        dupdate();

        int key = getkey().key;
        if((key == KEY_0 || key == KEY_1) && length < expected) {
            bits[length++] = (key == KEY_1) ? '1' : '0';
            bits[length] = '\0';
        }
        else if(key == KEY_DEL && length > 0) bits[--length] = '\0';
        else if(key == KEY_ACON) {
            length = 0;
            bits[0] = '\0';
        }
        else if(key == KEY_EXE && length == expected) return 1;
        else if(key == KEY_EXIT || key == KEY_MENU) return 0;
    }
}

static void ux_page_add_subset(TextPage *page, const int *values, int count)
{
    char line[96] = "Subset={";
    int used = 8;

    if(count == 0) {
        page_add(page, "Subset={}");
        return;
    }

    for(int i = 0; i < count; i++) {
        char item[20];
        snprintf(item, sizeof(item), "%s%d", i ? "," : "", values[i]);
        int item_len = (int)strlen(item);

        if(used + item_len + 2 >= (int)sizeof(line)) {
            page_add(page, line);
            snprintf(line, sizeof(line), "       %s", item + (i ? 1 : 0));
            used = (int)strlen(line);
        }
        else {
            snprintf(line + used, sizeof(line) - (size_t)used, "%s", item);
            used += item_len;
        }
    }

    snprintf(line + used, sizeof(line) - (size_t)used, "}");
    page_add(page, line);
}

static void ux_bitstring_to_subset(void)
{
    int first, length;
    char bits[33];

    if(!ux_prompt_int("BIT STRING 1/3", "First element of U",
        "Example U={0,1,...,9}: enter 0", -1000, 1000, &first)) return;
    if(!ux_prompt_int("BIT STRING 2/3", "Number of elements in U",
        "Maximum supported length is 32", 1, 32, &length)) return;
    if(!ux_prompt_bits(bits, length)) return;

    int selected[32];
    int count = 0;
    for(int i = 0; i < length; i++)
        if(bits[i] == '1') selected[count++] = first + i;

    TextPage page;
    page_init(&page);
    page_add(&page, "BIT STRING -> SUBSET");
    page_add(&page, "");
    page_addf(&page, "U starts at %d and has %d elements", first, length);
    page_addf(&page, "Bits=%s", bits);
    page_add(&page, "");
    page_add(&page, "Read left to right:");
    page_add(&page, "bit 1 = include that U element");
    page_add(&page, "bit 0 = do not include it");
    page_add(&page, "");

    for(int i = 0; i < length; i++)
        if(bits[i] == '1')
            page_addf(&page, "position %d -> element %d", i + 1, first + i);

    page_add(&page, "");
    ux_page_add_subset(&page, selected, count);
    show_page("Bit string result", &page);
}

static void ux_subset_to_bitstring(void)
{
    int first, length, count;

    if(!ux_prompt_int("SUBSET 1/3", "First element of U",
        "Example U={0,1,...,9}: enter 0", -1000, 1000, &first)) return;
    if(!ux_prompt_int("SUBSET 2/3", "Number of elements in U",
        "Maximum supported length is 32", 1, 32, &length)) return;
    if(!ux_prompt_int("SUBSET 3/3", "How many selected elements?",
        "Enter 0 for the empty subset", 0, length, &count)) return;

    char bits[33];
    for(int i = 0; i < length; i++) bits[i] = '0';
    bits[length] = '\0';

    int selected[32];
    for(int i = 0; i < count; i++) {
        while(1) {
            char section[28];
            char field[40];
            int value;
            snprintf(section, sizeof(section), "ELEMENT %d / %d", i + 1, count);
            snprintf(field, sizeof(field), "Choose from %d to %d", first, first + length - 1);
            if(!ux_prompt_int(section, field, "Duplicates are not allowed",
                first, first + length - 1, &value)) return;

            int position = value - first;
            if(bits[position] == '0') {
                bits[position] = '1';
                selected[i] = value;
                break;
            }

            TextPage duplicate;
            page_init(&duplicate);
            page_add(&duplicate, "That element was already selected.");
            page_add(&duplicate, "Press EXIT, then enter another value.");
            show_page("Duplicate element", &duplicate);
        }
    }

    TextPage page;
    page_init(&page);
    page_add(&page, "SUBSET -> BIT STRING");
    page_add(&page, "");
    page_addf(&page, "U starts at %d and has %d elements", first, length);
    ux_page_add_subset(&page, selected, count);
    page_add(&page, "");
    page_addf(&page, "Bit string=%s", bits);
    page_add(&page, "");
    page_add(&page, "The first bit belongs to the first");
    page_add(&page, "listed element of U.");
    show_page("Bit string result", &page);
}

static void ux_bitstring_guide(void)
{
    TextPage page;
    page_init(&page);
    page_add(&page, "BIT STRING / SUBSET GUIDE");
    page_add(&page, "");
    page_add(&page, "Write U in its given order.");
    page_add(&page, "Match one bit to each element.");
    page_add(&page, "1 means include; 0 means exclude.");
    page_add(&page, "");
    page_add(&page, "Exam example:");
    page_add(&page, "U={0,1,2,3,4,5,6,7,8,9}");
    page_add(&page, "bits=0101010101");
    page_add(&page, "1s are at elements 1,3,5,7,9");
    page_add(&page, "Answer={1,3,5,7,9}");
    page_add(&page, "");
    page_add(&page, "Important: count positions from the");
    page_add(&page, "actual order of U, not from bit value.");
    show_page("Bit string guide", &page);
}

static void ux_bitstring_tool(void)
{
    const char *items[] = {
        "Bit string -> subset",
        "Subset -> bit string",
        "Guide / exam example"
    };

    while(1) {
        int choice = menu_select("Bit string / subset", items, 3);
        if(choice < 0) return;
        if(choice == 0) ux_bitstring_to_subset();
        else if(choice == 1) ux_subset_to_bitstring();
        else ux_bitstring_guide();
    }
}

static int ux_lcg_confirm(int x0, int a, int c, int m, int target)
{
    while(1) {
        char line1[48], line2[48], line3[48];
        snprintf(line1, sizeof(line1), "x0=%d   a=%d   c=%d", x0, a, c);
        snprintf(line2, sizeof(line2), "m=%d   target n=%d", m, target);
        snprintf(line3, sizeof(line3), "x[n+1]=(%d*x[n]+%d) mod %d", a, c, m);

        dclear(C_WHITE);
        dtext(4, 4, C_BLACK, "LCG CONFIRM");
        dline(0, 22, DWIDTH - 1, 22, C_BLACK);
        dtext(4, 40, C_BLACK, line1);
        dtext(4, 64, C_BLACK, line2);
        dtext(4, 92, C_BLACK, line3);
        dtext(4, 132, C_BLACK, "EXE=calculate");
        dtext(4, 154, C_BLACK, "EXIT=go back");
        dupdate();

        int key = getkey().key;
        if(key == KEY_EXE) return 1;
        if(key == KEY_EXIT || key == KEY_MENU) return 0;
    }
}

static void ux_lcg_run(void)
{
    int x0, a, c, m, target;

    if(!ux_prompt_int("LCG INPUT 1/5", "x0 = initial seed",
        "This is the starting sequence value", -1000000, 1000000, &x0)) return;
    if(!ux_prompt_int("LCG INPUT 2/5", "a = multiplier",
        "Formula: a*x[n] + c", -1000000, 1000000, &a)) return;
    if(!ux_prompt_int("LCG INPUT 3/5", "c = increment",
        "Formula: a*x[n] + c", -1000000, 1000000, &c)) return;
    if(!ux_prompt_int("LCG INPUT 4/5", "m = modulus",
        "m must be positive", 1, 1000000, &m)) return;
    if(!ux_prompt_int("LCG INPUT 5/5", "Find x[n], enter n",
        "Use 0 to return x0; maximum n is 50", 0, 50, &target)) return;

    if(!ux_lcg_confirm(x0, a, c, m, target)) return;

    TextPage page;
    page_init(&page);
    page_add(&page, "LINEAR CONGRUENTIAL METHOD");
    page_add(&page, "");
    page_addf(&page, "x0=%d, a=%d, c=%d, m=%d", x0, a, c, m);
    page_addf(&page, "Target: x%d", target);
    page_add(&page, "");
    page_addf(&page, "x0 = %d", x0);

    int current = x0;
    for(int n = 0; n < target; n++) {
        long long raw = (long long)a * (long long)current + (long long)c;
        int next = (int)(raw % (long long)m);
        if(next < 0) next += m;

        page_addf(&page, "x%d=(%d*%d+%d) mod %d=%d",
            n + 1, a, current, c, m, next);
        current = next;
    }

    page_add(&page, "");
    page_addf(&page, "FINAL ANSWER: x%d = %d", target, current);
    show_page("LCG result", &page);
}

static void ux_lcg_guide(void)
{
    TextPage page;
    page_init(&page);
    page_add(&page, "LCG INPUT ORDER");
    page_add(&page, "");
    page_add(&page, "1/5 x0: initial seed");
    page_add(&page, "2/5 a : multiplier");
    page_add(&page, "3/5 c : increment");
    page_add(&page, "4/5 m : modulus");
    page_add(&page, "5/5 n : which term x[n] to find");
    page_add(&page, "");
    page_add(&page, "Formula:");
    page_add(&page, "x[n+1]=(a*x[n]+c) mod m");
    page_add(&page, "");
    page_add(&page, "Example 1:");
    page_add(&page, "x0=1, a=3, c=4, m=7, n=3");
    page_add(&page, "x1=0, x2=4, x3=2");
    page_add(&page, "Answer: x3=2");
    page_add(&page, "");
    page_add(&page, "Example 2:");
    page_add(&page, "x0=3, a=5, c=4, m=7, n=4");
    page_add(&page, "x1=5, x2=1, x3=2, x4=0");
    page_add(&page, "Answer: x4=0");
    show_page("LCG guide", &page);
}

static void ux_lcg_tool(void)
{
    const char *items[] = {
        "Enter LCG values (clear 1/5)",
        "Guide and exam examples"
    };

    while(1) {
        int choice = menu_select("LCG step-by-step", items, 2);
        if(choice < 0) return;
        if(choice == 0) ux_lcg_run();
        else ux_lcg_guide();
    }
}

'''

old_menu = '''static void menu_algorithms(void)
{
    const char *items[]={"Insertion sort trace","Huffman bit length","Big-O reference","Prefix evaluator","Postfix evaluator","Pre/Post tips & guide","Cipher formula solver","Base converter","Merge comparison counter"};while(1){int c=menu_select("5. ALGORITHMS",items,9);if(c<0)return;if(c==0)algo_insertion();else if(c==1)algo_huffman();else if(c==2)algo_big_o();else if(c==3)algo_expression_evaluator(1);else if(c==4)algo_expression_evaluator(0);else if(c==5)algo_prefix_postfix_tips();else if(c==6)algo_cipher_formula();else if(c==7)algo_base_converter();else algo_merge_counter();}
}
'''

new_menu = '''static void menu_algorithms(void)
{
    const char *items[]={"Insertion sort trace","Huffman bit length","Big-O reference","Prefix evaluator","Postfix evaluator","Pre/Post tips & guide","Cipher formula solver","Base converter","Merge comparison counter","Bit string / subset","LCG clear step-by-step"};while(1){int c=menu_select("5. ALGORITHMS",items,11);if(c<0)return;if(c==0)algo_insertion();else if(c==1)algo_huffman();else if(c==2)algo_big_o();else if(c==3)algo_expression_evaluator(1);else if(c==4)algo_expression_evaluator(0);else if(c==5)algo_prefix_postfix_tips();else if(c==6)algo_cipher_formula();else if(c==7)algo_base_converter();else if(c==8)algo_merge_counter();else if(c==9)ux_bitstring_tool();else ux_lcg_tool();}
}
'''

if "LCG clear step-by-step" in source and "Bit string / subset" in source:
    print("Bit-string and clear LCG tools already enabled")
else:
    if marker not in source:
        raise SystemExit("Could not find menu_algorithms insertion marker")
    if old_menu not in source:
        raise SystemExit("Could not find algorithms menu after merge counter patch")
    source = source.replace(marker, functions + marker, 1)
    source = source.replace(old_menu, new_menu, 1)
    path.write_text(source, encoding="utf-8")
    print(f"Added bit-string utility and clear LCG input UI to {path}")
