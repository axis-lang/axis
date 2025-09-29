from __future__ import annotations
from typing import ClassVar, Literal, Optional
from axis import items, syn, sem, log, expr



class Val(syn.Item, frozen=True):
    """
    Represents a 'val' item:
    val expr: bound = value
    """

    outline_keyword: ClassVar[str] = "val"
    #grammar: ClassVar = "val: 'val' expression ':' expression '=' expression EOF;"

    key: syn.Expr
    bound: Optional[syn.Expr]
    value: Optional[syn.Expr]

    @classmethod
    def build(
        cls,
        kw: Literal["val"],
        key: syn.Expr,
        *more,
        parent: syn.Item,
        pkg: items.Package,
        children: tuple[syn.Block, ...] = (),
    ):
        match more:
            case (":", bound, "=", value):
                pass
            case (":", bound):
                value = None
            case ("=", value):
                bound = None
            case ():
                bound = None
                value = None
            case _:
                raise ValueError(f"Invalid syntax for val: {more}")

        return Val(key=key, bound=bound, value=value)

    # class Binding(sem.Binding):
    #     item: Val

    #     @property
    #     def ref(self):
    #         match self.item.key:
    #             case expr.Sym(name=name):
    #                 ref = self.parent.ref.member(name)
    #             case _:
    #                 log.error(f"Value key must be a symbol, got {self.item.key}").with_label(
    #                     self.item.as_label
    #                 ).throw()

    #         return self.parent.ref.member(self.item.key.name) if isinstance(self.item.key, expr.Sym) else self.parent.ref


    # def generate_content_manifest_entries(self, base_ref):
    #     match self.key:
    #         case expr.Sym(name=name):
    #             yield base_ref.member(name), self
    #         case _:
    #             log.error(f"Value key must be a symbol, got {self.key}").with_label(
    #                 self.as_label
    #             ).emit()


# valor NaV (not a value) sera retornado cuando una evaluacion sea erronea
# existen varias estancias de NaV: never para cuando una funcion no retorna
# error para cuando una evaluacion falla
# undefined para cuando una variable no ha sido inicializada


# @sem.Binder.discover.register(Val)
# def discover_val(parent: sem.Binder, val: Val):
#     match val:
#         case Val(key=Sym(name=name)):
#             parent.export_item(val.key.name, val)
#         case _:
#             log.error(f"Value key must be a symbol, got {val.key}").with_label(
#                 val.as_label
#             ).emit()
