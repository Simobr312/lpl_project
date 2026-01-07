# Semantic Analysis for the Simplicial Complex DSL

## 1. Semantic Domains

The language operates on specific sets of values. We define these domains as follows:

| Domain | Symbol | Definition |
| :--- | :--- | :--- |
| **Vertices** | $V$ | A set of unique string identifiers (e.g., "A", "B"). |
| **Simplices** | $\Sigma$ | $\mathcal{P}_{finite}(V)$ (Finite subsets of $V$). |
| **Complexes** | $K$ | Collections of simplices satisfying the hereditary property. |
| **Locations** | $Loc$ | $\mathbb{N}$ (Addresses used to reference complexes in the Store). |
| **Integers** | $\mathbb{Z}$ | Numerical values resulting from observation (Dimension, Betti numbers). |
| **Closures** | $Clos$ | $\text{Params} \times \text{Body} \times Env$ (Function representations). |

### Value Sets
* **Denotable Values ($DVal$):** Values that can be bound to identifiers in the Environment.
    $$DVal = Loc \cup \mathbb{Z} \cup V \cup Clos$$
* **Storable Values ($MVal$):** Values that can be stored at memory addresses.
    $$MVal = Complex$$

---

## 2. Program State

The execution state is a pair $\langle \rho, \sigma \rangle$, representing the mapping of names to addresses and addresses to data.

1.  **Environment ($\rho \in Env$):** A partial function $Id \to DVal$.
2.  **Store ($\sigma \in Store$):** A partial function $Loc \to MVal$.



---

## 3. Semantics of Expressions ($\mathcal{E}$)

The evaluation function $\mathcal{E} \llbracket e \rrbracket \langle \rho, \sigma \rangle$ computes a value from an expression given a specific state.

### Complex Construction
* **Literal:** $\mathcal{E} \llbracket [v_1, ..., v_n] \rrbracket \langle \rho, \sigma \rangle$ generates the complex $K$ by taking the power set of $\{v_1, ..., v_n\}$, ensuring the downward-closure property.
* **Union:** $\mathcal{E} \llbracket \text{union}(e_1, e_2) \rrbracket = K_1 \cup K_2$.
* **Join:** $\mathcal{E} \llbracket \text{join}(e_1, e_2) \rrbracket = K_1 \star K_2$ (The topological join, where every simplex of $K_1$ is combined with every simplex of $K_2$).
* **Glue:** $\mathcal{E} \llbracket \text{glue}(e_1, e_2) \text{ mapping } a \to b \rrbracket$. This performs a vertex identification, merging the equivalence classes of vertex $a$ from the first complex and vertex $b$ from the second.
* **Pick Vertex:** $\mathcal{E} \llbracket pick\_vert(K) \rrbracket \langle \rho, \sigma \rangle = \rho(v)$ where $v$ is a vertex of $K$.



### Observation
* **Dimension:** $\mathcal{E} \llbracket \text{dim}(e) \rrbracket = \max(|s| - 1)$ for all $s \in K$.
* **Number of Vertices:** $\mathcal{E} \llbracket \text{num\_vert}(e) \rrbracket = |V|$ where $V$ is the set of vertices in $K$.
* **Betti Numbers:** $\mathcal{E} \llbracket \text{betti}(e, n) \rrbracket$ computes the rank of the $n$-th homology group.

---

## 4. Semantics of Commands ($\mathcal{C}$)

The execution function $\mathcal{C} \llbracket c \rrbracket \langle \rho, \sigma \rangle$ transforms one state into another.

### Declarations and Assignments
* **Complex Declaration:** `complex K = e`
    Allocates a fresh location $l \in Loc$ such that $l \notin dom(\sigma)$.
    $$\mathcal{C} \llbracket \text{complex } K = e \rrbracket \langle \rho, \sigma \rangle = \langle \rho[l/K], \sigma[v/l] \rangle$$
* **Assignment:** `K <- e`
    Updates the value at the location already associated with $K$.
    $$\mathcal{C} \llbracket K = e \rrbracket \langle \rho, \sigma \rangle = \langle \rho, \sigma[v/l] \rangle \text{ where } l = \rho(K)$$

* **Fresh vertex declaration:** `vertex v`
    Binds the identifier $v$ to a new unique vertex in the environment.
    $$\mathcal{C} \llbracket \text{vertex } v \rrbracket \langle \rho, \sigma \rangle = \langle \rho[ v/ \__\ vi], \sigma \rangle$$
    the name $v$ is now associated to a new  vertex $\__\ vi$ where $i$ is the first free index.

### Control Flow
* **Conditional:** `if e then s1 else s2 endif`
    Branching is decided by the integer value of $e$. If $e \neq 0$, $s1$ is executed; otherwise, $s2$ is executed.
* **Looping:** `while e do s endwhile`
    The command sequence $s$ is executed repeatedly as long as $\mathcal{E} \llbracket e \rrbracket$ results in a non-zero integer.

---

## 5. Functions and Scoping

The language implements **Static Scoping** to ensure mathematical predictability.

* **Function Definitions:** Defining a function captures the current environment $\rho$ into a **Closure**.
* **Calls:** When a function is called, the body is evaluated in the *definition* environment, not the environment of the caller. This prevents making recursive calls.
* **Restriction:** To maintain simplicity in topological modeling, functions contain a single expression (`Expr`) rather than a sequence of commands.

---