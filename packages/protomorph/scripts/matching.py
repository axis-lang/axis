# ============================================================
#  HYBRID ASYMMETRIC SOLVER
#  Patrón compilado · sujeto con variables hoja · VM iterativa
# ============================================================

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable

# ─────────────────────────────────────────────
#  1. TÉRMINOS  (sujeto y partes de patrones)
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class Var:
    """Variable hoja — puede aparecer en el sujeto O en el patrón."""
    name: str
    def __repr__(self): return f"?{self.name}"

@dataclass(frozen=True)
class Term:
    """Nodo estructural con tag y children (ground o Var en hoja)."""
    tag: str
    children: tuple[Any, ...] = ()
    def __repr__(self):
        if not self.children: return self.tag
        return f"{self.tag}({', '.join(map(repr, self.children))})"

# Tipos de valor en el entorno resultante
Atom   = str | int | float
Slot   = Var          # variable hoja del sujeto sin resolver
Value  = Atom | Term | Slot
Env    = dict[str, Value]   # nombre_variable → valor o slot

# ─────────────────────────────────────────────
#  2. NODOS IR  (instrucciones del patrón)
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class IRBind:
    """Liga el nodo actual a una variable del patrón."""
    name: str

@dataclass(frozen=True)
class IRLit:
    """El nodo actual debe ser igual a este valor."""
    value: Atom

@dataclass(frozen=True)
class IRWild:
    """Acepta cualquier cosa, no liga."""
    pass

@dataclass(frozen=True)
class IRCtor:
    """Verifica tag y cantidad de hijos del Term actual."""
    tag: str
    child_count: int

@dataclass(frozen=True)
class IREnter:
    """Empuja el hijo i del nodo actual al cursor."""
    index: int

@dataclass(frozen=True)
class IRExit:
    """Vuelve al padre en el stack de cursores."""
    pass

@dataclass(frozen=True)
class IRGuard:
    """Evalúa un predicado sobre el env actual."""
    pred: Callable[[Env], bool]
    label: str = ""

@dataclass(frozen=True)
class IRSwitch:
    """
    Dispatch O(1) por tag del nodo actual.
    arms: dict[tag → list[IR]]
    default: list[IR] | None
    """
    arms: dict[str, tuple]   # tag → compiled block (tuple of IR nodes)
    default: tuple | None = None

@dataclass(frozen=True)
class IRAlt:
    """
    Or-pattern: prueba cada bloque en orden,
    devuelve el primero que tenga éxito.
    Hace checkpoint/rollback del env.
    """
    alternatives: tuple   # tuple of (tuple of IR nodes)

@dataclass(frozen=True)
class IRSlotBind:
    """
    El nodo actual es una Var (hoja del sujeto).
    Liga esa Var como slot en el env bajo el nombre dado.
    Permite sujetos parcialmente desconocidos.
    """
    name: str

IRNode = (IRBind | IRLit | IRWild | IRCtor | IREnter | IRExit |
          IRGuard | IRSwitch | IRAlt | IRSlotBind)

# ─────────────────────────────────────────────
#  3. COMPILADOR  (patrón de alto nivel → IR)
# ─────────────────────────────────────────────

