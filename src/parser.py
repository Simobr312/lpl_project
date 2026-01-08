from lark import Lark, Token, Tree
from dataclasses import dataclass
from typing import Dict, List, FrozenSet

constructive_operations = {"union", "glue", "join", "dimension", "num_simplices", "num_vertices", "pick_vert"}
observational_operations = {"dim", "num_vert" }
other_operations = {"add", "sub", "mul", "not", "and", "or", "greater", "less", "leq", "geq", "betti"}

defined_operations = constructive_operations | observational_operations | other_operations
op_regex = "|".join(defined_operations)

# Parser grammar
grammar = fr"""
    program: command*

    ?command: complex_decl
            | assign
            | vertex_decl
            | if_cmd
            | while_cmd
            | function_decl

    complex_decl: "complex" IDENT "=" expr
    assign: IDENT "<-" expr
    vertex_decl: "vertex" IDENT

    if_cmd: "if" expr "then" command* ["else" command*] "endif"
    while_cmd: "while" expr "do" command* "endwhile"

    function_decl: "function" IDENT "(" param_list? ")" "=" expr

    ?expr: op_call
        | function_call
        | IDENT
        | vertices_list
        | NUMBER
        | "(" expr ")"

    op_call: OP "(" arg_list? ")" ["mapping" mapping_block]

    function_call: IDENT "(" arg_list? ")"
    
    vertices_list: "[" id_list "]"
    id_list: IDENT ("," IDENT)*

    param_list: IDENT ("," IDENT)*
    arg_list: expr ("," expr)*

    mapping_block: mapping_list
    mapping_list: mapping_pair ("," mapping_pair)*
    mapping_pair: IDENT "->" IDENT
            
    OP: /{op_regex}/
    IDENT: /[A-Za-z_][A-Za-z0-9_]*/
    NUMBER: /[0-9]+/

    COMMENT: "//" /[^\n]/*  "\n"
    %ignore COMMENT
    WS: /[ \t\f\r\n]+/
    %ignore WS
"""

parser = Lark(grammar, start="program")

from dataclasses import dataclass
from typing import List, Dict, Optional, Union

type Ref = str

@dataclass
class ComplexLiteral:
    vertices: List[Ref]

@dataclass
class OpCall:
    op: str
    args: List["Expr"]
    mapping: Dict[str, str] | None

@dataclass
class IntLiteral:
    value: int

@dataclass
class FunCall:
    name: str
    args: List["Expr"]

Expr = Ref | ComplexLiteral | OpCall | IntLiteral | FunCall

# == Commands == #

@dataclass
class ComplexDecl:
    name: str
    expr: Expr

@dataclass
class Assign:
    name: str
    expr: Expr

@dataclass
class VertexDecl:
    name: str

@dataclass
class IfCmd:
    cond: Expr
    then_branch: List["Command"]
    else_branch: List["Command"]

@dataclass
class WhileCmd:
    cond: Expr
    body: List["Command"]

@dataclass
class FunctionDecl:
    name: str
    params: List[str]
    body: Expr

@dataclass
class ReturnCmd:
    expr: Expr

type Command = ComplexDecl | Assign | VertexDecl | IfCmd | WhileCmd | FunctionDecl | ReturnCmd

type Program = List[Command]


def transform_expr_tree(tree) -> Expr:
    match tree:
        case Tree("vertices_list", [id_list]):
            return ComplexLiteral(
                [tok.value for tok in id_list.children]
            )

        case Tree("op_call", children):
            op = children[0].value

            args = []
            mapping = None

            if len(children) >= 2 and isinstance(children[1], Tree) and children[1].data == "arg_list":
                args = [transform_expr_tree(a) for a in children[1].children]

            if children and isinstance(children[-1], Tree) and children[-1].data == "mapping_block":
                mapping = {
                    p.children[0].value: p.children[1].value
                    for p in children[-1].children[0].children
                }

            return OpCall(op, args, mapping)

        case Tree("function_call", [Token("IDENT", name), *rest]):
            if rest:
                arg_list_tree = rest[0]
                args_exprs = [transform_expr_tree(a) for a in arg_list_tree.children]
            else:
                args_exprs = []
            return FunCall(name, args_exprs)


        case Token("IDENT", name):
            return name

        case Token("NUMBER", value):
            return IntLiteral(int(value))

        case Tree("expr", [sub]):
            return transform_expr_tree(sub)

        case _:
            raise ValueError(f"Unexpected expression tree: {tree}")

        
def transform_command_tree(tree) -> Command:
    match tree:
        case Tree("complex_decl", [Token("IDENT", name), expr]):
            return ComplexDecl(name, transform_expr_tree(expr))

        case Tree("assign", [Token("IDENT", name), expr]):
            return Assign(name, transform_expr_tree(expr))
        
        case Tree("vertex_decl", [Token("IDENT", name)]):
            return VertexDecl(name)

        case Tree("if_cmd", children):
            cond = transform_expr_tree(children[0])
            then_cmds = []
            else_cmds = []

            i = 1
            while i < len(children) and children[i].data == "command":
                then_cmds.append(transform_command_tree(children[i]))
                i += 1

            while i < len(children):
                else_cmds.append(transform_command_tree(children[i]))
                i += 1

            return IfCmd(cond, then_cmds, else_cmds)

        case Tree("while_cmd", children):
            cond = transform_expr_tree(children[0])
            body = [transform_command_tree(c) for c in children[1:]]
            return WhileCmd(cond, body)

        case Tree("function_decl", children):
            name = children[0].value
            params = []
            body = None

            if isinstance(children[1], Tree) and children[1].data == "param_list":
                params = [tok.value for tok in children[1].children]
                body = transform_expr_tree(children[2])
            else:
                body = transform_expr_tree(children[1])

            return FunctionDecl(name, params, body)

        case Tree("return_cmd", [expr]):
            return ReturnCmd(transform_expr_tree(expr))

        case _:
            raise ValueError(f"Unexpected command tree: {tree}")


def parse_ast(source_code: str) -> Program:
    parser = Lark(grammar, start="program")
    tree = parser.parse(source_code)

    return [
        transform_command_tree(cmd)
        for cmd in tree.children
    ]

if __name__ == "__main__":
    sample_code = """
    complex K = [a,b,c]
    complex L = [b,c,d]

    complex M = union(K, L)

    if dim(M) then
        M <- glue(M, K) mapping { b->b }
    else
    
    endif
    """

    ast = parse_ast(sample_code)
    for cmd in ast:
        print(cmd)