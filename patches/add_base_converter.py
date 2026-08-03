#!/usr/bin/env python3
# Add an interactive base converter to the MAD101 fx-CG50 add-in.
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "MAD101_G3A_Project/src/main.c")
source = path.read_text(encoding="utf-8")

marker = "static void menu_algorithms(void)\n"

functions = r'''static int base_prompt_int(const char *title, int minimum, int maximum, int *out)
{
    char buffer[8] = "";
    int length = 0;

    while(1) {
        dclear(C_WHITE);
        dtext(4, 4, C_BLACK, title);
        dline(0, 22, DWIDTH - 1, 22, C_BLACK);
        dtext(4, 40, C_BLACK, buffer[0] ? buffer : "_");
        dtext(4, 75, C_BLACK, "Digits: input   DEL: erase");
        dtext(4, 95, C_BLACK, "EXE: confirm   EXIT: cancel");
        dupdate();

        int key = getkey().key;
        int digit = -1;
        if(key == KEY_0) digit = 0;
        else if(key == KEY_1) digit = 1;
        else if(key == KEY_2) digit = 2;
        else if(key == KEY_3) digit = 3;
        else if(key == KEY_4) digit = 4;
        else if(key == KEY_5) digit = 5;
        else if(key == KEY_6) digit = 6;
        else if(key == KEY_7) digit = 7;
        else if(key == KEY_8) digit = 8;
        else if(key == KEY_9) digit = 9;

        if(digit >= 0 && length < (int)sizeof(buffer) - 1) {
            buffer[length++] = (char)('0' + digit);
            buffer[length] = '\0';
        }
        else if(key == KEY_DEL && length > 0) buffer[--length] = '\0';
        else if(key == KEY_ACON) {
            length = 0;
            buffer[0] = '\0';
        }
        else if(key == KEY_EXE && length > 0) {
            int value = 0;
            for(int i = 0; i < length; i++) value = value * 10 + (buffer[i] - '0');
            if(value >= minimum && value <= maximum) {
                *out = value;
                return 1;
            }
        }
        else if(key == KEY_EXIT || key == KEY_MENU) return 0;
    }
}

static char base_digit_char(int value)
{
    return value < 10 ? (char)('0' + value) : (char)('A' + value - 10);
}

static int base_char_value(char c)
{
    if(c >= '0' && c <= '9') return c - '0';
    if(c >= 'A' && c <= 'Z') return c - 'A' + 10;
    if(c >= 'a' && c <= 'z') return c - 'a' + 10;
    return -1;
}

static int base_number_editor(char *out, int out_size, int base)
{
    int selected = 0;
    int negative = 0;
    out[0] = '\0';

    while(1) {
        int length = (int)strlen(out);
        const char *view = out;
        if(length > 28) view = out + length - 28;

        char selected_text[32];
        snprintf(selected_text, sizeof(selected_text),
            "Selected: %c   base %d", base_digit_char(selected), base);

        dclear(C_WHITE);
        dtext(4, 3, C_BLACK, "Enter number");
        dline(0, 20, DWIDTH - 1, 20, C_BLACK);
        dtext(4, 31, C_BLACK, selected_text);
        dtext(4, 52, C_BLACK, "LEFT/RIGHT: choose digit");
        dtext(4, 72, C_BLACK, "UP/DOWN: jump 5");
        dtext(4, 92, C_BLACK, "EXE: append   DEL: erase");
        dtext(4, 112, C_BLACK, "F1: +/- sign   F6: finish");
        dtext(4, 139, C_BLACK, view[0] ? view : "_");
        dline(4, 159, DWIDTH - 8, 159, C_BLACK);
        dtext(4, 181, C_BLACK, "EXIT: cancel");
        dupdate();

        int key = getkey().key;
        if(key == KEY_LEFT) selected = (selected + base - 1) % base;
        else if(key == KEY_RIGHT) selected = (selected + 1) % base;
        else if(key == KEY_UP) selected = (selected + base - (5 % base)) % base;
        else if(key == KEY_DOWN) selected = (selected + 5) % base;
        else if(key == KEY_EXE && length < out_size - 1) {
            out[length] = base_digit_char(selected);
            out[length + 1] = '\0';
        }
        else if(key == KEY_DEL && length > 0) out[length - 1] = '\0';
        else if(key == KEY_ACON) out[0] = '\0';
        else if(key == KEY_F1) negative = !negative;
        else if(key == KEY_F6 && length > 0) {
            if(negative && length < out_size - 1) {
                memmove(out + 1, out, (size_t)length + 1);
                out[0] = '-';
            }
            return 1;
        }
        else if(key == KEY_EXIT || key == KEY_MENU) return 0;
    }
}

static int base_parse_u64(const char *text, int base, uint64_t *value, int *negative)
{
    int pos = 0;
    *negative = 0;
    if(text[pos] == '-') {
        *negative = 1;
        pos++;
    }
    if(text[pos] == '\0') return 0;

    uint64_t result = 0;
    uint64_t maximum = ~(uint64_t)0;

    for(; text[pos] != '\0'; pos++) {
        int digit = base_char_value(text[pos]);
        if(digit < 0 || digit >= base) return 0;
        if(result > (maximum - (uint64_t)digit) / (uint64_t)base) return 0;
        result = result * (uint64_t)base + (uint64_t)digit;
    }

    *value = result;
    return 1;
}

static void base_format_u64(uint64_t value, int base, int negative, char *out, int out_size)
{
    char reversed[70];
    int count = 0;

    do {
        reversed[count++] = base_digit_char((int)(value % (uint64_t)base));
        value /= (uint64_t)base;
    } while(value > 0 && count < (int)sizeof(reversed));

    int pos = 0;
    if(negative && pos < out_size - 1) out[pos++] = '-';
    while(count > 0 && pos < out_size - 1) out[pos++] = reversed[--count];
    out[pos] = '\0';
}

static void algo_base_convert_run(void)
{
    int from_base;
    int to_base;
    if(!base_prompt_int("Source base (2..36)", 2, 36, &from_base)) return;
    if(!base_prompt_int("Target base (2..36)", 2, 36, &to_base)) return;

    char input[70];
    if(!base_number_editor(input, sizeof(input), from_base)) return;

    uint64_t magnitude = 0;
    int negative = 0;
    int ok = base_parse_u64(input, from_base, &magnitude, &negative);

    TextPage page;
    page_init(&page);
    page_add(&page, "BASE CONVERTER");
    page_add(&page, "");

    if(!ok) {
        page_add(&page, "Input is invalid or too large.");
        page_add(&page, "Maximum magnitude is 64-bit unsigned.");
        show_page("Base conversion", &page);
        return;
    }

    char result[72];
    base_format_u64(magnitude, to_base, negative, result, sizeof(result));

    page_addf(&page, "(%s) base %d", input, from_base);
    page_addf(&page, "= (%s) base %d", result, to_base);
    page_add(&page, "");

    if(magnitude <= 999999999999ULL) {
        if(negative) page_addf(&page, "Decimal value: -%llu",
            (unsigned long long)magnitude);
        else page_addf(&page, "Decimal value: %llu",
            (unsigned long long)magnitude);
    }
    else {
        page_add(&page, "Decimal value is very large.");
    }

    page_add(&page, "");
    page_add(&page, "Horner steps to decimal:");
    uint64_t running = 0;
    int start = input[0] == '-' ? 1 : 0;
    int digit_count = (int)strlen(input) - start;

    if(digit_count <= 10) {
        for(int i = start; input[i] != '\0'; i++) {
            int digit = base_char_value(input[i]);
            uint64_t before = running;
            running = running * (uint64_t)from_base + (uint64_t)digit;
            if(before <= 999999999ULL && running <= 999999999ULL) {
                page_addf(&page, "%llu*%d+%d = %llu",
                    (unsigned long long)before, from_base, digit,
                    (unsigned long long)running);
            }
        }
    }
    else {
        page_add(&page, "Too many digits to list every step.");
    }

    page_add(&page, "");
    page_add(&page, "For decimal -> target base:");
    page_add(&page, "Repeatedly divide by target base.");
    page_add(&page, "Read remainders from bottom to top.");
    show_page("Base conversion", &page);
}

static void algo_base_converter_guide(void)
{
    TextPage page;
    page_init(&page);
    page_add(&page, "BASE CONVERTER GUIDE");
    page_add(&page, "");
    page_add(&page, "Common bases:");
    page_add(&page, "2 = binary, digits 0..1");
    page_add(&page, "8 = octal, digits 0..7");
    page_add(&page, "10 = decimal, digits 0..9");
    page_add(&page, "16 = hexadecimal, digits 0..9,A..F");
    page_add(&page, "");
    page_add(&page, "Example from the exam:");
    page_add(&page, "(204) base 5");
    page_add(&page, "2*5^2 + 0*5 + 4 = 54 decimal");
    page_add(&page, "54 decimal = (110110) base 2");
    page_add(&page, "Therefore the answer is 110110.");
    page_add(&page, "");
    page_add(&page, "The converter supports bases 2..36.");
    page_add(&page, "Letters A..Z represent values 10..35.");
    show_page("Base converter guide", &page);
}

static void algo_base_converter(void)
{
    const char *items[] = {"Convert any base", "Guide / exam example"};
    while(1) {
        int choice = menu_select("Base converter", items, 2);
        if(choice < 0) return;
        if(choice == 0) algo_base_convert_run();
        else algo_base_converter_guide();
    }
}

'''

