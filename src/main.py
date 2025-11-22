from __future__ import annotations
from itertools import combinations
from typing import List, Dict, Set, FrozenSet, Callable

from parser import VertexName, parse_ast, Statement, ComplexDecl, ComplexStmt
from union_find import UnionFind


vertices_order: List[VertexName] = []

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

    def get_classes(self) -> Dict[VertexName, Set[VertexName]]:
        return self.uf.get_classes()
    
    def __repr__(self) -> str:
        return (
        f"Complex(\n"
        f"  dimension={self.dimension},\n"
        f"  maximal_simplices={self.maximal_simplices},\n"
        f"  classes={{ {self.get_classes()} }}\n"
        f")"
        )


DVal = Complex
#I changed the typing here from Callable to Dict in order to see the domain of the environment in the web server
type Environment = Dict[str, DVal]

def empty_environment() -> Environment:
    return dict()

def initial_environment() -> Environment:
    env = empty_environment()
    return env

def lookup(env: Environment, name: str) -> DVal:
    if name not in env:
        raise ValueError(f"Undefined variable: {name}")

    return env[name]

def bind(env: Environment, x: str, value: DVal) -> Environment:
    new_env = env.copy()
    new_env[x] = value
    return new_env

def faces(simplex: Simplex):
    """Generate all faces of a simplex."""
    s = list(simplex)
    for k in range(len(s) + 1):
        for combo in combinations(s, k):
                yield frozenset(combo)


def build_complex_from_complex_decl(stmt: ComplexDecl) -> Complex:
    """Builds a simplicial complex from a complex declaration."""

    l = len(vertices_order)
    vertices_order.extend(stmt.vertices)
    if(len(vertices_order) != l + len(stmt.vertices)):
        raise ValueError(f"Duplicate vertex names in complex declaration: {stmt.vertices}")


    complex = frozenset(stmt.vertices)
    classes = UnionFind[VertexName]()
    for v in stmt.vertices:
        classes.add(v)
    return Complex({complex}, classes)

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

    for σ in K1.maximal_simplices | K2.maximal_simplices:

        canon = frozenset(new_uf.find(v) for v in σ)

        if len(canon) != len(σ):
            raise ValueError(
                f"Union created a degenerate simplex: {σ} collapsed to {canon} "
                f"because some vertices became identified."
            )

        new_simplices.add(canon)

    return Complex(maximal_simplices=new_simplices, uf=new_uf)

def glue(K1: Complex, K2: Complex, mapping: Dict[VertexName, VertexName]) -> Complex:
    """Returns the glueing of two simplicial complexes along a vertex mapping, with full semantic checks."""

    V1 = K1.vertices
    V2 = K2.vertices

    for a, b in mapping.items():
        if a not in V1:
            raise ValueError(f"glue(): vertex '{a}' is not in the first complex.")
        if b not in V2:
            raise ValueError(f"glue(): vertex '{b}' is not in the second complex.")

    inv = {}
    for a, b in mapping.items():
        if a in inv and inv[a] != b:
            raise ValueError(
                f"glue(): vertex '{a}' is mapped to two different targets: "
                f"{inv[a]} and {b}."
            )
        inv[a] = b

    items = list(mapping.items())
    for i in range(len(items)):
        a1, b1 = items[i]
        for j in range(i + 1, len(items)):
            a2, b2 = items[j]
            eq1 = K1.uf.find(a1) == K1.uf.find(a2)
            eq2 = K2.uf.find(b1) == K2.uf.find(b2)

            if eq1 != eq2:
                raise ValueError(
                    f"glue(): incompatible identifications: "
                    f"{a1}~{a2} in K1 but {b1}~{b2} is "
                    f"{'not ' if not eq2 else ''}true in K2."
                )

    new_uf = K1.uf.merge(K2.uf)

    for a, b in mapping.items():
        new_uf.union(a, b)

    new_simplices = set()

    for s in K1.maximal_simplices | K2.maximal_simplices:

        canon = frozenset(new_uf.find(v) for v in s)

        if len(canon) != len(s):
            raise ValueError(
                f"glue(): the simplex {s} collapsed to {canon} "
                f"after vertex identifications."
            )

        new_simplices.add(canon)

    return Complex(maximal_simplices=new_simplices, uf=new_uf)



def eval_complex_decl(env: Environment, stmt: ComplexDecl) -> Environment:
    complex_ = build_complex_from_complex_decl(stmt)
    return bind(env, stmt.name, complex_)    

def eval_complex_stmt(env: Environment, stmt: ComplexStmt) -> Environment:
    args = [lookup(env, name) for name in stmt.args]

    match stmt.op:
        case "union":
            if len(args) != 2:
                raise ValueError(f"Union operation requires exactly 2 arguments.")
            result = union(args[0], args[1])
        case "glue":
            if len(args) != 2:
                raise ValueError(f"Glue operation requires exactly 2 arguments.")
            mapping = stmt.mapping or {}
            result = glue(args[0], args[1], mapping)
        case _:
            raise ValueError(f"Unknown complex operation: {stmt.op}")
        
    return bind(env, stmt.name, result)

def eval_stmt(env: Environment, stmt: Statement) -> Environment:
    if isinstance(stmt, ComplexDecl):
        return eval_complex_decl(env, stmt)
    if isinstance(stmt, ComplexStmt):
        return eval_complex_stmt(env, stmt)
    raise ValueError(f"Unknown statement type: {stmt}")

def eval_program(statements) -> Environment:
    env = empty_environment()
    for stmt in statements:
        env = eval_stmt(env, stmt)
    return env

def main():
    source_code = """
        complex S1 = [A, B, C]
        complex S2 = [D, E, F]
        complex C1 = union(S1, S2)
        complex C2 = glue(S1, S2) mapping {B -> E, C -> F}
    """

    ast = parse_ast(source_code)
    env = eval_program(ast)


    for name in ["S1", "S2", "C1", "C2"]:
        complex_ = lookup(env, name)
        print(f"{name}: {complex_}")

if __name__ == "__main__":
    main()