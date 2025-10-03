#%%
from __future__ import annotations
from dataclasses import dataclass, field
from typing import FrozenSet, Tuple, Iterable, Dict, Set, Optional

@dataclass(frozen=True)
class Atom: ...

@dataclass(frozen=True)
class Top(Atom):
    def __str__(self): return "⊤"

@dataclass(frozen=True)
class Bottom(Atom):
    def __str__(self): return "⊥"

@dataclass(frozen=True)
class Prim(Atom):
    name: str
    def __str__(self): return self.name

@dataclass(frozen=True)
class Nominal(Atom):
    name: str
    def __str__(self): return self.name

@dataclass(frozen=True)
class Func(Atom):
    dom: 'TypeExpr'
    cod: 'TypeExpr'
    def __str__(self): return f"({self.dom} → {self.cod})"

@dataclass(frozen=True)
class Record(Atom):
    fields: Tuple[Tuple[str, 'TypeExpr'], ...]
    def __str__(self):
        inside = ", ".join(f"{k}: {v}" for k,v in self.fields)
        return f"{{{inside}}}"

@dataclass(frozen=True)
class TypeExpr:
    kind: str
    atoms: Tuple['TypeExpr', ...] = field(default_factory=tuple)
    atom: Optional[Atom] = None

    @staticmethod
    def A(a: Atom) -> 'TypeExpr':
        return TypeExpr(kind="atom", atom=a)

    @staticmethod
    def Union(*elems: 'TypeExpr') -> 'TypeExpr':
        return TypeExpr(kind="union", atoms=tuple(elems))

    @staticmethod
    def Inter(*elems: 'TypeExpr') -> 'TypeExpr':
        return TypeExpr(kind="inter", atoms=tuple(elems))

    def __str__(self):
        if self.kind == "atom":
            return str(self.atom)
        elif self.kind == "union":
            return " | ".join(str(x) for x in self.atoms) if self.atoms else "∅"
        elif self.kind == "inter":
            return " & ".join(str(x) for x in self.atoms) if self.atoms else "⊤"
        else:
            return "<?>"

Inter = FrozenSet[Atom]
TypeNF = FrozenSet[Inter]

TOP = Top()
BOT = Bottom()

def inter_to_str(I: Inter) -> str:
    if not I: return "⊤"
    return " & ".join(sorted(map(str, I)))

def typenf_to_str(U: TypeNF) -> str:
    if not U: return "⊥"
    return " | ".join(sorted(inter_to_str(I) for I in U))

class SubtypingOracle:
    def __init__(self):
        self.nominal_parents: Dict[str, Set[str]] = {}
        self.prim_parents: Dict[str, Set[str]] = {}
        self.disjoint_prims: Set[Tuple[str, str]] = set()
        self.disjoint_nominals: Set[Tuple[str, str]] = set()

    def add_nominal_edge(self, child: str, parent: str):
        self.nominal_parents.setdefault(child, set()).add(parent)

    def add_prim_edge(self, child: str, parent: str):
        self.prim_parents.setdefault(child, set()).add(parent)

    def add_disjoint_prims(self, a: str, b: str):
        self.disjoint_prims.add(tuple(sorted((a, b))))

    def add_disjoint_nominals(self, a: str, b: str):
        self.disjoint_nominals.add(tuple(sorted((a, b))))

    def _is_reachable(self, graph: Dict[str, Set[str]], src: str, dst: str) -> bool:
        if src == dst: return True
        seen = set()
        stack = [src]
        while stack:
            x = stack.pop()
            if x in seen: continue
            seen.add(x)
            for y in graph.get(x, ()):
                if y == dst: return True
                stack.append(y)
        return False

    def prim_leq(self, a: Prim, b: Prim) -> bool:
        return self._is_reachable(self.prim_parents, a.name, b.name)

    def nominal_leq(self, a: Nominal, b: Nominal) -> bool:
        return self._is_reachable(self.nominal_parents, a.name, b.name)

    def atom_leq(self, a: Atom, b: Atom) -> bool:
        if isinstance(b, Top): return True
        if isinstance(a, Bottom): return True
        if isinstance(a, Top): return isinstance(b, Top)
        if isinstance(b, Bottom): return isinstance(a, Bottom)
        if a == b: return True
        if isinstance(a, Prim) and isinstance(b, Prim):
            return self.prim_leq(a, b)
        if isinstance(a, Nominal) and isinstance(b, Nominal):
            return self.nominal_leq(a, b)
        if isinstance(a, Func) and isinstance(b, Func):
            return leq(b.dom, a.dom, self) and leq(a.cod, b.cod, self)
        if isinstance(a, Record) and isinstance(b, Record):
            fa = dict(a.fields); fb = dict(b.fields)
            for k, tb in fb.items():
                if k not in fa: return False
                if not leq(TypeExpr.A(fa[k]), TypeExpr.A(tb), self): return False
            return True
        return False

    def atom_conflict(self, a: Atom, b: Atom) -> bool:
        if isinstance(a, Bottom) or isinstance(b, Bottom): return True
        if isinstance(a, Top) or isinstance(b, Top): return False
        if a == b: return False
        if isinstance(a, Prim) and isinstance(b, Prim):
            return tuple(sorted((a.name, b.name))) in self.disjoint_prims
        if isinstance(a, Nominal) and isinstance(b, Nominal):
            return tuple(sorted((a.name, b.name))) in self.disjoint_nominals
        return False