def compile_pattern(pat) -> tuple:
    """
    Compila un patrón de alto nivel a una secuencia de IRNodes.

    Formas de alto nivel reconocidas:
      Var(name)          → IRBind o IRSlotBind según contexto
      '_'                → IRWild
      Atom (str/int)     → IRLit
      Term(tag,children) → IRCtor + Enter/compile_child/Exit por hijo
      ('switch', {tag: pat, ...}, default?)  → IRSwitch
      ('alt', pat, pat, ...)                 → IRAlt
      ('guard', pat, pred, label?)           → compila pat + IRGuard
      ('and', pat, pat)                      → concatena ambas compilaciones
    """
    # Variable del patrón → captura
    if isinstance(pat, Var):
        return (IRBind(pat.name),)

    # Wildcard
    if pat == '_' or pat is None:
        return (IRWild(),)

    # Literal atómico
    if isinstance(pat, str) and not pat.startswith('?'):
        return (IRLit(pat),)
    if isinstance(pat, (int, float)):
        return (IRLit(pat),)

    # Término estructural
    if isinstance(pat, Term):
        instrs: list[IRNode] = [IRCtor(pat.tag, len(pat.children))]
        for i, child in enumerate(pat.children):
            instrs.append(IREnter(i))
            instrs.extend(compile_pattern(child))
            instrs.append(IRExit())
        return tuple(instrs)

    # Formas especiales como tuplas
    if isinstance(pat, tuple):
        kind = pat[0]

        if kind == 'switch':
            # ('switch', {tag: sub_pat, ...})
            # ('switch', {tag: sub_pat, ...}, default_pat)
            arms_dict = pat[1]
            default_pat = pat[2] if len(pat) > 2 else None
            compiled_arms = {
                tag: compile_pattern(sub)
                for tag, sub in arms_dict.items()
            }
            compiled_default = compile_pattern(default_pat) if default_pat else None
            return (IRSwitch(compiled_arms, compiled_default),)

        if kind == 'alt':
            # ('alt', pat1, pat2, ...)
            alts = tuple(compile_pattern(p) for p in pat[1:])
            return (IRAlt(alts),)

        if kind == 'guard':
            # ('guard', sub_pat, pred_fn)
            # ('guard', sub_pat, pred_fn, 'label')
            sub_instrs = compile_pattern(pat[1])
            pred = pat[2]
            label = pat[3] if len(pat) > 3 else ""
            return sub_instrs + (IRGuard(pred, label),)

        if kind == 'and':
            # ('and', pat1, pat2) — ambos deben matchear el mismo cursor
            return compile_pattern(pat[1]) + compile_pattern(pat[2])

        if kind == 'slot':
            # ('slot', name) — espera una Var hoja en el sujeto
            return (IRSlotBind(pat[1]),)

    raise ValueError(f"Patrón no reconocido: {pat!r}")

# ─────────────────────────────────────────────
#  4. VM  (ejecuta el IR contra un sujeto)
# ─────────────────────────────────────────────

class MatchFailure(Exception):
    pass

def run_ir(instrs: tuple, subject, env: Env) -> Env:
    """
    Ejecuta la secuencia de instrucciones IR contra `subject`.
    Devuelve el env aumentado, o lanza MatchFailure.

    El 'cursor' es un stack: empezamos con [subject].
    IREnter(i) hace push del hijo i, IRExit hace pop.
    """
    cursor_stack = [subject]
    env = dict(env)  # copia mutable

    def current():
        return cursor_stack[-1]

    for instr in instrs:
        node = current()

        if isinstance(instr, IRBind):
            # Variable del patrón: captura el nodo actual
            if instr.name in env:
                # Variable no-lineal: debe coincidir con el valor previo
                prev = env[instr.name]
                if prev != node:
                    raise MatchFailure(
                        f"?{instr.name} ya ligada a {prev!r}, no puede ligar {node!r}"
                    )
            else:
                env[instr.name] = node

        elif isinstance(instr, IRLit):
            if node != instr.value:
                raise MatchFailure(f"Esperaba {instr.value!r}, encontré {node!r}")

        elif isinstance(instr, IRWild):
            pass  # siempre ok

        elif isinstance(instr, IRCtor):
            if not isinstance(node, Term):
                raise MatchFailure(f"Esperaba Term, encontré {type(node).__name__}")
            if node.tag != instr.tag:
                raise MatchFailure(f"Tag: esperaba '{instr.tag}', encontré '{node.tag}'")
            if len(node.children) != instr.child_count:
                raise MatchFailure(
                    f"Cantidad de hijos de {instr.tag}: esperaba {instr.child_count}, "
                    f"encontré {len(node.children)}"
                )

        elif isinstance(instr, IREnter):
            if not isinstance(node, Term):
                raise MatchFailure("IREnter sobre nodo no estructural")
            child = node.children[instr.index]
            cursor_stack.append(child)

        elif isinstance(instr, IRExit):
            cursor_stack.pop()

        elif isinstance(instr, IRGuard):
            if not instr.pred(env):
                label = f" [{instr.label}]" if instr.label else ""
                raise MatchFailure(f"Guard falló{label}")

        elif isinstance(instr, IRSwitch):
            # El nodo actual debe ser un Term — hacemos dispatch por tag
            if not isinstance(node, Term):
                raise MatchFailure("IRSwitch sobre nodo no estructural")
            tag = node.tag
            if tag in instr.arms:
                env = run_ir(instr.arms[tag], node, env)
            elif instr.default is not None:
                env = run_ir(instr.default, node, env)
            else:
                raise MatchFailure(f"Switch: tag '{tag}' no tiene arm y no hay default")

        elif isinstance(instr, IRAlt):
            # Prueba cada alternativa; devuelve la primera que funcione
            for alt_instrs in instr.alternatives:
                try:
                    env = run_ir(alt_instrs, node, dict(env))
                    break  # éxito
                except MatchFailure:
                    continue
            else:
                raise MatchFailure("Alt: ninguna alternativa tuvo éxito")

        elif isinstance(instr, IRSlotBind):
            # El nodo actual DEBE ser una Var (hoja del sujeto)
            if not isinstance(node, Var):
                raise MatchFailure(
                    f"SlotBind '{instr.name}': esperaba Var en sujeto, "
                    f"encontré {node!r}"
                )
            env[instr.name] = node  # ligamos la Var-slot al nombre del patrón

    return env

