#!/usr/bin/env python3
"""Add an interactive K_m,n Hamilton/path/spanning-tree reference."""
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "MAD101_G3A_Project/src/main.c")
source = path.read_text(encoding="utf-8")

marker = "static void graph_special(void)\n"
functions = r'''static long long kmn_power(int base, int exponent)
{
    long long result = 1;
    for(int i = 0; i < exponent; i++) result *= base;
    return result;
}

static void graph_kmn_check(void)
{
    int m, n;
    if(!base_prompt_int("K_m,n: enter m (1..10)", 1, 10, &m)) return;
    if(!base_prompt_int("K_m,n: enter n (1..10)", 1, 10, &n)) return;

    int difference = m > n ? m - n : n - m;
    int hamilton_circuit = (m == n && m >= 2);
    int hamilton_path = (difference <= 1);
    int odd_vertices = 0;
    if(n % 2 != 0) odd_vertices += m;
    if(m % 2 != 0) odd_vertices += n;

    long long trees = kmn_power(m, n - 1) * kmn_power(n, m - 1);

    TextPage page;
    page_init(&page);
    page_addf(&page, "COMPLETE BIPARTITE K_%d,%d", m, n);
    page_add(&page, "");
    page_addf(&page, "Vertices = %d", m + n);
    page_addf(&page, "Edges = m*n = %d", m * n);
    page_addf(&page, "%d vertices have degree %d", m, n);
    page_addf(&page, "%d vertices have degree %d", n, m);
    page_add(&page, "");

    page_addf(&page, "Hamilton circuit: %s", hamilton_circuit ? "YES" : "NO");
    page_add(&page, "Rule: m=n and m,n >= 2.");
    page_addf(&page, "Hamilton path: %s", hamilton_path ? "YES" : "NO");
    page_add(&page, "Rule: |m-n| <= 1.");
    page_add(&page, "Reason: a bipartite path alternates parts.");
    page_add(&page, "");

    page_addf(&page, "Spanning trees = %lld", trees);
    page_add(&page, "Formula: m^(n-1) * n^(m-1).");
    page_add(&page, "");

    page_addf(&page, "Odd-degree vertices = %d", odd_vertices);
    if(odd_vertices == 0) page_add(&page, "Euler: circuit (and path).");
    else if(odd_vertices == 2) page_add(&page, "Euler: path only, no circuit.");
    else page_add(&page, "Euler: no path and no circuit.");

    show_page("K_m,n checker", &page);
}

static void graph_kmn_guide(void)
{
    TextPage page;
    page_init(&page);
    page_add(&page, "COMPLETE BIPARTITE K_m,n");
    page_add(&page, "");
    page_add(&page, "The vertices are split into two parts:");
    page_add(&page, "one has m vertices, the other has n.");
    page_add(&page, "Every edge joins opposite parts.");
    page_add(&page, "");
    page_add(&page, "QUICK FORMULAS");
    page_add(&page, "Vertices: m+n");
    page_add(&page, "Edges: mn");
    page_add(&page, "Degrees: m vertices degree n;");
    page_add(&page, "         n vertices degree m.");
    page_add(&page, "Spanning trees: m^(n-1)n^(m-1)");
    page_add(&page, "");
    page_add(&page, "HAMILTON");
    page_add(&page, "Circuit iff m=n>=2.");
    page_add(&page, "Path iff |m-n|<=1.");
    page_add(&page, "Memory trick: every move switches part,");
    page_add(&page, "so a circuit uses equal numbers from both.");
    page_add(&page, "");
    page_add(&page, "EXAM EXAMPLE");
    page_add(&page, "Find all m,n such that K_m,n has");
    page_add(&page, "a Hamilton circuit.");
    page_add(&page, "Answer: m=n and m,n>=2.");
    page_add(&page, "Smallest example: K_2,2 = C_4.");
    page_add(&page, "K_2,3 has a Hamilton path but no circuit.");
    show_page("K_m,n guide", &page);
}

static void graph_kmn_tool(void)
{
    const char *items[] = {
        "Enter m,n and check",
        "Rules / exam example"
    };
    while(1) {
        int choice = menu_select("K_m,n tools", items, 2);
        if(choice < 0) return;
        if(choice == 0) graph_kmn_check();
        else graph_kmn_guide();
    }
}

'''

old_menu = '''static void menu_graph(void)
{
    const char *items[]={"Graph types reference","Special graph formulas","Euler + graphical degrees","Full m-ary tree","Hamilton / spanning counts","Adjacency matrix walks","Dijkstra shortest paths","Prim minimum spanning tree"};while(1){int c=menu_select("4. GRAPHS / TREES",items,8);if(c<0)return;if(c==0)graph_types_reference();else if(c==1)graph_special();else if(c==2)graph_euler();else if(c==3)graph_mary();else if(c==4)graph_counts();else if(c==5)graph_walks();else if(c==6)graph_dijkstra();else graph_prim();}
}
'''

new_menu = '''static void menu_graph(void)
{
    const char *items[]={"Graph types reference","Special graph formulas","Euler + graphical degrees","Full m-ary tree","Hamilton / spanning counts","K_m,n Hamilton / trees","Adjacency matrix walks","Dijkstra shortest paths","Prim minimum spanning tree"};while(1){int c=menu_select("4. GRAPHS / TREES",items,9);if(c<0)return;if(c==0)graph_types_reference();else if(c==1)graph_special();else if(c==2)graph_euler();else if(c==3)graph_mary();else if(c==4)graph_counts();else if(c==5)graph_kmn_tool();else if(c==6)graph_walks();else if(c==7)graph_dijkstra();else graph_prim();}
}
'''

if "K_m,n Hamilton / trees" in source and "graph_kmn_tool" in source:
    print("K_m,n tool already enabled")
else:
    if marker not in source:
        raise SystemExit("Could not find graph_special insertion marker")
    if old_menu not in source:
        raise SystemExit("Could not find graph menu after graph-types patch")
    source = source.replace(marker, functions + marker, 1)
    source = source.replace(old_menu, new_menu, 1)
    path.write_text(source, encoding="utf-8")
    print(f"Added complete bipartite tool to {path}")
