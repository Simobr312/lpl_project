from lark import Lark, Token, Tree
from dataclasses import dataclass
from typing import Dict, List, FrozenSet

defined_operations = {"union", "glue", "join"}

# Parser grammar
grammar = r"""
    program: statement*

    statement: "complex" IDENT "=" expr -> statement

    ?expr: operation | IDENT | vertices_list | "(" expr ")"

    operation: OP "(" expr "," expr ")" ["mapping" mapping_block]

    vertices_list: "[" id_list "]"
    id_list: IDENT ("," IDENT)*

    mapping_block: "{" mapping_list "}"
    mapping_list: mapping_pair ("," mapping_pair)*
    mapping_pair: IDENT "->" IDENT

    OP: /[a-zA-Z_][a-zA-Z0-9_]*/
    IDENT: /[A-Za-z_][A-Za-z0-9_]*/

    COMMENT: "//" /[^\n]/* | "\#" /(.|\n)*?/
    %ignore COMMENT
    %import common.WS
    %ignore WS

"""

parser = Lark(grammar, start="program")

type Ref = str

@dataclass
class ComplexLiteral:
    vertices: List[Ref]

type Expr = Ref | OpExpr

@dataclass
class OpExpr:
    op: str
    left: "Expr"
    right: "Expr"
    mapping: dict[str, str] | None


type Statement = ComplexStmt
type Program = List[Statement]

@dataclass
class ComplexStmt:
    name: str
    expr: Expr

        
def transform_expr_tree(tree: Tree) -> Expr:
    match tree:
        case Tree(data="paren", children=[sub]):
            return transform_expr_tree(sub)
        
        case Tree(data="vertices_list", children=[id_list]):
            vertices = [tok.value for tok in id_list.children]
            return ComplexLiteral(vertices=vertices)
        
        case Tree("operation", 
                  children = [op, left, right, mapping_block]):
            if op not in defined_operations:
                raise ValueError(f"Undefined operation: {op}")
            
            mapping_dict = None
            if mapping_block:
                mapping_dict = {
                    p.children[0].value: p.children[1].value
                    for p in mapping_block.children[0].children
                }

            return OpExpr(op, transform_expr_tree(left), transform_expr_tree(right), mapping_dict)
        
        case Token(type="IDENT", value=name):
            return name
        case x:
            raise ValueError(f"Unexpected parse tree for expression: {tree}")
        
def transform_command_tree(tree: Tree) -> Statement:
    match tree:
        case Tree(data="statement", children = [
            Token(type="IDENT", value = name),
            expr_tree
        ]):
            return ComplexStmt(
                name=name,
                expr = transform_expr_tree(expr_tree)
            )
            
        case _:
            raise ValueError(f"Unexpected parse tree for statement: {tree}")

def transform_program_tree(tree: Tree) -> Program:
    program: Program = []
    match tree:
        case Tree(data="program", children=statements):
            for stmt_tree in statements:
                stmt = transform_command_tree(stmt_tree)
                program.append(stmt)
            return program
        case _:
            raise ValueError(f"Unexpected parse tree for program: {tree}")


def parse_ast(source_code: str) -> Program:

    parse_tree = parser.parse(source_code)
    ast = transform_program_tree(parse_tree)

    print("AST:", ast)

    return ast
