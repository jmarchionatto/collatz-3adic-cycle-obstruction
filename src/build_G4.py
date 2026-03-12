from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

# ------------------------------------------------------------
# Graph G_r for the k = 4 compatibility condition (mod 81)
#
# This script constructs the directed graphs G_r used in the
# refinement step of the paper (window length k = 4).
#
# From the k = 3 analysis we know that all exponents satisfy
#
#     e_i ≡ r (mod 18)
#
# so we write
#
#     e_i = r + 18 t_i
#
# where t_i ∈ Z/3Z.
#
# Vertices:
#   quadruples (a,b,c,d) in (Z/3Z)^4 representing
#
#       (t_i, t_{i+1}, t_{i+2}, t_{i+3})
#
# Edge rule:
#   (a,b,c,d) → (b,c,d,x)
#
# if the compatibility condition derived from the length–4
# window identity holds modulo 81.
#
# A separate graph G_r is constructed for each residue class
#
#       r ∈ Z/18Z.
#
# The paper proves that these graphs contain only constant cycles.
# ------------------------------------------------------------

MOD = 81
BASE_PERIOD = 18
T_PERIOD = 3

Node4 = Tuple[int, int, int, int]


def epsilon(r: int, x: int) -> int:
    """
    Recover the full exponent from its decomposition

        e_i = r + 18 t_i

    where r ∈ Z/18Z and t_i ∈ Z/3Z.
    """
    return r + 18 * x


def pow2_exp(exp: int, mod: int = MOD) -> int:
    """
    Compute 2^exp modulo mod.
    """
    return pow(2, exp, mod)


def inv_pow2_exp(exp: int, mod: int = MOD) -> int:
    """
    Compute the modular inverse of 2^exp modulo mod.

    Since gcd(2,81)=1, all powers of 2 are invertible mod 81.
    """
    return pow(pow2_exp(exp, mod), -1, mod)


def r4(r: int, a: int, b: int, c: int, d: int, mod: int = MOD) -> int:
    """
    Compute the residue map R_4 for the length–4 window identity.

    In the notation of the paper:

        R_4(a,b,c,d) =
            2^{-(ea+eb+ec+ed)}
            (2^{ed+ec+eb} + 3·2^{ed+ec} + 9·2^{ed} + 27)
            (mod 81)

    where

        ea = r + 18a
        eb = r + 18b
        ec = r + 18c
        ed = r + 18d.
    """

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
    """
    Test the compatibility condition defining edges in G_r.

    The transition

        (a,b,c,d) → (b,c,d,x)

    is allowed if

        R_4(b,c,d,x) ==
        (3 R_4(a,b,c,d) + 1) * 2^{-e_a}    (mod 81)

    where e_a = r + 18a.
    """

    left = r4(r, b, c, d, x, MOD)

    right = (
        (3 * r4(r, a, b, c, d, MOD) + 1) % MOD
    ) * inv_pow2_exp(epsilon(r, a), MOD)

    return left == (right % MOD)


def sanity_checks() -> None:
    """
    Basic arithmetic sanity checks.

    Verify that powers of 2 and their inverses behave correctly
    modulo 81 for all exponent residues that appear in the graph.
    """

    for r in range(BASE_PERIOD):
        for x in range(T_PERIOD):
            val = pow2_exp(epsilon(r, x), MOD)
            inv = inv_pow2_exp(epsilon(r, x), MOD)
            assert (val * inv) % MOD == 1


def build_graph_for_r(r: int) -> Dict[str, object]:
    """
    Construct the directed graph G_r corresponding to a fixed
    exponent residue r (mod 18).

    Vertices:
        (a,b,c,d) in (Z/3Z)^4

    Edges:
        (a,b,c,d) → (b,c,d,x)
        whenever the compatibility condition holds.
    """

    nodes: List[Node4] = []
    edges: Dict[Node4, List[Node4]] = {}

    # Build vertex set (Z/3Z)^4
    for a in range(T_PERIOD):
        for b in range(T_PERIOD):
            for c in range(T_PERIOD):
                for d in range(T_PERIOD):
                    node = (a, b, c, d)
                    nodes.append(node)
                    edges[node] = []

    # Test all possible successors x ∈ Z/3Z
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
    """
    Build all graphs G_r for r ∈ Z/18Z and store them as JSON files.
    """

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