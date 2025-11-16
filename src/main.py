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
    new_uf = complex1.uf.merge(complex2.uf)
    all_simplices = complex1.maximal_simplices.union(complex2.maximal_simplices)

    return Complex(all_simplices, new_uf)


def glue(complex1: Complex, complex2: Complex, mapping: Dict[VertexName, VertexName]) -> Complex:
    new_uf = complex1.uf.merge(complex2.uf)

    for a, b in mapping.items():
        new_uf.union(a, b)

    all_simplices: Set[Simplex] = set()

    for simplex in complex1.maximal_simplices | complex2.maximal_simplices:
        all_simplices.update(faces(simplex))

    maximal = set(all_simplices)
    for s1 in all_simplices:
        for s2 in all_simplices:
            if s1 != s2 and s1.issubset(s2):
                maximal.discard(s1)

    return Complex(maximal, new_uf)


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
        simplex S2 = [D, E, F]
        complex C1 = union(S1, S2)
        complex C2 = glue(S1, S2) mapping {B -> D, C -> E}
    """

    ast = parse_ast(source_code)
    env = eval_program(ast)


    for name in ["S1", "S2", "C1", "C2"]:
        complex_ = lookup(env, name)
        print(f"{name}: {complex_}")

    

if __name__ == "__main__":
    main()