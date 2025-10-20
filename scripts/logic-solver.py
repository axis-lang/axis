"""Axis Logic Mini Solver
=================================

let image: (canvas: Array[_,_] {
    (c: (r:R,g:R,b:R) :> Array[_] R)
}) = zero

def Range N: {start: N, stop: N -> (start, stop)}

Este módulo implementa un núcleo lógico muy pequeño de estilo Prolog/Datalog
para experimentación interna. Se evita por ahora toda la capa de parsing:
las reglas y consultas se construyen con clases Python (Records de protobase).

Características soportadas (fase inicial):
 - Términos: Var, Atom, Num, Fun (compuesto)
 - Literales y Reglas (head :- body)
 - Programa con índice por (predicado, aridad)
 - Unificación sin occur-check por ahora
 - Resolución SLD con backtracking (profundidad limitada)
 - Predicados built-in: '=' (unificación), '!=' (diferencia)
 - Iterador de soluciones devuelve sólo las variables libres de la consulta

Limitaciones actuales:
 - Sin occur-check (posibles términos cíclicos si se amplía impropiamente)
 - Sin negación como fallo ni agregados
 - Sin estratificación Datalog ni optimizaciones semi-naïve
 - Sin indexing avanzado (solo tabla por nombre/aridad)
 - Sin optimización de sharing / e-graphs (plan a futuro)

Extensiones futuras previstas:
 - Tabla de memo (tabling) / resolución SLG
 - Reglas recursivas estratificadas para Datalog
 - Integración con un motor de reescritura / e-graph (egglog style)
 - Reglas con restricciones (CLP) y dominios
 - Occur-check opcional y tipos en términos

API rápida:
 >>> from axis.logic import Var, Atom, Fun, Lit, Rule, Program, Solver
 >>> X, Y = Var('X'), Var('Y')
 >>> parent = lambda a,b: Lit('parent', a, b)
 >>> rules = [
 ...   Rule(parent(Atom('john'), Atom('mary'))),
 ...   Rule(parent(Atom('mary'), Atom('anne'))),
 ...   Rule(Lit('ancestor', X, Y), parent(X,Y)),
 ...   Rule(Lit('ancestor', X, Y), parent(X, Var('Z')), Lit('ancestor', Var('Z'), Y)),
 ... ]
 >>> prog = Program(rules)
 >>> solver = Solver(prog)
 >>> list(solver.query(Lit('ancestor', Atom('john'), Y)))
 [{'Y': Atom('mary')}, {'Y': Atom('anne')}]

Nota: Las variables se renombran por regla durante la resolución para evitar colisiones.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Iterable, Optional, Callable, Sequence, Dict, Any
from protobase import Record, cached_property

###############################################################################
# Terms
###############################################################################

class Term(Record, frozen=True, abstract=True):
	"""Term base."""
	def substitute(self, subst: Dict[str, Term]) -> Term:  # pragma: no cover - abstract
		raise NotImplementedError

	def vars(self) -> set[str]:  # pragma: no cover - abstract
		raise NotImplementedError


class Var(Term, consed=True):
	name: str

	def substitute(self, subst: Dict[str, Term]) -> Term:
		t: Term = self
		visited = set()
		while isinstance(t, Var) and t.name in subst:
			if t.name in visited:  # prevención simple de bucles
				break
			visited.add(t.name)
			t = subst[t.name]
		return t

	def vars(self) -> set[str]:
		return {self.name}

	def __repr__(self):  # representación más clara
		return f"Var({self.name})"


class Atom(Term, consed=True):
	name: str

	def substitute(self, subst: Dict[str, Term]) -> Term:
		return self

	def vars(self) -> set[str]:
		return set()

	def __repr__(self):
		return f"Atom({self.name})"


class Num(Term):
	value: int | float

	def substitute(self, subst: Dict[str, Term]) -> Term:
		return self

	def vars(self) -> set[str]:
		return set()

	def __repr__(self):
		return f"Num({self.value})"


class Fun(Term):
	functor: str
	args: tuple[Term, ...]

	def substitute(self, subst: Dict[str, Term]) -> Term:
		if not self.args:
			return self
		new_args = tuple(arg.substitute(subst) for arg in self.args)
		if new_args == self.args:
			return self
		return Fun(self.functor, new_args)

	def vars(self) -> set[str]:
		vs: set[str] = set()
		for a in self.args:
			vs.update(a.vars())
		return vs

	def __repr__(self):
		inner = ', '.join(repr(a) for a in self.args)
		return f"Fun({self.functor}, ({inner}))"


class Tup(Term, frozen=True):
	"""Tupla posicional (registro simple) usada para agrupar valores.

	Se comporta como un término estructural sin functor nombrado.
	Unifica por longitud y unificación de cada posición.
	"""
	items: tuple[Term, ...]

	def substitute(self, subst: Dict[str, Term]) -> Term:
		if not self.items:
			return self
		new_items = tuple(it.substitute(subst) for it in self.items)
		if new_items == self.items:
			return self
		return Tup(new_items)

	def vars(self) -> set[str]:
		vs: set[str] = set()
		for it in self.items:
			vs.update(it.vars())
		return vs

	def __repr__(self):
		inner = ', '.join(repr(a) for a in self.items)
		return f"Tup({inner})"


###############################################################################
# Literals / Rules
###############################################################################

class Lit(Record, frozen=True):
	predicate: str
	args: tuple[Term, ...]

	def substitute(self, subst: Dict[str, Term]) -> 'Lit':
		return Lit(self.predicate, tuple(a.substitute(subst) for a in self.args))

	@property
	def arity(self) -> int:
		return len(self.args)

	def vars(self) -> set[str]:
		vs: set[str] = set()
		for a in self.args:
			vs.update(a.vars())
		return vs

	def __repr__(self):
		inner = ', '.join(repr(a) for a in self.args)
		return f"Lit({self.predicate}/{self.arity}: {inner})"


class Rule(Record, frozen=True):
	head: Lit
	body: tuple[Lit, ...] = ()

	def __repr__(self):
		if not self.body:
			return f"Rule({self.head}.)"
		return f"Rule({self.head} :- {', '.join(repr(b) for b in self.body)})"


###############################################################################
# Program & indexing
###############################################################################

class Program(Record, frozen=True):
	rules: tuple[Rule, ...]

	@cached_property
	def index(self) -> Dict[tuple[str, int], tuple[Rule, ...]]:
		buckets: Dict[tuple[str, int], list[Rule]] = {}
		for r in self.rules:
			key = (r.head.predicate, r.head.arity)
			buckets.setdefault(key, []).append(r)
		return {k: tuple(v) for k, v in buckets.items()}

	def lookup(self, predicate: str, arity: int) -> tuple[Rule, ...]:
		return self.index.get((predicate, arity), ())


###############################################################################
# Unification
###############################################################################

Substitution = Dict[str, Term]

def deref(t: Term, subst: Substitution) -> Term:
	return t.substitute(subst)


def unify(a: Term, b: Term, subst: Substitution) -> Optional[Substitution]:
	a = deref(a, subst)
	b = deref(b, subst)

	if a is b:
		return subst
	# Variable cases
	if isinstance(a, Var):
		subst2 = dict(subst)
		subst2[a.name] = b
		return subst2
	if isinstance(b, Var):
		subst2 = dict(subst)
		subst2[b.name] = a
		return subst2

	# Atoms / numbers
	if isinstance(a, Atom) and isinstance(b, Atom):
		return subst if a.name == b.name else None
	if isinstance(a, Num) and isinstance(b, Num):
		return subst if a.value == b.value else None

	# Functors
	if isinstance(a, Fun) and isinstance(b, Fun):
		if a.functor != b.functor or len(a.args) != len(b.args):
			return None
		cur = subst
		for x, y in zip(a.args, b.args):
			cur = unify(x, y, cur)
			if cur is None:
				return None
		return cur

	# Tuplas
	if isinstance(a, Tup) and isinstance(b, Tup):
		if len(a.items) != len(b.items):
			return None
		cur = subst
		for x, y in zip(a.items, b.items):
			cur = unify(x, y, cur)
			if cur is None:
				return None
		return cur

	return None


###############################################################################
# Solver
###############################################################################

class Solver:
	"""Motor de resolución lógica básico.

	No hereda de Record para permitir estado mutable interno (_var_counter, builtins).
	"""
	def __init__(self, program: Program, max_depth: int = 1000):
		self.program = program
		self.max_depth = max_depth
		self._builtins: Dict[str, Callable[[tuple[Term, ...], Substitution], Optional[Substitution]]] = {
			'=': self._builtin_eq,
			'!=': self._builtin_neq,
		}
		self._var_counter: int = 0

	# Builtins ----------------------------------------------------------------
	def _builtin_eq(self, args: tuple[Term, ...], subst: Substitution) -> Optional[Substitution]:
		if len(args) != 2:
			return None
		return unify(args[0], args[1], subst)

	def _builtin_neq(self, args: tuple[Term, ...], subst: Substitution) -> Optional[Substitution]:
		if len(args) != 2:
			return None
		temp = unify(args[0], args[1], subst)
		# éxito si no unifican
		if temp is None:
			return subst
		# si unifican y equivalen tras sustitución => falla
		a = deref(args[0], temp)
		b = deref(args[1], temp)
		if repr(a) == repr(b):  # comparación estructural básica
			return None
		return subst

	# Query -------------------------------------------------------------------
	def query(self, goal: Lit | Sequence[Lit], max_solutions: Optional[int] = None) -> Iterator[Dict[str, Term]]:
		goals: tuple[Lit, ...]
		if isinstance(goal, Lit):
			goals = (goal,)
		else:
			goals = tuple(goal)
		query_vars = set().union(*(g.vars() for g in goals))
		count = 0
		for subst in self._resolve(goals, {}, 0):
			result = {v: deref(Var(v), subst) for v in query_vars if v in subst}
			yield result
			count += 1
			if max_solutions is not None and count >= max_solutions:
				break

	# Core resolution ---------------------------------------------------------
	def _resolve(self, goals: tuple[Lit, ...], subst: Substitution, depth: int) -> Iterator[Substitution]:
		if depth > self.max_depth:
			return
		if not goals:
			yield subst
			return

		first, *rest = goals
		# Builtin literal by predicate name
		if first.predicate in self._builtins:
			new_subst = self._builtins[first.predicate](tuple(a.substitute(subst) for a in first.args), subst)
			if new_subst is not None:
				yield from self._resolve(tuple(rest), new_subst, depth)
			return

		# Ordinary predicate: fetch candidate rules
		candidates = self.program.lookup(first.predicate, first.arity)
		for rule in candidates:
			renamed_rule = self._rename_rule(rule)
			unif = unify_fun_heads(renamed_rule.head, first, subst)
			if unif is None:
				continue
			new_goals = renamed_rule.body + tuple(rest)
			yield from self._resolve(new_goals, unif, depth + 1)

	# Variable renaming -------------------------------------------------------
	def _rename_rule(self, rule: Rule) -> Rule:
		mapping: Dict[str, Var] = {}
		def rename_term(t: Term) -> Term:
			if isinstance(t, Var):
				if t.name not in mapping:
					self._var_counter += 1
					mapping[t.name] = Var(f"{t.name}_G{self._var_counter}")
				return mapping[t.name]
			if isinstance(t, Fun):
				return Fun(t.functor, tuple(rename_term(a) for a in t.args))
			return t
		def rename_lit(l: Lit) -> Lit:
			return Lit(l.predicate, tuple(rename_term(a) for a in l.args))
		return Rule(rename_lit(rule.head), tuple(rename_lit(b) for b in rule.body))


###############################################################################
# Helpers de construcción sintáctica ligera
###############################################################################

def sym(name: str) -> Atom:
	return Atom(name)

def fn(functor: str, *args: Term) -> Fun:
	return Fun(functor, args)

def tpl(*items: Term) -> Tup:
	return Tup(tuple(items))


###############################################################################
# Utilidades internas adicionales
###############################################################################

def unify_fun_heads(rule_head: Lit, goal: Lit, subst: Substitution) -> Optional[Substitution]:
	"""Unifica dos literales convirtiéndolos en Fun simbólicos para reutilizar unify.

	Se modela como Fun(<predicate>, args...) para simplificar y permitir reutilizar
	la unificación estructural ya implementada.
	"""
	a = Fun(rule_head.predicate, rule_head.args)
	b = Fun(goal.predicate, goal.args)
	return unify(a, b, subst)

__all__ = [
	'Term', 'Var', 'Atom', 'Num', 'Fun',
	'Lit', 'Rule', 'Program', 'Solver',
	'unify', 'sym', 'fn', 'Tup', 'tpl'
]

