#!/usr/bin/env python3
# Add a sorted-list merge comparison counter to the MAD101 fx-CG50 add-in.
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "MAD101_G3A_Project/src/main.c")
source = path.read_text(encoding="utf-8")

marker = "static void menu_algorithms(void)\n"

functions = r'''static int merge_prompt_int(const char *title, int *out)
{
    char buffer[14] = "";
    int length = 0;
    int negative = 0;

    while(1) {
        char display[20];
        if(length == 0) snprintf(display, sizeof(display), "%s_", negative ? "-" : "");
        else snprintf(display, sizeof(display), "%s%s", negative ? "-" : "", buffer);

        dclear(C_WHITE);
        dtext(4, 4, C_BLACK, title);
        dline(0, 22, DWIDTH - 1, 22, C_BLACK);
        dtext(4, 42, C_BLACK, display);
        dtext(4, 76, C_BLACK, "Digits: input   F1: +/-");
        dtext(4, 96, C_BLACK, "DEL: erase     AC: clear");
        dtext(4, 116, C_BLACK, "EXE: confirm   EXIT: cancel");
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
        else if(key == KEY_F1) negative = !negative;
        else if(key == KEY_DEL && length > 0) buffer[--length] = '\0';
        else if(key == KEY_ACON) {
            length = 0;
            negative = 0;
            buffer[0] = '\0';
        }
        else if(key == KEY_EXE && length > 0) {
            int value = 0;
            for(int i = 0; i < length; i++) value = value * 10 + (buffer[i] - '0');
            *out = negative ? -value : value;
            return 1;
        }
        else if(key == KEY_EXIT || key == KEY_MENU) return 0;
    }
}

static int merge_is_sorted(const int *values, int count)
{
    for(int i = 1; i < count; i++) if(values[i] < values[i - 1]) return 0;
    return 1;
}

static void merge_add_array_line(TextPage *page, const char *label, const int *values, int count)
{
    char line[96];
    int used = snprintf(line, sizeof(line), "%s[", label);
    for(int i = 0; i < count && used < (int)sizeof(line) - 2; i++) {
        used += snprintf(line + used, sizeof(line) - (size_t)used,
            "%s%d", i ? "," : "", values[i]);
    }
    snprintf(line + used, sizeof(line) - (size_t)used, "]");
    page_add(page, line);
}

static void algo_merge_counter_run(void)
{
    int n, m;
    if(!base_prompt_int("Length of list A (1..12)", 1, 12, &n)) return;
    if(!base_prompt_int("Length of list B (1..12)", 1, 12, &m)) return;

    int a[12], b[12], merged[24];
    char title[36];

    for(int i = 0; i < n; i++) {
        snprintf(title, sizeof(title), "A[%d] (ascending)", i + 1);
        if(!merge_prompt_int(title, &a[i])) return;
    }
    for(int i = 0; i < m; i++) {
        snprintf(title, sizeof(title), "B[%d] (ascending)", i + 1);
        if(!merge_prompt_int(title, &b[i])) return;
    }

    TextPage page;
    page_init(&page);
    page_add(&page, "MERGE COMPARISON COUNTER");
    page_add(&page, "");
    merge_add_array_line(&page, "A=", a, n);
    merge_add_array_line(&page, "B=", b, m);
    page_add(&page, "");

    if(!merge_is_sorted(a, n) || !merge_is_sorted(b, m)) {
        page_add(&page, "Input error: both lists must already");
        page_add(&page, "be sorted in ascending order.");
        page_add(&page, "The app does not silently sort them.");
        show_page("Merge counter", &page);
        return;
    }

    int i = 0, j = 0, k = 0, comparisons = 0;
    while(i < n && j < m) {
        int left = a[i];
        int right = b[j];
        comparisons++;
        if(left <= right) {
            merged[k++] = left;
            page_addf(&page, "%d) %d vs %d -> take %d (A)",
                comparisons, left, right, left);
            i++;
        }
        else {
            merged[k++] = right;
            page_addf(&page, "%d) %d vs %d -> take %d (B)",
                comparisons, left, right, right);
            j++;
        }
    }

    int copied_without_comparison = 0;
    while(i < n) {
        merged[k++] = a[i++];
        copied_without_comparison++;
    }
    while(j < m) {
        merged[k++] = b[j++];
        copied_without_comparison++;
    }

    page_add(&page, "");
    page_addf(&page, "COMPARISONS = %d", comparisons);
    page_addf(&page, "Maximum possible = %d", n + m - 1);
    if(copied_without_comparison > 0)
        page_addf(&page, "Copied after one list ended = %d", copied_without_comparison);
    page_add(&page, "");
    merge_add_array_line(&page, "Merged=", merged, k);
    show_page("Merge counter", &page);
}

static void algo_merge_counter_guide(void)
{
    TextPage page;
    page_init(&page);
    page_add(&page, "MERGING TWO SORTED LISTS");
    page_add(&page, "");
    page_add(&page, "Compare only the first unused value");
    page_add(&page, "of each list. Move the smaller one.");
    page_add(&page, "Each such check counts as 1 comparison.");
    page_add(&page, "");
    page_add(&page, "When one list becomes empty, copy all");
    page_add(&page, "remaining values. No more comparisons.");
    page_add(&page, "");
    page_add(&page, "Exam example:");
    page_add(&page, "A=[2,3,5,6,8,21]");
    page_add(&page, "B=[1,4,7]");
    page_add(&page, "Checks: 2v1,2v4,3v4,5v4,");
    page_add(&page, "5v7,6v7,8v7 = 7 comparisons.");
    page_add(&page, "Then append 8 and 21 directly.");
    page_add(&page, "Answer: 7.");
    page_add(&page, "");
    page_add(&page, "Quick bound for lengths n and m:");
    page_add(&page, "minimum = min(n,m)");
    page_add(&page, "maximum = n+m-1");
    show_page("Merge guide", &page);
}

static void algo_merge_counter(void)
{
    const char *items[] = {"Enter two sorted lists", "Guide / exam example"};
    while(1) {
        int choice = menu_select("Merge comparisons", items, 2);
        if(choice < 0) return;
        if(choice == 0) algo_merge_counter_run();
        else algo_merge_counter_guide();
    }
}

'''

