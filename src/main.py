from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations
from typing import List, Dict, Set, FrozenSet, Callable

from parser import VertexName, parse_ast, Statement, SimplexStmt, ComplexStmt
from union_find import UnionFind



vertices_order: List[VertexName] = []

type Simplex = FrozenSet[VertexName]

class Complex:
    maximal_simplices : Set[Simplex]
    classes: UnionFind[VertexName]

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
    
    def __init__(self, maximal_simplices: Set[Simplex], classes: UnionFind[VertexName]) -> None:
        self.maximal_simplices = maximal_simplices
        self.classes = classes or UnionFind[VertexName]()

    def canonical_vertex(self, v: VertexName) -> VertexName:
        return self.classes.find(v)
    
    def __repr__(self) -> str:
        reps: Dict[VertexName, Set[VertexName]] = {}
        for v in self.vertices:
            r = self.classes.find(v)
            reps.setdefault(r, set()).add(v)

        classes_str = ", ".join(
            f"{repr(rep)}: {sorted(list(elems))}"
            for rep, elems in reps.items()
        )

        return (
            f"Complex(\n"
            f"  dimension={self.dimension},\n"
            f"  maximal_simplices={self.maximal_simplices},\n"
            f"  classes={{ {classes_str} }}\n"
            f")"
        )


DVal = Complex
type Environment = Callable[[str], DVal]

def empty_environment() -> Environment:
    def env(name: str) -> DVal:
        raise ValueError(f"Undefined identifier: {name}")

    return env

def initial_environment() -> Environment:
    env = empty_environment()
    
    return env

def lookup(env: Environment, name: str) -> DVal:
    return env(name)

def bind(env: Environment, name: str, value: DVal) -> Environment:
    return lambda n: value if n == name else env(n)

def faces(simplex: Simplex):
    s = list(simplex)
    for k in range(len(s) + 1):
        for combo in combinations(s, k):
                yield frozenset(combo)


def build_complex_from_simplex_stmt(stmt: SimplexStmt) -> Complex:
    
    for v in stmt.vertices:
        if v not in vertices_order:
            vertices_order.append(v)
        else:
            raise ValueError(f"You can not repeat two vertices declaration in the same program.")

    simplex = frozenset(stmt.vertices)
    classes = UnionFind[VertexName]()
    for v in stmt.vertices:
        classes.add(v)
    return Complex({simplex}, classes)

def union(complex1: Complex, complex2: Complex) -> Complex:
    new_classes = complex1.classes.merge(complex2.classes)
    all_simplices = complex1.maximal_simplices.union(complex2.maximal_simplices)

    return Complex(all_simplices, new_classes)

def glue(complex1: Complex, complex2: Complex, mapping: Dict[VertexName, VertexName]) -> Complex:
    new_classes = complex1.classes.merge(complex2.classes)

    for a, b in mapping.items():
        new_classes.union(a, b)

    all_simplices: Set[Simplex] = set()

    for simplex in complex1.maximal_simplices | complex2.maximal_simplices:
        canonical = frozenset(new_classes.find(v) for v in simplex)
        all_simplices.add(canonical)

    maximal = set(all_simplices)
    for s1 in all_simplices:
        for s2 in all_simplices:
            if s1 != s2 and s1.issubset(s2):
                maximal.discard(s1)

    return Complex(maximal, new_classes)


def eval_simplex_stmt(env: Environment, stmt: SimplexStmt) -> Environment:
    complex_ = build_complex_from_simplex_stmt(stmt)
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
    if isinstance(stmt, SimplexStmt):
        return eval_simplex_stmt(env, stmt)
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
        simplex S1 = [A, B, C]
        simplex S2 = [D, E]
        complex C2 = glue(S1, S2) mapping {C -> D, B -> E}
    """

    ast = parse_ast(source_code)
    env = eval_program(ast)

    for name in ["S1", "S2", "C2"]:
        complex_ = lookup(env, name)
        print(f"{name}: {complex_}")

    

if __name__ == "__main__":
    main()