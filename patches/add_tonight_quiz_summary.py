#!/usr/bin/env python3
"""Add the unique MAD101 questions reviewed on 2026-08-03/04 to the answer-first quiz bank."""
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "MAD101_G3A_Project/src/main.c")
source = path.read_text(encoding="utf-8")

QUESTIONS = [
    ("Recurrence", "If f(1)=4 and f(n)=f(n-1)*n, find f(5).", ["120", "240", "360", "480"], 3, "f(5)=4*2*3*4*5=480."),
    ("Recurrence", "T(n)=3 for n<3; T(n)=n for even n; otherwise T(n)=3T(n-1)-2. Find T(9).", ["22", "25", "27", "9"], 0, "8 is even, so T(8)=8. Hence T(9)=3*8-2=22."),
    ("Recurrence", "S starts with (0,0). From (a,b), add (a+2,b+3) or (a+3,b+2). Which is in S?", ["(7,8)", "(6,7)", "(8,9)", "(5,10)"], 0, "Use two (+2,+3) steps and one (+3,+2) step: (0,0)->(2,3)->(4,6)->(7,8)."),
    ("Recurrence", "f(0)=2 and f(n+1)=f(n)^2+2f(n)-3. Find f(3).", ["32", "15", "1085", "93"], 2, "f(1)=5, f(2)=32, and f(3)=32^2+64-3=1085."),
    ("Recurrence", "The sum of the first n positive even integers equals which expression?", ["n(n+1)", "(n+1)^2", "(n-1)^2", "2n^2"], 0, "2+4+...+2n=2(1+...+n)=n(n+1)."),
    ("Number", "Find gcd(899,941).", ["13", "17", "31", "1"], 3, "Euclid: 941=899+42, 899=21*42+17, 42=2*17+8, 17=2*8+1."),
    ("Number", "Convert hexadecimal (2BE0) to binary.", ["0010101111100000", "0010101011100000", "0011101111100000", "0010101111000000"], 0, "Convert each hex digit to 4 bits: 2=0010, B=1011, E=1110, 0=0000."),
    ("Number", "Find gcd(2^3*3^2*5*7, 2^4*5^2*11^3).", ["2310", "40", "120", "360"], 1, "Take common primes with minimum exponents: 2^3*5=40."),
    ("Number", "The prime factorization of 1025 is p^2*q. Find q-p.", ["36", "46", "11", "66"], 0, "1025=25*41=5^2*41, so q-p=41-5=36."),
    ("Algorithm", "x0=1 and x[n+1]=(3x[n]+4) mod 7. Find x3.", ["7", "4", "2", "16"], 2, "x1=0, x2=4, x3=2."),
    ("Logic", "A truth table has outputs T,F,T,F for rows TT,TF,FT,FF. Which proposition matches?", ["not p AND q", "q OR (not p AND q)", "p", "p XOR q"], 1, "The output column is exactly q; q OR (not p AND q) simplifies to q."),
    ("Logic", "Evaluate (101101 OR 110001) XOR 001101.", ["101100", "110000", "001101", "111101"], 1, "The OR is 111101; XOR with 001101 gives 110000."),
    ("Logic", "Simplify (p -> q) OR ((not p) -> q).", ["q", "F", "p", "T"], 3, "Replace implications: (not p OR q) OR (p OR q)=T."),
    ("Logic", "All students either play badminton or know Java, but not both. Which form is correct?", ["for all x: C(x) AND (P(x) OR J(x))", "for all x: C(x) -> (P(x) OR J(x))", "for all x: C(x) -> (P(x) XOR J(x))", "exists x: C(x) AND (P(x) XOR J(x))"], 2, "All people are quantified; being a student implies exactly one of P and J."),
    ("Logic", "P(x): born in Hanoi; Q(x): visited the Temple of Literature. Express: every Hanoi-born person visited it.", ["exists x (P(x) AND Q(x))", "for all x (P(x) -> Q(x))", "exists x (P(x) -> Q(x))", "for all x (P(x) AND Q(x))"], 1, "Universal conditional: every person satisfying P must satisfy Q."),
    ("Logic", "For integers, P(x,y) means x+2y=5. Which statement is true?", ["exists y P(2,y)", "for all x exists y P(x,y)", "for all y exists x P(x,y)", "for all x for all y P(x,y)"], 2, "For every integer y, choose x=5-2y, which is an integer."),
    ("Logic", "Negate: exists x exists y [F(x,y) AND for all z L(y,z)].", ["exists x exists y [not F OR exists z not L]", "for all x for all y [not F AND exists z not L]", "for all x for all y [not F OR exists z not L]", "for all x exists y [not F OR for all z not L]"], 2, "Change exists to for all, then De Morgan: not F OR exists z not L."),
    ("Logic", "If sick then not in class. Which argument is valid?", ["Not in class, therefore sick", "Not sick, therefore in class", "In class, therefore not sick", "All three"], 2, "This is modus tollens: S->not C and C imply not S."),
    ("Sets", "What is the power set of {empty,a}?", ["{empty,{a},{empty,a}}", "{empty,{empty},{a},{empty,a}}", "{empty,{a},{empty},{a,{empty}}}", "{empty,{empty,a}}"], 1, "A 2-element set has 4 subsets: empty, each singleton, and the whole set."),
    ("Sets", "For U={a,b,c,d,e,f,g,h,i,j}, which bit string represents {a,c,d,g,h,j}?", ["1011101110", "1011011110", "1011001011", "1011001101"], 3, "Write 1 at a,c,d,g,h,j and 0 elsewhere: 1011001101."),
    ("Sets", "X={1,2,3,4,5}, Y={0,3,6,9}. Which has minimum cardinality?", ["X intersect Y", "X-Y", "Y-X", "X union Y"], 0, "X intersect Y={3} has size 1; the others have sizes 4,3,8."),
    ("Sets", "Which rule defines a function from R to Z?", ["g(x)=ceil(x+pi)", "f(x)=1/floor(x)", "h(x)=sqrt(x^2+1)", "All three"], 0, "ceil(x+pi) is defined for every real x and always gives an integer."),
    ("Sets", "Which identity is false for arbitrary real x,y?", ["floor(ceil(x))=ceil(x)", "ceil(floor(x))=floor(x)", "floor(xy)=floor(x)floor(y)", "The first two"], 2, "Floor does not distribute over multiplication; for example x=y=1.5."),
    ("Recurrence", "List the first five terms of a_n=2^n-n! for n=0,1,2,3,4.", ["0,1,2,2,-18", "0,1,2,3,-8", "1,1,2,2,-8", "0,1,2,2,-8"], 3, "Substitution gives 0,1,2,2,-8."),
    ("Algorithm", "Which loop is an algorithm: n increases forever, division reaches zero, n increases forever, or divide then decrement?", ["Increase n while n>0", "Divide after decrementing n", "Multiply and increase n", "Divide by n, then decrement n"], 3, "Only the last loop terminates and never divides by zero."),
    ("Algorithm", "Insertion sort starts 7,2,4,3,1,6,5. What is the list after outer-loop i=4?", ["2,3,4,7,1,6,5", "2,4,7,3,1,6,5", "2,4,7,1,3,6,5", "1,2,3,4,7,6,5"], 0, "After inserting 2,4,3, the first four entries are 2,3,4,7."),
    ("Algorithm", "If f=O(log n), g=O(1), h=O(n), estimate f^3+(g+2)h.", ["O(log n)", "O(n)", "O(n log n)", "O(n^2)"], 1, "(log n)^3 grows slower than n, while (g+2)h=O(n)."),
    ("Algorithm", "An algorithm uses 2^(n^2) operations, each 10^-12 s. Largest n solvable in one second?", ["6", "7", "39", "40"], 0, "Need n^2<=log2(10^12)≈39.86, so n<=6."),
    ("Algorithm", "x0=3 and x_n=(5x_(n-1)+4) mod 7. Find x4.", ["6", "4", "2", "0"], 3, "x1=5, x2=1, x3=2, x4=0."),
    ("Graph", "A connected graph has vertex degrees 2,3,2,2,3. What Euler property does it have?", ["Euler path but no Euler circuit", "Euler circuit", "No Euler path", "Both impossible to determine"], 0, "Exactly two vertices have odd degree, so there is an Euler path but no circuit."),
    ("Algorithm", "Binary search [2,4,5,7,8,9,10,13] for 6. After the second division, which sublist remains?", ["5,7,8", "2,4,5", "5,7", "7,8,9"], 2, "First compare with 7, then 4; the remaining indices contain 5 and 7."),
    ("Recurrence", "Which procedure is recursive: one calls A(b,n div 2), while the other uses only a for-loop?", ["Only the self-calling procedure", "Neither", "Only the loop procedure", "Both"], 0, "A recursive procedure calls itself; a loop alone is iterative."),
    ("Graph", "A weighted graph has edges AB2, AC6, BC8, BD3, BE3, CE4, DE4, DZ2, EZ3. MST weight?", ["12", "13", "15", "14"], 3, "One MST uses AB2, BD3, DZ2, BE3, CE4, totaling 14."),
    ("Graph", "A graph G has 8 edges and its complement has 2 edges. How many vertices does G have?", ["5", "6", "7", "8"], 0, "Together G and its complement form K_n: n(n-1)/2=10, so n=5."),
    ("Tree", "Convert [5+((1+2)*4)]-3 to postfix notation.", ["5 1 2 + 4 * + 3 -", "- 3 + * 4 + 2 1 5", "+ 5 * + 1 2 4 - 3", "5 1 + 2 4 * 3 - +"], 0, "Postorder places each operator after its operands."),
    ("Counting", "How many length-4 decimal strings have exactly two zero digits?", ["486", "560", "600", "810"], 0, "Choose the two zero positions in C(4,2)=6 ways; other digits have 9 choices each: 6*9^2=486."),
    ("Number", "f(p)=(3p+7) mod 26 encrypts a message as BXMF. What was the original message?", ["HELP", "GIUP", "YOTI", "SAVE"], 2, "The inverse of 3 mod 26 is 9. Decode p=9(c-7) mod 26 to get YOTI."),
    ("Number", "Find the binary expansion of (204)_5.", ["1110100", "110110", "1101110", "1110110"], 1, "(204)_5=2*25+4=54, and 54=(110110)_2."),
    ("Recurrence", "Give a recursive definition for a_n=5n, n>=1.", ["a0=0; a_n=a_(n-1)+5 for n>=1", "a1=1; a_n=a_(n-1)+5 for n>=2", "a1=5; a_(n-1)=a_n+5", "a1=5; a_n=a_(n-1)+5 for n>=2"], 3, "Start with a1=5 and add 5 to obtain every next term."),
    ("Algorithm", "How many comparisons merge [2,3,5,6,8,21] and [1,4,7]?", ["5", "6", "7", "8"], 2, "Compare until the second list is exhausted: 7 comparisons; append the remaining items without comparison."),
    ("Recurrence", "In induction for 1^2+...+n^2=n(n+1)(2n+1)/6, what is added in the k+1 step?", ["k^2+1", "2k+1", "(k+1)^2", "k^2"], 2, "The next sum is the induction-hypothesis sum through k plus (k+1)^2."),
    ("Logic", "p=pass, q=grade above 5, r=submit by deadline. Translate: r and q, but not p.", ["q AND r AND not p", "(q AND r) -> not p", "q OR r OR not p", "not(q AND r AND p)"], 0, "The word 'but' acts as AND, and 'did not pass' is not p."),
    ("Counting", "A 20-team soccer tournament has every pair play twice. How many games?", ["40", "400", "380", "190"], 2, "There are C(20,2)=190 pairs and two games per pair: 380."),
    ("Graph", "Two graphs have the same adjacency after relabeling A->7,B->4,C->3,D->6,E->5,F->2,G->1. Are they isomorphic?", ["Yes", "No", "Only if weighted", "Not enough vertices"], 0, "The relabeling preserves every edge, so it is an isomorphism."),
    ("Graph", "Two 4-cycles are connected by one bridge edge. How many spanning trees?", ["14", "16", "20", "18"], 1, "The bridge is mandatory. Each C4 has 4 spanning trees, so 4*4=16."),
    ("Sets", "U={0,1,2,3,4,5,6,7,8,9}. Which subset is represented by 0101010101?", ["{1,2,3,5,7}", "{1,3,5,7,9}", "{0,1,2,5,9}", "{0,2,4,6,8}"], 1, "Take the universe elements at positions containing 1."),
    ("Sets", "Which statements are true: a in {a}; {a} in {a}; a subseteq {a,b}; {a,b} in {a,b,c,d}; empty subseteq {empty}; empty x {a}=empty?", ["1,4,6", "1,5,6", "1,2,3", "2,3,5"], 1, "Membership and subset are different; empty is a subset of every set, and an empty Cartesian factor gives empty."),
    ("Sets", "For f:N->N, f(x)=x^2+4, how is f classified?", ["Bijection", "One-to-one only", "Onto only", "Neither"], 1, "On N it is strictly increasing, hence injective, but values such as 1,2,3 are never produced."),
    ("Tree", "Huffman probabilities are .30,.15,.25,.20,.10. What is the average code length?", ["2.25", "3.05", "2.75", "3.15"], 0, "Merge 10+15, 20+25, 25+30, 45+55. Weighted path length is 225/100=2.25."),
    ("Graph", "Which adjacency matrix has exactly 8 ones?", ["W4", "Q4", "K4", "C4"], 3, "For a simple undirected graph, the number of ones is 2|E|. C4 has 4 edges, hence 8 ones."),
    ("Sets", "Nonempty A,B,C satisfy A x B subseteq B x C. What follows?", ["A subseteq B subseteq C", "B subseteq C subseteq A", "C subseteq B subseteq A", "No inclusion follows"], 0, "Compare first coordinates to get A subseteq B and second coordinates to get B subseteq C."),
]