old_menu = '''static void menu_algorithms(void)
{
    const char *items[]={"Insertion sort trace","Huffman bit length","Big-O reference","Prefix evaluator","Postfix evaluator","Pre/Post tips & guide","Cipher formula solver","Base converter"};while(1){int c=menu_select("5. ALGORITHMS",items,8);if(c<0)return;if(c==0)algo_insertion();else if(c==1)algo_huffman();else if(c==2)algo_big_o();else if(c==3)algo_expression_evaluator(1);else if(c==4)algo_expression_evaluator(0);else if(c==5)algo_prefix_postfix_tips();else if(c==6)algo_cipher_formula();else algo_base_converter();}
}
'''

new_menu = '''static void menu_algorithms(void)
{
    const char *items[]={"Insertion sort trace","Huffman bit length","Big-O reference","Prefix evaluator","Postfix evaluator","Pre/Post tips & guide","Cipher formula solver","Base converter","Merge comparison counter"};while(1){int c=menu_select("5. ALGORITHMS",items,9);if(c<0)return;if(c==0)algo_insertion();else if(c==1)algo_huffman();else if(c==2)algo_big_o();else if(c==3)algo_expression_evaluator(1);else if(c==4)algo_expression_evaluator(0);else if(c==5)algo_prefix_postfix_tips();else if(c==6)algo_cipher_formula();else if(c==7)algo_base_converter();else algo_merge_counter();}
}
'''

if "Merge comparison counter" in source and "algo_merge_counter" in source:
    print("Merge comparison counter already enabled")
else:
    if marker not in source:
        raise SystemExit("Could not find menu_algorithms insertion marker")
    if old_menu not in source:
        raise SystemExit("Could not find algorithms menu after base converter patch")
    source = source.replace(marker, functions + marker, 1)
    source = source.replace(old_menu, new_menu, 1)
    path.write_text(source, encoding="utf-8")
    print(f"Added merge comparison counter to {path}")
