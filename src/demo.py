"""
Demo program for the DSL for Simplicial Complexes

This script exercises:
- complex declarations
- union, glue, join
- observational operators (dimension, num_vertices, num_simplices)
- assignments
- if / while control flow (integer-based)
- environment–store behavior
"""

from parser import parse_ast
from core import (
    initial_env_state,
    execute_command_seq,
)

# ============================================================
# Demo DSL program
# ============================================================

demo_program = """
// ------------------------------------------------------------
// Basic simplex declarations
// ------------------------------------------------------------
complex T = [A, B, C]          // 2-simplex (triangle)
complex E = [C, D]             // 1-simplex (edge)
complex V = [E]                // 0-simplex (vertex)

// ------------------------------------------------------------
// Union
// ------------------------------------------------------------
complex U1 = union(T, E)
complex U2 = union(U1, V)

// ------------------------------------------------------------
// Join
// ------------------------------------------------------------
complex J = join(T, V)

// ------------------------------------------------------------
// Glue (identify vertices)
// ------------------------------------------------------------
complex G = glue(T, E) mapping { C -> C }

// ------------------------------------------------------------
// Observational operators
// ------------------------------------------------------------
complex X = T
if dimension(X) then
    X <- union(X, V)
else
    X <- T
endif

// ------------------------------------------------------------
// While loop (integer condition)
// ------------------------------------------------------------
while num_vertices(X) do
    X <- union(X, [Z])
endwhile
"""

# ============================================================
# Run the program
# ============================================================

if __name__ == "__main__":
    print("===== DSL DEMO PROGRAM =====")
    print(demo_program)
    print("============================\n")

    # Parse
    commands = parse_ast(demo_program)

    # Initialize environment and state
    env, state = initial_env_state()

    # Execute
    env, state = execute_command_seq(commands, env, state)

    # ========================================================
    # Inspect results
    # ========================================================

    print("===== FINAL ENVIRONMENT =====")
    for name, dval in env.items():
        print(f"{name} -> {dval}")

    print("\n===== FINAL STORE =====")
    for addr, value in state.store.items():
        print(f"@{addr} -> {value}")

    print("\n===== VERTEX ORDER =====")
    for v, i in state.vertices_order.items():
        print(f"{v}: {i}")
    print("============================")