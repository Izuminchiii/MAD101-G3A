#!/usr/bin/env python3
"""Add an interactive quantified-logic negation solver to the Logic menu."""
from pathlib import Path
import re
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "MAD101_G3A_Project/src/main.c")
source = path.read_text(encoding="utf-8")

if "NEGATION SOLVER - INPUT" in source:
    print("Negation solver already enabled")
    raise SystemExit(0)

menu_signature = "static void menu_logic(void)"
menu_start = source.find(menu_signature)
if menu_start < 0:
    raise SystemExit("Could not find menu_logic(void)")

open_brace = source.find("{", menu_start)
if open_brace < 0:
    raise SystemExit("Could not find opening brace of menu_logic")

depth = 0
menu_end = -1
for index in range(open_brace, len(source)):
    if source[index] == "{":
        depth += 1
    elif source[index] == "}":
        depth -= 1
        if depth == 0:
            menu_end = index + 1
            break
if menu_end < 0:
    raise SystemExit("Could not find closing brace of menu_logic")

functions = r'''/* NEGATION SOLVER - INPUT
   Calculator syntax:
   Ux = FOR ALL x, Ex = EXISTS x
   N=NOT, A=AND, O=OR, X=XOR, I=IMPLIES, B=IFF
   Example: ExUy(P(x,y)BNQ(x,y))
*/
enum {
    NEGSOLVE_ATOM = 1,
    NEGSOLVE_NOT,
    NEGSOLVE_AND,
    NEGSOLVE_OR,
    NEGSOLVE_XOR,
    NEGSOLVE_IMP,
    NEGSOLVE_IFF,
    NEGSOLVE_FORALL,
    NEGSOLVE_EXISTS
};

typedef struct {
    int type;
    int left;
    int right;
    char variable;
    char atom[24];
} NegSolveNode;

typedef struct {
    const char *text;
    int pos;
    int ok;
} NegSolveParser;

static NegSolveNode negsolve_nodes[96];
static int negsolve_node_count;

static void negsolve_skip_spaces(NegSolveParser *p)
{
    while(p->text[p->pos] == ' ') p->pos++;
}

static int negsolve_new_node(int type, int left, int right)
{
    if(negsolve_node_count >= 96) return -1;
    int index = negsolve_node_count++;
    negsolve_nodes[index].type = type;
    negsolve_nodes[index].left = left;
    negsolve_nodes[index].right = right;
    negsolve_nodes[index].variable = 0;
    negsolve_nodes[index].atom[0] = '\0';
    return index;
}

static int negsolve_parse_iff(NegSolveParser *p);

static int negsolve_parse_atom(NegSolveParser *p)
{
    negsolve_skip_spaces(p);
    char first = p->text[p->pos];
    if(first < 'P' || first > 'T') {
        p->ok = 0;
        return -1;
    }

    char atom[24];
    int length = 0;
    atom[length++] = first;
    p->pos++;
    negsolve_skip_spaces(p);

    if(p->text[p->pos] == '(') {
        int depth = 0;
        do {
            char c = p->text[p->pos];
            if(c == '\0') {
                p->ok = 0;
                return -1;
            }
            if(length >= (int)sizeof(atom) - 1) {
                p->ok = 0;
                return -1;
            }
            atom[length++] = c;
            p->pos++;
            if(c == '(') depth++;
            else if(c == ')') depth--;
        } while(depth > 0);
    }
    atom[length] = '\0';

    int node = negsolve_new_node(NEGSOLVE_ATOM, -1, -1);
    if(node < 0) {
        p->ok = 0;
        return -1;
    }
    strncpy(negsolve_nodes[node].atom, atom, sizeof(negsolve_nodes[node].atom) - 1);
    negsolve_nodes[node].atom[sizeof(negsolve_nodes[node].atom) - 1] = '\0';
    return node;
}

static int negsolve_parse_unary(NegSolveParser *p)
{
    negsolve_skip_spaces(p);
    char c = p->text[p->pos];

    if(c == 'N') {
        p->pos++;
        int child = negsolve_parse_unary(p);
        if(!p->ok) return -1;
        int node = negsolve_new_node(NEGSOLVE_NOT, child, -1);
        if(node < 0) p->ok = 0;
        return node;
    }

    if(c == 'U' || c == 'E') {
        p->pos++;
        negsolve_skip_spaces(p);
        char variable = p->text[p->pos];
        if(variable != 'x' && variable != 'y' && variable != 'z') {
            p->ok = 0;
            return -1;
        }
        p->pos++;
        int child = negsolve_parse_unary(p);
        if(!p->ok) return -1;
        int node = negsolve_new_node(c == 'U' ? NEGSOLVE_FORALL : NEGSOLVE_EXISTS,
            child, -1);
        if(node < 0) {
            p->ok = 0;
            return -1;
        }
        negsolve_nodes[node].variable = variable;
        return node;
    }

    if(c == '(') {
        p->pos++;
        int node = negsolve_parse_iff(p);
        negsolve_skip_spaces(p);
        if(p->text[p->pos] != ')') {
            p->ok = 0;
            return -1;
        }
        p->pos++;
        return node;
    }

    return negsolve_parse_atom(p);
}

static int negsolve_parse_and(NegSolveParser *p)
{
    int left = negsolve_parse_unary(p);
    while(p->ok) {
        negsolve_skip_spaces(p);
        if(p->text[p->pos] != 'A') break;
        p->pos++;
        int right = negsolve_parse_unary(p);
        if(!p->ok) return -1;
        left = negsolve_new_node(NEGSOLVE_AND, left, right);
        if(left < 0) {
            p->ok = 0;
            return -1;
        }
    }
    return left;
}

static int negsolve_parse_xor(NegSolveParser *p)
{
    int left = negsolve_parse_and(p);
    while(p->ok) {
        negsolve_skip_spaces(p);
        if(p->text[p->pos] != 'X') break;
        p->pos++;
        int right = negsolve_parse_and(p);
        if(!p->ok) return -1;
        left = negsolve_new_node(NEGSOLVE_XOR, left, right);
        if(left < 0) {
            p->ok = 0;
            return -1;
        }
    }
    return left;
}

static int negsolve_parse_or(NegSolveParser *p)
{
    int left = negsolve_parse_xor(p);
    while(p->ok) {
        negsolve_skip_spaces(p);
        if(p->text[p->pos] != 'O') break;
        p->pos++;
        int right = negsolve_parse_xor(p);
        if(!p->ok) return -1;
        left = negsolve_new_node(NEGSOLVE_OR, left, right);
        if(left < 0) {
            p->ok = 0;
            return -1;
        }
    }
    return left;
}

static int negsolve_parse_imp(NegSolveParser *p)
{
    int left = negsolve_parse_or(p);
    negsolve_skip_spaces(p);
    if(p->ok && p->text[p->pos] == 'I') {
        p->pos++;
        int right = negsolve_parse_imp(p);
        if(!p->ok) return -1;
        int node = negsolve_new_node(NEGSOLVE_IMP, left, right);
        if(node < 0) p->ok = 0;
        return node;
    }
    return left;
}

static int negsolve_parse_iff(NegSolveParser *p)
{
    int left = negsolve_parse_imp(p);
    while(p->ok) {
        negsolve_skip_spaces(p);
        if(p->text[p->pos] != 'B') break;
        p->pos++;
        int right = negsolve_parse_imp(p);
        if(!p->ok) return -1;
        left = negsolve_new_node(NEGSOLVE_IFF, left, right);
        if(left < 0) {
            p->ok = 0;
            return -1;
        }
    }
    return left;
}

static int negsolve_parse(const char *text, int *error_pos)
{
    NegSolveParser parser;
    parser.text = text;
    parser.pos = 0;
    parser.ok = 1;
    negsolve_node_count = 0;

    int root = negsolve_parse_iff(&parser);
    negsolve_skip_spaces(&parser);
    if(!parser.ok || root < 0 || parser.text[parser.pos] != '\0') {
        if(error_pos) *error_pos = parser.pos;
        return -1;
    }
    if(error_pos) *error_pos = -1;
    return root;
}

static void negsolve_append_char(char *out, int size, char c)
{
    int length = (int)strlen(out);
    if(length < size - 1) {
        out[length] = c;
        out[length + 1] = '\0';
    }
}

static void negsolve_append_text(char *out, int size, const char *text)
{
    while(*text) {
        negsolve_append_char(out, size, *text);
        text++;
    }
}

static void negsolve_emit(int node, int negate, char *out, int size)
{
    if(node < 0 || node >= negsolve_node_count) return;
    NegSolveNode *n = &negsolve_nodes[node];

    if(n->type == NEGSOLVE_ATOM) {
        if(negate) negsolve_append_char(out, size, 'N');
        negsolve_append_text(out, size, n->atom);
        return;
    }

    if(n->type == NEGSOLVE_NOT) {
        negsolve_emit(n->left, !negate, out, size);
        return;
    }

    if(n->type == NEGSOLVE_FORALL || n->type == NEGSOLVE_EXISTS) {
        int output_type = n->type;
        if(negate) {
            output_type = (n->type == NEGSOLVE_FORALL) ? NEGSOLVE_EXISTS : NEGSOLVE_FORALL;
        }
        negsolve_append_char(out, size, output_type == NEGSOLVE_FORALL ? 'U' : 'E');
        negsolve_append_char(out, size, n->variable);
        negsolve_emit(n->left, negate, out, size);
        return;
    }

    int left_negate = 0;
    int right_negate = 0;
    char op = '?';

    if(n->type == NEGSOLVE_AND) {
        op = negate ? 'O' : 'A';
        left_negate = right_negate = negate;
    }
    else if(n->type == NEGSOLVE_OR) {
        op = negate ? 'A' : 'O';
        left_negate = right_negate = negate;
    }
    else if(n->type == NEGSOLVE_XOR) {
        op = negate ? 'B' : 'X';
    }
    else if(n->type == NEGSOLVE_IFF) {
        op = negate ? 'X' : 'B';
    }
    else if(n->type == NEGSOLVE_IMP) {
        if(negate) {
            op = 'A';
            right_negate = 1;
        }
        else op = 'I';
    }

    negsolve_append_char(out, size, '(');
    negsolve_emit(n->left, left_negate, out, size);
    negsolve_append_char(out, size, op);
    negsolve_emit(n->right, right_negate, out, size);
    negsolve_append_char(out, size, ')');
}

static void negsolve_page_add_chunks(TextPage *page, const char *text)
{
    int length = (int)strlen(text);
    int start = 0;
    while(start < length) {
        char line[37];
        int count = length - start;
        if(count > 36) count = 36;
        memcpy(line, text + start, count);
        line[count] = '\0';
        page_add(page, line);
        start += count;
    }
    if(length == 0) page_add(page, "(empty)");
}

static int negsolve_editor(char *out, int out_size)
{
    out[0] = '\0';
    int page = 0;
    int error_pos = -1;

    while(1) {
        int length = (int)strlen(out);
        const char *view = out;
        if(length > 48) view = out + length - 48;
        char status[48];
        if(error_pos >= 0) snprintf(status, sizeof(status), "Invalid near position %d", error_pos + 1);
        else snprintf(status, sizeof(status), "EXE: solve   DEL: erase   AC: clear");

        dclear(C_WHITE);
        dtext(4, 3, C_BLACK, "NEGATION SOLVER - INPUT");
        dline(0, 20, DWIDTH - 1, 20, C_BLACK);
        dtext(4, 27, C_BLACK, "Syntax example:");
        dtext(4, 44, C_BLACK, "ExUy(P(x,y)BNQ(x,y))");
        dtext(4, 65, C_BLACK, view[0] ? view : "_");
        dline(4, 82, DWIDTH - 8, 82, C_BLACK);

        if(page == 0) {
            dtext(4, 94, C_BLACK, "F1:U F2:E F3:N F4:( F5:)");
        }
        else if(page == 1) {
            dtext(4, 94, C_BLACK, "F1:P F2:Q F3:R F4:x F5:y");
        }
        else if(page == 2) {
            dtext(4, 94, C_BLACK, "F1:z F2:, F3:A F4:O F5:X");
        }
        else {
            dtext(4, 94, C_BLACK, "F1:I F2:B F3:S F4:T F5:space");
        }
        dtext(4, 112, C_BLACK, "F6: next key page");
        dtext(4, 137, C_BLACK, status);
        dtext(4, 165, C_BLACK, "EXIT: cancel");
        dupdate();

        int key = getkey().key;
        char token = '\0';
        if(key == KEY_F6) {
            page = (page + 1) % 4;
            error_pos = -1;
            continue;
        }
        if(page == 0) {
            if(key == KEY_F1) token = 'U';
            else if(key == KEY_F2) token = 'E';
            else if(key == KEY_F3) token = 'N';
            else if(key == KEY_F4) token = '(';
            else if(key == KEY_F5) token = ')';
        }
        else if(page == 1) {
            if(key == KEY_F1) token = 'P';
            else if(key == KEY_F2) token = 'Q';
            else if(key == KEY_F3) token = 'R';
            else if(key == KEY_F4) token = 'x';
            else if(key == KEY_F5) token = 'y';
        }
        else if(page == 2) {
            if(key == KEY_F1) token = 'z';
            else if(key == KEY_F2) token = ',';
            else if(key == KEY_F3) token = 'A';
            else if(key == KEY_F4) token = 'O';
            else if(key == KEY_F5) token = 'X';
        }
        else {
            if(key == KEY_F1) token = 'I';
            else if(key == KEY_F2) token = 'B';
            else if(key == KEY_F3) token = 'S';
            else if(key == KEY_F4) token = 'T';
            else if(key == KEY_F5) token = ' ';
        }

        if(token) {
            negsolve_append_char(out, out_size, token);
            error_pos = -1;
        }
        else if(key == KEY_DEL && length > 0) {
            out[length - 1] = '\0';
            error_pos = -1;
        }
        else if(key == KEY_ACON) {
            out[0] = '\0';
            error_pos = -1;
        }
        else if(key == KEY_EXE && length > 0) {
            int root = negsolve_parse(out, &error_pos);
            if(root >= 0) return 1;
        }
        else if(key == KEY_EXIT || key == KEY_MENU) return 0;
    }
}

static void negsolve_show_result(const char *formula)
{
    int error_pos = -1;
    int root = negsolve_parse(formula, &error_pos);
    if(root < 0) {
        TextPage error;
        page_init(&error);
        page_add(&error, "INVALID EXPRESSION");
        page_addf(&error, "Error near position %d", error_pos + 1);
        page_add(&error, "Open Syntax guide for input rules.");
        show_page("Negation error", &error);
        return;
    }

    char result[256] = "";
    negsolve_emit(root, 1, result, sizeof(result));

    TextPage page;
    page_init(&page);
    page_add(&page, "NEGATION RESULT");
    page_add(&page, "");
    page_add(&page, "INPUT:");
    negsolve_page_add_chunks(&page, formula);
    page_add(&page, "");
    page_add(&page, "NEGATION:");
    negsolve_page_add_chunks(&page, result);
    page_add(&page, "");
    page_add(&page, "Legend: U=FOR ALL, E=EXISTS");
    page_add(&page, "N=NOT A=AND O=OR X=XOR");
    page_add(&page, "I=IMPLIES B=IFF");
    show_page("Negation result", &page);
}

static void negsolve_syntax_guide(void)
{
    TextPage page;
    page_init(&page);
    page_add(&page, "NEGATION SOLVER SYNTAX");
    page_add(&page, "");
    page_add(&page, "Quantifiers:");
    page_add(&page, "Ux = FOR ALL x");
    page_add(&page, "Ex = EXISTS x");
    page_add(&page, "Variables supported: x, y, z");
    page_add(&page, "");
    page_add(&page, "Connectives:");
    page_add(&page, "N NOT, A AND, O OR, X XOR");
    page_add(&page, "I implication, B biconditional");
    page_add(&page, "");
    page_add(&page, "Atoms: P, Q, R, S, T");
    page_add(&page, "Arguments may be added: P(x,y)");
    page_add(&page, "");
    page_add(&page, "Example from the review:");
    page_add(&page, "ExUy(P(x,y)BNQ(x,y))");
    page_add(&page, "Negation produced:");
    page_add(&page, "UxEy(P(x,y)XNQ(x,y))");
    page_add(&page, "");
    page_add(&page, "Operator priority:");
    page_add(&page, "N/quantifier, A, X, O, I, B");
    page_add(&page, "Use parentheses when unsure.");
    show_page("Negation syntax", &page);
}

static void logic_negation_solver(void)
{
    const char *items[] = {
        "Enter expression",
        "Load exam example",
        "Syntax guide"
    };

    while(1) {
        int choice = menu_select("Negation solver", items, 3);
        if(choice < 0) return;
        if(choice == 0) {
            char formula[128];
            if(negsolve_editor(formula, sizeof(formula))) negsolve_show_result(formula);
        }
        else if(choice == 1) {
            negsolve_show_result("ExUy(P(x,y)BNQ(x,y))");
        }
        else negsolve_syntax_guide();
    }
}

'''

source = source[:menu_start] + functions + source[menu_start:]
menu_start += len(functions)
menu_end += len(functions)
menu_text = source[menu_start:menu_end]

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
new_body += '"Negation solver (input)"'
menu_text = (
    menu_text[:items_match.start("body")]
    + new_body
    + menu_text[items_match.end("body"):]
)

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
    f"else logic_negation_solver();"
)
menu_text = menu_text[:last_else.start()] + replacement + menu_text[last_else.end():]

source = source[:menu_start] + menu_text + source[menu_end:]
path.write_text(source, encoding="utf-8")
print(f"Added interactive negation solver to {path}")
