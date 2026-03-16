from __future__ import annotations

from typing import Any, ClassVar, cast

from protobase import frozendict

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

    def layout(self) -> morph.Layout | None:
        return None

    def decode(self, raw_data: Data) -> morph.Val:
        return self._wrap(self.deserialize(raw_data))

    def construct(self, *args, **kwargs) -> morph.Val:
        raise TypeError(f"{type(self).__name__}.construct is not available for opaque types")

    def serialize(self, data: Data, format: str | None = None) -> Data:
        _ = format
        return data

    def deserialize(self, raw_data: Data) -> Data:
        return raw_data

    def _get(self, data: Data, key: str | int) -> morph.Val:
        layout = self.layout()
        if layout is None:
            raise KeyError(f"No member {key!r} on opaque type {type(self).__name__}")
        if not isinstance(layout, morph.StructLayout):
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
    ANCHOR: ClassVar[str] = "dom.Struct.Type"

    meta_attrs: morph.Struct[str, Type]

    @property
    def struct_shape(self) -> morph.Struct.Shape[str]:
        return self.meta_attrs.shape

    @property
    def struct_index(self) -> morph.Struct.Index[str]:
        return self.meta_attrs.index

    def _metaspec(self):
        return morph.struct(
            *self.meta_attrs.map(lambda meta_attr: morph.type_of(morph.val(meta_attr)))
        )

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

    def layout(self) -> morph.StructLayout:
        return morph.StructLayout(fields=self.meta_attrs)

    def decode(self, raw_data: Data) -> morph.Val:
        return self._wrap(self.deserialize(raw_data))

    def construct(self, *args, **kwargs) -> morph.Val:
        raw = _normalize_struct_input(self.meta_attrs, args, kwargs)
        return self.decode(raw)

    def serialize(self, data: Data, format: str | None = None) -> Data:
        _ = format
        return _encode_struct_data(self.meta_attrs, data)


class NominalType(Type):
    ANCHOR: ClassVar[str] = "dom.Nominal.Type"

    spec_ref: morph.Spec

    def _metaspec(self):
        return self.spec_ref._args_const()

    def layout(self) -> morph.Layout | None:
        return morph.layout_of(self)

    def qualify(self, underlying: type | morph.Type) -> morph.NominalQualifier:
        return morph.nominal_qual(self.spec_ref.anchor, self.spec_ref._args_const(), underlying=morph.type_(underlying))

    def decode(self, raw_data: Data) -> morph.Val:
        decoded = self.deserialize(raw_data)
        return self._wrap(decoded)

    def construct(self, *args, **kwargs) -> morph.Val:
        layout = self.layout()
        if not isinstance(layout, morph.StructLayout):
            raise TypeError(f"{type(self).__name__}.construct is not available for opaque nominal types")
        raw = _normalize_struct_input(layout.fields, args, kwargs)
        return self.decode(raw)

    def serialize(self, data: Data, format: str | None = None) -> Data:
        _ = format
        layout = self.layout()
        if isinstance(layout, morph.AtomicLayout):
            _validate_atomic_data(self, layout, data)
            return data
        if layout is None:
            raise TypeError(f"{type(self).__name__}.encode is not available for opaque nominal types")
        if not isinstance(layout, morph.StructLayout):
            raise TypeError(f"{type(self).__name__}.encode requires a struct or atomic layout")
        return _encode_struct_data(layout.fields, data)

    def deserialize(self, raw_data: Data) -> Data:
        layout = self.layout()
        if isinstance(layout, morph.AtomicLayout):
            _validate_atomic_data(self, layout, raw_data)
            return raw_data
        if layout is None:
            raise TypeError(f"{type(self).__name__}.decode is not available for opaque nominal types")
        if not isinstance(layout, morph.StructLayout):
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

    def deserialize(self, raw_data: Data) -> Data:
        raise NotImplementedError("decode for UnionType is not yet supported")


def _normalize_struct_input(
    fields: morph.Struct[str, Type],
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
    if isinstance(value, morph.Val):
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
    if isinstance(layout, morph.StructLayout):
        if isinstance(value, tuple):
            return cast(Data, _decode_struct_data(layout.fields, value, preserve_raw=True))
        if isinstance(value, list):
            return cast(Data, _decode_struct_data(layout.fields, tuple(value), preserve_raw=True))
        if isinstance(value, dict):
            return cast(Data, _normalize_struct_input(layout.fields, (), value))
        raise TypeError(f"Expected tuple/list/dict input for {type_!r}")

    if isinstance(layout, morph.AtomicLayout):
        if isinstance(value, list):
            return cast(Data, tuple(value))
        if isinstance(value, dict):
            return cast(Data, frozendict(value))
        _validate_atomic_data(type_, layout, cast(Data, value))
        return cast(Data, value)

    raise TypeError(f"Cannot construct opaque field type {type_!r}")


def _decode_struct_data(
    fields: morph.Struct[str, Type],
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
                if not isinstance(layout, morph.StructLayout):
                    raise TypeError(f"Cannot normalize mapping for opaque field type {field_type!r}")
                field_raw = _normalize_struct_input(layout.fields, (), field_raw)
            decoded.append(cast(Data, field_raw))
            continue
        decoded.append(cast(Data, field_type.decode(cast(Data, field_raw)).__data__))
    return tuple(decoded)


def _encode_struct_data(fields: morph.Struct[str, Type], data: Data) -> tuple[Data, ...]:
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


def _validate_atomic_data(type_: Type, layout: morph.AtomicLayout, data: Data) -> None:
    valid_types = tuple(layout.valid_types)
    if not isinstance(data, valid_types):
        names = ", ".join(sorted(tp.__name__ for tp in layout.valid_types))
        raise TypeError(f"{type_!r} expects raw data of type {names}, got {type(data).__name__}")
