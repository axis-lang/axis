from __future__ import annotations

from typing import Any, ClassVar, cast

from protobase import frozendict

import protomorph_ as pm

from .base import Builtin, Data

__all__ = [
    "Type",
    "StructType",
    "NominalType",
    "UnionType",
]


class Type(Builtin, abstract=True):
    val_cls: ClassVar[type[pm.Val] | None] = None
    ANCHOR: ClassVar[str]

    @classmethod
    def _type(cls, *args: type | pm.Type) -> pm.Type:
        if args:
            raise TypeError(
                f"{cls.__name__}._type does not accept host-specific type arguments in protomorph core"
            )
        return pm.nominal_type(cls._anchor_path())

    def _metatype(self) -> pm.Type:
        return pm.nominal_type(self._anchor_path(), self._metaspec())

    def _wrap(self, data: Data) -> pm.Val:
        val_cls = type(self).val_cls or pm.Const
        return val_cls(self, data)

    def _metaspec(self) -> pm.Const:
        return pm.EmptyStruct

    def layout(self) -> pm.Layout | None:
        return None

    def decode(self, raw_data: Data) -> pm.Val:
        return self._wrap(self.deserialize(raw_data))

    def construct(self, *args, **kwargs) -> pm.Val:
        raise TypeError(f"{type(self).__name__}.construct is not available for opaque types")

    def serialize(self, data: Data, format: str | None = None) -> Data:
        _ = format
        return data

    def deserialize(self, raw_data: Data) -> Data:
        return raw_data

    def _get(self, data: Data, key: str | int) -> pm.Val:
        layout = self.layout()
        if layout is None:
            raise KeyError(f"No member {key!r} on opaque type {type(self).__name__}")
        if not isinstance(layout, pm.StructLayout):
            raise KeyError(f"No member {key!r} on non-struct type {type(self).__name__}")
        fields = layout.fields

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
    ANCHOR: ClassVar[str] = "std.types.StructType"

    meta_attrs: pm.Struct[str, Type]

    @property
    def struct_shape(self) -> pm.Struct.Shape[str]:
        return self.meta_attrs.shape

    @property
    def struct_index(self) -> pm.Struct.Index[str]:
        return self.meta_attrs.index

    def _metaspec(self) -> pm.Const:
        positional: list[pm.Const | pm.Var] = []
        nominal: dict[str, pm.Const | pm.Var] = {}

        schema_fields = self.meta_attrs.map(lambda meta_attr: pm.type_of(pm.val(meta_attr)))
        for key, value in zip(schema_fields.index.keys, schema_fields.values):
            typed = cast(pm.Const | pm.Var, value)
            if key is None:
                positional.append(typed)
            else:
                nominal[key] = typed

        return pm.struct(*positional, **nominal)

    def deserialize(self, raw_data: Data) -> Data:
        match raw_data:
            case tuple() as raw_fields:
                if len(raw_fields) != len(self.meta_attrs):
                    raise ValueError(
                        f"Expected {len(self.meta_attrs)} fields, got {len(raw_fields)}"
                    )
                return tuple(
                    field_type.deserialize(field_raw)
                    for field_type, field_raw in zip(self.meta_attrs.values, raw_fields)
                )
            case _:
                raise TypeError(
                    f"Expected tuple data for StructType, got {type(raw_data)}"
                )

    def layout(self) -> pm.StructLayout:
        return pm.StructLayout(fields=self.meta_attrs)

    def decode(self, raw_data: Data) -> pm.Val:
        return self._wrap(self.deserialize(raw_data))

    def construct(self, *args, **kwargs) -> pm.Val:
        raw = _normalize_struct_input(self.meta_attrs, args, kwargs)
        return self.decode(raw)

    def serialize(self, data: Data, format: str | None = None) -> Data:
        _ = format
        return _encode_struct_data(self.meta_attrs, data)


class NominalType(Type):
    ANCHOR: ClassVar[str] = "std.types.NominalType"

    spec_ref: pm.Spec

    def _metaspec(self):
        return self.spec_ref.__type__._metaspec()

    def layout(self) -> pm.Layout | None:
        return pm.layout_of(self)

    def qualify(self, underlying: type | pm.Type) -> pm.NominalQualifier:
        return pm.nominal_qual(self.spec_ref.anchor, self.spec_ref._args_const(), underlying=pm.type_(underlying))

    def decode(self, raw_data: Data) -> pm.Val:
        decoded = self.deserialize(raw_data)
        return self._wrap(decoded)

    def construct(self, *args, **kwargs) -> pm.Val:
        layout = self.layout()
        if not isinstance(layout, pm.StructLayout):
            raise TypeError(f"{type(self).__name__}.construct is not available for opaque nominal types")
        raw = _normalize_struct_input(layout.fields, args, kwargs)
        return self.decode(raw)

    def serialize(self, data: Data, format: str | None = None) -> Data:
        _ = format
        layout = self.layout()
        if isinstance(layout, pm.AtomicLayout):
            _validate_atomic_data(self, layout, data)
            return data
        if layout is None:
            raise TypeError(f"{type(self).__name__}.encode is not available for {self.spec_ref!r}")
        if not isinstance(layout, pm.StructLayout):
            raise TypeError(f"{type(self).__name__}.encode requires a struct or atomic layout for {self.spec_ref!r}")
        return _encode_struct_data(layout.fields, data)

    def deserialize(self, raw_data: Data) -> Data:
        layout = self.layout()
        if isinstance(layout, pm.AtomicLayout):
            _validate_atomic_data(self, layout, raw_data)
            return raw_data
        if layout is None:
            raise TypeError(f"{type(self).__name__}.decode is not available for opaque nominal types")
        if not isinstance(layout, pm.StructLayout):
            raise TypeError(f"{type(self).__name__}.decode requires a struct or atomic layout")

        decoded = _decode_struct_data(layout.fields, raw_data)
        if layout.builtin_cls is None:
            return decoded

        attrs = {
            key: value
            for key, value in zip(layout.fields.index.keys, decoded)
            if key is not None
        }
        return cast(Data, layout.builtin_cls(**attrs))


