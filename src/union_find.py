from __future__ import annotations
from typing import Dict, Generic, Set, TypeVar

T = TypeVar("T")

class UnionFind(Generic[T]):
    def __init__(self):
        self.parent: Dict[T, T] = {}
        self.rank: Dict[T, int] = {}

    def add(self, x: T):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0

    def find(self, x: T) -> T:
        if x not in self.parent:
            self.add(x)
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x: T, y: T) -> T:
        rx = self.find(x)
        ry = self.find(y)

        if rx == ry:
            return rx
        
        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
            return ry
        elif self.rank[rx] > self.rank[ry]:
            self.parent[ry] = rx
            return rx
        else:
            self.parent[ry] = rx
            self.rank[rx] += 1
            return rx
    
    def get_classes(self) -> Dict[T, Set[T]]:
        out: Dict[T, Set[T]] = {}
        for x in self.parent:
            rep = self.find(x)
            out.setdefault(rep, set()).add(x)
        return out
    
    def get_nodes(self) -> Set[T]:
        return set(self.parent.keys())

    def merge(self, other: UnionFind) -> "UnionFind":
        new_uf = UnionFind()
        # add all nodes
        for v in self.get_nodes() | other.get_nodes():
            new_uf.add(v)
        # union all equivalences from self
        for cls in self.get_classes().values():
            nodes = list(cls)
            for i in range(1, len(nodes)):
                new_uf.union(nodes[0], nodes[i])
        # union all equivalences from other
        for cls in other.get_classes().values():
            nodes = list(cls)
            for i in range(1, len(nodes)):
                new_uf.union(nodes[0], nodes[i])
        return new_uf