def c_escape(text: str) -> str:
    return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

marker = "static int quiz_filter_count(const char *filter)\n"
if marker not in source:
    raise SystemExit("Run enable_quiz_review.py before this patch")

if "MAD_TONIGHT_QUIZ" not in source:
    entries = []
    for category, question, choices, answer, explain in QUESTIONS:
        choice_text = ", ".join(f'\"{c_escape(x)}\"' for x in choices)
        entries.append(
            "    { .category=\"%s\", .question=\"%s\", .choice={%s}, .answer=%d, .explain=\"%s\" },"
            % (c_escape(category), c_escape(question), choice_text, answer, c_escape(explain))
        )
    block = "static const MadQuizQuestion MAD_TONIGHT_QUIZ[] = {\n" + "\n".join(entries) + "\n};\n"
    block += "#define MAD_TONIGHT_QUIZ_COUNT ((int)(sizeof(MAD_TONIGHT_QUIZ)/sizeof(MAD_TONIGHT_QUIZ[0])))\n\n"
    source = source.replace(marker, block + marker, 1)

old_count = '''static int quiz_filter_count(const char *filter)
{
    int n = 0;
    for(int i = 0; i < MAD_QUIZ_COUNT; i++) {
        if(quiz_category_match(MAD_QUIZ[i].category, filter)) n++;
    }
    return n;
}
'''
new_count = '''static int quiz_filter_count(const char *filter)
{
    int n = 0;
    for(int i = 0; i < MAD_QUIZ_COUNT; i++) {
        if(quiz_category_match(MAD_QUIZ[i].category, filter)) n++;
    }
    for(int i = 0; i < MAD_TONIGHT_QUIZ_COUNT; i++) {
        if(quiz_category_match(MAD_TONIGHT_QUIZ[i].category, filter)) n++;
    }
    return n;
}

static const MadQuizQuestion *quiz_review_get(const char *filter, int position)
{
    int seen = 0;
    for(int i = 0; i < MAD_QUIZ_COUNT; i++) {
        if(!quiz_category_match(MAD_QUIZ[i].category, filter)) continue;
        if(seen++ == position) return &MAD_QUIZ[i];
    }
    for(int i = 0; i < MAD_TONIGHT_QUIZ_COUNT; i++) {
        if(!quiz_category_match(MAD_TONIGHT_QUIZ[i].category, filter)) continue;
        if(seen++ == position) return &MAD_TONIGHT_QUIZ[i];
    }
    return NULL;
}
'''
if old_count in source:
    source = source.replace(old_count, new_count, 1)
