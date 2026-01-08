from __future__ import annotations
from typing import Any, List, Dict,  Callable, Tuple, Type
from dataclasses import dataclass

from abc import ABC, abstractmethod

from parser import FunctionDecl, VertexDecl, parse_ast, Command, Expr, Program, IntLiteral
from complex import Complex, VertexName, pick_vertex
from union_find import UnionFind

@dataclass
class Loc:
    addr: int

@dataclass
class Closure:
    function: FunctionDecl
    env: Environment

type EVal = Complex | int | bool | Closure
type MVal = Complex
type DVal = EVal | Loc | Operator | int | VertexName | Closure

type Environment = Dict[str, DVal]

# == State Management == #
@dataclass
class State:
    store: Dict[int, MVal]
    next_loc: int
    vertices_order: Dict[VertexName, int]
    new_vertex_id: int 

def empty_store() -> Dict[int, MVal]:
    return {}

def empty_state() -> State:
    return State(
        store=empty_store(), 
        next_loc=0, 
        vertices_order={},
        new_vertex_id=0
        )

def allocate(state: State, value: MVal) -> tuple[Loc, State]:
    loc = Loc(state.next_loc)
    prev_store = state.store.copy()
    prev_store[loc.addr] = value
    return loc, State(store=prev_store, next_loc=state.next_loc + 1, vertices_order=state.vertices_order, new_vertex_id=state.new_vertex_id)

def update(state: State, addr: int, value: MVal) -> State:
    prev_store = state.store.copy()
    prev_store[addr] = value
    return State(store=prev_store, next_loc=state.next_loc, vertices_order=state.vertices_order, new_vertex_id=state.new_vertex_id)

def access(state: State, loc: Loc) -> MVal:
    if loc.addr in state.store:
        return state.store[loc.addr]
    raise KeyError(f"Address '{loc.addr}' not found in store")

def ensure_vertices_order(state: State, vertices: set[VertexName]) -> State:
    vo = state.vertices_order.copy()
    next_index = len(vo)

    for v in vertices:
        if v not in vo:
            vo[v] = next_index
            next_index += 1

    return State(
        store=state.store,
        next_loc=state.next_loc,
        vertices_order=vo,
        new_vertex_id=state.new_vertex_id
    )

def fresh_vertex(state: State, env: Environment) -> tuple[VertexName, State]:
    candidate : VertexName = f"__v{state.new_vertex_id}"

    if candidate in state.vertices_order:
        return candidate, State(
            store=state.store,
            next_loc=state.next_loc,
            vertices_order=state.vertices_order,
            new_vertex_id=state.new_vertex_id + 1
        )

    new_vertices_order = state.vertices_order.copy()
    new_vertices_order[candidate] = len(new_vertices_order)   # 

    return candidate, State(
        store=state.store,
        next_loc=state.next_loc,
        vertices_order=new_vertices_order,
        new_vertex_id=state.new_vertex_id + 1
    )

# == Environment Management == #

def empty_environment() -> Environment:
    return {}

def bind(env: Environment, name: str, value: DVal) -> Environment:
    new_env = env.copy()
    new_env[name] = value
    return new_env

def lookup(env: Environment, name: str) -> DVal:
    if name in env:
        return env[name]
    raise KeyError(f"Identifier '{name}' not found in environment")

@dataclass(frozen=True)
class Operator(ABC):
    name: str
    fn: Callable
    arg_types: Tuple[Type, ...]
    ret_type: Type

    @abstractmethod
    def apply(self, args: list[Any], *, mapping=None, state: State) -> Any:
        pass

class ConstructiveOperator(Operator):
    def apply(self, args: List[Any], *, mapping = None, state: State = empty_state()) -> Complex:

        if self.name == "pick_vert":
            if len(args) != 1:
                raise ValueError("pick_vert expects exactly one complex argument")
            return self.fn(args[0], state)

        if self.name == "glue":
            if mapping is None:
                raise ValueError("glue requires a mapping")
            if len(args) != 2:
                raise ValueError("glue expects exactly two complexes")
            return self.fn(args[0], args[1], mapping)

        if mapping is not None:
            raise ValueError(
                f"{self.name} does not accept a mapping"
            )

        if len(args) == 1:
            return self.fn(args[0])

        # Variadic fold
        result = args[0]
        for k in args[1:]:
            result = self.fn(result, k)
        return result

