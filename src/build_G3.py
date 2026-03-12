from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

# ------------------------------------------------------------
# Graph G_3 for the k = 3 compatibility condition (mod 27)
#
# This script constructs the directed graph G_3 used in the paper.
#
# Vertices:
#   triples (a, b, c) in (Z/18Z)^3
#
# Interpretation:
#   a, b, c are residue classes of three consecutive exponents modulo 18.
#   This reduction modulo 18 is justified by ord_27(2) = 18.
#
# Edge rule:
#   (a, b, c) -> (b, c, d)
#   if the compatibility condition
#
#       R_3(b, c, d) == (3*R_3(a, b, c) + 1) * 2^{-a}   (mod 27)
#
#   holds.
#
# Thus G_3 encodes all length-3 exponent windows that can occur
# consecutively along a hypothetical odd Collatz cycle.
# ------------------------------------------------------------

MOD = 27
PER = 18

Node3 = Tuple[int, int, int]


def pow2(k: int, mod: int = MOD) -> int:
    """
    Compute 2^k modulo mod, reducing the exponent modulo PER = 18.

    For mod = 27 we have ord_27(2) = 18, so powers of 2 depend only on
    the exponent modulo 18.
    """
    return pow(2, k % PER, mod)


def inv_pow2(k: int, mod: int = MOD) -> int:
    """
    Compute the inverse of 2^k modulo mod.

    Since gcd(2, 27) = 1, every power of 2 is invertible modulo 27.
    """
    return pow(pow2(k, mod), -1, mod)


def r3(a: int, b: int, c: int, mod: int = MOD) -> int:
    """
    Compute the residue map R_3(a, b, c) modulo 27.

    In the notation of the paper:
        R_3(a, b, c) =
            2^{-(a+b+c)} * (2^{b+c} + 3*2^c + 9)   (mod 27)

    This is the residue class forced by the length-3 window identity.
    """
    e_sum = (a + b + c) % PER
    term = (pow2(b + c, mod) + 3 * pow2(c, mod) + 9) % mod
    return (term * inv_pow2(e_sum, mod)) % mod


def edge_ok(a: int, b: int, c: int, d: int) -> bool:
    """
    Check whether the compatibility condition holds for the transition

        (a, b, c) -> (b, c, d).

    This is exactly the edge condition defining G_3:
        R_3(b, c, d) == (3*R_3(a, b, c) + 1) * 2^{-a}   (mod 27).
    """
    left = r3(b, c, d, MOD)
    right = ((3 * r3(a, b, c, MOD) + 1) % MOD) * inv_pow2(a, MOD)
    return left == (right % MOD)


def sanity_checks() -> None:
    """
    Basic arithmetic sanity checks.

    These verify:
      1. 2^k and its inverse multiply to 1 modulo 27;
      2. exponent reduction modulo 18 behaves as expected.

    This is useful because the entire graph construction relies on the
    periodicity of powers of 2 modulo 27.
    """
    for k in range(PER):
        assert (pow2(k, MOD) * inv_pow2(k, MOD)) % MOD == 1
        assert pow2(k + PER, MOD) == pow2(k, MOD)
        assert inv_pow2(k + PER, MOD) == inv_pow2(k, MOD)


def build_graph() -> Dict[str, object]:
    """
    Construct the full directed graph G_3.

    The graph has:
      - one vertex for each triple (a, b, c) in (Z/18Z)^3;
      - an edge (a, b, c) -> (b, c, d) whenever edge_ok(a, b, c, d) holds.

    The result is returned as a dictionary that can be serialized to JSON.
    """
    nodes: List[Node3] = []
    edges: Dict[Node3, List[Node3]] = {}

    # Build the full vertex set (Z/18Z)^3.
    for a in range(PER):
        for b in range(PER):
            for c in range(PER):
                node = (a, b, c)
                nodes.append(node)
                edges[node] = []

    # Test every possible successor d in Z/18Z.
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
    """
    Run sanity checks, build G_3, and save it to results/G3_graph.json.
    """
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