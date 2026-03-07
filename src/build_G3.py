from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

MOD = 27
PER = 18

Node3 = Tuple[int, int, int]


def pow2(k: int, mod: int = MOD) -> int:
    return pow(2, k % PER, mod)


def inv_pow2(k: int, mod: int = MOD) -> int:
    return pow(pow2(k, mod), -1, mod)


def r3(a: int, b: int, c: int, mod: int = MOD) -> int:
    e_sum = (a + b + c) % PER
    term = (pow2(b + c, mod) + 3 * pow2(c, mod) + 9) % mod
    return (term * inv_pow2(e_sum, mod)) % mod


def edge_ok(a: int, b: int, c: int, d: int) -> bool:
    left = r3(b, c, d, MOD)
    right = ((3 * r3(a, b, c, MOD) + 1) % MOD) * inv_pow2(a, MOD)
    return left == (right % MOD)


def sanity_checks() -> None:
    for k in range(PER):
        assert (pow2(k, MOD) * inv_pow2(k, MOD)) % MOD == 1
        assert pow2(k + PER, MOD) == pow2(k, MOD)
        assert inv_pow2(k + PER, MOD) == inv_pow2(k, MOD)


def build_graph() -> Dict[str, object]:
    nodes: List[Node3] = []
    edges: Dict[Node3, List[Node3]] = {}

    for a in range(PER):
        for b in range(PER):
            for c in range(PER):
                node = (a, b, c)
                nodes.append(node)
                edges[node] = []

    for a, b, c in nodes:
        for d in range(PER):
            if edge_ok(a, b, c, d):
                edges[(a, b, c)].append((b, c, d))

    edge_count = sum(len(v) for v in edges.values())
    return {
        "modulus": MOD,
        "period": PER,
        "node_count": len(nodes),
        "edge_count": edge_count,
        "nodes": nodes,
        "edges": {str(k): v for k, v in edges.items()},
    }


def main() -> None:
    sanity_checks()
    graph = build_graph()

    out_dir = Path("results")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "G3_graph.json"
    out_file.write_text(json.dumps(graph, indent=2))

    print(f"G3 graph written to {out_file}")
    print(f"Nodes: {graph['node_count']}")
    print(f"Edges: {graph['edge_count']}")


if __name__ == "__main__":
    main()