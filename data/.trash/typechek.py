#%%
from __future__ import annotations
from typing import Dict, Tuple

# --- Definición de tipos para la inferencia de tipos ---

class Type:
    """Clase base para los tipos."""
    pass

class TVar(Type):
    """Representa una variable de tipo, ej.: t0, t1, ..."""
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return self.name

class TFunc(Type):
    """Representa una función: TFunc(t_in, t_out) equivale a t_in -> t_out"""
    def __init__(self, from_type: Type, to_type: Type) -> None:
        self.from_type = from_type
        self.to_type = to_type

    def __repr__(self) -> str:
        return f"({self.from_type} -> {self.to_type})"

class TCon(Type):
    """Constructor de tipo para tipos básicos (p.ej. Int, Bool)"""
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return self.name

# --- Definición del AST para expresiones (lenguaje lambda simple) ---

class Expr:
    """Clase base para expresiones."""
    pass

class Var(Expr):
    """Variable: representa una variable identificada por su nombre."""
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return self.name

class Lambda(Expr):
    """Abstracción lambda: (\\x -> body)"""
    def __init__(self, var: str, body: Expr) -> None:
        self.var = var
        self.body = body

    def __repr__(self) -> str:
        return f"(\\{self.var} -> {self.body})"

class App(Expr):
    """Aplicación de función: (func arg)"""
    def __init__(self, func: Expr, arg: Expr) -> None:
        self.func = func
        self.arg = arg

    def __repr__(self) -> str:
        return f"({self.func} {self.arg})"

class Let(Expr):
    """Let-binding: (let var = expr in body)"""
    def __init__(self, var: str, expr: Expr, body: Expr) -> None:
        self.var = var
        self.expr = expr
        self.body = body

    def __repr__(self) -> str:
        return f"(let {self.var} = {self.expr} in {self.body})"

# --- Definición de sustituciones y funciones auxiliares ---

# Una sustitución mapea nombres de variables de tipo a un objeto Type.
Subst = Dict[str, Type]

# Contador global para generar variables de tipo frescas
next_typevar_id: int = 0

def fresh_typevar() -> TVar:
    """Genera una nueva variable de tipo única."""
    global next_typevar_id
    tv = TVar(f"t{next_typevar_id}")
    next_typevar_id += 1
    return tv

def occur_check(var: str, typ: Type) -> bool:
    """
    Verifica si la variable 'var' aparece en 'typ' para evitar ciclos en la unificación.
    """
    if isinstance(typ, TVar):
        return typ.name == var
    elif isinstance(typ, TFunc):
        return occur_check(var, typ.from_type) or occur_check(var, typ.to_type)
    return False

def apply_subst(subst: Subst, typ: Type) -> Type:
    """
    Aplica la sustitución 'subst' al tipo 'typ'.
    """
    if isinstance(typ, TVar):
        if typ.name in subst:
            return apply_subst(subst, subst[typ.name])
        return typ
    elif isinstance(typ, TFunc):
        return TFunc(apply_subst(subst, typ.from_type), apply_subst(subst, typ.to_type))
    else:
        return typ

def compose_subst(s1: Subst, s2: Subst) -> Subst:
    """
    Compone dos sustituciones: primero aplica s1 y luego s2.
    """
    result: Subst = {var: apply_subst(s1, t) for var, t in s2.items()}
    result.update(s1)
    return result

def apply_subst_env(subst: Subst, env: Dict[str, Type]) -> Dict[str, Type]:
    """
    Aplica la sustitución a cada tipo del entorno.
    """
    return {var: apply_subst(subst, typ) for var, typ in env.items()}

# --- Unificación: hace coincidir dos tipos, generando una sustitución ---

def unify(t1: Type, t2: Type) -> Subst:
    """
    Unifica dos tipos t1 y t2.
    Retorna una sustitución que hace que t1 y t2 sean iguales.
    """
    if isinstance(t1, TVar):
        if t1.name != getattr(t2, 'name', None) and occur_check(t1.name, t2):
            raise Exception(f"Occur check fallido: {t1} aparece en {t2}")
        return {t1.name: t2}
    elif isinstance(t2, TVar):
        return unify(t2, t1)
    elif isinstance(t1, TFunc) and isinstance(t2, TFunc):
        s1 = unify(t1.from_type, t2.from_type)
        s2 = unify(apply_subst(s1, t1.to_type), apply_subst(s1, t2.to_type))
        return compose_subst(s2, s1)
    elif isinstance(t1, TCon) and isinstance(t2, TCon) and t1.name == t2.name:
        return {}
    else:
        raise Exception(f"No se pueden unificar los tipos {t1} y {t2}")

# --- Inferencia de tipos: implementación básica del algoritmo W ---

def infer(env: Dict[str, Type], expr: Expr) -> Tuple[Subst, Type]:
    """
    Realiza la inferencia de tipos sobre la expresión 'expr' dada un entorno 'env'.
    Retorna una tupla (sustitución, tipo inferido).
    
    Nota: Esta implementación es simplificada y no realiza generalización
    para obtener tipos polimórficos en la forma completa del algoritmo Hindley-Milner.
    """
    if isinstance(expr, Var):
        if expr.name in env:
            return {}, env[expr.name]
        else:
            raise Exception(f"Variable no enlazada: {expr.name}")
    elif isinstance(expr, Lambda):
        tv = fresh_typevar()
        new_env = env.copy()
        new_env[expr.var] = tv
        s1, t1 = infer(new_env, expr.body)
        return s1, TFunc(apply_subst(s1, tv), t1)
    elif isinstance(expr, App):
        s1, t1 = infer(env, expr.func)
        s2, t2 = infer(apply_subst_env(s1, env), expr.arg)
        tv = fresh_typevar()
        s3 = unify(apply_subst(s2, t1), TFunc(t2, tv))
        s = compose_subst(s3, compose_subst(s2, s1))
        return s, apply_subst(s, tv)
    elif isinstance(expr, Let):
        # En una implementación completa se aplicaría generalización aquí
        s1, t1 = infer(env, expr.expr)
        new_env = apply_subst_env(s1, env)
        new_env[expr.var] = t1
        s2, t2 = infer(new_env, expr.body)
        return compose_subst(s2, s1), t2
    else:
        raise Exception("Expresión desconocida")

# --- Ejemplos de uso del prototipo ---

if __name__ == "__main__":
    # Entorno inicial vacío
    env: Dict[str, Type] = {}

    # Ejemplo 1: Función identidad (\x -> x)
    expr1: Expr = Lambda("x", Var("x"))
    subst1, type1 = infer(env, expr1)
    print("Tipo de la identidad:", type1)  # Se espera algo como (t0 -> t0)

    # Ejemplo 2: Let-binding: let id = (\x -> x) in id id
    expr2: Expr = Let("id", Lambda("x", Var("x")), App(Var("id"), Var("id")))
    subst2, type2 = infer(env, expr2)
    print("Tipo de id id:", type2)
