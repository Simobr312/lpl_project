# LANGUAGE FOR THE SPECIFIC DOMAIN OF SIMPLICIAL COMPLEXES

### Simone Riccio

# Overview
This project defines a domain-specific programming language for simplicial complexes, designed to combine:

- formal mathematical correctness,
- high-level topological abstractions,
- imperative control flow,
- and interactive geometric visualization.

The language allows users to **construct, combine, inspect, and reason** about **simplicial complexes** using a syntax and semantic model inspired by both algebraic topology and classical programming languages.

A web-based 3D visualization interface is provided to render simplicial complexes defined in the language.

## Design Philosophy
The language is built around three guiding principles:

- **Mathematical Faithfulness**
All constructs correspond directly to standard notions in algebraic topology.

- **Explicit State, Minimal Types**
Simplicial complexes are stored in memory and manipulated via references.
All observable values are integers.

- **Separation of Construction and Observation**
Complexes are constructed and stored; numerical invariants are observed.

## Language Architecture

### Mathematical Foundations

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


### Core Semantic Model
The language follows a **store-based denotational semantics**.

- **Semantic Domains**

- **Environment** Maps identifiers to denotable values.

- **Store** Maps memory locations to storable values.

Values in the language are either:
 - **Denotable Values**: Integer or memory locations.
 - **Storable Values**: Simplicial complexes.

Operations are divided into:
1. **Constructive Operations**: Create new simplicial complexes from existing ones.
2. **Observational Operations**: Calculate properties of simplicial complexes.

### Constructive Operations

1. **Define Simplex**:
```
complex S1 = [A, B, C]
complex S2 = [D, E]
```

It is important to note that simplices respect the propriety that every non-empty subset of a simplex is also a simplex, and so the real meaning of 

```
complex S1 = [A, B, C]
```
is that S1 is a complex which contains the simplices {A, B, C}, {A, B}, {A, C}, {B, C}, {A}, {B}, {C}.

2. **Union of Simplicial Complexes**: 
Create a new simplicial complex that is the set-theoretic union of two simplicial complexes.
For example:
```   
complex K3 = union(K1, K2)
```


3. **Glue Simplicial Complexes**: 
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

There are other operations which are not discussede here for brevity, for more details see `docs/semantics.md`.

## Observational Operations

1. **Calculate Dimension**:
Calculate the dimension of a simplicial complex.
   ```
   dim(K1)
   ```
   return di dimension of the complex $K$.
2. **Calculate Betti Numbers**:
Calculate the Betti numbers of a simplicial complex.
   ```
   betti(K1, [n])
   ```
   returns the n-th Betti number of the complex $K$.

there are other operations which are not discussed here for brevity, for more details see `docs/semantics.md`.

## Control Flow Structures

All conditions are integer-valued: zero = false, non-zero = true.

1. **Conditional Statements**:
```
if condition then
   statement1
else
   statement2
endif
```

The `condition` could be any expression that evaluates to an integer, for example an observation operation like `dim(K)`.

2. **Loops**:
```
while condition do
   statement
endwhile
```

## Geometry and Visualization

Due to embedding constraints, the visualization may not always be topologically faithful.
The current version includes an online editor for the language which also provides a 3D visualization of the simplicial complexes defined in the code.

In order to determine vertex coordinates, a friend of mine suggested me to treat it as a problem of spring constraints, so I implemented a simple physics engine that simulates springs between connected vertices to find a visually appealing layout in JavaScript for the 3D visualization.

The main tool for the rendering is Three.js.

# Implementation Details

The language is implemented in Python 3.13.

## Project Structure
The files of the project will be organized as follows:
```
- /src: Contains the source code of the language implementation.
    - /parser.py: Code for parsing the DSL syntax.
    - /core.py: Main interpreter and semantic analysis.
    - /homology.py: Code for computing homological invariants.
    - /visualization : Code related to 3D visualization.
        -/frontend: Frontend code for visualization using Three.js.
        -server.py: Backend server to serve the visualization.
- /examples: Contains code examples demonstrating the language features.
- /readme.md: This readme file.
- /docs: Documentation for the language.
    - /mathematics.md: Mathematical definitions and concepts.
    - /semantics.md: Denotational semantics of the language.
```

The project uses the following libraries:

In Python
- lark-parser: For parsing the DSL syntax.

- uvicorn and fastapi: For serving the web interface.

In JavaScript
- Three.js: For 3d rendering of the simplicial complexes

## Syntax analysis
The parser is implemented using lark parsing library.

The grammar of the language is defined as follows:
```
?program: statement*
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
````

For more details, see `docs/semantic.md` and `docs/mathematics.md`.

## Installation instructions

To set up the environment for running the language interpreter and use the web interface locally, follow these steps:
1. **Install the required Python packages**:
   Install the necessary Python packages using pip(possibly in a virtual environment):
   ```
   pip install -r requirements.txt
   ```
2. **Run the web server**:
   Navigate to the `src/` directory and start the web server:
    ```
    cd src/
    uvicorn server:app --reloadx
    ```

3. **Access the web interface**:
   Open your web browser and go to `http://127.0.0.1:8000/index.html` to access the web interface for visualizing simplicial complexes.

4. **Run examples**:
   Copy the contents from /examples into the web interface code editor.

## Web Interface
The web interface lets you:
- Write DSL code
- Run them
- Inspect the defined simplicial complexes
- Render them in the 3D viewer