old_menu = '''static void menu_algorithms(void)
{
    const char *items[]={"Insertion sort trace","Huffman bit length","Big-O reference","Prefix evaluator","Postfix evaluator","Pre/Post tips & guide","Cipher formula solver"};while(1){int c=menu_select("5. ALGORITHMS",items,7);if(c<0)return;if(c==0)algo_insertion();else if(c==1)algo_huffman();else if(c==2)algo_big_o();else if(c==3)algo_expression_evaluator(1);else if(c==4)algo_expression_evaluator(0);else if(c==5)algo_prefix_postfix_tips();else algo_cipher_formula();}
}
'''

new_menu = '''static void menu_algorithms(void)
{
    const char *items[]={"Insertion sort trace","Huffman bit length","Big-O reference","Prefix evaluator","Postfix evaluator","Pre/Post tips & guide","Cipher formula solver","Base converter"};while(1){int c=menu_select("5. ALGORITHMS",items,8);if(c<0)return;if(c==0)algo_insertion();else if(c==1)algo_huffman();else if(c==2)algo_big_o();else if(c==3)algo_expression_evaluator(1);else if(c==4)algo_expression_evaluator(0);else if(c==5)algo_prefix_postfix_tips();else if(c==6)algo_cipher_formula();else algo_base_converter();}
}
'''

if "Base converter" in source and "algo_base_converter" in source:
    print("Base converter already enabled")
else:
    if marker not in source:
        raise SystemExit("Could not find menu_algorithms insertion marker")
    if old_menu not in source:
        raise SystemExit("Could not find algorithms menu after cipher patch")
    source = source.replace(marker, functions + marker, 1)
    source = source.replace(old_menu, new_menu, 1)
    path.write_text(source, encoding="utf-8")
    print(f"Added base converter to {path}")
