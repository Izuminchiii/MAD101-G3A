#!/usr/bin/env python3
"""Add an affine cipher encoder/decoder to the MAD101 fx-CG50 add-in."""
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "MAD101_G3A_Project/src/main.c")
source = path.read_text(encoding="utf-8")

marker = "static void menu_algorithms(void)\n"
functions = r'''static int affine_mod26(int value)
{
    value %= 26;
    if(value < 0) value += 26;
    return value;
}

static int affine_gcd_int(int a, int b)
{
    if(a < 0) a = -a;
    if(b < 0) b = -b;
    while(b != 0) {
        int r = a % b;
        a = b;
        b = r;
    }
    return a;
}

static int affine_inverse26(int a)
{
    a = affine_mod26(a);
    for(int x = 1; x < 26; x++) {
        if((a * x) % 26 == 1) return x;
    }
    return -1;
}

static int affine_prompt_int(const char *title, int minimum, int maximum, int *out)
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
        else if(key == KEY_DEL && length > 0) {
            buffer[--length] = '\0';
        }
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

static void algo_affine_run(int decode)
{
    int a, b, count;
    if(!affine_prompt_int("Affine coefficient a (0..25)", 0, 25, &a)) return;
    if(!affine_prompt_int("Affine shift b (0..25)", 0, 25, &b)) return;

    int inverse = affine_inverse26(a);
    if(inverse < 0) {
        TextPage error;
        page_init(&error);
        page_addf(&error, "a = %d is not valid modulo 26.", a);
        page_add(&error, "Need gcd(a,26)=1 so that a has an inverse.");
        page_add(&error, "Valid a values:");
        page_add(&error, "1,3,5,7,9,11,15,17,19,21,23,25");
        show_page("Affine cipher error", &error);
        return;
    }

    if(!affine_prompt_int("Number of letters (1..20)", 1, 20, &count)) return;

    TextPage page;
    page_init(&page);
    page_add(&page, decode ? "AFFINE DECODE" : "AFFINE ENCODE");
    page_addf(&page, "a=%d, b=%d, inverse(a)=%d", a, b, inverse);
    page_add(&page, "A=0, B=1, ..., Z=25");
    page_add(&page, "");

    char result[24];
    for(int i = 0; i < count; i++) {
        char prompt[40];
        snprintf(prompt, sizeof(prompt), "%s code %d/%d (0..25)",
            decode ? "Cipher" : "Plain", i + 1, count);
        int input_code;
        if(!affine_prompt_int(prompt, 0, 25, &input_code)) return;

        int output_code;
        if(decode) output_code = affine_mod26(inverse * (input_code - b));
        else output_code = affine_mod26(a * input_code + b);

        result[i] = (char)('A' + output_code);
        page_addf(&page, "%c(%d) -> %c(%d)",
            (char)('A' + input_code), input_code,
            (char)('A' + output_code), output_code);
    }
    result[count] = '\0';

    page_add(&page, "");
    page_addf(&page, "RESULT: %s", result);
    show_page(decode ? "Affine decoded text" : "Affine encoded text", &page);
}

static void algo_affine_guide(void)
{
    TextPage page;
    page_init(&page);
    page_add(&page, "AFFINE CIPHER QUICK GUIDE");
    page_add(&page, "");
    page_add(&page, "Letter codes: A=0, B=1, ..., Z=25.");
    page_add(&page, "Encryption: c=(a*p+b) mod 26.");
    page_add(&page, "Decryption: p=a^(-1)*(c-b) mod 26.");
    page_add(&page, "Need gcd(a,26)=1.");
    page_add(&page, "");
    page_add(&page, "Example: c=(3p+7) mod 26");
    page_add(&page, "inverse of 3 modulo 26 is 9.");
    page_add(&page, "BXMF => codes 1,23,12,5.");
    page_add(&page, "Decoded result: YOTI.");
    page_add(&page, "");
    page_add(&page, "Use Decode, then enter:");
    page_add(&page, "a=3, b=7, count=4");
    page_add(&page, "codes: 1, 23, 12, 5");
    show_page("Affine cipher guide", &page);
}

static void algo_affine_cipher(void)
{
    const char *items[] = {"Decode ciphertext", "Encode plaintext", "Guide / example"};
    while(1) {
        int choice = menu_select("Affine cipher", items, 3);
        if(choice < 0) return;
        if(choice == 0) algo_affine_run(1);
        else if(choice == 1) algo_affine_run(0);
        else algo_affine_guide();
    }
}

'''

old_menu = '''static void menu_algorithms(void)
{
    const char *items[]={"Insertion sort trace","Huffman bit length","Big-O reference","Prefix evaluator","Postfix evaluator","Pre/Post tips & guide"};while(1){int c=menu_select("5. ALGORITHMS",items,6);if(c<0)return;if(c==0)algo_insertion();else if(c==1)algo_huffman();else if(c==2)algo_big_o();else if(c==3)algo_expression_evaluator(1);else if(c==4)algo_expression_evaluator(0);else algo_prefix_postfix_tips();}
}
'''

new_menu = '''static void menu_algorithms(void)
{
    const char *items[]={"Insertion sort trace","Huffman bit length","Big-O reference","Prefix evaluator","Postfix evaluator","Pre/Post tips & guide","Affine cipher solver"};while(1){int c=menu_select("5. ALGORITHMS",items,7);if(c<0)return;if(c==0)algo_insertion();else if(c==1)algo_huffman();else if(c==2)algo_big_o();else if(c==3)algo_expression_evaluator(1);else if(c==4)algo_expression_evaluator(0);else if(c==5)algo_prefix_postfix_tips();else algo_affine_cipher();}
}
'''

if "Affine cipher solver" in source and "algo_affine_cipher" in source:
    print("Affine cipher solver already enabled")
else:
    if marker not in source:
        raise SystemExit("Could not find menu_algorithms insertion marker")
    if old_menu not in source:
        raise SystemExit("Could not find current menu_algorithms block")
    source = source.replace(marker, functions + marker, 1)
    source = source.replace(old_menu, new_menu, 1)
    path.write_text(source, encoding="utf-8")
    print(f"Added affine cipher solver to {path}")