elif "quiz_review_get" not in source:
    raise SystemExit("Could not extend quiz_filter_count")

old_pick = '''        int idx = quiz_pick(filter, 0, pos);
        if(idx < 0) return;
        int command = quiz_review_screen(&MAD_QUIZ[idx], pos, total);'''
new_pick = '''        const MadQuizQuestion *q = quiz_review_get(filter, pos);
        if(q == NULL) return;
        int command = quiz_review_screen(q, pos, total);'''
if old_pick in source:
    source = source.replace(old_pick, new_pick, 1)
elif "quiz_review_screen(q, pos, total)" not in source:
    raise SystemExit("Could not switch review mode to combined quiz bank")

menu_start = source.find("static void quiz_menu(void)\n{")
if menu_start < 0:
    raise SystemExit("Could not find quiz_menu")
menu_end = source.find("\n}\n", menu_start)
if menu_end < 0:
    raise SystemExit("Could not find end of quiz_menu")
menu_end += 3
new_menu = r'''static void quiz_tonight_review_run(void)
{
    int pos = 0;
    while(1) {
        int command = quiz_review_screen(&MAD_TONIGHT_QUIZ[pos], pos, MAD_TONIGHT_QUIZ_COUNT);
        if(command == 0) return;
        pos = command > 0 ? (pos + 1) % MAD_TONIGHT_QUIZ_COUNT
                          : (pos + MAD_TONIGHT_QUIZ_COUNT - 1) % MAD_TONIGHT_QUIZ_COUNT;
    }
}

static void quiz_menu(void)
{
    const char *items[]={
        "Review ALL - answer shown",
        "Review TONIGHT summary",
        "Review Logic",
        "Review Sets",
        "Review Number",
        "Review Algorithm",
        "Review Counting",
        "Review Recurrence",
        "Review Graph",
        "Review Tree",
        "Practice random (original)"
    };
    const char *filters[]={"Logic","Sets","Number","Algorithm","Counting","Recurrence","Graph","Tree"};
    while(1) {
        int c = menu_select("7. QUIZ BANK + TONIGHT", items, 11);
        if(c < 0) return;
        if(c == 0) quiz_review_run("");
        else if(c == 1) quiz_tonight_review_run();
        else if(c >= 2 && c <= 9) quiz_review_run(filters[c-2]);
        else quiz_run("", 1);
    }
}
'''
source = source[:menu_start] + new_menu + source[menu_end:]

path.write_text(source, encoding="utf-8")
print(f"Added {len(QUESTIONS)} reviewed questions to the combined quiz bank")
