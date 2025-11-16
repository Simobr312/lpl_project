from lark import Lark, Token, Tree
from dataclasses import dataclass
from typing import Dict, List, FrozenSet

# Parser grammar
grammar = r"""
    ?program: statement*
    statement: simplex_stmt | complex_stmt

    simplex_stmt: "simplex" IDENT "=" "[" id_list "]"
    complex_stmt: "complex" IDENT "=" complex_expr
    complex_expr: OP "(" IDENT "," IDENT ")" ["mapping" mapping_block]

                
    id_list: IDENT ("," IDENT)*
    mapping_block: "{" mapping_list "}"
    mapping_list: mapping_pair ("," mapping_pair)*
    mapping_pair: IDENT "->" IDENT

    OP: "union" | "glue" | "join"
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
    op: str
    args: List[str]
    mapping: Dict[str, str] | None = None

type Statement = SimplexStmt | ComplexStmt
type Program = List[Statement]


def transform_parse_tree(tree: Tree) -> Program:
    match tree:
        case Tree(
            data = "program", 
            children = statements
        ):
            program: Program = []
            for stmt in statements:
                program.extend(transform_parse_tree(stmt))
            return program
        
        case Tree(data="statement", children=[stmt]):
            return transform_parse_tree(stmt)
        
        case Tree(
            data="simplex_stmt", 
            children=[
                Token(type="IDENT", value=name), 
                id_list]
            ):
            match id_list:
                case Tree(
                    data="id_list", 
                    children=ids
                ):
                    vertices = [token.value for token in ids]
                case _:
                    raise ValueError(f"Unexpected id_list structure.")
            return [SimplexStmt(name=name, vertices=vertices)]
        case Tree(
            data = "complex_stmt", 
            children = [
                Token(type="IDENT", value=name), 
                expr
            ]
        ):
            match expr:
                case Tree(
                    data="complex_expr", 
                    children=[
                        Token(type="OP", value = op),
                        Token(type="IDENT", value=id1), 
                        Token(type="IDENT", value=id2),
                        mapping_block
                        ]):

                        mapping = {}
                        
                        if mapping_block:
                            for pair in mapping_block.children[0].children:
                                mapping[pair.children[0].value] = pair.children[1].value

                        return [ComplexStmt(name=name, op=op, args=[id1, id2], mapping= mapping if mapping else None)]
        
                case _:
                    raise ValueError(f"Unexpected complex expression: {expr}")
            return [ComplexStmt(name=name, kind=kind, args=args, mapping=mapping)] 
        case _:
            raise ValueError(f"Unexpected parse tree node: {tree.pretty()}")


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
complex C2 = join(S1, S2)
complex C3 = glue(S1, S2) mapping {v1 -> v4, v2 -> v5}
"""

ast = parse_ast(source)
print(ast)