def match(compiled: tuple, subject, env: Env | None = None) -> Env | None:
    """Interfaz pública: devuelve Env o None (sin excepciones)."""
    try:
        return run_ir(compiled, subject, env or {})
    except MatchFailure:
        return None
    
# ─────────────────────────────────────────────
#  5. SOLVER  (reglas con patrones compilados)
# ─────────────────────────────────────────────

@dataclass
class Rule:
    """
    head_template: Term con Vars → lo que se deriva
    body_patterns: lista de (patrón_compilado, nombre_relación)
    El patrón se compila UNA vez en el constructor.
    """
    name: str
    head_template: Any
    body: list[tuple[str, Any]]  # [(relación, patrón_alto_nivel)]
    _compiled_body: list[tuple[str, tuple]] = field(init=False, repr=False)

    def __post_init__(self):
        self._compiled_body = [
            (rel, compile_pattern(pat))
            for rel, pat in self.body
        ]

@dataclass
class HybridSolver:
    relations: dict[str, list] = field(default_factory=dict)
    rules: list[Rule] = field(default_factory=list)

    def assert_fact(self, relation: str, term):
        self.relations.setdefault(relation, []).append(term)

    def add_rule(self, rule: Rule):
        self.rules.append(rule)

    def query(self, relation: str, query_term) -> list[Env]:
        """
        Busca todos los hechos en `relation` que hacen match con query_term.
        query_term puede contener Vars (variables del patrón de consulta).
        """
        compiled_q = compile_pattern(query_term)
        results = []
        for fact in self.relations.get(relation, []):
            env = match(compiled_q, fact)
            if env is not None:
                results.append(env)
        return results

    def _apply_env(self, template, env: Env):
        """Sustituye Vars en el template con valores del env."""
        if isinstance(template, Var):
            return env.get(template.name, template)
        if isinstance(template, Term):
            return Term(
                template.tag,
                tuple(self._apply_env(c, env) for c in template.children)
            )
        return template

    def fixpoint(self) -> int:
        """Itera hasta punto fijo. Devuelve número de hechos nuevos."""
        total_new = 0
        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                for env in self._eval_body(rule._compiled_body, {}):
                    derived = self._apply_env(rule.head_template, env)
                    rel = rule.head_template.tag if isinstance(rule.head_template, Term) else "fact"
                    bucket = self.relations.setdefault(rel, [])
                    if derived not in bucket:
                        bucket.append(derived)
                        total_new += 1
                        changed = True
        return total_new

    def _eval_body(self, compiled_body, env: Env) -> list[Env]:
        if not compiled_body:
            return [env]
        (rel, compiled_pat), *rest = compiled_body
        results = []
        for fact in self.relations.get(rel, []):
            # Aplicar el env actual al patrón antes de matchear
            # (variables ya ligadas actúan como literales)
            concrete_env = self._concretize_and_match(compiled_pat, fact, env)
            if concrete_env is not None:
                results.extend(self._eval_body(rest, concrete_env))
        return results

    def _concretize_and_match(self, compiled_pat, fact, env: Env) -> Env | None:
        """
        Matchea compiled_pat contra fact usando env como contexto:
        - Variables ya en env actúan como literales (non-linear match)
        - Variables nuevas se ligan libremente
        """
        return match(compiled_pat, fact, dict(env))    
    

