from __future__ import annotations
from typing import List, Dict, Set, FrozenSet, Callable
from itertools import combinations

from union_find import UnionFind

type VertexName = str
type Simplex = FrozenSet[VertexName]

class Complex:
    """A simplicial complex represented by its maximal simplices and a union-find structure for vertex identifications."""
    maximal_simplices : Set[Simplex]
    uf: UnionFind[VertexName]

    @property
    def dimension(self) -> int:
        if not self.maximal_simplices:
            return -1
        return max(len(face) - 1 for face in self.maximal_simplices)

    @property
    def vertices(self) -> Set[VertexName]:
        verts: Set[VertexName] = set()
        for face in self.maximal_simplices:
            verts.update(face)
        return verts
    
    def __init__(self, maximal_simplices: Set[Simplex], uf: UnionFind[VertexName]) -> None:
        self.maximal_simplices = maximal_simplices
        self.uf = uf or UnionFind[VertexName]()

    @property
    def classes(self) -> Dict[VertexName, Set[VertexName]]:
        return self.uf.get_classes()
    
    def __repr__(self) -> str:
        return (
        f"Complex(\n"
        f"  dimension={self.dimension},\n"
        f"  maximal_simplices={self.maximal_simplices},\n"
        f"  classes={{ {self.classes} }}\n"
        f")"
        )
    
    @property
    def simplices(self) -> Set[Simplex]:
        """Returns all faces of the complex."""
        simplices : Set[Simplex] = set()
        for simplex in self.maximal_simplices:
            n = len(simplex)
            for k in range(1, n + 1):
                for face in combinations(simplex, k):
                    simplices.add(frozenset(face))
        return simplices
    
    @property
    def vertex_order(self) -> Dict[str, int]:
        """Returns the list of vertices in a consistent order."""
        return {v: i for i, v in enumerate(self.vertices)}
    
    
# == OPERATIONS == #
def union(K1: Complex, K2: Complex) -> Complex:
    """Returns the union of two simplicial complex"""
    common_vertices = set(K1.vertices) & set(K2.vertices)

    for v in common_vertices:
        for w in common_vertices:
            k1_eq = (K1.uf.find(v) == K1.uf.find(w))
            k2_eq = (K2.uf.find(v) == K2.uf.find(w))

            if k1_eq != k2_eq:
                raise ValueError(
                    f"Incompatible vertex identifications in union(): "
                    f"{v} and {w} are equivalent in one complex but not the other."
                )
            
    new_uf = K1.uf.merge(K2.uf)

    new_simplices = set()

    for s in K1.maximal_simplices | K2.maximal_simplices:

        canon = frozenset(new_uf.find(v) for v in s)

        if len(canon) != len(s):
            raise ValueError(
                f"Union created a degenerate simplex: {s} collapsed to {canon} "
                f"because some vertices became identified."
            )

        new_simplices.add(canon)

    return Complex(maximal_simplices=new_simplices, uf=new_uf)

def glue(K1: Complex, K2: Complex, mapping: Dict[VertexName, VertexName]) -> Complex:
    """
    Glue two simplicial complexes using a mapping.
    The mapping can be specified using any vertex from each equivalence class.
    Internally, it is normalized to canonical representatives.
    """
    rep_map: Dict[VertexName, VertexName] = {}
    for a, b in mapping.items():
        ra = K1.uf.find(a)
        rb = K2.uf.find(b)


        if ra not in K1.vertices:
            raise ValueError(f"glue(): vertex '{a}' (rep {ra}) is not in the first complex.")
        if rb not in K2.vertices:
            raise ValueError(f"glue(): vertex '{b}' (rep {rb}) is not in the second complex.")

        if ra in rep_map and rep_map[ra] != rb:
            raise ValueError(
                f"glue(): conflicting mapping for class '{ra}': {rep_map[ra]} vs {rb}"
            )

        rep_map[ra] = rb

    new_uf = K1.uf.merge(K2.uf)

    for ra, rb in rep_map.items():
        class_a = K1.uf.get_classes()[ra]
        class_b = K2.uf.get_classes()[rb]

        new_uf.union(ra, rb)

        for x in class_a:
            new_uf.union(x, rb)
        for y in class_b:
            new_uf.union(ra, y)

    new_simplices = set()
    for s in K1.maximal_simplices | K2.maximal_simplices:
        canon = frozenset(new_uf.find(v) for v in s)
        if len(canon) != len(s):
            raise ValueError(
                f"glue(): simplex {s} collapsed to {canon} after vertex identifications."
            )
        new_simplices.add(canon)

    return Complex(maximal_simplices=new_simplices, uf=new_uf)



def join(K1: Complex, K2: Complex) -> Complex:
    """Returns the join of two simplicial complexes."""
    new_uf = K1.uf.merge(K2.uf)

    new_simplices: Set[Simplex] = set()
    for s in K1.maximal_simplices:
        for t in K2.maximal_simplices:
            canon = frozenset(new_uf.find(v) for v in s | t)
            if len(canon) != len(s | t):
                raise ValueError(
                    f"Join created degenerate simplex: {s | t} collapsed to {canon}"
                )
            new_simplices.add(canon)

    return Complex(maximal_simplices=new_simplices, uf=new_uf)

def dimension(K: Complex) -> int:
    return K.dimension

def num_simplices(K: Complex) -> int:
    """Returns the number of simplices in the complex."""
    return len(K.simplices)

def num_vertices(K: Complex) -> int:
    """Returns the number of vertices in the complex."""
    return len(K.vertices)

def pick_vertex(C: Complex, state) -> Complex:
    """Picks a vertex from the complex according to insertion order."""
    if not C.vertices:
        raise ValueError("Cannot pick a vertex from an empty complex")
    
    # pick vertex to insertion order
    v = max(C.vertices, key=lambda x: state.vertices_order.get(x, float('inf')))
    
    new_uf = UnionFind[VertexName]()
    new_uf.add(v)
    for w in C.uf.get_classes()[v]:
        new_uf.union(v, w)
    
    return Complex(maximal_simplices={frozenset({v})}, uf=new_uf)