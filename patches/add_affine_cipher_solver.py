#!/usr/bin/env python3
"""Add a formula-driven classical cipher encoder/decoder to the MAD101 fx-CG50 add-in."""
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "MAD101_G3A_Project/src/main.c")
source = path.read_text(encoding="utf-8")

marker = "static void menu_algorithms(void)\n"
functions = r'''typedef struct {
    const char *text;
    int pos;
    int p_value;
    int ok;
} CipherFormulaParser;

static int cipher_mod64(int64_t value, int modulus)
{
    int result = (int)(value % modulus);
    if(result < 0) result += modulus;
    return result;
}

static void cipher_skip_spaces(CipherFormulaParser *parser)
{
    while(parser->text[parser->pos] == ' ') parser->pos++;
}

static int cipher_factor_starts(char c)
{
    return (c >= '0' && c <= '9') || c == 'P' || c == 'p' || c == '(';
}

static int64_t cipher_parse_expression(CipherFormulaParser *parser);

static int64_t cipher_parse_factor(CipherFormulaParser *parser)
{
    cipher_skip_spaces(parser);
    char c = parser->text[parser->pos];

    if(c == '+') {
        parser->pos++;
        return cipher_parse_factor(parser);
    }
    if(c == '-') {
        parser->pos++;
        return -cipher_parse_factor(parser);
    }
    if(c == 'P' || c == 'p') {
        parser->pos++;
        return parser->p_value;
    }
    if(c == '(') {
        parser->pos++;
        int64_t value = cipher_parse_expression(parser);
        cipher_skip_spaces(parser);
        if(parser->text[parser->pos] != ')') {
            parser->ok = 0;
            return 0;
        }
        parser->pos++;
        return value;
    }
    if(c >= '0' && c <= '9') {
        int64_t value = 0;
        while(parser->text[parser->pos] >= '0' && parser->text[parser->pos] <= '9') {
            value = value * 10 + (parser->text[parser->pos] - '0');
            parser->pos++;
        }
        return value;
    }

    parser->ok = 0;
    return 0;
}

static int64_t cipher_parse_term(CipherFormulaParser *parser)
{
    int64_t value = cipher_parse_factor(parser);
    while(parser->ok) {
        cipher_skip_spaces(parser);
        char c = parser->text[parser->pos];
        if(c == '*') {
            parser->pos++;
            value *= cipher_parse_factor(parser);
        }
        else if(cipher_factor_starts(c)) {
            /* Permit familiar implicit multiplication such as 3P or 3(P+1). */
            value *= cipher_parse_factor(parser);
        }
        else break;
    }
    return value;
}

static int64_t cipher_parse_expression(CipherFormulaParser *parser)
{
    int64_t value = cipher_parse_term(parser);
    while(parser->ok) {
        cipher_skip_spaces(parser);
        char c = parser->text[parser->pos];
        if(c == '+') {
            parser->pos++;
            value += cipher_parse_term(parser);
        }
        else if(c == '-') {
            parser->pos++;
            value -= cipher_parse_term(parser);
        }
        else break;
    }
    return value;
}

static int64_t cipher_eval_formula(const char *formula, int p_value, int *ok)
{
    CipherFormulaParser parser;
    parser.text = formula;
    parser.pos = 0;
    parser.p_value = p_value;
    parser.ok = 1;

    int64_t value = cipher_parse_expression(&parser);
    cipher_skip_spaces(&parser);
    if(parser.text[parser.pos] != '\0') parser.ok = 0;
    *ok = parser.ok;
    return value;
}

static void cipher_append_char(char *text, int size, char c)
{
    int length = (int)strlen(text);
    if(length < size - 1) {
        text[length] = c;
        text[length + 1] = '\0';
    }
}

static int cipher_formula_editor(char *out, int out_size)
{
    out[0] = '\0';
    while(1) {
        int length = (int)strlen(out);
        const char *view = out;
        if(length > 44) view = out + length - 44;

        dclear(C_WHITE);
        dtext(4, 3, C_BLACK, "Enter ENCODE formula f(P)");
        dline(0, 20, DWIDTH - 1, 20, C_BLACK);
        dtext(4, 28, C_BLACK, "Do not type MOD here");
        dtext(4, 48, C_BLACK, "F1:P F2:+ F3:- F4:* F5:( F6:)");
        dtext(4, 68, C_BLACK, "Digits: constants   DEL: erase");
        dtext(4, 88, C_BLACK, "Example: 3P+7 or 3*(P+7)");
        dtext(4, 119, C_BLACK, view[0] ? view : "_");
        dline(4, 139, DWIDTH - 8, 139, C_BLACK);
        dtext(4, 166, C_BLACK, "EXE: confirm   EXIT: cancel");
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

        if(digit >= 0) cipher_append_char(out, out_size, (char)('0' + digit));
        else if(key == KEY_F1) cipher_append_char(out, out_size, 'P');
        else if(key == KEY_F2) cipher_append_char(out, out_size, '+');
        else if(key == KEY_F3 || key == KEY_NEG || key == KEY_SUB) cipher_append_char(out, out_size, '-');
        else if(key == KEY_F4) cipher_append_char(out, out_size, '*');
        else if(key == KEY_F5) cipher_append_char(out, out_size, '(');
        else if(key == KEY_F6) cipher_append_char(out, out_size, ')');
        else if(key == KEY_DEL && length > 0) out[length - 1] = '\0';
        else if(key == KEY_ACON) out[0] = '\0';
        else if(key == KEY_EXE && length > 0) {
            int ok0 = 0, ok1 = 0;
            (void)cipher_eval_formula(out, 0, &ok0);
            (void)cipher_eval_formula(out, 1, &ok1);
            if(ok0 && ok1) return 1;
        }
        else if(key == KEY_EXIT || key == KEY_MENU) return 0;
    }
}

static int cipher_prompt_int(const char *title, int minimum, int maximum, int *out)
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

static int cipher_text_editor(char *out, int out_size, const char *title, int alphabet_size)
{
    int selected = 0;
    out[0] = '\0';

    while(1) {
        int length = (int)strlen(out);
        const char *view = out;
        if(length > 20) view = out + length - 20;
        char selected_text[20];
        snprintf(selected_text, sizeof(selected_text), "Selected: %c", 'A' + selected);

        dclear(C_WHITE);
        dtext(4, 3, C_BLACK, title);
        dline(0, 20, DWIDTH - 1, 20, C_BLACK);
        dtext(4, 31, C_BLACK, selected_text);
        dtext(4, 52, C_BLACK, "LEFT/RIGHT: choose letter");
        dtext(4, 72, C_BLACK, "UP/DOWN: jump 5 letters");
        dtext(4, 92, C_BLACK, "EXE: append   DEL: erase");
        dtext(4, 119, C_BLACK, view[0] ? view : "_");
        dline(4, 139, DWIDTH - 8, 139, C_BLACK);
        dtext(4, 166, C_BLACK, "F6: finish   EXIT: cancel");
        dupdate();

        int key = getkey().key;
        if(key == KEY_LEFT) selected = (selected + alphabet_size - 1) % alphabet_size;
        else if(key == KEY_RIGHT) selected = (selected + 1) % alphabet_size;
        else if(key == KEY_UP) selected = (selected + alphabet_size - (5 % alphabet_size)) % alphabet_size;
        else if(key == KEY_DOWN) selected = (selected + 5) % alphabet_size;
        else if(key == KEY_EXE && length < out_size - 1) {
            out[length] = (char)('A' + selected);
            out[length + 1] = '\0';
        }
        else if(key == KEY_DEL && length > 0) out[length - 1] = '\0';
        else if(key == KEY_ACON) out[0] = '\0';
        else if(key == KEY_F6 && length > 0) return 1;
        else if(key == KEY_EXIT || key == KEY_MENU) return 0;
    }
}

static int cipher_letter_to_code(char letter, int one_based)
{
    int index = letter - 'A';
    return one_based ? index + 1 : index;
}

static char cipher_residue_to_letter(int residue, int modulus, int one_based)
{
    int index;
    residue = cipher_mod64(residue, modulus);
    if(one_based) index = (residue == 0) ? modulus - 1 : residue - 1;
    else index = residue;
    return (char)('A' + index);
}

static void algo_cipher_formula_run(int decode)
{
    char formula[96];
    if(!cipher_formula_editor(formula, sizeof(formula))) return;

    int modulus;
    if(!cipher_prompt_int("Modulus m (2..26)", 2, 26, &modulus)) return;

    const char *conventions[] = {"A=0, B=1, ...", "A=1, B=2, ..."};
    int convention = menu_select("Letter numbering", conventions, 2);
    if(convention < 0) return;
    int one_based = (convention == 1);

    char input[24];
    if(!cipher_text_editor(input, sizeof(input),
        decode ? "Enter CIPHERTEXT" : "Enter PLAINTEXT", modulus)) return;

    TextPage page;
    page_init(&page);
    page_add(&page, decode ? "FORMULA DECODE" : "FORMULA ENCODE");
    page_addf(&page, "f(P) = %s", formula);
    page_addf(&page, "C = f(P) mod %d", modulus);
    page_add(&page, one_based ? "Letters: A=1, B=2, ..." : "Letters: A=0, B=1, ...");
    page_addf(&page, "INPUT: %s", input);
    page_add(&page, "");

    char result[24];
    int ambiguous = 0;
    int count = (int)strlen(input);
    for(int i = 0; i < count; i++) {
        int input_code = cipher_letter_to_code(input[i], one_based);
        int input_residue = cipher_mod64(input_code, modulus);

        if(!decode) {
            int ok = 0;
            int64_t raw = cipher_eval_formula(formula, input_code, &ok);
            int output_residue = ok ? cipher_mod64(raw, modulus) : 0;
            int output_code = one_based && output_residue == 0 ? modulus : output_residue;
            char output_letter = ok ? cipher_residue_to_letter(output_residue, modulus, one_based) : '?';
            result[i] = output_letter;
            if(ok) page_addf(&page, "%c(%d) -> %c(%d)", input[i], input_code,
                output_letter, output_code);
            else page_addf(&page, "%c: formula error", input[i]);
        }
        else {
            int match_count = 0;
            int matched_code = 0;
            for(int index = 0; index < modulus; index++) {
                int p_code = one_based ? index + 1 : index;
                int ok = 0;
                int64_t raw = cipher_eval_formula(formula, p_code, &ok);
                if(ok && cipher_mod64(raw, modulus) == input_residue) {
                    match_count++;
                    matched_code = p_code;
                }
            }

            if(match_count == 1) {
                char output_letter = one_based
                    ? (char)('A' + matched_code - 1)
                    : (char)('A' + matched_code);
                result[i] = output_letter;
                page_addf(&page, "%c(%d) -> %c(%d)", input[i], input_code,
                    output_letter, matched_code);
            }
            else {
                result[i] = '?';
                ambiguous = 1;
                page_addf(&page, "%c: %d possible P values", input[i], match_count);
            }
        }
    }
    result[count] = '\0';

    page_add(&page, "");
    page_addf(&page, "RESULT: %s", result);
    if(ambiguous) {
        page_add(&page, "? means no unique decoding.");
        page_add(&page, "The formula may not be one-to-one mod m.");
    }
    show_page(decode ? "Decoded result" : "Encoded result", &page);
}

static void algo_cipher_formula_guide(void)
{
    TextPage page;
    page_init(&page);
    page_add(&page, "CIPHER FORMULA SOLVER");
    page_add(&page, "");
    page_add(&page, "Order used by the app:");
    page_add(&page, "1. Choose Encode or Decode.");
    page_add(&page, "2. Enter the ENCODE formula f(P).");
    page_add(&page, "3. Enter modulus and letter numbering.");
    page_add(&page, "4. Enter the text string.");
    page_add(&page, "");
    page_add(&page, "Formula keys:");
    page_add(&page, "F1:P F2:+ F3:- F4:* F5:( F6:)");
    page_add(&page, "Supported: integers, P, +, -, *, parentheses.");
    page_add(&page, "Implicit multiply is allowed: 3P = 3*P.");
    page_add(&page, "Enter only the body before MOD.");
    page_add(&page, "");
    page_add(&page, "Examples:");
    page_add(&page, "c=(3p+7) mod 26 => enter 3P+7, m=26");
    page_add(&page, "c=3(p+7) mod 26 => enter 3(P+7), m=26");
    page_add(&page, "Caesar c=p+5 mod 26 => enter P+5");
    page_add(&page, "");
    page_add(&page, "Decode checks every possible P value.");
    page_add(&page, "So no manual modular inverse is required.");
    page_add(&page, "If decoding is not unique, RESULT shows ?.");
    show_page("Cipher formula guide", &page);
}

static void algo_cipher_formula(void)
{
    const char *items[] = {"Decode using formula", "Encode using formula", "Guide / examples"};
    while(1) {
        int choice = menu_select("Cipher formula solver", items, 3);
        if(choice < 0) return;
        if(choice == 0) algo_cipher_formula_run(1);
        else if(choice == 1) algo_cipher_formula_run(0);
        else algo_cipher_formula_guide();
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
    const char *items[]={"Insertion sort trace","Huffman bit length","Big-O reference","Prefix evaluator","Postfix evaluator","Pre/Post tips & guide","Cipher formula solver"};while(1){int c=menu_select("5. ALGORITHMS",items,7);if(c<0)return;if(c==0)algo_insertion();else if(c==1)algo_huffman();else if(c==2)algo_big_o();else if(c==3)algo_expression_evaluator(1);else if(c==4)algo_expression_evaluator(0);else if(c==5)algo_prefix_postfix_tips();else algo_cipher_formula();}
}
'''

if "Cipher formula solver" in source and "algo_cipher_formula" in source:
    print("Cipher formula solver already enabled")
else:
    if marker not in source:
        raise SystemExit("Could not find menu_algorithms insertion marker")
    if old_menu not in source:
        raise SystemExit("Could not find current menu_algorithms block")
    source = source.replace(marker, functions + marker, 1)
    source = source.replace(old_menu, new_menu, 1)
    path.write_text(source, encoding="utf-8")
    print(f"Added formula-driven cipher solver to {path}")
