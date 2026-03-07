from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple

Node3 = Tuple[int, int, int]
Node4 = Tuple[int, int, int, int]


def parse_edges(raw_edges: Dict[str, List[List[int]]]) -> Dict[tuple, List[tuple]]:
    parsed: Dict[tuple, List[tuple]] = {}
    for k, v in raw_edges.items():
        key = ast.literal_eval(k)
        parsed[key] = [tuple(x) for x in v]
    return parsed


def strongly_connected_components(graph: Dict[tuple, List[tuple]]) -> List[List[tuple]]:
    index = 0
    stack: List[tuple] = []
    on_stack = set()
    indices: Dict[tuple, int] = {}
    lowlink: Dict[tuple, int] = {}
    sccs: List[List[tuple]] = []

    def strongconnect(v: tuple) -> None:
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
    if len(comp) > 1:
        return True
    v = comp[0]
    return v in graph[v]


def verify_g3(results_dir: Path) -> str:
    data = json.loads((results_dir / "G3_graph.json").read_text())
    graph = parse_edges(data["edges"])
    sccs = strongly_connected_components(graph)
    cyclic_sccs = [comp for comp in sccs if is_cycle_scc(comp, graph)]

    constant_loops = []
    nonconstant_cycles = []

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

    assert data["node_count"] == 5832
    assert data["edge_count"] == 5832
    assert len(constant_loops) == 18
    assert len(nonconstant_cycles) == 0

    return "\n".join(lines) + "\n"


def verify_g4(results_dir: Path) -> str:
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

        assert data["node_count"] == 81
        assert len(constant_loops) == 3
        assert len(nonconstant_cycles) == 0

        total_nonconstant += len(nonconstant_cycles)

    lines.append(f"Total nonconstant cycles across all r: {total_nonconstant}")
    return "\n".join(lines) + "\n"


def main() -> None:
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