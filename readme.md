# IMPLEMENTATION OF A LANGUAGE FOR THE SPECIFIC DOMAIN OF SIMPLICIAL COMPLEXES

### Simone Riccio

## Overview
This repository will contain an implementation of a domain-specific language(DSL) for representing simplicial complexes.
The language will first be implemented in order to represent simplicial complexes in a mathematical meaningful way, with operations of glueing and union of complexes. I will do some work in order to let the complexes of dimension 2 and 3 be visualized.
But the main goal of this project is to calculate topological proprieties of the represented simplicial complexes: such as homology groups, Betti numbers, Euler characteristic, etc.
In order to do that I will also need to add the possibility to represent chain complexes and boundary operators.
I think I will do the implementation of these later after the midterm evaluation.

## Language Architecture

In this section I will describe the architecture of the language, the main data objects and the operations that will be implemented.

For clarity, here is the mathemtical definition of a simplicial complex which I will follow:
 
**Definitinon:** Given an ordered set $V$ called **vertices**, a **simplicial complex ** $K$ on is a collection of finite subsets of **V** called **simplices** such that:
- For every **simplex** σ in $K$, every non-empty subset of σ is also in $K$.

**Definition**: I will give some definitions of the objects that will be represented in the language:
1. **Dimension**: The dimension of a simplex σ is defined as dim(σ) = |σ| - 1, where |σ| is the number of vertices in σ. The dimension of a simplicial complex K is the maximum dimension of its simplices.
2. **n-skeleton**: The n-skeleton K_n of a a simplicial complex K is the subcomplex consisting of all simplces σ such that dim(σ) ≤ n.

**Vertex**: A vertex will be represented as a unique identifier, such as an integer or a string. 
In order to do topology calculations I will also need to store the total ordering of the vertices. 

**Simplex**: A simplex will be represented as a collection of vertices.

**Simplicial Complex**: A simplicial complex will be represented as a collection of simplices.
In order to ensure that the simplicial complex is valid, the operations which will give simplicial complexes will semantically prove the definition of a simplicial complex.

The geometry of these objects will be considered only for visualization purposes and it will be clarified after.

### Operations

The following operations will be implemented in the MIDTERM version of the project:

1. **Define Simplex**: Create a simplex by specifying its vertices.
For example:
 ```
    simplex S1 = {A, B, C}
    simplex S2 = {B, C}
```

I will semantically check that the is no repeating vertices in the definition of simplex and store the ordering of the vertices, which will be used as a default ordering for the vertices.
I think there will be no need to implement a definition of vertex, since they will be represented as unique identifiers, but I will think about it more, because maybe it could be useful a way to define an ordering of the vertices, before defining simplices.

1. **Glue Simplicial Complexes**: Glue two simplicial complexes along a common subcomplex.
For example:
 ```   complex K1 = {S1, S2}
    complex K2 = {S3, S4}
    complex K3 = glue(K1, K2) along {S2, S4}
```

1. **Union of Simplicial Complexes**: Create a new simplicial complex that is the union of two simplicial complexes.
For example:
 ```   complex K1 = {S1, S2}
    complex K2 = {S3, S4}
    complex K3 = union(K1, K2)
```

The glue operation is geometrically more meaningful than the union operation, but I will implement both for completeness.

### Geometry and Visualization

My idea will be to have a 3d camera with basic controls to rotate, zoom in and out the scene.
The visualization will be done only for simplicial complexes of dimension $\leq$ 3 and even for these will be difficult.

There is a theorem which states that every simplicial complex of dimension 1, which is a way of representing graphs, can be embedded in the plane without crossings.

But the strongest result I know is that:
**Theorem**: 
Every simplicial complex $K$ such that $dim(K) = n$ can be embedded in $\mathbb{R}^{2n+1}$. 

This means that, even if I found a way to visualize simplicial complexes of dimension 2 and 3, the visualization will not be always topologically faithful, since there could be intersections between simplices which are not present in the actual simplicial complex.

### Future Work
In the future, I plan to implement the following operations for calculating topological properties of simplicial complexes:
1. **Calculate baricentric subdivision**: Implement an operation to compute the barycentric subdivision of a simplicial complex, which is classically useful for some proofs, but here I think will just be a funny operation to have.
2. **Implementing Chain Complexes and Boundary Operators**: Represent chain complexes and boundary operators to facilitate homology calculations.
3. **Calculate (Simplicial) Homology Groups**: Compute the homology groups of a simplicial complex, providing insights into its topological structure, such as connected components, holes, and voids.


