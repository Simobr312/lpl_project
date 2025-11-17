from lark import Lark, Token, Tree
from dataclasses import dataclass
from typing import Dict, List, FrozenSet

# Parser grammar
grammar = r"""
    ?program: statement*
    statement:  complex_stmt

    complex_stmt: "complex" IDENT "=" (complex_expr | vertices_list)
    complex_expr: OP "(" IDENT "," IDENT ")" ["mapping" mapping_block]

                
    vertices_list: "[" id_list "]"
    id_list: IDENT ("," IDENT)*
    mapping_block: "{" mapping_list "}"
    mapping_list: mapping_pair ("," mapping_pair)*
    mapping_pair: IDENT "->" IDENT

    OP: /[A-Za-z_][A-Za-z]*/
    IDENT: /[A-Za-z_][A-Za-z0-9_]*/

    %import common.WS
    %ignore WS
"""

parser = Lark(grammar, start="program")

# AST dataclasses


type VertexName = str

@dataclass
class ComplexDecl:
    name: str
    vertices: List[VertexName]


@dataclass
class ComplexStmt:
    name: str
    op: str
    args: List[str]
    mapping: Dict[str, str] | None = None

type Statement = ComplexDecl | ComplexStmt
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
        
        case Tree(data="complex_stmt", 
                  children=[
                      Token(type="IDENT", 
                            value=name), 
                            rhs
            ]):
            match rhs:

                case Tree(data="vertices_list", children=[id_list]):
                    vertices = [tok.value for tok in id_list.children]
                    return [ComplexDecl(name=name, vertices=vertices)]

                case Tree(
                    data="complex_expr",
                    children=[
                        Token(type="OP", value=op),
                        Token(type="IDENT", value=id1),
                        Token(type="IDENT", value=id2),
                        mapping_block
                    ]
                ):
                    mapping = None
                    if mapping_block:
                        mapping = {
                            pair.children[0].value: pair.children[1].value
                            for pair in mapping_block.children[0].children
                        }
                    return [ComplexStmt(name=name, op=op, args=[id1, id2], mapping=mapping)]

                case _:
                    raise ValueError(f"Unexpected RHS for complex_stmt:")
        case _:
            raise ValueError(f"Unexpected parse tree node: {tree.pretty()}")


def parse_ast(source_code: str) -> Program:

    parse_tree = parser.parse(source_code)
    ast = transform_parse_tree(parse_tree)

    return ast

source = """
complex S1 = [A, B, C]"""

print(parse_ast(source))