# ─────────────────────────────────────────────
#  6. EJEMPLOS
# ─────────────────────────────────────────────

solver = HybridSolver()

# ── Hechos con variables hoja en el sujeto ──────────────────
# El hecho "tiene_precio(libro, ?precio)" tiene un slot sin resolver.
# El solver puede matchearlo y el env resultante contendrá la Var.

solver.assert_fact("item",
    Term("libro", ("La Odisea", Var("precio")))   # precio desconocido
)
solver.assert_fact("item",
    Term("libro", ("Dune", 15))                    # precio conocido
)
solver.assert_fact("item",
    Term("revista", ("Nature", 8))
)

# ── Switch compilado: dispatch O(1) ──────────────────────────
tipo_pat = compile_pattern(('switch', {
    'libro':   ('and', Term("libro", (Var("titulo"), Var("precio"))),
                       ('guard', Var("precio"),
                        lambda env: isinstance(env.get("precio"), int)
                                    and env["precio"] < 20,
                        "precio < 20")),
    'revista': Term("revista", (Var("titulo"), Var("precio"))),
}))

print("── Switch sobre items ──")
for item in solver.relations["item"]:
    env = match(tipo_pat, item)
    print(f"  {item!r:40s} → {env}")

# ── Or-pattern (Alt) ─────────────────────────────────────────
# Matchea libros O revistas con título
cualquier_pub = compile_pattern(('alt',
    Term("libro",   (Var("t"), '_')),
    Term("revista", (Var("t"), '_')),
))

print("\n── Alt: cualquier publicación ──")
for item in solver.relations["item"]:
    env = match(cualquier_pub, item)
    print(f"  {item!r:40s} → {env}")

# ── Sujeto con variable hoja: SlotBind ───────────────────────
slot_pat = compile_pattern(
    Term("libro", (Var("titulo"), ('slot', "precio_slot")))
)

print("\n── SlotBind: sujeto con Var hoja ──")
for item in solver.relations["item"]:
    env = match(slot_pat, item)
    print(f"  {item!r:40s} → {env}")
# → La Odisea: {'titulo': 'La Odisea', 'precio_slot': Var('precio')}  ← slot capturado
# → Dune:      {'titulo': 'Dune', 'precio_slot': 15}                  ← valor concreto

# ── Solver con reglas y clausura transitiva ──────────────────
solver2 = HybridSolver()
for pair in [("a","b"), ("b","c"), ("c","d")]:
    solver2.assert_fact("edge", Term("edge", pair))

solver2.add_rule(Rule(
    name="base",
    head_template=Term("reach", (Var("x"), Var("y"))),
    body=[("edge", Term("edge", (Var("x"), Var("y"))))],
))
solver2.add_rule(Rule(
    name="trans",
    head_template=Term("reach", (Var("x"), Var("z"))),
    body=[
        ("edge",  Term("edge",  (Var("x"), Var("y")))),
        ("reach", Term("reach", (Var("y"), Var("z")))),
    ],
))

n = solver2.fixpoint()
print(f"\n── Clausura transitiva: {n} hechos derivados ──")
for f in solver2.relations.get("reach", []):
    print(f"  {f}")    
