#%%
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union

# ---------- Núcleo de términos/átomos ----------

@dataclass(frozen=True)
class Var:
    name: str
    def __repr__(self): return f"?{self.name}"

def is_var(t): return isinstance(t, Var)

@dataclass(frozen=True)
class Atom:
    pred: str
    args: Tuple[Any, ...]
    def __repr__(self):
        args = ", ".join(map(repr, self.args))
        return f"{self.pred}({args})"

def atom(pred: str, *args: Any) -> Atom:
    return Atom(pred, tuple(args))

@dataclass(frozen=True)
class Rule:
    head: Atom
    body: Tuple[Atom, ...]  # orden izquierda→derecha
    def __repr__(self):
        if not self.body:
            return f"{self.head}."
        body = ", ".join(map(repr, self.body))
        return f"{self.head} :- {body}."

# ---------- Unificación y entornos ----------

Env = Dict[Var, Any]

def deref(x: Any, env: Env) -> Any:
    while is_var(x) and x in env:
        x = env[x]
    return x

def unify(a: Any, b: Any, env: Env) -> Optional[Env]:
    a = deref(a, env); b = deref(b, env)
    if is_var(a):
        if is_var(b) and a == b: return env
        env2 = dict(env); env2[a] = b; return env2
    if is_var(b):
        env2 = dict(env); env2[b] = a; return env2
    return env if a == b else None

def unify_tuple(ts: Tuple[Any, ...], us: Tuple[Any, ...], env: Env) -> Optional[Env]:
    if len(ts) != len(us): return None
    out = env
    for t,u in zip(ts, us):
        out = unify(t, u, out)
        if out is None: return None
    return out

def ground_tuple(args: Tuple[Any, ...], env: Env) -> Tuple[Any, ...]:
    return tuple(deref(a, env) for a in args)

# ---------- Índices sencillos por columnas ----------

class IndexedRelation:
    """
    Relación con:
      - facts: set de tuplas
      - indices[col][val] -> set de tuplas que tienen args[col] == val
    """
    def __init__(self, arity: int):
        self.arity = arity
        self.facts: Set[Tuple[Any, ...]] = set()
        self.indices: List[Dict[Any, Set[Tuple[Any, ...]]]] = [defaultdict(set) for _ in range(arity)]

    def add(self, tup: Tuple[Any, ...]) -> bool:
        if tup in self.facts: return False
        self.facts.add(tup)
        for i, val in enumerate(tup):
            self.indices[i][val].add(tup)
        return True

    def extend(self, it: Iterable[Tuple[Any, ...]]):
        for t in it: self.add(t)

    def select(self, col_eq: Dict[int, Any]) -> Iterable[Tuple[Any, ...]]:
        """Devuelve tuplas que cumplen igualdades en columnas dadas."""
        if not col_eq:
            return self.facts
        # Escoge la columna más selectiva
        best_col, best_val = next(iter(col_eq.items()))
        best_set = self.indices[best_col].get(best_val, set())
        # Filtrado final (por si hay >1 columna filtrada)
        for t in best_set:
            ok = True
            for c, v in col_eq.items():
                if t[c] != v:
                    ok = False; break
            if ok: yield t

# ---------- Motor on-demand con tabling ----------

