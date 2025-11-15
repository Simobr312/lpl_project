from lark import Lark, Token, Tree
from dataclasses import dataclass
from typing import Dict, List, FrozenSet

# Parser grammar
grammar = r"""
    ?program: statement*
    statement: simplex_stmt | complex_stmt

    simplex_stmt: "simplex" IDENT "=" "[" id_list "]"
    complex_stmt: "complex" IDENT "=" complex_expr
    complex_expr: "union" "(" IDENT "," IDENT ")" 
                | "glue" "(" IDENT "," IDENT ")" "mapping" mapping_block
                | IDENT -> identifier_ref

    id_list: IDENT ("," IDENT)*
    mapping_block: "{" mapping_list "}"
    mapping_list: mapping_pair ("," mapping_pair)*
    mapping_pair: IDENT "->" IDENT

    IDENT: /[A-Za-z_][A-Za-z0-9_]*/

    %import common.WS
    %ignore WS
"""

parser = Lark(grammar, start="program")

# AST dataclasses


type Vertex = str
type Complex = FrozenSet[Vertex]

@dataclass
class SimplexStmt:
    name: str
    vertices: List[Vertex]


@dataclass
class ComplexStmt:
    name: str
    kind: str
    args: List[str]
    mapping: Dict[str, str] | None = None

type Statement = SimplexStmt | ComplexStmt
type Program = List[Statement]


def transform_parse_tree(tree: Tree) -> Program:
    match tree:
        case Tree(
            data = "program", 
            children = [
                Tree(data = "statements", children = statements)
                ]):

            program: Program = []
            for stmt in statements:
                stmt_ast = transform_parse_tree(stmt)
                program.extend(stmt_ast)
            return program
        
        case Tree(
            data = "simplex_stmt", 
            children = [
                Token(type="IDENT", value=name),
                Tree(data="id_list", children=vertices)]
                ):
            vertices_ast = [tok.value for tok in vertices.children]
            return [SimplexStmt(
                name = name,
                vertices = vertices_ast
            )]
        
        case Tree(
            data = "complex_stmt", 
            children = [
                Token(type="IDENT", value=name),
                Tree(data="complex_expr", children=expr)]
                ):
            match expr:
                case Tree(
                    data = "union", 
                    children = [
                        Token(type="IDENT", value=K1),
                        Token(type="IDENT", value=K2)]
                        ):
                    return [ComplexStmt(
                        name = name,
                        kind = "union",
                        args = [K1, K2]
                    )]
                case Tree(
                    data = "glue", 
                    children = [
                        Token(type="IDENT", value=k1),
                        Token(type="IDENT", value=k2),
                        Tree(data="mapping_block", children=mapping_block)]
                        ):
                    mapping: Dict[str, str] = {}
                    
                    return [ComplexStmt(
                        name = name,
                        kind = "glue",
                        args = [k1, k2],
                        mapping = mapping
                    )]
                
                case _:
                    raise ValueError(f"Unexpected complex expression structure")
        case _:
            raise ValueError(f"Unexpected parse tree structure")


def parse_ast(source_code: str) -> Program:
    parse_tree = parser.parse(source_code)
    print(parse_tree.pretty())
    ast = transform_parse_tree(parse_tree)
    return ast

# Example usage
source = """
simplex S1 = [v1, v2, v3]
simplex S2 = [v4, v5]
complex C1 = union(S1, S2)
complex C2 = glue(S1, S2) mapping {v1 -> v4, v2 -> v5}
"""
ast = parse_ast(source)
print(ast)
