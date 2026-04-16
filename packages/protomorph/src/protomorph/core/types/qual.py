from __future__ import annotations

from typing import cast as _cast

import protomorph.core as _pm
from protobase import flux as _flux

from .spec import Spec as _Spec
from .type_ import Type as _Type


class Qual(_Type):
    qualifier: _Spec
    qualified: _pm.Type

    def metatype(self) -> _pm.Type:
        return _Spec.of("std.metas.Qualifier")

    @property
    def schema(self) -> _pm.Schema | None:
        qualified_schema = self.qualified.schema
        if qualified_schema is None:
            return None
        return qualified_schema.map(
            lambda child: _pm.val(type(self)(self.qualifier, child.fetch()))
        )

    @_flux.property
    def underlying(self) -> _pm.Type:
        current: _pm.Type = self.qualified
        while isinstance(current, Qual):
            current = current.qualified
        return current

    @_flux.property
    def qualifiers(self) -> _pm.Tuple:
        if isinstance(self.qualified, Qual):
            return _pm.Tuple.extends(
                self.qualified.qualifiers,
                _pm.Tuple(
                    _pm.VaryingType((self.qualifier.metatype(),)), (self.qualifier,)
                ),
            )
        return _pm.Tuple(
            _pm.VaryingType((self.qualifier.metatype(),)), (self.qualifier,)
        )

    @classmethod
    def of(cls, underlying: _pm.Type, *qualifiers: _Spec) -> Qual:
        if not qualifiers:
            if isinstance(underlying, Qual):
                return underlying
            raise TypeError("Qual.of() requires at least one qualifier")

        first, *rest = qualifiers
        result = cls(first, underlying)
        for qualifier in rest:
            result = cls(qualifier, result)
        return result