class Engine:
    """
    Motor Datalog positivo, on-demand (estilo Ascent):
      - Solo evalúa lo necesario para la consulta
      - Tabling por predicado + patrón de ligadura (adornment)
      - Reglas seguras, sin negación/aggreg.
    """

    def __init__(self):
        # EDB + IDB comparten almacenamiento por predicado
        self.rels: Dict[str, IndexedRelation] = {}
        self.rules_by_head: Dict[str, List[Rule]] = defaultdict(list)
        self.arity: Dict[str, int] = {}
        # Tabling: cache por (pred, adornment_mask, bound_values_tuple) -> set de resultados
        self.table: Dict[Tuple[str, Tuple[bool, ...], Tuple[Any, ...]], Set[Tuple[Any, ...]]] = {}
        # En progreso (para manejar ciclos sin recursión infinita)
        self.in_progress: Set[Tuple[str, Tuple[bool, ...], Tuple[Any, ...]]] = set()

    # ----- Definición del programa -----

    def _ensure_rel(self, pred: str, arity: int):
        if pred in self.rels:
            if self.rels[pred].arity != arity:
                raise ValueError(f"Aridad inconsistente para {pred}")
            return
        self.rels[pred] = IndexedRelation(arity)
        self.arity[pred] = arity

    def add_facts(self, pred: str, facts: Iterable[Tuple[Any, ...]]):
        facts = list(facts)
        if not facts:
            return
        ar = len(facts[0])
        self._ensure_rel(pred, ar)
        for t in facts:
            if len(t) != ar: raise ValueError("Aridad incorrecta en fact")
            self.rels[pred].add(t)

    def add_rule(self, rule: Rule):
        ar = len(rule.head.args)
        self._ensure_rel(rule.head.pred, ar)
        # chequeo de seguridad: todas las vars del head aparecen en el body
        head_vars = {v for v in rule.head.args if is_var(v)}
        body_vars = {v for a in rule.body for v in a.args if is_var(v)}
        if not head_vars.issubset(body_vars):
            raise ValueError(f"Regla no segura: {rule}")
        self.rules_by_head[rule.head.pred].append(rule)


    # ----- Consulta on-demand -----

    def query(self, q: Atom) -> Set[Tuple[Any, ...]]:
        """q puede contener constantes y/o Var(). Devuelve tuplas que satisfacen q."""
        if q.pred not in self.rels:
            self._ensure_rel(q.pred, len(q.args))

        # Construye patrón de ligadura (adornment) y valores enlazados
        mask = tuple(not is_var(a) for a in q.args)
        bound_vals = tuple(a for a in q.args if not is_var(a))
        key = (q.pred, mask, bound_vals)

        if key in self.table:
            return self._project_and_filter(q, self.table[key])

        # Marca en progreso para ciclos
        if key in self.in_progress:
            # En caso recursivo, devolver hechos ya materializados que cumplan el patrón
            # en lugar de un conjunto vacío, para no perder soluciones.
            rel = self.rels[q.pred]
            col_eq = {i: a for i, a in enumerate(q.args) if not is_var(a)}
            known = set(rel.select(col_eq))
            # Unir con cualquier parcial ya tabulado (si existiera)
            if key in self.table:
                known |= self.table[key]
            return self._project_and_filter(q, known)

        self.in_progress.add(key)

        # 1) Traer coincidencias directas de EDB/IDB por índices (filtro por constantes)
        direct = self._edb_lookup(q)

        # 2) Derivar por reglas cuyo head sea q.pred (goal-directed)
        derived = set(direct)
        for rule in self.rules_by_head.get(q.pred, []):
            derived |= self._prove_rule(rule, q)

        # 3) Cachear resultados por patrón (tabling)
        self.table[key] = derived
        self.in_progress.remove(key)

        # 4) Proyectar y filtrar por patrón (por si hay más constantes repetidas, etc.)
        return self._project_and_filter(q, derived)

    # ----- Utilidades internas -----

    def _edb_lookup(self, q: Atom) -> Set[Tuple[Any, ...]]:
        """Filtra por constantes usando índices; devuelve tuplas ground del predicado q.pred."""
        rel = self.rels[q.pred]
        col_eq = {i: a for i, a in enumerate(q.args) if not is_var(a)}
        out: Set[Tuple[Any, ...]] = set()
        for t in rel.select(col_eq):
            # Verifica consistencia si la consulta repite la misma constante/var enlazada
            ok = True
            env: Env = {}
            if unify_tuple(q.args, t, env) is None:
                ok = False
            if ok:
                out.add(t)
        return out

    def _project_and_filter(self, q: Atom, tuples: Set[Tuple[Any, ...]]) -> Set[Tuple[Any, ...]]:
        rel = self.rels[q.pred]
        if len(q.args) != rel.arity: raise ValueError("Aridad inválida en query")
        # Ya están ground; solo verificar repetición de constantes/consistencia
        out = set()
        for t in tuples:
            env: Env = {}
            if unify_tuple(q.args, t, env) is not None:
                out.add(t)
        return out

    def _prove_rule(self, rule: Rule, goal: Atom) -> Set[Tuple[Any, ...]]:
        """
        Evalúa la regla para el goal (con sus constantes) de manera demand-driven.
        Hace join left-to-right, usando:
          - hechos existentes (EDB/IDB)
          - subconsultas on-demand (con tabling)
        Devuelve tuplas ground para el head.
        """
        results: Set[Tuple[Any, ...]] = set()
        # Semilla: unifica head(rule) con goal para propagar bindings iniciales
        env_head = unify_tuple(rule.head.args, goal.args, {})
        if env_head is None:
            return results
        agenda: List[Env] = [env_head]

        # Join secuencial sobre el cuerpo
        for lit in rule.body:
            new_agenda: List[Env] = []
            for env in agenda:
                # Construye subconsulta con variables parcialmente ligadas por env
                instantiated = tuple(deref(a, env) for a in lit.args)
                subq = Atom(lit.pred, instantiated)
                # Subresultado on-demand (tabling)
                subtuples = self.query(subq)
                # Por cada tupla ground del subobjetivo, intenta extender el env
                for t in subtuples:
                    env2 = unify_tuple(instantiated, t, env)
                    if env2 is not None:
                        new_agenda.append(env2)
            agenda = new_agenda
            if not agenda:
                break  # poda: no hay soluciones parciales

        # Proyecta el head ground usando los env finales
        for env in agenda:
            head_t = ground_tuple(rule.head.args, env)
            # Materializa en relación (IDB) e índice
            self.rels[rule.head.pred].add(head_t)
            results.add(head_t)
        return results

# ---------- Ejemplos de uso ----------

if __name__ == "__main__":
    X, Y, Z = Var("X"), Var("Y"), Var("Z")

    eng = Engine()

    # --- Hechos base (EDB) ---
    eng.add_facts("padre", [
        ("juan", "maria"),
        ("maria", "ana"),
        ("maria", "leo"),
        ("carlos", "maria"),
    ])

    # --- Reglas (IDB) ---
    # abuelo(X,Y) :- padre(X,Z), padre(Z,Y).
    eng.add_rule(Rule(
        head=atom("abuelo", X, Y),
        body=(atom("padre", X, Z), atom("padre", Z, Y))
    ))

    # ancestro(X,Y) :- padre(X,Y).
    eng.add_rule(Rule(
        head=atom("ancestro", X, Y),
        body=(atom("padre", X, Y),)
    ))
    # ancestro(X,Y) :- padre(X,Z), ancestro(Z,Y).
    eng.add_rule(Rule(
        head=atom("ancestro", X, Y),
        body=(atom("padre", X, Z), atom("ancestro", Z, Y))
    ))

    # --- Consultas on-demand ---
    print("abuelo(juan, ?Y):", eng.query(atom("abuelo", "juan", Y)))
    print("ancestro(juan, ?Y):", eng.query(atom("ancestro", "juan", Y)))
    print("ancestro(?X, ana):", eng.query(atom("ancestro", X, "ana")))

    # Nota: la segunda consulta reutiliza resultados tabulados/materializados.
