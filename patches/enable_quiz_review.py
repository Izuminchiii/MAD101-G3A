#!/usr/bin/env python3
"""Enable an answer-first review mode in the MAD101 quiz bank."""
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "MAD101_G3A_Project/src/main.c")
source = path.read_text(encoding="utf-8")

old = '''static void quiz_menu(void)
{
    const char *items[]={"Random all categories","Logic","Sets","Number","Algorithm","Counting","Recurrence","Graph","Tree"};const char *filters[]={"","Logic","Sets","Number","Algorithm","Counting","Recurrence","Graph","Tree"};while(1){int c=menu_select("7. QUIZ BANK (106 unique)",items,9);if(c<0)return;quiz_run(filters[c],1);}
}
'''

new = r'''static int quiz_filter_count(const char *filter)
{
    int n = 0;
    for(int i = 0; i < MAD_QUIZ_COUNT; i++) {
        if(quiz_category_match(MAD_QUIZ[i].category, filter)) n++;
    }
    return n;
}

/* Review mode shows the correct answer and explanation immediately. */
static int quiz_review_screen(const MadQuizQuestion *q, int position, int total)
{
    TextPage p;
    page_init(&p);
    page_add(&p, q->question);
    page_add(&p, "");
    for(int i = 0; i < 4; i++) page_addf(&p, "%c. %s", 'A' + i, q->choice[i]);
    page_add(&p, "");
    page_addf(&p, "CORRECT: %c. %s", 'A' + q->answer, q->choice[q->answer]);
    page_add(&p, "");
    page_add(&p, q->explain);

    int top = 0;
    const int visible = 11;
    while(1) {
        dclear(C_WHITE);
        char title[64];
        snprintf(title, sizeof(title), "REVIEW %s  %d/%d", q->category, position + 1, total);
        dtext(4, 3, C_BLACK, title);
        dline(0, 20, DWIDTH - 1, 20, C_BLACK);
        for(int i = 0; i < visible && top + i < p.count; i++) {
            dtext(4, 25 + i * LINE_H, C_BLACK, p.line[top + i]);
        }
        dline(0, DHEIGHT - 18, DWIDTH - 1, DHEIGHT - 18, C_BLACK);
        dtext(4, DHEIGHT - 15, C_BLACK, "EXE/F6 next F5 prev EXIT back");
        dupdate();
        int key = getkey().key;
        if(key == KEY_EXIT || key == KEY_MENU) return 0;
        if(key == KEY_EXE || key == KEY_F6) return 1;
        if(key == KEY_F5) return -1;
        if(key == KEY_UP && top > 0) top--;
        if(key == KEY_DOWN && top + visible < p.count) top++;
    }
}

static void quiz_review_run(const char *filter)
{
    int total = quiz_filter_count(filter);
    if(total <= 0) return;
    int pos = 0;
    while(1) {
        int idx = quiz_pick(filter, 0, pos);
        if(idx < 0) return;
        int command = quiz_review_screen(&MAD_QUIZ[idx], pos, total);
        if(command == 0) return;
        pos = command > 0 ? (pos + 1) % total : (pos + total - 1) % total;
    }
}

static void quiz_menu(void)
{
    const char *items[]={
        "Review ALL - answer shown",
        "Review Logic",
        "Review Sets",
        "Review Number",
        "Review Algorithm",
        "Review Counting",
        "Review Recurrence",
        "Review Graph",
        "Review Tree",
        "Practice random (F1-F4)"
    };
    const char *filters[]={"","Logic","Sets","Number","Algorithm","Counting","Recurrence","Graph","Tree"};
    while(1) {
        int c = menu_select("7. QUIZ BANK (106 unique)", items, 10);
        if(c < 0) return;
        if(c < 9) quiz_review_run(filters[c]);
        else quiz_run("", 1);
    }
}
'''

if "Review ALL - answer shown" in source:
    print("Quiz review mode already enabled")
elif old not in source:
    raise SystemExit("Could not find the original quiz_menu block")
else:
    path.write_text(source.replace(old, new), encoding="utf-8")
    print(f"Enabled answer-first quiz review mode in {path}")
