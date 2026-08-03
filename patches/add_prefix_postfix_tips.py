#!/usr/bin/env python3
"""Add a detailed prefix/postfix exam tips reference to the MAD101 add-in."""
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "MAD101_G3A_Project/src/main.c")
source = path.read_text(encoding="utf-8")

marker = "static void menu_algorithms(void)\n"
function = r'''static void algo_prefix_postfix_tips(void)
{
    TextPage p;
    page_init(&p);

    page_add(&p, "PREFIX / POSTFIX QUICK TIPS");
    page_add(&p, "");
    page_add(&p, "1. BASIC ORDER");
    page_add(&p, "Infix:   LEFT operator RIGHT");
    page_add(&p, "Prefix:  operator LEFT RIGHT");
    page_add(&p, "Postfix: LEFT RIGHT operator");
    page_add(&p, "Memory: PRE=sign first; POST=sign last.");

    page_add(&p, "");
    page_add(&p, "2. TREE TRAVERSAL");
    page_add(&p, "Prefix  = Root, Left, Right (NLR)");
    page_add(&p, "Infix   = Left, Root, Right (LNR)");
    page_add(&p, "Postfix = Left, Right, Root (LRN)");

    page_add(&p, "");
    page_add(&p, "3. CONVERT INFIX INSIDE-OUT");
    page_add(&p, "Start with the innermost parentheses.");
    page_add(&p, "For every block A op B:");
    page_add(&p, "Prefix  => op A B");
    page_add(&p, "Postfix => A B op");
    page_add(&p, "Treat each converted block as one unit.");

    page_add(&p, "");
    page_add(&p, "Example 1: (1+2)*4");
    page_add(&p, "Prefix:  * + 1 2 4");
    page_add(&p, "Postfix: 1 2 + 4 *");

    page_add(&p, "");
    page_add(&p, "Example 2: [5+((1+2)*4)]-3");
    page_add(&p, "Prefix:  - + 5 * + 1 2 4 3");
    page_add(&p, "Postfix: 5 1 2 + 4 * + 3 -");
    page_add(&p, "Value: 14");

    page_add(&p, "");
    page_add(&p, "4. EVALUATE PREFIX");
    page_add(&p, "Scan from RIGHT to LEFT.");
    page_add(&p, "Number: push onto the stack.");
    page_add(&p, "Operator: pop LEFT, then RIGHT.");
    page_add(&p, "Compute LEFT op RIGHT, then push.");

    page_add(&p, "");
    page_add(&p, "5. EVALUATE POSTFIX");
    page_add(&p, "Scan from LEFT to RIGHT.");
    page_add(&p, "Number: push onto the stack.");
    page_add(&p, "Operator: pop RIGHT first, then LEFT.");
    page_add(&p, "Compute LEFT op RIGHT, then push.");

    page_add(&p, "");
    page_add(&p, "6. FAST RECOGNITION");
    page_add(&p, "Whole prefix usually starts with an operator.");
    page_add(&p, "Whole postfix usually ends with an operator.");
    page_add(&p, "No parentheses are needed in prefix/postfix.");

    page_add(&p, "");
    page_add(&p, "7. COMMON TRAPS");
    page_add(&p, "Order matters for subtraction and division.");
    page_add(&p, "Postfix: first pop is RIGHT operand.");
    page_add(&p, "Prefix: first pop is LEFT operand.");
    page_add(&p, "Separate every number/operator by a space.");
    page_add(&p, "A negative number is one token, e.g. -5.");
    page_add(&p, "Do not calculate while only converting form.");

    page_add(&p, "");
    page_add(&p, "8. APP INPUT KEYS");
    page_add(&p, "F1:+  F2:-  F3:*  F4:/  F5:^");
    page_add(&p, "EXE ends a number token; F6 evaluates.");
    page_add(&p, "Use Prefix/Postfix evaluator to verify.");

    show_page("Pre/Post tips & guide", &p);
}

'''

old_menu = '''static void menu_algorithms(void)
{
    const char *items[]={"Insertion sort trace","Huffman bit length","Big-O reference","Prefix evaluator","Postfix evaluator","Prefix/postfix guide"};while(1){int c=menu_select("5. ALGORITHMS",items,6);if(c<0)return;if(c==0)algo_insertion();else if(c==1)algo_huffman();else if(c==2)algo_big_o();else if(c==3)algo_expression_evaluator(1);else if(c==4)algo_expression_evaluator(0);else algo_prefix_postfix();}
}
'''

new_menu = '''static void menu_algorithms(void)
{
    const char *items[]={"Insertion sort trace","Huffman bit length","Big-O reference","Prefix evaluator","Postfix evaluator","Pre/Post tips & guide"};while(1){int c=menu_select("5. ALGORITHMS",items,6);if(c<0)return;if(c==0)algo_insertion();else if(c==1)algo_huffman();else if(c==2)algo_big_o();else if(c==3)algo_expression_evaluator(1);else if(c==4)algo_expression_evaluator(0);else algo_prefix_postfix_tips();}
}
'''

if "PREFIX / POSTFIX QUICK TIPS" in source:
    print("Prefix/postfix tips already enabled")
else:
    if marker not in source:
        raise SystemExit("Could not find menu_algorithms insertion marker")
    if old_menu not in source:
        raise SystemExit("Could not find evaluator-enabled menu_algorithms block")
    source = source.replace(marker, function + marker, 1)
    source = source.replace(old_menu, new_menu, 1)
    path.write_text(source, encoding="utf-8")
    print(f"Added prefix/postfix tips to {path}")
