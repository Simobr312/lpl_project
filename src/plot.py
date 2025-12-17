import matplotlib
# Force TkAgg backend for cross-platform interactive 3D plotting
matplotlib.use("TkAgg")  # MUST be before pyplot import

import numpy as np
from itertools import combinations
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import minimize

from core import Complex, lookup, eval_program

# --------------------------
# Step 1: Canonical vertices
# --------------------------
def get_canonical_vertices(complex_):
    vertex_classes = complex_.get_classes()  # {rep: set of vertices}
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
# Step 3: Spring layout (3D)
# --------------------------
def assign_coordinates_canonical(vertices: list, edges: list, min_dist=0.5):
    n = len(vertices)
    vertex_index = {v: i for i, v in enumerate(vertices)}
    x0 = np.random.rand(n*3)

    def energy(x):
        coords = x.reshape((n, 3))
        E = 0
        # Edge lengths
        for v1, v2 in edges:
            i, j = vertex_index[v1], vertex_index[v2]
            dist = np.linalg.norm(coords[i] - coords[j])
            E += (dist - 1)**2
        # Repulsion to prevent overlaps
        for i in range(n):
            for j in range(i+1, n):
                dist = np.linalg.norm(coords[i] - coords[j])
                if dist < min_dist:
                    E += 1e2 * (min_dist - dist)**2
        return E

    res = minimize(energy, x0, method='L-BFGS-B')
    coords = res.x.reshape((n, 3))
    return {v: coords[i] for i, v in enumerate(vertices)}


from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def plot_complex_3d_glued(complex_):
    canonical_map = get_canonical_vertices(complex_)
    canonical_vertices = list(set(canonical_map.values()))
    edges = get_edges_canonical(complex_)
    coords = assign_coordinates_canonical(canonical_vertices, edges)

    fig = plt.figure("3D Glued Simplicial Complex")
    ax = fig.add_subplot(111, projection='3d')

    # --------------------------
    # Draw edges
    # --------------------------
    for v1, v2 in edges:
        x = [coords[v1][0], coords[v2][0]]
        y = [coords[v1][1], coords[v2][1]]
        z = [coords[v1][2], coords[v2][2]]
        ax.plot(x, y, z, 'b-', alpha=0.7)

    # --------------------------
    # Draw faces for simplices of 3+ vertices
    # --------------------------
    for simplex in complex_.maximal_simplices:
        # Convert to canonical representatives
        canonical_simplex = [canonical_map[v] for v in simplex]
        if len(canonical_simplex) < 3:
            continue  # cannot form a face

        # Get coordinates
        face_coords = [coords[v] for v in canonical_simplex]
        poly = Poly3DCollection([face_coords], alpha=0.2, facecolor='cyan', edgecolor='k')
        ax.add_collection3d(poly)

    # --------------------------
    # Draw vertices
    # --------------------------
    xs = [coords[v][0] for v in canonical_vertices]
    ys = [coords[v][1] for v in canonical_vertices]
    zs = [coords[v][2] for v in canonical_vertices]
    ax.scatter(xs, ys, zs, c='r', s=50)

    # --------------------------
    # Annotate vertices with all original names
    # --------------------------
    for rep in canonical_vertices:
        original_names = [v for v, r in canonical_map.items() if r == rep]
        label = ",".join(original_names)
        x, y, z = coords[rep]
        ax.text(x, y, z, label, color='k', size=10)

    ax.set_box_aspect([1,1,1])
    plt.show()

# --------------------------
# Step 5: Example usage
# --------------------------
if __name__ == "__main__":
    from parser import parse_ast

    source_code = """
        // Costruzione del bordo di un tetraedro (Hollow Tetrahedron)
        // Vertici: V1, V2, V3, V4

        // Definiamo le 4 facce separatamente
        complex face1 = [V1, V2, V3]
        complex face2 = [V1, V2, V4]
        complex face3 = [V2, V3, V4]
        complex face4 = [V1, V3, V4]

        // Uniamo le facce passo dopo passo
        // Base + Faccia laterale 1
        complex step1 = union(face1, face2)

        // Aggiungiamo Faccia laterale 2
        complex step2 = union(step1, face3)

        // Aggiungiamo Faccia laterale 3 (Chiudiamo la forma)
        complex tetrahedron_boundary = union(step2, face4)
    """

    ast = parse_ast(source_code)
    env = eval_program(ast)

    K = lookup(env, "tetrahedron_boundary")
    plot_complex_3d_glued(K)
