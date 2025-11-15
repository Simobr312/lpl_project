# LANGUAGE FOR THE SPECIFIC DOMAIN OF SIMPLICIAL COMPLEXES

### Simone Riccio

# Overview
This repository will contain an implementation of a domain-specific language(DSL) for representing simplicial complexes.
The language will first be implemented in order to represent simplicial complexes in a mathematical meaningful way, with operations of glueing and union of complexes, I will also attempt to implement a way to visualize complexes of dimneison up to 3 in a 3d scene.
For the midterm version of the project I will focus on the representation of simplicial complexes and the operations to create new complexes from existing ones.
In the future, I plan to implement operations to calculate topological properties of simplicial complexes, such as homology groups.


## Language Architecture

In this section I will describe the architecture of the language, the main data objects and the operations that will be implemented.

In the matter of clarity, here is the mathematical definition of a simplicial complex which I will follow:
 
**Definitinon:** Given an ordered set $V$ called **vertices**, a **simplicial complex** $K$ is a collection of finite subsets of **V** called **simplices** such that:
- For every **simplex** $\sigma$ in $K$, every non-empty subset of $\sigma$ is also in $K$.

**Definition**: I will give some definitions of the objects that will be represented in the language:
1. **Dimension**: The dimension of a simplex $\sigma$ is defined as $dim(\sigma) = |\sigma| - 1$, where $|\sigma|$ is the number of vertices in $\sigma$. The dimension of a simplicial complex $K$ is the maximum dimension of its simplices.
2. **n-skeleton**: The n-skeleton $K^n$ of a a simplicial complex $K$ is the subcomplex consisting of all simplces $\sigma$ such that $dim(\sigma) ≤ n $.

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
    simplex S1 = [A, B, C]
    simplex S2 = [D, E]
```

It is important to note that simpleces respect the propriety that every non-empty subset of a simplex is also a simplex, and so the real meaning of 

```
    simplex S1 = [A, B, C]
```
is that S1 is a complex which contains the simplices {A, B, C}, {A, B}, {A, C}, {B, C}, {A}, {B}, {C}.

I will semantically check that the is no repeating vertices and store the ordering of the vertices, which will be used as a default ordering for the vertices.

I think there is no need to implement a "vertex" construct, since they will be represented as unique identifiers, but I will think about it more, because maybe it could be useful a way to define an ordering of the vertices, before defining simplices.

1. **Glue Simplicial Complexes**: Glue two simplicial complexes along a common subcomplex.
For example:
 ```   
    complex K3 = glue(K1, K2) mapping {A1 -> A2, B1 -> B2}
```

I will need to semantically check that K1 and K2 share the simplices specified in the glue operation.
In order to obtain the glued complex I will need to represent vertices as equivalence classes, glueing two simplicial complexes will merge the equivalence classes of the vertices which are identified by the glueing operation.
 

1. **Union of Simplicial Complexes**: Create a new simplicial complex that is the union of two simplicial complexes.
For example:
 ```   
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

My idea is not easy to implement, but I think it could be fun to try to do it, I have to find a way to choose the coordinates of the vertices in order to have connected simplices near each other and minimize intersections.

### Future Work
In the future, I plan to implement the following operations for calculating topological properties of simplicial complexes:
1. **More operations to have simplicial complexes**: Implement more operations to create simplicial complexes, such as taking the join or product of two simplicial complexes or the one point suspension.
2. **Calculate baricentric subdivision**: Implement an operation to compute the barycentric subdivision of a simplicial complex, which is classically useful for some proofs, but here I think will just be a funny operation to have.
3. **Implementing Chain Complexes and Boundary Operators**: Represent chain complexes and boundary operators to facilitate homology calculations.
4. **Calculate (Simplicial) Homology Groups**: Compute the homology groups of a simplicial complex, providing insights into its topological structure, such as connected components, holes, and voids.

# Implementation Details

The language will be implemented in Python 3.13.

## Project Structure
The files of the project will be organized as follows:
```
- /src: Contains the source code of the language implementation.

    - /visualization : Code related to 3D visualization.
- /tests: Contains test cases for the language features and operations.
- /readme.md: This readme file.
- /docs: Documentation for the language.
    - /mathematics.md: Mathematical definitions and concepts.
    - /semantics.md: Denotational semantics of the language.
```

The project will use the following libraries:
    - lark-parser: For parsing the DSL syntax.

## Sintax analysis
The parser will be implemented using the Lark library, which is a modern parsing library for Python.

Here the definition of the grammar of the language in EBNF notation:

```
program   ::= statement*
statement ::= simplex_stmt | complex_stmt | vertices_stmt
simplex_stmt ::= "simplex" ID "=" "[" id_list "]"
complex_stmt ::= "complex" ID "=" ( "union(" ID "," ID ")" | "glue(" ID "," ID ")" "mapping" mapping_block | ID )
id_list  ::= IDENT ("," IDENT)*
mapping_block ::= "{" mapping_list "}"
mapping_list ::= IDENT "->" IDENT ("," IDENT "->" IDENT)*

IDENT ::= /[a-zA-Z_][a-zA-Z0-9_]*/
````

## Semantic Analysis

