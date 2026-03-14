from __future__ import annotations

from typing import ClassVar, cast

from protobase import Missing, MissingType

import protomorph as morph

from .base import Builtin, Data

__all__ = [
    "META_TYPE_PATHS",
    "register_meta_type_paths",
    "Type",
    "StructType",
    "NominalType",
    "UnionType",
]


META_TYPE_PATHS: set[str] = set()


def register_meta_type_paths(*paths: str) -> None:
    META_TYPE_PATHS.update(paths)


class Type(Builtin, abstract=True):
    val_cls: ClassVar[type[morph.Val] | None] = None
    ANCHOR: ClassVar[str]

    @property
    def is_meta(self) -> bool:
        if isinstance(self, morph.NominalType):
            return self.spec_ref.path in META_TYPE_PATHS
        return False

    @classmethod
    def _type(cls, *args: type | morph.Type) -> morph.Type:
        if args:
            raise TypeError(
                f"{cls.__name__}._type does not accept host-specific type arguments in protomorph core"
            )
        return morph.nominal_type(cls._anchor_path())

    def _metatype(self) -> morph.Type:
        return morph.nominal_type(self._anchor_path(), self._metaspec())

    def _wrap(self, data: Data) -> morph.Val:
        val_cls = type(self).val_cls or morph.Const
        return val_cls(self, data)

    def _metaspec(self) -> morph.Const | None:
        return None

    def _encode(self, data: Data) -> Data:
        return data

    def _decode(self, raw_data: Data) -> Data:
        return raw_data

    def _dir(self, data: Data | MissingType = Missing) -> morph.Struct[str, Type] | None:
        _ = data
        return None

    def _get(self, data: Data, key: str | int) -> morph.Val:
        fields = self._dir(data)
        if fields is None:
            raise KeyError(f"No member {key!r} on opaque type {type(self).__name__}")

        if isinstance(key, str):
            offset = fields.index.get(key)
        elif isinstance(key, int):
            offset = key
        else:
            raise TypeError(f"Unsupported key type: {type(key)}")

        if isinstance(data, tuple):
            return fields[offset]._wrap(data[offset])
        if isinstance(data, Builtin):
            attr_name = fields.index.keys[offset]
            if attr_name is None:
                raise KeyError(f"Struct has no positional field at offset {offset}")
            return fields[offset]._wrap(getattr(data, attr_name))
        raise TypeError(f"Unsupported data type: {type(data)}")


class StructType(Type):
    ANCHOR: ClassVar[str] = "dom.Struct.Type"

    meta_attrs: morph.Struct[str, Type]

    def _metaspec(self):
        return morph.struct(
            *self.meta_attrs.map(lambda meta_attr: morph.type_of(morph.val(meta_attr)))
        )

    def _decode(self, raw_data: Data) -> Data:
        match raw_data:
            case tuple() as raw_fields:
                if len(raw_fields) != len(self.meta_attrs):
                    raise ValueError(
                        f"Expected {len(self.meta_attrs)} fields, got {len(raw_fields)}"
                    )
                return tuple(
                    field_type._decode(field_raw)
                    for field_type, field_raw in zip(self.meta_attrs.values, raw_fields)
                )
            case _:
                raise TypeError(
                    f"Expected tuple data for StructType, got {type(raw_data)}"
                )

    def _dir(self, data: Data | MissingType = Missing) -> morph.Struct[str, Type] | None:
        _ = data
        return self.meta_attrs


class NominalType(Type):
    ANCHOR: ClassVar[str] = "dom.Nominal.Type"

    spec_ref: morph.Spec

    def _metaspec(self):
        return self.spec_ref._args_const()

    def _dir(self, data: Data | MissingType = Missing) -> morph.Struct[str, Type] | None:
        _ = data
        bridge = morph.BRIDGE.get(morph.DEFAULT_BRIDGE)
        return bridge.fields(self)

    def _fields(self) -> morph.Struct[str, Type] | None:
        return morph.BRIDGE.get(morph.DEFAULT_BRIDGE).fields(self)

    def _encode(self, data: Data) -> Data:
        fields = self._fields()

        if fields is None:
            return data

        if isinstance(data, Builtin):
            data = tuple(getattr(data, k) for k in cast(tuple[str, ...], fields.index.keys))
        elif not isinstance(data, tuple):
            raise ValueError(
                f"Expected tuple data for NominalType with fields, got {type(data)}"
            )

        if len(data) != len(fields):
            raise ValueError(f"Expected {len(fields)} fields, got {len(data)}")

        from .api import _encode

        return cast(
            Data,
            tuple(
                _encode(field_type, field_value)
                for field_type, field_value in zip(fields, data)
            ),
        )

    def _decode(self, raw_data: Data) -> Data:
        fields = self._fields()
        bridge = morph.BRIDGE.get(morph.DEFAULT_BRIDGE)

        if self.spec_ref.path == "std.Any":
            return raw_data

        if fields is None:
            construct = getattr(bridge, "construct", None)
            if construct is not None:
                try:
                    return construct(self, ())
                except ValueError:
                    return raw_data
            return raw_data

        if not isinstance(raw_data, tuple):
            raise ValueError(
                f"Expected tuple data for NominalType with fields, got {type(raw_data)}"
            )
        if len(raw_data) != len(fields):
            raise ValueError(f"Expected {len(fields)} fields, got {len(raw_data)}")

        from .api import _decode

        decoded = tuple(
            _decode(field_type, field_value)
            for field_type, field_value in zip(fields, raw_data)
        )
        construct = getattr(bridge, "construct", None)
        if construct is not None:
            try:
                return construct(self, decoded)
            except ValueError:
                pass
        return decoded


class UnionType(Type):
    ANCHOR: ClassVar[str] = "dom.Union.Type"

    types: frozenset[Type]

    def __invariants__(self) -> None:
        if not self.types:
            raise TypeError("UnionType.types must not be empty")
        for type in self.types:
            if isinstance(type, UnionType):
                raise TypeError(
                    "UnionType.types must not contain nested UnionTypes; use protomorph.union_type() for automatic flattening"
                )

    def _decode(self, raw_data: Data) -> Data:
        raise NotImplementedError("decode for UnionType is not yet supported")