class UnionType(Type):
    ANCHOR: ClassVar[str] = "std.types.UnionType"

    types: frozenset[Type]

    def __invariants__(self) -> None:
        if not self.types:
            raise TypeError("UnionType.types must not be empty")
        for type in self.types:
            if isinstance(type, UnionType):
                raise TypeError(
                    "UnionType.types must not contain nested UnionTypes; use protomorph.union_type() for automatic flattening"
                )

    def deserialize(self, raw_data: Data) -> Data:
        raise NotImplementedError("decode for UnionType is not yet supported")


def _normalize_struct_input(
    fields: pm.Struct[str, Type],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> tuple[Data, ...]:
    keys = fields.index.keys
    if not keys:
        if args or kwargs:
            raise ValueError("Expected no fields")
        return ()

    positional_slots = sum(1 for key in keys if key is None)
    named_slots = {key for key in keys if key is not None}

    if len(args) > positional_slots:
        raise ValueError(f"Expected at most {positional_slots} positional args, got {len(args)}")

    extras = set(kwargs) - named_slots
    if extras:
        raise ValueError(f"Unexpected named fields: {sorted(extras)!r}")

    raw_values: list[Data] = []
    positional_index = 0
    for key, field_type in zip(keys, fields.values):
        if key is None:
            if positional_index >= len(args):
                raise ValueError("Missing positional field")
            value = args[positional_index]
            positional_index += 1
        else:
            if key not in kwargs:
                raise ValueError(f"Missing named field {key!r}")
            value = kwargs[key]
        raw_values.append(_normalize_input_for_type(field_type, value))

    if positional_index != len(args):
        raise ValueError("Too many positional args")

    return tuple(raw_values)


def _normalize_input_for_type(type_: Type, value: Any) -> Data:
    if isinstance(value, pm.Val):
        if value.__type__ != type_:
            raise TypeError(f"Expected value of type {type_!r}, got {value.__type__!r}")
        return value.__data__

    if isinstance(type_, StructType):
        if isinstance(value, tuple):
            return cast(Data, _decode_struct_data(type_.meta_attrs, value, preserve_raw=True))
        if isinstance(value, list):
            return cast(Data, _decode_struct_data(type_.meta_attrs, tuple(value), preserve_raw=True))
        if isinstance(value, dict):
            return cast(Data, _normalize_struct_input(type_.meta_attrs, (), value))
        raise TypeError(f"Expected tuple/list/dict input for {type_!r}")

    layout = type_.layout()
    if isinstance(layout, pm.StructLayout):
        if isinstance(value, tuple):
            return cast(Data, _decode_struct_data(layout.fields, value, preserve_raw=True))
        if isinstance(value, list):
            return cast(Data, _decode_struct_data(layout.fields, tuple(value), preserve_raw=True))
        if isinstance(value, dict):
            return cast(Data, _normalize_struct_input(layout.fields, (), value))
        raise TypeError(f"Expected tuple/list/dict input for {type_!r}")

    if isinstance(layout, pm.AtomicLayout):
        if isinstance(value, list):
            return cast(Data, tuple(value))
        if isinstance(value, dict):
            return cast(Data, frozendict(value))
        _validate_atomic_data(type_, layout, cast(Data, value))
        return cast(Data, value)

    raise TypeError(f"Cannot construct opaque field type {type_!r}")


def _decode_struct_data(
    fields: pm.Struct[str, Type],
    raw_data: Any,
    *,
    preserve_raw: bool = False,
) -> tuple[Data, ...]:
    if not isinstance(raw_data, tuple):
        raise TypeError(f"Expected tuple data for structured decode, got {type(raw_data)}")
    if len(raw_data) != len(fields):
        raise ValueError(f"Expected {len(fields)} fields, got {len(raw_data)}")

    decoded: list[Data] = []
    for field_type, field_raw in zip(fields.values, raw_data):
        if preserve_raw:
            if isinstance(field_raw, list):
                field_raw = tuple(field_raw)
            if isinstance(field_raw, dict):
                layout = field_type.layout()
                if not isinstance(layout, pm.StructLayout):
                    raise TypeError(f"Cannot normalize mapping for opaque field type {field_type!r}")
                field_raw = _normalize_struct_input(layout.fields, (), field_raw)
            decoded.append(cast(Data, field_raw))
            continue
        decoded.append(cast(Data, field_type.decode(cast(Data, field_raw)).__data__))
    return tuple(decoded)


def _encode_struct_data(fields: pm.Struct[str, Type], data: Data) -> tuple[Data, ...]:
    if isinstance(data, Builtin):
        data = tuple(
            getattr(data, key)
            for key in cast(tuple[str | None, ...], fields.index.keys)
            if key is not None
        )

    if not isinstance(data, tuple):
        raise TypeError(f"Expected tuple/builtin data for structured encode, got {type(data)}")
    if len(data) != len(fields):
        raise ValueError(f"Expected {len(fields)} fields, got {len(data)}")

    return tuple(field_type.serialize(field_data) for field_type, field_data in zip(fields.values, data))


def _validate_atomic_data(type_: Type, layout: pm.AtomicLayout, data: Data) -> None:
    valid_types = tuple(layout.valid_types)
    if not isinstance(data, valid_types):
        names = ", ".join(sorted(tp.__name__ for tp in layout.valid_types))
        raise TypeError(f"{type_!r} expects raw data of type {names}, got {type(data).__name__}")
