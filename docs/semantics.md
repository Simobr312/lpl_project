# Semantic Analysis for the DSL for Simplicial Complexes

The mathematical definitions of simplicial complexes and related concepts are provided in the documentation (see [here](docs/mathematics.md)).

## Domains
   The main domain of the language is the set of simplicial complexes.
   \[
         Complex := \{ K : K \text{ is a simplicial complex} \}
   \]

   A program denotes an enviroment mapping identifiers to simplicial complexes: ***Env*** : ***Identifier*** -> ***Complex***

  Let $\rho$ be an environment.
  $\rho(id)$ denotes the simplicial complex associated to the identifier $id$ in the environment $\rho$.
  The update of an environment $\rho$ with a new binding $x \mapsto K$ is denoted as $\rho[K / x]$ is the enviroment:

  \[
        \rho[K / x](y) =
        \begin{cases}
            K & \text{if } y = x \\
            \rho(y) & \text{otherwise}
        \end{cases}
  \]

## Denotational Semantics

A program is a sequence of statements $s_1; s_2; \ldots; s_n$.
Given the empty environment $\rho_0$, the semantics of a program is defined as:
\[
      \llbracket s_1; s_2; \ldots; s_n \rrbracket(\rho_0) = \rho_n
\]

**Simplex Statement**
\[
      \llbracket simplex \ S = [v_1, v_2, \ldots, v_k] \rrbracket(\rho) = \rho[ \sigma(\{v_1, v_2, \ldots, v_k\}) / S]
\]
   
**Union Statement**
\[
      \llbracket complex \ C = union(A, B) \rrbracket(\\rho) = \rho[(\rho(A) \cup \rho(B))/ C]
\]


**Glue Statement**
\[
      \llbracket complex \ C = glue(A, B) \ mapping \ \{v_{A1} \to v_{B1}, v_{A2} \to v_{B2}, \ldots, v_{An} \to v_{Bn}\} \rrbracket(\rho) = \rho[K / C]
\]
where $K$ is the simplicial complex obtained by glueing $\rho(A)$ and $\rho(B)$ along the identified vertices.

