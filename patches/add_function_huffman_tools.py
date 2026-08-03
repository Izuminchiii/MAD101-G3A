#!/usr/bin/env python3
# Add a domain/codomain-aware function classifier and a Huffman average-bit solver.
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "MAD101_G3A_Project/src/main.c")
source = path.read_text(encoding="utf-8")
marker = "static void menu_algorithms(void)\n"

functions = r'''enum {
    FN_N0 = 0,
    FN_N1 = 1,
    FN_Z  = 2,
    FN_Q  = 3,
    FN_R  = 4
};

static const char *fn_set_name(int set_id)
{
    static const char *names[] = {
        "N0={0,1,2,...}",
        "N+={1,2,3,...}",
        "Z (integers)",
        "Q (rationals)",
        "R (reals)"
    };
    return names[set_id];
}

static int fn_choose_set(const char *title)
{
    const char *items[] = {
        "N0 = {0,1,2,...}",
        "N+ = {1,2,3,...}",
        "Z = integers",
        "Q = rational numbers",
        "R = real numbers"
    };
    return menu_select(title, items, 5);
}

static int fn_natural_start(int set_id)
{
    if(set_id == FN_N0) return 0;
    if(set_id == FN_N1) return 1;
    return -1000000000;
}

static long long fn_eval_poly(int qa, int lb, int c, long long x)
{
    return (long long)qa * x * x + (long long)lb * x + (long long)c;
}

static long long fn_floor_div(long long numerator, long long denominator)
{
    long long q = numerator / denominator;
    long long r = numerator % denominator;
    if(r != 0 && ((r > 0) != (denominator > 0))) q--;
    return q;
}

static long long fn_quad_min_from(int qa, int lb, int c, int start)
{
    long long best = fn_eval_poly(qa, lb, c, start);
    if(qa <= 0) return best;

    long long den = 2LL * qa;
    long long q = fn_floor_div(-(long long)lb, den);
    for(long long x = q - 2; x <= q + 2; x++) {
        if(x < start) continue;
        long long value = fn_eval_poly(qa, lb, c, x);
        if(value < best) best = value;
    }
    return best;
}

static long long fn_quad_min_z(int qa, int lb, int c)
{
    long long den = 2LL * qa;
    long long q = fn_floor_div(-(long long)lb, den);
    long long best = fn_eval_poly(qa, lb, c, q);
    for(long long x = q - 2; x <= q + 2; x++) {
        long long value = fn_eval_poly(qa, lb, c, x);
        if(value < best) best = value;
    }
    return best;
}

static int fn_constant_in_codomain(int value, int codomain)
{
    if(codomain == FN_N0) return value >= 0;
    if(codomain == FN_N1) return value >= 1;
    return 1;
}

static int fn_well_defined(int domain, int codomain, int qa, int lb, int c)
{
    int degree = qa != 0 ? 2 : (lb != 0 ? 1 : 0);

    if(codomain == FN_R) return 1;
    if(codomain == FN_Q) {
        if(domain != FN_R) return 1;
        return degree == 0;
    }
    if(codomain == FN_Z) {
        if(domain == FN_N0 || domain == FN_N1 || domain == FN_Z) return 1;
        return degree == 0;
    }

    int lower = fn_natural_start(codomain);
    if(degree == 0) return c >= lower;
    if(domain == FN_Q || domain == FN_R) return 0;

    if(domain == FN_Z) {
        if(degree == 1) return 0;
        if(qa < 0) return 0;
        return fn_quad_min_z(qa, lb, c) >= lower;
    }

    int start = fn_natural_start(domain);
    if(degree == 1) {
        if(lb < 0) return 0;
        return fn_eval_poly(0, lb, c, start) >= lower;
    }
    if(qa < 0) return 0;
    return fn_quad_min_from(qa, lb, c, start) >= lower;
}

static int fn_is_injective(int domain, int qa, int lb)
{
    int degree = qa != 0 ? 2 : (lb != 0 ? 1 : 0);
    if(degree == 0) return 0;
    if(degree == 1) return 1;

    if(domain == FN_Q || domain == FN_R) return 0;

    if((-(long long)lb) % (long long)qa != 0) return 1;
    long long symmetric_sum = (-(long long)lb) / (long long)qa;

    if(domain == FN_Z) return 0;
    int start = fn_natural_start(domain);
    long long smallest_distinct_sum = 2LL * start + 1;
    return symmetric_sum < smallest_distinct_sum;
}

static int fn_is_onto(int domain, int codomain, int qa, int lb, int c)
{
    int degree = qa != 0 ? 2 : (lb != 0 ? 1 : 0);
    if(degree != 1) return 0;

    int slope = lb;
    int intercept = c;
    if(domain == FN_R && codomain == FN_R) return slope != 0;
    if(domain == FN_Q && codomain == FN_Q) return slope != 0;
    if(domain == FN_Z && codomain == FN_Z)
        return slope == 1 || slope == -1;

    if((domain == FN_N0 || domain == FN_N1) &&
       (codomain == FN_N0 || codomain == FN_N1)) {
        int d0 = fn_natural_start(domain);
        int c0 = fn_natural_start(codomain);
        return slope == 1 && intercept == c0 - d0;
    }
    return 0;
}

static void fn_add_formula(TextPage *page, int qa, int lb, int c)
{
    if(qa != 0)
        page_addf(page, "f(x)=%d*x^2 %+d*x %+d", qa, lb, c);
    else
        page_addf(page, "f(x)=%d*x %+d", lb, c);
}

static void fn_analyzer_run(void)
{
    int domain = fn_choose_set("Choose DOMAIN first");
    if(domain < 0) return;
    int codomain = fn_choose_set("Choose CODOMAIN");
    if(codomain < 0) return;

    const char *forms[] = {
        "Linear: a*x + b",
        "Quadratic: a*x^2 + b*x + c"
    };
    int form = menu_select("Choose formula type", forms, 2);
    if(form < 0) return;

    int qa = 0, lb = 0, c = 0;
    if(form == 0) {
        if(!ux_prompt_int("FUNCTION 1/2", "a in f(x)=a*x+b",
            "Use a nonzero a for a linear function", -1000, 1000, &lb)) return;
        if(!ux_prompt_int("FUNCTION 2/2", "b in f(x)=a*x+b",
            "This is the constant term", -1000, 1000, &c)) return;
    }
    else {
        if(!ux_prompt_int("FUNCTION 1/3", "a in a*x^2+b*x+c",
            "Quadratic coefficient", -1000, 1000, &qa)) return;
        if(!ux_prompt_int("FUNCTION 2/3", "b in a*x^2+b*x+c",
            "Linear coefficient", -1000, 1000, &lb)) return;
        if(!ux_prompt_int("FUNCTION 3/3", "c in a*x^2+b*x+c",
            "Constant term", -1000, 1000, &c)) return;
    }

    int well = fn_well_defined(domain, codomain, qa, lb, c);
    int injective = well ? fn_is_injective(domain, qa, lb) : 0;
    int onto = well ? fn_is_onto(domain, codomain, qa, lb, c) : 0;

    TextPage page;
    page_init(&page);
    page_add(&page, "FUNCTION CLASSIFIER");
    page_add(&page, "");
    page_addf(&page, "Domain:   %s", fn_set_name(domain));
    page_addf(&page, "Codomain: %s", fn_set_name(codomain));
    fn_add_formula(&page, qa, lb, c);
    page_add(&page, "");

    if(!well) {
        page_add(&page, "RESULT: NOT A FUNCTION D -> C");
        page_add(&page, "Some domain input produces a value");
        page_add(&page, "outside the selected codomain.");
        page_add(&page, "Change the codomain or formula.");
        show_page("Function result", &page);
        return;
    }

    page_addf(&page, "One-to-one (injective): %s", injective ? "YES" : "NO");
    page_addf(&page, "Onto (surjective):      %s", onto ? "YES" : "NO");
    page_add(&page, "");
    if(injective && onto) page_add(&page, "CLASSIFICATION: BIJECTION");
    else if(injective) page_add(&page, "CLASSIFICATION: ONE-TO-ONE ONLY");
    else if(onto) page_add(&page, "CLASSIFICATION: ONTO ONLY");
    else page_add(&page, "CLASSIFICATION: NEITHER");

    page_add(&page, "");
    if(qa != 0) {
        if(injective)
            page_add(&page, "No distinct selected-domain inputs");
        else
            page_add(&page, "Distinct inputs can share one output");
        page_add(&page, "because f(x)=f(y) uses x+y=-b/a.");
        page_add(&page, "A genuine quadratic is not onto any");
        page_add(&page, "standard infinite codomain listed here.");
    }
    else if(lb != 0) {
        page_add(&page, "A nonconstant linear rule is injective.");
        if(domain == FN_Z && codomain == FN_Z)
            page_add(&page, "It is onto Z only when |a|=1.");
        else if((domain == FN_N0 || domain == FN_N1) &&
                (codomain == FN_N0 || codomain == FN_N1))
            page_add(&page, "Natural-set onto requires slope 1");
        else
            page_add(&page, "Onto depends on domain and codomain.");
    }
    else page_add(&page, "A constant rule is neither on infinite sets.");

    show_page("Function result", &page);
}

static void fn_analyzer_guide(void)
{
    TextPage page;
    page_init(&page);
    page_add(&page, "1-1 / ONTO: SETS MATTER");
    page_add(&page, "");
    page_add(&page, "Always choose DOMAIN and CODOMAIN first.");
    page_add(&page, "The same formula may get a different answer.");
    page_add(&page, "");
    page_add(&page, "Exam image example:");
    page_add(&page, "f:N0->N0, f(x)=x^2+4");
    page_add(&page, "On N0 it is one-to-one, but not onto.");
    page_add(&page, "Answer: ONE-TO-ONE.");
    page_add(&page, "");
    page_add(&page, "Change domain to Z:");
    page_add(&page, "f:Z->Z, x^2+4 is not one-to-one");
    page_add(&page, "because f(x)=f(-x); it is not onto.");
    page_add(&page, "Answer: NEITHER.");
    page_add(&page, "");
    page_add(&page, "Other quick examples:");
    page_add(&page, "R->R, 2x+3: BIJECTION");
    page_add(&page, "Z->Z, 2x+1: 1-1, not onto");
    page_add(&page, "N0->N+, x+1: BIJECTION");
    page_add(&page, "");
    page_add(&page, "This tool uses N0={0,1,...} and also");
    page_add(&page, "offers N+={1,2,...} separately.");
    show_page("Function guide", &page);
}

static void fn_analyzer_tool(void)
{
    const char *items[] = {
        "Analyze a function",
        "Guide / exam examples"
    };
    while(1) {
        int choice = menu_select("Function 1-1 / onto", items, 2);
        if(choice < 0) return;
        if(choice == 0) fn_analyzer_run();
        else fn_analyzer_guide();
    }
}

static int huff_pick_min(const int *weights, const int *active, int count, int skip)
{
    int best = -1;
    for(int i = 0; i < count; i++) {
        if(!active[i] || i == skip) continue;
        if(best < 0 || weights[i] < weights[best] ||
           (weights[i] == weights[best] && i < best)) best = i;
    }
    return best;
}

static void huff_average_run(int probability_mode)
{
    int n;
    if(!ux_prompt_int("HUFFMAN INPUT", "Number of symbols (2..12)",
        probability_mode ? "Example has A,B,C,D,E: enter 5" : "Enter number of frequencies",
        2, 12, &n)) return;

    int original[12];
    for(int i = 0; i < n; i++) {
        char section[32];
        char field[48];
        snprintf(section, sizeof(section), "HUFFMAN %d / %d", i + 1, n);
        snprintf(field, sizeof(field), "Weight for symbol %d", i + 1);
        if(!ux_prompt_int(section, field,
            probability_mode ? "Use 0.30 -> 30, 0.15 -> 15" : "Enter a positive integer frequency",
            1, 1000000, &original[i])) return;
    }

    int weights[24] = {0};
    unsigned int masks[24] = {0};
    int active[24] = {0};
    int depth[12] = {0};
    int total_weight = 0;

    for(int i = 0; i < n; i++) {
        weights[i] = original[i];
        masks[i] = 1u << i;
        active[i] = 1;
        total_weight += original[i];
    }

    TextPage page;
    page_init(&page);
    page_add(&page, "HUFFMAN AVERAGE BITS");
    page_add(&page, "");
    if(probability_mode) {
        page_add(&page, "Decimal probabilities were scaled.");
        page_add(&page, "Example: 0.30 entered as 30.");
    }
    else page_add(&page, "Using integer frequencies.");
    page_addf(&page, "Symbols=%d, total weight=%d", n, total_weight);
    page_add(&page, "");

    int node_count = n;
    int active_count = n;
    int merge_cost = 0;
    int merge_number = 1;

    while(active_count > 1) {
        int p = huff_pick_min(weights, active, node_count, -1);
        int q = huff_pick_min(weights, active, node_count, p);
        int sum = weights[p] + weights[q];
        unsigned int combined = masks[p] | masks[q];

        page_addf(&page, "%d) merge %d + %d = %d",
            merge_number++, weights[p], weights[q], sum);
        merge_cost += sum;

        for(int leaf = 0; leaf < n; leaf++)
            if(combined & (1u << leaf)) depth[leaf]++;

        active[p] = 0;
        active[q] = 0;
        weights[node_count] = sum;
        masks[node_count] = combined;
        active[node_count] = 1;
        node_count++;
        active_count--;
    }

    int hundredths = (merge_cost * 100 + total_weight / 2) / total_weight;
    int whole = hundredths / 100;
    int frac = hundredths % 100;

    page_add(&page, "");
    page_addf(&page, "Weighted bit total = %d", merge_cost);
    page_addf(&page, "AVERAGE = %d.%02d bits/symbol", whole, frac);
    page_add(&page, "");
    for(int i = 0; i < n; i++)
        page_addf(&page, "S%d: weight=%d, code length=%d", i + 1, original[i], depth[i]);
    page_add(&page, "");
    page_add(&page, "Tie choices may swap codewords, but the");
    page_add(&page, "optimal average length stays the same.");
    show_page("Huffman result", &page);
}

static void huff_average_guide(void)
{
    TextPage page;
    page_init(&page);
    page_add(&page, "HUFFMAN AVERAGE GUIDE");
    page_add(&page, "");
    page_add(&page, "Repeatedly merge the two smallest weights.");
    page_add(&page, "The sum of ALL merge results equals the");
    page_add(&page, "weighted total number of bits.");
    page_add(&page, "Average = merge total / total weight.");
    page_add(&page, "");
    page_add(&page, "Exam image example:");
    page_add(&page, "A=.30 B=.15 C=.25 D=.20 E=.10");
    page_add(&page, "Enter weights: 30,15,25,20,10");
    page_add(&page, "Merges: 10+15=25");
    page_add(&page, "        20+25=45");
    page_add(&page, "        25+30=55");
    page_add(&page, "        45+55=100");
    page_add(&page, "Merge total=25+45+55+100=225");
    page_add(&page, "Total weight=100");
    page_add(&page, "Average=225/100=2.25 bits");
    page_add(&page, "Answer: 2.25");
    show_page("Huffman guide", &page);
}

static void huff_average_tool(void)
{
    const char *items[] = {
        "Probabilities (0.30 -> 30)",
        "Integer frequencies",
        "Guide / exam example"
    };
    while(1) {
        int choice = menu_select("Huffman average bits", items, 3);
        if(choice < 0) return;
        if(choice == 0) huff_average_run(1);
        else if(choice == 1) huff_average_run(0);
        else huff_average_guide();
    }
}

'''

