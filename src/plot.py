import numpy as np
from itertools import combinations
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from main import Complex, lookup, eval_program

# --------------------------
# Step 1: Canonical vertices
# --------------------------
def get_canonical_vertices(complex_):
    """
    Returns a mapping from each vertex to its canonical representative
    according to the union-find structure.
    """
    vertex_classes = complex_.get_classes()  # {repr: set of vertices}
    canonical_map = {}
    for rep, vertices in vertex_classes.items():
        for v in vertices:
            canonical_map[v] = rep
    return canonical_map

# --------------------------
# Step 2: Edges using canonical vertices
# --------------------------
def get_edges_canonical(complex_):
    edges = set()
    canonical_map = get_canonical_vertices(complex_)
    
    for simplex in complex_.maximal_simplices:
        canonical_simplex = [canonical_map[v] for v in simplex]
        for a, b in combinations(canonical_simplex, 2):
            if a != b:
                edges.add(tuple(sorted([a, b])))
    return list(edges)

# --------------------------
# Step 3: Spring layout
# --------------------------
def assign_coordinates_canonical(vertices: list, edges: list):
    n = len(vertices)
    vertex_index = {v: i for i, v in enumerate(vertices)}
    x0 = np.random.rand(n*3)

    def energy(x):
        coords = x.reshape((n, 3))
        E = 0
        for v1, v2 in edges:
            i, j = vertex_index[v1], vertex_index[v2]
            dist = np.linalg.norm(coords[i] - coords[j])
            E += (dist - 1)**2
        return E

    from scipy.optimize import minimize
    res = minimize(energy, x0)
    coords = res.x.reshape((n, 3))
    return {v: coords[i] for i, v in enumerate(vertices)}

# --------------------------
# Step 4: Plotting
# --------------------------
def plot_complex_3d_glued(complex_):
    canonical_map = get_canonical_vertices(complex_)
    canonical_vertices = list(set(canonical_map.values()))

    edges = get_edges_canonical(complex_)
    coords = assign_coordinates_canonical(canonical_vertices, edges)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Draw edges
    for v1, v2 in edges:
        x = [coords[v1][0], coords[v2][0]]
        y = [coords[v1][1], coords[v2][1]]
        z = [coords[v1][2], coords[v2][2]]
        ax.plot(x, y, z, 'b-')

    # Draw vertices
    xs = [coords[v][0] for v in canonical_vertices]
    ys = [coords[v][1] for v in canonical_vertices]
    zs = [coords[v][2] for v in canonical_vertices]
    ax.scatter(xs, ys, zs, c='r', s=50)

    # Annotate vertices with all original names
    for rep in canonical_vertices:
        original_names = [v for v, r in canonical_map.items() if r == rep]
        label = ",".join(original_names)
        x, y, z = coords[rep]
        ax.text(x, y, z, label, color='k', size=10)

    ax.set_box_aspect([1,1,1])
    plt.show()

# --------------------------
# Step 5: Example usage with your code
# --------------------------
if __name__ == "__main__":
    from parser import parse_ast
    # assuming you have eval_program, lookup, Complex etc. from your code

    source_code = """
        complex a = [v1, v2]
        complex b = [v2, v3]
        complex c = [v3, v1]

        complex D = [v4, v5, v6]

        complex A = union(a, b)
        complex B = union(A, c)

        complex K = glue(B, D) mapping {v1 -> v4, v2 -> v5}

        complex L = [v7, v8, v9, v10]

        complex M = glue(K, L) mapping {v3 -> v7, v6 -> v10}

    """

    ast = parse_ast(source_code)
    env = eval_program(ast)

    K = lookup(env, "M")
    plot_complex_3d_glued(K)
