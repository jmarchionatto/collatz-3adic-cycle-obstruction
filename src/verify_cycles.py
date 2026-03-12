from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple

# ------------------------------------------------------------
# Verification of the graph constraints appearing in the paper
#
# This script reads the graphs previously constructed by:
#
#   - build_G3.py
#   - build_G4.py
#
# and verifies the computational statements used in the paper:
#
#   1. For G_3:
#      the only strongly connected components containing directed
#      cycles are the 18 constant loops (a,a,a).
#
#   2. For each G_r:
#      the only strongly connected components containing directed
#      cycles are the 3 constant loops (a,a,a,a).
#
# The script uses Tarjan's algorithm to compute strongly connected
# components (SCCs) directly, without external graph libraries.
# ------------------------------------------------------------

Node3 = Tuple[int, int, int]
Node4 = Tuple[int, int, int, int]


def parse_edges(raw_edges: Dict[str, List[List[int]]]) -> Dict[tuple, List[tuple]]:
    """
    Convert the JSON representation of the adjacency lists back into
    Python tuples.

    In the stored JSON files, dictionary keys are serialized as strings,
    so here we recover them as tuples using ast.literal_eval.
    """
    parsed: Dict[tuple, List[tuple]] = {}
    for k, v in raw_edges.items():
        key = ast.literal_eval(k)
        parsed[key] = [tuple(x) for x in v]
    return parsed


def strongly_connected_components(graph: Dict[tuple, List[tuple]]) -> List[List[tuple]]:
    """
    Compute the strongly connected components of a directed graph using
    Tarjan's algorithm.

    Input:
        graph[node] = list of out-neighbors of node

    Output:
        a list of SCCs, each represented as a list of vertices

    This is the main graph-theoretic step in the computational verification:
    directed cycles can only occur inside strongly connected components.
    """
    index = 0
    stack: List[tuple] = []
    on_stack = set()
    indices: Dict[tuple, int] = {}
    lowlink: Dict[tuple, int] = {}
    sccs: List[List[tuple]] = []

    def strongconnect(v: tuple) -> None:
        """
        Recursive Tarjan step starting from vertex v.
        """
        nonlocal index
        indices[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)
        on_stack.add(v)

        for w in graph[v]:
            if w not in indices:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in on_stack:
                lowlink[v] = min(lowlink[v], indices[w])

        # If v is the root of an SCC, pop the whole component.
        if lowlink[v] == indices[v]:
            comp: List[tuple] = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                comp.append(w)
                if w == v:
                    break
            sccs.append(comp)

    for v in graph:
        if v not in indices:
            strongconnect(v)

    return sccs


def is_cycle_scc(comp: List[tuple], graph: Dict[tuple, List[tuple]]) -> bool:
    """
    Decide whether a strongly connected component actually contains a
    directed cycle.

    - Any SCC with more than one vertex contains a directed cycle.
    - An SCC with one vertex contains a directed cycle only if that
      vertex has a self-loop.
    """
    if len(comp) > 1:
        return True
    v = comp[0]
    return v in graph[v]


def verify_g3(results_dir: Path) -> str:
    """
    Verify the graph-theoretic statement for G_3.

    Expected result:
      - node_count = 5832 = 18^3
      - edge_count = 5832
      - exactly 18 constant loops
      - no nonconstant directed cycles
    """
    data = json.loads((results_dir / "G3_graph.json").read_text())
    graph = parse_edges(data["edges"])
    sccs = strongly_connected_components(graph)
    cyclic_sccs = [comp for comp in sccs if is_cycle_scc(comp, graph)]

    constant_loops = []
    nonconstant_cycles = []

    # Separate constant one-vertex loops from all other cyclic SCCs.
    for comp in cyclic_sccs:
        if len(comp) == 1:
            v = comp[0]
            if v[0] == v[1] == v[2]:
                constant_loops.append(v)
            else:
                nonconstant_cycles.append(comp)
        else:
            nonconstant_cycles.append(comp)

    lines = []
    lines.append("G3 verification")
    lines.append(f"Nodes: {data['node_count']}")
    lines.append(f"Edges: {data['edge_count']}")
    lines.append(f"Cyclic SCCs: {len(cyclic_sccs)}")
    lines.append(f"Constant loops: {len(constant_loops)}")
    lines.append(f"Nonconstant cycles: {len(nonconstant_cycles)}")
    lines.append(f"Constant loop representatives: {sorted(constant_loops)}")

    # Assertions implementing the statement used in the paper.
    assert data["node_count"] == 5832
    assert data["edge_count"] == 5832
    assert len(constant_loops) == 18
    assert len(nonconstant_cycles) == 0

    return "\n".join(lines) + "\n"


def verify_g4(results_dir: Path) -> str:
    """
    Verify the graph-theoretic statement for the family of graphs G_r.

    For each residue class r in Z/18Z, the graph G_r should satisfy:
      - node_count = 81 = 3^4
      - exactly 3 constant loops
      - no nonconstant directed cycles
    """
    lines = []
    lines.append("G4 verification")
    total_nonconstant = 0

    for r in range(18):
        data = json.loads((results_dir / f"G4_r{r}.json").read_text())
        graph = parse_edges(data["edges"])
        sccs = strongly_connected_components(graph)
        cyclic_sccs = [comp for comp in sccs if is_cycle_scc(comp, graph)]

        constant_loops = []
        nonconstant_cycles = []

        # Separate constant one-vertex loops from all other cyclic SCCs.
        for comp in cyclic_sccs:
            if len(comp) == 1:
                v = comp[0]
                if v[0] == v[1] == v[2] == v[3]:
                    constant_loops.append(v)
                else:
                    nonconstant_cycles.append(comp)
            else:
                nonconstant_cycles.append(comp)

        lines.append(
            f"r={r}: nodes={data['node_count']}, edges={data['edge_count']}, "
            f"constant_loops={len(constant_loops)}, nonconstant_cycles={len(nonconstant_cycles)}"
        )

        # Assertions implementing the statement used in the paper.
        assert data["node_count"] == 81
        assert len(constant_loops) == 3
        assert len(nonconstant_cycles) == 0

        total_nonconstant += len(nonconstant_cycles)

    lines.append(f"Total nonconstant cycles across all r: {total_nonconstant}")
    return "\n".join(lines) + "\n"


def main() -> None:
    """
    Run the computational verification for both G_3 and the family G_r.

    The textual results are written to:
      - results/G3_scc.txt
      - results/Gr_scc.txt

    and also printed to stdout.
    """
    results_dir = Path("results")
    out_g3 = verify_g3(results_dir)
    out_g4 = verify_g4(results_dir)

    (results_dir / "G3_scc.txt").write_text(out_g3)
    (results_dir / "Gr_scc.txt").write_text(out_g4)

    print(out_g3)
    print(out_g4)
    print("Verification complete.")


if __name__ == "__main__":
    main()