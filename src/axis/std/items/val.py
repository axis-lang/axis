from typing import ClassVar, Literal, Optional
from axis.core import syn, sem, log
from axis.std.expr import Sym


class Val(syn.Item):
    """
    Represents a 'val' item:
    val expr: bound = value
    """

    keyword: ClassVar = "val"
    grammar: ClassVar = "val: 'val' expression ':' expression '=' expression EOF;"

    key: syn.Expr
    bound: Optional[syn.Expr]
    value: Optional[syn.Expr]

    @classmethod
    def build(
        cls,
        kw: Literal["val"],
        key: syn.Expr,
        *more,
        children: tuple[syn.Block, ...] = (),
    ):
        bound = None
        value = None
        for operator, operand in zip(more[0::2], more[1::2]):
            if operator == ":":
                bound = operand
            elif operator == "=":
                value = operand
            else:
                raise ValueError(f"Unknown operator {operator}")

        return Val(key=key, bound=bound, value=value, children=children)

    def generate_content_manifest_entries(self, base_ref):
        match self.key:
            case Sym(name=name):
                yield base_ref.member(name), self
            case _:
                log.error(f"Value key must be a symbol, got {self.key}").with_label(
                    self.as_label
                ).emit()


# valor NaV (not a value) sera retornado cuando una evaluacion sea erronea
# existen varias estancias de NaV: never para cuando una funcion no retorna
# error para cuando una evaluacion falla
# undefined para cuando una variable no ha sido inicializada


@sem.Binder.discover.register(Val)
def discover_val(parent: sem.Binder, val: Val):
    match val:
        case Val(key=Sym(name=name)):
            parent.export_item(val.key.name, val)
        case _:
            log.error(f"Value key must be a symbol, got {val.key}").with_label(
                val.as_label
            ).emit()
