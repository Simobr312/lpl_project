# Semantic Analysis for the DSL for Simplicial Complexes

The mathematical definitions of simplicial complexes and related concepts are provided in the documentation (see [here](docs/mathematics.md)).

## Domains
The main domain of the language is the set of simplicial complexes.

$$
      Complex := \{K : K \text{is a simplicial complex}\}
$$

A program denotes an enviroment mapping identifiers to simplicial complexes: 
***Env*** := ***Identifier*** -> ***Complex***

Let $\rho \in \text{Env}$
$\rho(x)$ denotes the simplicial complex associated to the identifier $x$ in the environment $\rho$.
The update of an environment $\rho$ with a new binding $x \mapsto K$ is denoted as $\rho[K / x]$ is the enviroment:

$$
      \rho[K / x](y) =
      \begin{cases}
      K & \text{if } y = x \\
      \rho(y) & \text{otherwise}
      \end{cases}
$$

## Denotational Semantics

A program is a sequence of statements $s_1; s_2; \ldots; s_n$.
Given the empty environment $\rho_0$, the semantics of a program is defined as:

$$
 \left[ s_1; s_2; \ldots; s_n \right](\rho_0) = \rho_n
$$

**Complex Declaration**

$$
\left[ \text{complex} \ S = [v_1, v_2, \ldots, v_k] \right](\rho) = \rho[ \sigma(\{v_1, v_2, \ldots, v_k\}) / S]
$$

**Union Statement**

$$
\left[ \text{complex} \ C = \text{union}(A, B) \right](\rho) = \rho[(\rho(A) \cup \rho(B))/ C]
$$


**Glue Statement**

$$
\left[ \text{complex} \ C = \text{glue}(A, B) \ \text{mapping} \{ a_1 \text{->} b_1, \cdots, a_n \text{->} b_n \} \right](\rho) = \rho[K / C]
$$
Where $K$ is the simplicial complex obtained by glueing $\rho(A)$ and $\rho(B)$ along the identified vertices.