old_menu = '''static void menu_algorithms(void)
{
    const char *items[]={"Insertion sort trace","Huffman bit length","Big-O reference","Prefix evaluator","Postfix evaluator","Pre/Post tips & guide","Cipher formula solver","Base converter","Merge comparison counter","Bit string / subset","LCG clear step-by-step"};while(1){int c=menu_select("5. ALGORITHMS",items,11);if(c<0)return;if(c==0)algo_insertion();else if(c==1)algo_huffman();else if(c==2)algo_big_o();else if(c==3)algo_expression_evaluator(1);else if(c==4)algo_expression_evaluator(0);else if(c==5)algo_prefix_postfix_tips();else if(c==6)algo_cipher_formula();else if(c==7)algo_base_converter();else if(c==8)algo_merge_counter();else if(c==9)ux_bitstring_tool();else ux_lcg_tool();}
}
'''

new_menu = '''static void menu_algorithms(void)
{
    const char *items[]={"Insertion sort trace","Huffman bit length","Big-O reference","Prefix evaluator","Postfix evaluator","Pre/Post tips & guide","Cipher formula solver","Base converter","Merge comparison counter","Bit string / subset","LCG clear step-by-step","Function 1-1 / onto","Huffman average bits"};while(1){int c=menu_select("5. ALGORITHMS",items,13);if(c<0)return;if(c==0)algo_insertion();else if(c==1)algo_huffman();else if(c==2)algo_big_o();else if(c==3)algo_expression_evaluator(1);else if(c==4)algo_expression_evaluator(0);else if(c==5)algo_prefix_postfix_tips();else if(c==6)algo_cipher_formula();else if(c==7)algo_base_converter();else if(c==8)algo_merge_counter();else if(c==9)ux_bitstring_tool();else if(c==10)ux_lcg_tool();else if(c==11)fn_analyzer_tool();else huff_average_tool();}
}
'''

if "Function 1-1 / onto" in source and "Huffman average bits" in source:
    print("Function and Huffman average tools already enabled")
else:
    if marker not in source:
        raise SystemExit("Could not find menu_algorithms insertion marker")
    if old_menu not in source:
        raise SystemExit("Could not find algorithms menu after LCG patch")
    source = source.replace(marker, functions + marker, 1)
    source = source.replace(old_menu, new_menu, 1)
    path.write_text(source, encoding="utf-8")
    print(f"Added function classifier and Huffman average solver to {path}")
