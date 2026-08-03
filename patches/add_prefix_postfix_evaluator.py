#!/usr/bin/env python3
"""Add interactive prefix/postfix evaluators to the MAD101 fx-CG50 add-in."""
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "MAD101_G3A_Project/src/main.c")
source = path.read_text(encoding="utf-8")

marker = "static void algo_prefix_postfix(void)\n"
functions = r'''static void expr_add_operator(char *expr, int size, char op)
{
    int len = (int)strlen(expr);
    while(len > 0 && expr[len - 1] == ' ') expr[--len] = '\0';
    if(len > 0 && len < size - 1) expr[len++] = ' ';
    if(len < size - 1) expr[len++] = op;
    if(len < size - 1) expr[len++] = ' ';
    expr[len] = '\0';
}

static void expr_add_digit(char *expr, int size, int digit)
{
    int len = (int)strlen(expr);
    if(len < size - 1) {
        expr[len++] = (char)('0' + digit);
        expr[len] = '\0';
    }
}

static void expr_finish_token(char *expr, int size)
{
    int len = (int)strlen(expr);
    if(len > 0 && expr[len - 1] != ' ' && len < size - 1) {
        expr[len++] = ' ';
        expr[len] = '\0';
    }
}

static void expr_toggle_negative(char *expr, int size)
{
    int len = (int)strlen(expr);
    while(len > 0 && expr[len - 1] == ' ') len--;
    int start = len;
    while(start > 0 && expr[start - 1] != ' ') start--;
    if(start < len && expr[start] == '-') {
        memmove(expr + start, expr + start + 1, strlen(expr + start + 1) + 1);
    } else if(start < len && len < size - 1) {
        memmove(expr + start + 1, expr + start, strlen(expr + start) + 1);
        expr[start] = '-';
    } else if(start == len && len < size - 1) {
        expr[len++] = '-';
        expr[len] = '\0';
    }
}

static int arithmetic_expression_editor(char *out, int out_size, const char *title)
{
    out[0] = '\0';
    while(1) {
        int len = (int)strlen(out);
        const char *view = out;
        if(len > 42) view = out + len - 42;

        dclear(C_WHITE);
        dtext(4, 3, C_BLACK, title);
        dline(0, 20, DWIDTH - 1, 20, C_BLACK);
        dtext(4, 29, C_BLACK, "Enter tokens separated by spaces");
        dtext(4, 49, C_BLACK, "F1:+ F2:- F3:* F4:/ F5:^");
        dtext(4, 69, C_BLACK, "Digits:number  EXE:end token");
        dtext(4, 89, C_BLACK, "(-):negative  DEL:erase AC:clear");
        dtext(4, 119, C_BLACK, view);
        dline(4, 139, DWIDTH - 8, 139, C_BLACK);
        dtext(4, 166, C_BLACK, "F6 evaluate    EXIT back");
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

        if(digit >= 0) expr_add_digit(out, out_size, digit);
        else if(key == KEY_F1) expr_add_operator(out, out_size, '+');
        else if(key == KEY_F2) expr_add_operator(out, out_size, '-');
        else if(key == KEY_F3) expr_add_operator(out, out_size, '*');
        else if(key == KEY_F4) expr_add_operator(out, out_size, '/');
        else if(key == KEY_F5) expr_add_operator(out, out_size, '^');
        else if(key == KEY_EXE) expr_finish_token(out, out_size);
        else if(key == KEY_NEG || key == KEY_SUB) expr_toggle_negative(out, out_size);
        else if(key == KEY_DEL && len > 0) out[len - 1] = '\0';
        else if(key == KEY_ACON) out[0] = '\0';
        else if(key == KEY_F6 && len > 0) {
            while(len > 0 && out[len - 1] == ' ') out[--len] = '\0';
            return len > 0;
        }
        else if(key == KEY_EXIT || key == KEY_MENU) return 0;
    }
}

static void algo_expression_evaluator(int prefix)
{
    char expr[192];
    if(!arithmetic_expression_editor(expr, sizeof(expr),
        prefix ? "Prefix evaluator" : "Postfix evaluator")) return;

    int64_t result = 0;
    int ok = prefix ? mad_eval_prefix(expr, &result)
                    : mad_eval_postfix(expr, &result);
    TextPage p;
    page_init(&p);
    page_addf(&p, "%s: %s", prefix ? "Prefix" : "Postfix", expr);
    page_add(&p, "");
    if(ok) page_addf(&p, "RESULT = %lld", (long long)result);
    else {
        page_add(&p, "Invalid expression or arithmetic error.");
        page_add(&p, "Use spaces between every token.");
        page_add(&p, "Operators supported: + - * / ^");
        page_add(&p, "Examples:");
        page_add(&p, "Prefix:  - * 3 4 5");
        page_add(&p, "Postfix: 3 4 * 5 -");
    }
    show_page(prefix ? "Prefix result" : "Postfix result", &p);
}

'''

old_menu = '''static void menu_algorithms(void)
{
    const char *items[]={"Insertion sort trace","Huffman bit length","Big-O reference","Prefix/postfix guide"};while(1){int c=menu_select("5. ALGORITHMS",items,4);if(c<0)return;if(c==0)algo_insertion();else if(c==1)algo_huffman();else if(c==2)algo_big_o();else algo_prefix_postfix();}
}
'''

new_menu = '''static void menu_algorithms(void)
{
    const char *items[]={"Insertion sort trace","Huffman bit length","Big-O reference","Prefix evaluator","Postfix evaluator","Prefix/postfix guide"};while(1){int c=menu_select("5. ALGORITHMS",items,6);if(c<0)return;if(c==0)algo_insertion();else if(c==1)algo_huffman();else if(c==2)algo_big_o();else if(c==3)algo_expression_evaluator(1);else if(c==4)algo_expression_evaluator(0);else algo_prefix_postfix();}
}
'''

if "Prefix evaluator" in source and "algo_expression_evaluator" in source:
    print("Prefix/postfix evaluators already enabled")
else:
    if marker not in source:
        raise SystemExit("Could not find prefix/postfix insertion marker")
    if old_menu not in source:
        raise SystemExit("Could not find original menu_algorithms block")
    source = source.replace(marker, functions + marker, 1)
    source = source.replace(old_menu, new_menu, 1)
    path.write_text(source, encoding="utf-8")
    print(f"Added prefix/postfix evaluators to {path}")
