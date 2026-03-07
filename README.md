# Collatz 3-adic Cycle Obstruction

Repository accompanying the paper  
"A Finite 3-Adic Obstruction to Odd Collatz Cycles"  
Juan R. Marchionatto

## Overview

The paper studies the odd-to-odd dynamics of the Collatz map using
exponent sequences defined by

3n + 1 = 2^e n'

Compatibility conditions between consecutive exponent windows are
encoded as finite directed graphs.

The code constructs these graphs and verifies that:

- the graph G3 (window length 3, modulo 27) has no nonconstant cycles
- the graphs Gr (window length 4, modulo 81) have no nonconstant cycles

This eliminates all nonconstant exponent configurations compatible with
the required 3-adic constraints.

The verification performed by the code corresponds to the computational
statements in:

- Lemma 4.3 (structure of G3)
- Lemma 5.3 (structure of Gr)

## Requirements

Python 3.10+

Install dependency:

```
pip install networkx
```

## Quick reproduction

Clone the repository and run

```
pip install networkx
python src/build_G3.py
python src/build_G4.py
```

The scripts construct the graphs and verify that the only directed cycles
are constant exponent configurations.

## Repository structure

```
src/
    build_G3.py
    build_G4.py
    verify_cycles.py

results/
    G3_scc.txt
    Gr_scc.txt
```

## Reproducibility

Results reported in the paper can be reproduced by running the scripts in `src/`.

All computations are finite and complete.

The graphs contain:

- 5832 vertices for G3
- 81 vertices for each Gr

Cycle detection is performed using Tarjan's strongly connected
components algorithm.

## License

MIT License