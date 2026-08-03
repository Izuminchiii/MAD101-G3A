#!/usr/bin/env python3
"""Add a graph-types glossary to the MAD101 fx-CG50 add-in."""
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "MAD101_G3A_Project/src/main.c")
source = path.read_text(encoding="utf-8")

marker = "static void graph_special(void)\n"
function = r'''static void graph_types_reference(void)
{
    TextPage p;
    page_init(&p);

    page_add(&p, "BASIC GRAPH TYPES");
    page_add(&p, "Simple graph: no loops and no parallel edges.");
    page_add(&p, "Multigraph: parallel edges are allowed.");
    page_add(&p, "Pseudograph: loops and parallel edges may occur.");
    page_add(&p, "Undirected graph: edges have no direction.");
    page_add(&p, "Directed graph: edges are arrows.");
    page_add(&p, "Weighted graph: each edge has a cost or weight.");
    page_add(&p, "Connected graph: every pair of vertices has a path.");
    page_add(&p, "Regular graph: all vertices have the same degree.");

    page_add(&p, "");
    page_add(&p, "SPECIAL GRAPHS");
    page_add(&p, "Complete K_n: every pair of vertices is adjacent.");
    page_add(&p, "Complement G': same vertices; missing edges of G.");
    page_add(&p, "Path P_n: vertices form one open chain.");
    page_add(&p, "Cycle C_n: vertices form one closed cycle.");
    page_add(&p, "Bipartite: vertices split into two parts; edges cross parts.");
    page_add(&p, "Complete bipartite K_m,n: every cross-part pair is joined.");
    page_add(&p, "Wheel W_n: cycle C_n plus one hub (course convention).");
    page_add(&p, "Hypercube Q_n: binary strings of length n; differ in one bit.");

    page_add(&p, "");
    page_add(&p, "TREES");
    page_add(&p, "Tree: connected and has no cycle.");
    page_add(&p, "Spanning tree: tree containing every graph vertex.");
    page_add(&p, "Minimum spanning tree: spanning tree with minimum total weight.");

    page_add(&p, "");
    page_add(&p, "QUICK FORMULAS");
    page_add(&p, "K_n: E=n(n-1)/2, degree=n-1");
    page_add(&p, "K_m,n: E=mn");
    page_add(&p, "P_n: E=n-1");
    page_add(&p, "C_n: E=n, degree=2");
    page_add(&p, "W_n(course): V=n+1, E=2n");
    page_add(&p, "Q_n: V=2^n, E=n*2^(n-1)");
    page_add(&p, "Tree: E=V-1");

    show_page("Graph types reference", &p);
}

'''

old_menu = '''static void menu_graph(void)
{
    const char *items[]={"Special graph formulas","Euler + graphical degrees","Full m-ary tree","Hamilton / spanning counts","Adjacency matrix walks","Dijkstra shortest paths","Prim minimum spanning tree"};while(1){int c=menu_select("4. GRAPHS / TREES",items,7);if(c<0)return;if(c==0)graph_special();else if(c==1)graph_euler();else if(c==2)graph_mary();else if(c==3)graph_counts();else if(c==4)graph_walks();else if(c==5)graph_dijkstra();else graph_prim();}
}
'''

new_menu = '''static void menu_graph(void)
{
    const char *items[]={"Graph types reference","Special graph formulas","Euler + graphical degrees","Full m-ary tree","Hamilton / spanning counts","Adjacency matrix walks","Dijkstra shortest paths","Prim minimum spanning tree"};while(1){int c=menu_select("4. GRAPHS / TREES",items,8);if(c<0)return;if(c==0)graph_types_reference();else if(c==1)graph_special();else if(c==2)graph_euler();else if(c==3)graph_mary();else if(c==4)graph_counts();else if(c==5)graph_walks();else if(c==6)graph_dijkstra();else graph_prim();}
}
'''

if "Graph types reference" in source:
    print("Graph types reference already enabled")
else:
    if marker not in source:
        raise SystemExit("Could not find graph_special insertion marker")
    if old_menu not in source:
        raise SystemExit("Could not find original menu_graph block")
    source = source.replace(marker, function + marker, 1)
    source = source.replace(old_menu, new_menu, 1)
    path.write_text(source, encoding="utf-8")
    print(f"Added graph-types reference to {path}")