class ObservationalOperator(Operator):
    def apply(self, args: list[Any], *, mapping=None , state: State = empty_state()) -> EVal:
        if mapping is not None:
            raise ValueError(
                f"{self.name} does not accept a mapping"
            )
        
        if self.name == "betti":
            if len(args) != 2 or not isinstance(args[0], Complex) or not isinstance(args[1], int):
                raise TypeError(
                    f"{self.name} expects exactly one Complex and one integer argument"
                )
            return self.fn(args[0], args[1])

        if len(args) != 1 or not isinstance(args[0], Complex):
            raise TypeError(
                f"{self.name} expects exactly one Complex argument"
            )

        return self.fn(args[0])

class ArithmeticOperator(Operator):
    def apply(self, args: list[Any], *, mapping=None, state: State = empty_state()):
        if mapping is not None:
            raise ValueError(
                f"{self.name} does not accept a mapping"
            )

        if len(args) != len(self.arg_types):
            raise ValueError(
                f"{self.name} expects {len(self.arg_types)} arguments"
            )

        for v in args:
            if not isinstance(v, int):
                raise TypeError(
                    f"{self.name} expects integer arguments"
                )

        return self.fn(*args)

from complex import union, glue, join, dimension, num_vertices
from arithmetic import lnot, lor, land, add, sub, mul, greater, less, leq, geq 
from homology import betti

# == Enviroment and State == #
def initial_env_state() -> tuple[Environment, State]:
    env = empty_environment()

    # Constructive
    env = bind(env, "union",
        ConstructiveOperator("union", union, (Complex, Complex), Complex)
    )
    env = bind(env, "join",
        ConstructiveOperator("join", join, (Complex, Complex), Complex)
    )
    env = bind(env, "glue",
        ConstructiveOperator("glue", glue, (Complex, Complex), Complex)
    )

    env = bind(env, "pick_vert",
        ConstructiveOperator("pick_vert", pick_vertex, (Complex,), Complex)
    )

    # Observational
    env = bind(env, "dim",
        ObservationalOperator("dim", dimension, (Complex,), int)
    )
    env = bind(env, "num_vert",
        ObservationalOperator("num_vert", num_vertices, (Complex,), int)
    )

    # Arithmetic
    env = bind(env, "add",
        ArithmeticOperator("add", add, (int, int), int)
    )
    env = bind(env, "sub",
        ArithmeticOperator("sub", sub, (int, int), int)
    )
    env = bind(env, "mul",
        ArithmeticOperator("mul", mul, (int, int), int)
    )
    env = bind(env, "and",
        ArithmeticOperator("and", land, (int, int), int)
    )
    env = bind(env, "or",
        ArithmeticOperator("or", lor, (int, int), int)
    )
    env = bind(env, "not",
        ArithmeticOperator("not", lnot, (int,), int)
    )

    env = bind(env, "greater",
        ArithmeticOperator("greater", greater, (int, int), int)
    )
    env = bind(env, "less",
        ArithmeticOperator("less", less, (int, int), int)
    )

    env = bind(env, "leq",
        ArithmeticOperator("leq", leq, (int, int), int)
    )
    env = bind(env, "geq",
        ArithmeticOperator("geq", geq, (int, int), int)
    )

    env = bind(env, "betti",
        ObservationalOperator("betti", betti, (Complex, int), int)
    )

    state = empty_state()
    return env, state

# == EVALUATION == #
from parser import ComplexLiteral, OpCall, FunCall

def evaluate_expr(expr: Expr, env: Environment, state: State) -> EVal:
    # Identifier
    if isinstance(expr, str):
        dval = lookup(env, expr)

        if isinstance(dval, Loc):
            val = access(state, dval)
            if not isinstance(val, Complex):
                raise ValueError(f"{expr} is not a complex")
            return val
    
        if isinstance(dval, (Complex, int, Closure)):
            return dval

        if isinstance(dval, str):
            uf = UnionFind[VertexName]()
            uf.add(dval)
            return Complex({frozenset({dval})}, uf)

        raise ValueError(f"Identifier '{expr}' is not a value")
    
    # Complex Literal
    if isinstance(expr, ComplexLiteral):
        simplex = frozenset(expr.vertices)

        uf = UnionFind[VertexName]()
        for v in expr.vertices:
            uf.add(v)

        return Complex({simplex}, uf)
    
    # Integer Literal
    if isinstance(expr, IntLiteral):
        return expr.value
    
    # Operator Call Expression
    if isinstance(expr, OpCall):
        op = lookup(env, expr.op)

        if not isinstance(op, Operator):
            raise ValueError(f"{expr.op} is not an operator")

        arg_vals = [evaluate_expr(a, env, state) for a in expr.args]

        return op.apply(arg_vals, mapping=expr.mapping, state=state)

    # Function Call Expression
    if isinstance(expr, FunCall):
        dval = lookup(env, expr.name)
        if not isinstance(dval, Closure):
            raise ValueError(f"{expr.name} is not a function")

        closure: Closure = dval
        params = closure.function.params
        args = expr.args

        if len(args) != len(params):
            raise ValueError(
                f"Function {expr.name} expects {len(params)} args, got {len(args)}"
            )

        arg_vals = [evaluate_expr(a, env, state) for a in args]

        call_env = closure.env

        for p, v in zip(params, arg_vals):
            call_env = bind(call_env, p, v)

        return evaluate_expr(closure.function.body, call_env, state)
        
    raise TypeError(f"Unknown expression type: {expr}")


