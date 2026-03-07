from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

MOD = 81
BASE_PERIOD = 18
T_PERIOD = 3

Node4 = Tuple[int, int, int, int]


def epsilon(r: int, x: int) -> int:
    return r + 18 * x


def pow2_exp(exp: int, mod: int = MOD) -> int:
    return pow(2, exp, mod)


def inv_pow2_exp(exp: int, mod: int = MOD) -> int:
    return pow(pow2_exp(exp, mod), -1, mod)


def r4(r: int, a: int, b: int, c: int, d: int, mod: int = MOD) -> int:
    ea = epsilon(r, a)
    eb = epsilon(r, b)
    ec = epsilon(r, c)
    ed = epsilon(r, d)

    e_sum = ea + eb + ec + ed
    term = (
        pow2_exp(ed + ec + eb, mod)
        + 3 * pow2_exp(ed + ec, mod)
        + 9 * pow2_exp(ed, mod)
        + 27
    ) % mod
    return (term * inv_pow2_exp(e_sum, mod)) % mod


def edge_ok(r: int, a: int, b: int, c: int, d: int, x: int) -> bool:
    left = r4(r, b, c, d, x, MOD)
    right = ((3 * r4(r, a, b, c, d, MOD) + 1) % MOD) * inv_pow2_exp(epsilon(r, a), MOD)
    return left == (right % MOD)


def sanity_checks() -> None:
    for r in range(BASE_PERIOD):
        for x in range(T_PERIOD):
            val = pow2_exp(epsilon(r, x), MOD)
            inv = inv_pow2_exp(epsilon(r, x), MOD)
            assert (val * inv) % MOD == 1


def build_graph_for_r(r: int) -> Dict[str, object]:
    nodes: List[Node4] = []
    edges: Dict[Node4, List[Node4]] = {}

    for a in range(T_PERIOD):
        for b in range(T_PERIOD):
            for c in range(T_PERIOD):
                for d in range(T_PERIOD):
                    node = (a, b, c, d)
                    nodes.append(node)
                    edges[node] = []

    for a, b, c, d in nodes:
        for x in range(T_PERIOD):
            if edge_ok(r, a, b, c, d, x):
                edges[(a, b, c, d)].append((b, c, d, x))

    edge_count = sum(len(v) for v in edges.values())
    return {
        "r": r,
        "modulus": MOD,
        "node_count": len(nodes),
        "edge_count": edge_count,
        "nodes": nodes,
        "edges": {str(k): v for k, v in edges.items()},
    }


def main() -> None:
    sanity_checks()
    out_dir = Path("results")
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = []
    for r in range(BASE_PERIOD):
        graph = build_graph_for_r(r)
        out_file = out_dir / f"G4_r{r}.json"
        out_file.write_text(json.dumps(graph, indent=2))
        summary.append(
            {
                "r": r,
                "node_count": graph["node_count"],
                "edge_count": graph["edge_count"],
            }
        )

    summary_file = out_dir / "G4_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2))

    print(f"G4 graphs written to {out_dir}")
    print(f"Residue classes checked: {BASE_PERIOD}")


if __name__ == "__main__":
    main()