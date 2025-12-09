from __future__ import annotations
from itertools import combinations
from typing import List, Dict, Set, FrozenSet, Callable

from parser import Expr, OpExpr, Ref, Program, ComplexStmt, ComplexLiteral, Statement, parse_ast
from union_find import UnionFind

type VertexName = Ref

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

# == ENVIRONMENT == #

type DenOperator = Callable[..., Complex]
type DVal = Complex | DenOperator
#I changed the typing here from Callable to Dict in order to see the domain of the environment in the web server
type Environment = Dict[str, DVal]

def empty_environment() -> Environment:
    return dict()

def initial_environment() -> Environment:
    env = empty_environment()

    env = bind(env, "union", union)
    env = bind(env, "glue", glue)
    env = bind(env, "join", join)

    return env

def lookup(env: Environment, name: str) -> DVal:
    if name not in env:
        raise ValueError(f"Undefined symbol: {name}")
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

# == BUILDING == #

def build_complex_from_vtx(stmt: ComplexDeclVtx) -> Complex:
    """Builds a simplicial complex from a vertex declaration."""
    l = len(vertices_order)
    vertices_order.extend(stmt.vertices)
    if(len(vertices_order) != l + len(stmt.vertices)):
        raise ValueError(f"Duplicate vertex names in complex declaration: {stmt.vertices}")


    complex = frozenset(stmt.vertices)
    uf = UnionFind[VertexName]()
    for v in stmt.vertices:
        uf.add(v)

    return Complex({complex}, uf)

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

def join(K1: Complex, K2: Complex) -> Complex:
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


# == EVALUATION == #

def eval_expr(env: Environment, expr: Expr) -> Complex:
    if isinstance(expr, str):
        val = lookup(env, expr)
        if isinstance(val, Complex):
            return val
        raise ValueError(f"Identifier '{expr}' is not a complex")
    
    if isinstance(expr, ComplexLiteral):
        complex = frozenset(expr.vertices)
        uf = UnionFind[VertexName]()
        for v in expr.vertices:
            uf.add(v)

        return Complex({complex}, uf)


    if isinstance(expr, OpExpr):
        op_fun = lookup(env, expr.op)
        if not callable(op_fun):
            raise ValueError(f"Identifier '{expr.op}' is not an operation")

        K1 = eval_expr(env, expr.left)
        K2 = eval_expr(env, expr.right)

        if expr.op == "glue":
            if expr.mapping is None:
                raise ValueError("glue operation requires a mapping")
            return op_fun(K1, K2, expr.mapping)
        else:
            return op_fun(K1, K2)

    raise TypeError("Unknown expr")

def eval_stmt(env: Environment, stmt: Statement) -> Environment:
    match stmt:
        case ComplexStmt(name=name, expr=expr):
            complex = eval_expr(env, expr)
            return bind(env, name, complex)
        case _:
            raise ValueError(f"Unknown statement: {stmt}")


vertices_order: List[VertexName] = []
def eval_program(statements: Program) -> Environment:
    vertices_order.clear()

    env = initial_environment()
    print(env)
    for stmt in statements:
        env = eval_stmt(env, stmt)
    return env

def main():
    source_code = """
        // S0
        // Define a triangle
        complex A = [v1, v2, v3]

    """

    ast = parse_ast(source_code)
    env = eval_program(ast)


    for name in env.keys():
        if callable(env[name]):
            continue

        complex_ = lookup(env, name)
        print(f"{name}: {complex_}")

if __name__ == "__main__":
    main()