def to_dnf(t: TypeExpr) -> TypeNF:
    if t.kind == "atom":
        if isinstance(t.atom, Top): return frozenset({frozenset()})
        if isinstance(t.atom, Bottom): return frozenset()
        return frozenset({frozenset({t.atom})})
    if t.kind == "union":
        acc: Set[Inter] = set()
        for e in t.atoms: acc |= set(to_dnf(e))
        return frozenset(acc)
    if t.kind == "inter":
        dnfs = [to_dnf(e) for e in t.atoms]
        if not dnfs: return frozenset({frozenset()})
        acc: Set[Inter] = set(dnfs[0])
        for d in dnfs[1:]:
            new_acc: Set[Inter] = set()
            for I in acc:
                for J in d:
                    new_acc.add(frozenset(set(I) | set(J)))
            acc = new_acc
        return frozenset(acc)
    raise ValueError("Tipo desconocido")

def inter_prune(I: Inter, oracle: SubtypingOracle) -> Optional[Inter]:
    atoms = list(I)
    for i in range(len(atoms)):
        for j in range(i+1, len(atoms)):
            if oracle.atom_conflict(atoms[i], atoms[j]):
                return None
    keep = []
    for a in atoms:
        redundant = False
        for b in atoms:
            if a is b: continue
            if oracle.atom_leq(b, a) and not oracle.atom_leq(a, b):
                redundant = True; break
        if not redundant: keep.append(a)
    keep = [a for a in keep if not isinstance(a, Top)]
    return frozenset(keep)

def inter_leq(I: Inter, J: Inter, oracle: SubtypingOracle) -> bool:
    if len(J) == 0: return True
    if len(I) == 0 and len(J) > 0: return False
    for beta in J:
        if not any(oracle.atom_leq(alpha, beta) for alpha in I):
            return False
    return True

def union_prune(U: TypeNF, oracle: SubtypingOracle) -> TypeNF:
    if any(len(I) == 0 for I in U):
        return frozenset({frozenset()})
    keep: Set[Inter] = set(U)
    for I in list(U):
        for J in list(U):
            if I is J: continue
            if inter_leq(I, J, oracle):
                if I in keep and J in keep:
                    keep.discard(I)
    return frozenset(keep)

def normalize(t: TypeExpr, oracle: SubtypingOracle) -> TypeNF:
    U = to_dnf(t)
    inters: Set[Inter] = set()
    for I in U:
        K = inter_prune(I, oracle)
        if K is not None: inters.add(K)
    return union_prune(frozenset(inters), oracle)

def leq(a: TypeExpr, b: TypeExpr, oracle: SubtypingOracle) -> bool:
    X = normalize(a, oracle); Y = normalize(b, oracle)
    if not X: return True
    if not Y: return len(X) == 0
    for I in X:
        if not any(inter_leq(I, J, oracle) for J in Y):
            return False
    return True

def join(a: TypeExpr, b: TypeExpr, oracle: SubtypingOracle) -> TypeNF:
    A = normalize(a, oracle); B = normalize(b, oracle)
    return union_prune(frozenset(set(A) | set(B)), oracle)

def meet(a: TypeExpr, b: TypeExpr, oracle: SubtypingOracle) -> TypeNF:
    A = normalize(a, oracle); B = normalize(b, oracle)
    if not A or not B: return frozenset()
    out: Set[Inter] = set()
    for I in A:
        for J in B:
            K = inter_prune(frozenset(set(I) | set(J)), oracle)
            if K is not None: out.add(K)
    return union_prune(frozenset(out), oracle)
