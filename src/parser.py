from lark import Lark, Token, Tree
from dataclasses import dataclass
from typing import Dict, List, FrozenSet

defined_operations = {"union", "glue"}

# Parser grammar
grammar = r"""
    ?program: statement*

    statement: "complex" IDENT "=" expr | "complex" IDENT "=" vertices_list

    ?expr: operation | IDENT | "(" expr ")"

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

@dataclass
class Ref:
    name: str

@dataclass
class OpExpr:
    op: str
    left: "Expr"
    right: "Expr"
    mapping: dict[str, str] | None

type Expr = Ref | OpExpr

@dataclass
class ComplexDeclVtx:
    name: str
    vertices: List[Ref]


@dataclass
class ComplexDeclExpr:
    name: str
    expr : Expr

type Statement = ComplexDeclVtx | ComplexDeclExpr
type Program = List[Statement]


def transform_parse_tree(tree: Tree) -> Program | Expr:
    match tree:
        case Tree(
            data = "program", 
            children = statements
        ):
            program: Program = []
            for stmt in statements:
                program.extend(transform_parse_tree(stmt))
            return program
        
        case Tree(
            data = "statement", 
            children = [Token("IDENT", name), expr]):

            if expr.data == "vertices_list":
                vtx_decls = transform_parse_tree(expr)
                for decl in vtx_decls:
                    decl.name = name
                return vtx_decls
            else:
                expr_ast = transform_parse_tree(expr)
                return [ComplexDeclExpr(name=name, expr=expr_ast)]
        
        case Tree(
            data = "vertices_list", 
            children = [id_list]
            ):
            vertices = [token.value for token in id_list.children]
            return [ComplexDeclVtx(name="", vertices=vertices)]
        
        case Tree(
            data = "expr", 
            children = [operation]
            ):
            return transform_parse_tree(operation)
        
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

            return OpExpr(op, transform_parse_tree(left), transform_parse_tree(right), mapping_dict)
        
        case Token("IDENT", name):
            return Ref(name)
        
        case Token("expr", expr):
            return transform_parse_tree(expr)
        
        case Tree("paren", [sub]):
            return transform_parse_tree(sub)
            
        case _:
            raise ValueError(f"Unexpected parse tree node: {tree.pretty()}")


def parse_ast(source_code: str) -> Program:

    parse_tree = parser.parse(source_code)
    ast = transform_parse_tree(parse_tree)

    return ast