# LANGUAGE FOR THE SPECIFIC DOMAIN OF SIMPLICIAL COMPLEXES

### Simone Riccio

# Overview
This repository provides a domain-specific language (DSL) for representing and manipulating simplicial complexes.
The language is designed to model simplicial complexes in a mathematically meaningful way, allowing users to define simplices, construct complexes, perform union and gluing operations, and reason about their structure.

The current version focuses on the representation and construction of simplicial complexes.
Future iterations will explore geometric visualization (up to dimension 3) and the computation of topological invariants.
In the future, I plan to implement operations to calculate topological properties of simplicial complexes, such as homology groups.


## Language Architecture

### Mathematical Foundations

This DSL implements the core mathematical notions of simplicial complexes and enforces their structural rules through semantic checks.

A simplicial complex is defined over a totally ordered set of vertices $V$.

**Definition(Simplicial Complex):** 
A simplicial complex $K$ is a collection of finite subsets of $V$ called **simplices**, such that every non-empty subset of any simplex $\sigma \in K$ is also a simplex in $K$.

**Definition**: 
The **dimension** of a simplex $\sigma$ is defined as $dim(\sigma) = |\sigma| - 1$, where $|\sigma|$ is the number of vertices in $\sigma$.
The **dimension** of a simplicial complex $K$ is the maximum dimension among all its simplices.

### Representation

- **Vertices** are represented by a unique identifier (a string).
- **Simplices** are represented as collections of vertices (a FrozenSet).
- **Simplicial complexes** are represented as a collection of maximal simplices (those not contained in any larger simplex) along with a union-find data structure to manage vertex identifications during gluing operations.

Semantic checks ensure that:
- No simplex contains duplicate vertices.
- Gluing operations are valid, meaning the complexes share the specified simplices.

### Operations

The midterm version of the project implements the following core operations.

1. **Define Simplex**: Create a complex by specifying its vertices.
For example:
```
complex S1 = [A, B, C]
complex S2 = [D, E]
```

It is important to note that simplices respect the propriety that every non-empty subset of a simplex is also a simplex, and so the real meaning of 

```
complex S1 = [A, B, C]
```
is that S1 is a complex which contains the simplices {A, B, C}, {A, B}, {A, C}, {B, C}, {A}, {B}, {C}.

1. **Union of Simplicial Complexes**: 
Create a new simplicial complex that is the set-theoretic union of two simplicial complexes.
For example:
```   
complex K3 = union(K1, K2)
```


2. **Glue Simplicial Complexes**: 
Create a new simplicial complex by gluing two simplicial complexes along specified vertices.

For example:
```   
complex K3 = glue(K1, K2) mapping {A1 -> A2, B1 -> B2}
```

Gluing identifies specified vertices of one complex with those of another.
Internally, the implementation merges the corresponding equivalence classes of vertices, producing a valid merged complex.

It is possible to nest operations, for example:
```
complex K4 = union(K1, glue(K2, K3) mapping {C2 -> D3})
```
### Geometry and Visualization

Due to embedding constraints, the visualization may not always be topologically faithful.
The current version includes an online editor for the language which also provides a 3D visualization of the simplicial complexes defined in the code.

In order to determinate vertex coordinates, a friend of mine suggested me to treat it as a problem of spring constraints, so I implemented a simple physics engine that simulates springs between connected vertices to find a visually appealing layout in JavaScript for the 3D visualization.

The main tool for the rendering is Three.js.

### Future Work
In the future, I plan to implement the following operations to calculate topological properties of simplicial complexes:
1. **More operations to have simplicial complexes**: Implement more operations to create simplicial complexes, such as taking the join or product of two simplicial complexes or the one point suspension.
2. **Calculate baricentric subdivision**: Implement an operation to compute the barycentric subdivision of a simplicial complex, which is classically useful for some proofs, but here I think will just be a funny operation to have.
3. **Implementing Chain Complexes and Boundary Operators**: Represent chain complexes and boundary operators to facilitate homology calculations. And these will add more elements to the semantic domain of the language.
4. **Calculate (Simplicial) Homology Groups**: Compute the homology groups of a simplicial complex, providing insights into its topological structure, such as connected components, holes, and voids.

# Implementation Details

The language is implemented in Python 3.13.

## Project Structure
The files of the project will be organized as follows:
```
- /src: Contains the source code of the language implementation.
    - /parser.py: Code for parsing the DSL syntax.
    - /main.py: Main interpreter and semantic analysis.
    - /visualization : Code related to 3D visualization.
        -/frontend: Frontend code for visualization using Three.js.
        -server.py: Backend server to serve the visualization.
- /examples: Contains code examples demonstrating the language features.
- /readme.md: This readme file.
- /docs: Documentation for the language.
    - /mathematics.md: Mathematical definitions and concepts.
    - /semantics.md: Denotational semantics of the language.
```

The project will is using the following libraries:
In Python
- lark-parser: For parsing the DSL syntax.
In JavaScript
- Three.js: For 3d rendering of the simplicial complexes

## Syntax analysis
The parser is implemented using lark parsing library.

The grammar of the language is defined as follows:
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

For more details, see `docs/semantic.md` and `docs/mathematics.md`.