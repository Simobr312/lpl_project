import numpy as numpy
from typing import List, Set, FrozenSet, Dict, Tuple

from parser import parse_ast
from union_find import UnionFind
from core import Loc, eval_program, lookup, access
from complex import Complex, Simplex

import numpy

def skeleton_map(complex: Complex) -> Dict[int, List[Simplex]]:
    """Returns a mapping from dimension k to the k-skeleton of the complex."""
    skeleton: Dict[int, List[Simplex]] = {}
    simplices = complex.simplices

    for simplex in simplices:
        dim = len(simplex) - 1
        if dim not in skeleton:
            skeleton[dim] = []
        skeleton[dim].append(simplex)

    return skeleton

def k_simplices(complex: Complex, k: int) -> List[Simplex]:
    """Return the list of k-simplices in the complex."""
    skeleton = skeleton_map(complex)
    return skeleton.get(k, [])

def ordered(simplex: Simplex, complex: Complex) -> Tuple[str, ...]:
    order = complex.vertex_order
    return tuple(sorted(simplex, key = lambda v: order[v]))


import numpy as np

def boundary_matrix(complex: Complex, k: int) -> np.ndarray:
    """Constructs the boundary matrix d_k: C_k -> C_{k-1} over F_2."""
    k_simp = k_simplices(complex, k)
    k1_simp = k_simplices(complex, k - 1)

    row_index = {s: i for i, s in enumerate(k1_simp)}
    col_index = {s: j for j, s in enumerate(k_simp)}

    M = np.zeros((len(k1_simp), len(k_simp)), dtype=int)

    for simplex in k_simp:
        verts = ordered(simplex, complex)
        j = col_index[simplex]

        for i in range(len(verts)):
            face = frozenset(verts[:i] + verts[i + 1:])
            r = row_index[face]
            M[r, j] ^= 1

    return M

def rank_mod2(M: np.ndarray) -> int:
    """Computes the rank of matrix M over F_2 using Gaussian elimination."""
    M = M.copy() % 2
    rows, cols = M.shape
    rank = 0

    for col in range(cols):
        pivot = None
        for r in range(rank, rows):
            if M[r, col] == 1:
                pivot = r
                break

        if pivot is None:
            continue

        M[[rank, pivot]] = M[[pivot, rank]]

        for r in range(rows):
            if r != rank and M[r, col] == 1:
                M[r] ^= M[rank]

        rank += 1

    return rank

def homology_rank(complex: Complex, k: int) -> int:
    """Computes the rank of the k-th homology group H_k(X) over F_2."""
    if k < 0 or complex.dimension < k:
        return 0
    
    dimC_k = len(k_simplices(complex, k))
    
    if k == 0:
        rank_dk = 0   # d_0 = 0
    else:
        d_k = boundary_matrix(complex, k)
        rank_dk = rank_mod2(d_k) if d_k.size > 0 else 0

    if k + 1 > complex.dimension:
        rank_dk1 = 0
    else:
        d_k1 = boundary_matrix(complex, k + 1)
        rank_dk1 = rank_mod2(d_k1) if d_k1.size > 0 else 0

    dimKer_dk = dimC_k - rank_dk

    return dimKer_dk - rank_dk1

def compute_homology(complex: Complex) -> Dict[int, int]:
    """Computes the homology groups of the complex and returns the rank of each group."""
    homology: Dict[int, int] = {}
    for k in range(0, complex.dimension + 1):
        rank = homology_rank(complex, k)
        homology[k] = rank
    return homology

def print_homology(complex: Complex):
    """Computes the homology groups of the complex and returns the rank of each group."""
    
    for k in range(0, complex.dimension + 1):
        k_simp = k_simplices(complex, k)
        print(f"{k}-simplices: {[ordered(s, complex) for s in k_simp]}")

    for k in range(0, complex.dimension + 1):
        rank = homology_rank(complex, k)
        print(f"Rank of H_{k}: {rank}")

def main():
    source_code = """
        complex A = [v1, v2, v3]
complex B = union(A, union([v2, v4], [v3, v4]))
    """
    ast = parse_ast(source_code)
    env, state = eval_program(ast)

    B = lookup(env, "B")
    if isinstance(B, Loc):
        complex_B = access(state, B)
        print(complex_B)
        print(compute_homology(complex_B))

if __name__ == "__main__":
    main()