from parser import ComplexDecl, Assign, IfCmd, WhileCmd
def execute_command(cmd: Command, env: Environment, state: State) -> tuple[Environment, State]:
    match cmd:
        case ComplexDecl(name=name, expr=expr):
            complex_val = evaluate_expr(expr, env, state)

            if not isinstance(complex_val, Complex):
                raise ValueError(f"Expression does not evaluate to a complex")

            state1 = ensure_vertices_order(state, complex_val.vertices)
            
            loc, state2 = allocate(state1, complex_val)

            env1 = bind(env, name, loc)
            return env1, state2
        
        case VertexDecl(name):
            v, state1 = fresh_vertex(state, env)
            env1 = bind(env, name, v)

            return env1, state1
        
        case Assign(name=name, expr=expr):
            dval = lookup(env, name)
            match dval:
                case Loc(addr=addr) as loc:
                    value = evaluate_expr(expr, env, state)

                    if not isinstance(value, Complex):
                        raise ValueError(f"Expression does not evaluate to a complex")
                    
                    state1 = update(state, addr, value)
                    return env, state1
                case _:
                    raise ValueError(f"Identifier '{name}' is not a variable")

        case IfCmd(cond, then_branch, else_branch):
            cond_val = evaluate_expr(cond, env, state)

            print(cond_val)

            if not isinstance(cond_val, int):
                raise ValueError("Condition expression does not evaluate to an integer")
            
            saved_next_loc = state.next_loc

            if cond_val:
                _, state1 = execute_command_seq(then_branch, env, state)
                #Restore next_loc after block
                state2 = State(store = state1.store, next_loc = saved_next_loc, vertices_order = state1.vertices_order, new_vertex_id = state1.new_vertex_id)
                return env, state2
            else:
                _, state1 = execute_command_seq(else_branch, env, state)
                state2 = State(store = state1.store, next_loc = saved_next_loc, vertices_order = state1.vertices_order, new_vertex_id = state1.new_vertex_id)
                return env, state2

        case WhileCmd(cond, body):
            current_state = state

            max_iterations = range(10000000)  # Prevent infinite loops
            for _ in max_iterations:  
                cond_val = evaluate_expr(cond, env, current_state)

                if not isinstance(cond_val, int):
                    raise ValueError("Condition must be integer")

                if not cond_val:
                    return env, current_state

                _, current_state = execute_command_seq(body, env, current_state)

            raise RuntimeError("Maximum iterations reached in while loop, possible infinite loop")

        case FunctionDecl(name, params, body):
            closure = Closure(function=cmd, env=env)
            new_env = bind(env, name, closure)
            return new_env, state    
        
        case _:
            raise ValueError(f"Command type '{type(cmd)}' not implemented yet")

def execute_command_seq(seq: Program, env: Environment, state: State) -> tuple[Environment, State]:
    current_env = env
    current_state = state

    for cmd in seq:
        current_env, current_state = execute_command(cmd, current_env, current_state)

    return current_env, current_state

def eval_program(ast: Program) -> tuple[Environment, State]:
    env, state = initial_env_state()
    env1, state1 = execute_command_seq(ast, env, state)
    return env1, state1

if __name__ == "__main__":
    sample_program = """
    complex K = [a,b,c]

    function f(x) = union(x, K)

    complex L = [d,e]
    complex M = f(L)
    """
    
    cmds = parse_ast(sample_program)
    env, state = initial_env_state()
    env, state = execute_command_seq(cmds, env, state)

    print("Final Environment:", env)
    print("Final State:", state)