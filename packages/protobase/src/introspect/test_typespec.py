"""
Tests completos de typespec.
Cubren: TypeNode, AnnotationResolver, TypeSpecInspector y casos edge.
"""

from __future__ import annotations

import dataclasses
import sys
import typing
from typing import Annotated, Any, Callable, ClassVar, Final, Literal, Optional, Union

import pytest

# Agregar el directorio padre al path para poder importar typespec
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

import typespec
from typespec import (
    ClassInfo,
    EvalStrategy,
    FieldInfo,
    TypeKind,
    TypeNode,
    TypeSpecInspector,
    get_annotated_metadata,
    inspect_class,
    inspect_func,
    inspect_type,
    strip_annotated,
)


# ===========================================================================
# TypeNode.from_type — tipos básicos
# ===========================================================================

class TestTypeNodeSimple:
    def test_int(self):
        node = TypeNode.from_type(int)
        assert node.kind == TypeKind.SIMPLE
        assert node.raw is int

    def test_none_type(self):
        node = TypeNode.from_type(type(None))
        assert node.kind == TypeKind.NONE_TYPE

    def test_none_literal(self):
        node = TypeNode.from_type(None)
        assert node.kind == TypeKind.NONE_TYPE

    def test_custom_class(self):
        class Foo: pass
        node = TypeNode.from_type(Foo)
        assert node.kind == TypeKind.SIMPLE
        assert node.raw is Foo
        assert node.name == "Foo"

    def test_forward_ref(self):
        ref = typing.ForwardRef("SomeClass")
        node = TypeNode.from_type(ref)
        assert node.kind == TypeKind.FORWARD
        assert node.name == "SomeClass"
        assert node.is_forward_ref

    def test_typevar(self):
        T = typing.TypeVar("T")
        node = TypeNode.from_type(T)
        assert node.kind == TypeKind.TYPEVAR
        assert node.name == "T"
        assert node.is_typevar

    def test_paramspec(self):
        P = typing.ParamSpec("P")
        node = TypeNode.from_type(P)
        assert node.kind == TypeKind.PARAMSPEC
        assert node.name == "P"


# ===========================================================================
# TypeNode — Annotated
# ===========================================================================

class TestTypeNodeAnnotated:
    def test_simple_annotated(self):
        tp = Annotated[int, "meta"]
        node = TypeNode.from_type(tp)
        assert node.is_annotated
        assert node.kind == TypeKind.ANNOTATED
        assert node.metadata == ["meta"]
        assert node.inner is not None
        assert node.inner.raw is int

    def test_multiple_metadata(self):
        tp = Annotated[str, "doc", 42, {"key": "val"}]
        node = TypeNode.from_type(tp)
        assert node.metadata == ["doc", 42, {"key": "val"}]

    def test_nested_annotated(self):
        tp = Annotated[Annotated[int, "inner"], "outer"]
        node = TypeNode.from_type(tp)
        assert node.is_annotated
        assert node.metadata == ["outer"]
        assert node.inner is not None
        assert node.inner.is_annotated
        assert node.inner.metadata == ["inner"]
        assert node.inner.inner.raw is int

    def test_all_metadata_nested(self):
        tp = Annotated[Annotated[int, "inner"], "outer"]
        node = TypeNode.from_type(tp)
        assert "outer" in node.all_metadata
        # inner metadata accesible a través de inner
        assert "inner" in node.inner.all_metadata

    def test_base_type(self):
        tp = Annotated[int, "meta"]
        node = TypeNode.from_type(tp)
        assert node.base_type is int

    def test_base_type_nested(self):
        tp = Annotated[Annotated[int, "inner"], "outer"]
        node = TypeNode.from_type(tp)
        assert node.base_type is int

    def test_get_metadata_of_type(self):
        @dataclasses.dataclass
        class Validator:
            min_val: int

        v = Validator(min_val=0)
        tp = Annotated[int, "doc", v]
        node = TypeNode.from_type(tp)
        found = node.get_metadata_of_type(Validator)
        assert found == [v]

    def test_get_metadata_of_type_none_found(self):
        tp = Annotated[int, "doc"]
        node = TypeNode.from_type(tp)
        assert node.get_metadata_of_type(int) == []

    def test_first_metadata_of_type(self):
        @dataclasses.dataclass
        class Tag:
            label: str

        t1, t2 = Tag(label="a"), Tag(label="b")
        tp = Annotated[str, t1, t2]
        node = TypeNode.from_type(tp)
        assert node.first_metadata_of_type(Tag) is t1

    def test_annotated_in_generic(self):
        tp = list[Annotated[int, "item_meta"]]
        node = TypeNode.from_type(tp)
        assert node.kind == TypeKind.GENERIC
        assert node.args[0].is_annotated
        assert node.args[0].metadata == ["item_meta"]


# ===========================================================================
# TypeNode — Union y Optional
# ===========================================================================

class TestTypeNodeUnion:
    def test_union(self):
        tp = Union[int, str]
        node = TypeNode.from_type(tp)
        assert node.kind == TypeKind.UNION
        assert len(node.args) == 2
        assert not node.is_nullable

    def test_optional(self):
        tp = Optional[int]
        node = TypeNode.from_type(tp)
        assert node.kind == TypeKind.OPTIONAL
        assert node.is_optional
        assert node.is_nullable
        assert node.inner.raw is int

    def test_union_with_none(self):
        tp = Union[int, str, None]
        node = TypeNode.from_type(tp)
        assert node.kind == TypeKind.UNION
        assert node.is_nullable

    def test_optional_annotated(self):
        tp = Optional[Annotated[int, "meta"]]
        node = TypeNode.from_type(tp)
        assert node.is_optional
        assert node.inner.is_annotated
        assert node.inner.metadata == ["meta"]

    def test_union_of_annotated(self):
        tp = Union[Annotated[int, "a"], Annotated[str, "b"]]
        node = TypeNode.from_type(tp)
        assert node.kind == TypeKind.UNION
        assert all(a.is_annotated for a in node.args)


# ===========================================================================
# TypeNode — Genéricos
# ===========================================================================

class TestTypeNodeGenerics:
    def test_list(self):
        tp = list[int]
        node = TypeNode.from_type(tp)
        assert node.kind == TypeKind.GENERIC
        assert node.origin is list
        assert node.args[0].raw is int

    def test_dict(self):
        tp = dict[str, int]
        node = TypeNode.from_type(tp)
        assert node.kind == TypeKind.GENERIC
        assert node.origin is dict
        assert len(node.args) == 2

    def test_nested_generic(self):
        tp = dict[str, list[int]]
        node = TypeNode.from_type(tp)
        assert node.args[1].kind == TypeKind.GENERIC
        assert node.args[1].origin is list

    def test_classvar(self):
        tp = ClassVar[int]
        node = TypeNode.from_type(tp)
        assert node.kind == TypeKind.CLASSVAR
        assert node.inner.raw is int

    def test_final(self):
        tp = Final[str]
        node = TypeNode.from_type(tp)
        assert node.kind == TypeKind.FINAL
        assert node.inner.raw is str

    def test_literal(self):
        tp = Literal["a", "b", 1]
        node = TypeNode.from_type(tp)
        assert node.is_literal
        assert node.literal_values == ["a", "b", 1]

    def test_callable(self):
        tp = Callable[[int, str], bool]
        node = TypeNode.from_type(tp)
        assert node.kind == TypeKind.CALLABLE


# ===========================================================================
# TypeNode — walk y find
# ===========================================================================

class TestTypeNodeWalk:
    def test_walk_simple(self):
        node = TypeNode.from_type(int)
        nodes = list(node.walk())
        assert len(nodes) == 1

    def test_walk_annotated(self):
        tp = Annotated[int, "meta"]
        node = TypeNode.from_type(tp)
        nodes = list(node.walk())
        # Annotated + int inner
        assert len(nodes) == 2

    def test_walk_complex(self):
        tp = Annotated[dict[str, list[Annotated[int, "x"]]], "outer"]
        node = TypeNode.from_type(tp)
        nodes = list(node.walk())
        annotated_nodes = [n for n in nodes if n.is_annotated]
        assert len(annotated_nodes) == 2  # outer + inner

    def test_find_all_annotated(self):
        tp = Annotated[dict[str, list[Annotated[int, "x"]]], "outer"]
        node = TypeNode.from_type(tp)
        found = node.find_annotated()
        assert len(found) == 2

    def test_find_all_custom(self):
        tp = dict[str, list[int]]
        node = TypeNode.from_type(tp)
        generics = node.find_all(lambda n: n.kind == TypeKind.GENERIC)
        assert len(generics) == 2  # dict + list


# ===========================================================================
# AnnotationResolver
# ===========================================================================

class TestAnnotationResolver:
    def test_resolve_class_basic(self):
        from typespec.resolver import AnnotationResolver

        class Foo:
            x: int
            y: str

        r = AnnotationResolver()
        hints = r.resolve(Foo)
        assert hints["x"] is int
        assert hints["y"] is str

    def test_resolve_with_annotated(self):
        from typespec.resolver import AnnotationResolver

        class Foo:
            x: Annotated[int, "meta"]

        r = AnnotationResolver()
        hints = r.resolve(Foo)
        assert typing.get_origin(hints["x"]) is Annotated

    def test_resolve_include_extras_false(self):
        from typespec.resolver import AnnotationResolver

        class Foo:
            x: Annotated[int, "meta"]

        strategy = EvalStrategy(include_extras=False)
        r = AnnotationResolver(strategy)
        hints = r.resolve(Foo)
        assert hints["x"] is int  # Annotated stripped

    def test_resolve_function(self):
        from typespec.resolver import AnnotationResolver

        def foo(x: Annotated[int, "meta"]) -> str: ...

        r = AnnotationResolver()
        hints = r.resolve(foo)
        assert "x" in hints
        assert "return" in hints

    def test_resolve_classmethod(self):
        from typespec.resolver import AnnotationResolver

        class MyClass:
            @classmethod
            def create(cls, x: Annotated[int, "x"]) -> "MyClass": ...

        r = AnnotationResolver()
        cm = MyClass.__dict__["create"]
        hints = r.resolve(cm)
        assert "x" in hints

    def test_resolve_staticmethod(self):
        from typespec.resolver import AnnotationResolver

        class MyClass:
            @staticmethod
            def helper(x: Annotated[str, "x"]) -> bool: ...

        r = AnnotationResolver()
        sm = MyClass.__dict__["helper"]
        hints = r.resolve(sm)
        assert "x" in hints

    def test_resolve_property(self):
        from typespec.resolver import AnnotationResolver

        class MyClass:
            @property
            def value(self) -> Annotated[float, "val"]: ...

        r = AnnotationResolver()
        prop = MyClass.__dict__["value"]
        hints = r.resolve(prop)
        assert "return" in hints

    def test_resolve_string_annotation(self):
        from typespec.resolver import AnnotationResolver

        class Foo:
            pass

        Foo.__annotations__ = {"x": "int", "y": "str"}

        r = AnnotationResolver()
        hints = r.resolve(Foo)
        assert hints.get("x") is int

    def test_resolve_with_mro(self):
        from typespec.resolver import AnnotationResolver

        class Base:
            x: Annotated[int, "base"]
            y: str

        class Child(Base):
            y: Annotated[str, "overridden"]
            z: float

        r = AnnotationResolver()
        hints = r.resolve(Child, follow_mro=True)
        assert "x" in hints  # heredado
        assert "y" in hints  # sobreescrito
        assert "z" in hints  # propio

    def test_strategy_string_mode(self):
        from typespec.resolver import AnnotationResolver

        class Foo:
            x: "int"

        strategy = EvalStrategy(mode=EvalStrategy.STRING)
        r = AnnotationResolver(strategy)
        hints = r.resolve(Foo)
        # En modo string, devuelve sin evaluar
        assert hints.get("x") == "int"


# ===========================================================================
# inspect_class
# ===========================================================================

class TestInspectClass:
    def test_basic_class(self):
        class Model:
            name: Annotated[str, "El nombre"]
            age: int

        info = inspect_class(Model)
        assert "name" in info.fields
        assert "age" in info.fields
        assert info.fields["name"].annotation.is_annotated
        assert info.fields["name"].metadata == ["El nombre"]
        assert not info.fields["age"].annotation.is_annotated

    def test_dataclass(self):
        @dataclasses.dataclass
        class DC:
            name: Annotated[str, "nombre"]
            count: int = 0

        info = inspect_class(DC)
        assert info.is_dataclass
        assert info.fields["count"].has_default
        assert info.fields["count"].default == 0
        assert not info.fields["name"].has_default

    def test_classvar_detection(self):
        class WithClassVar:
            count: ClassVar[int] = 0
            name: str

        info = inspect_class(WithClassVar)
        assert info.fields["count"].is_classvar
        assert not info.fields["name"].is_classvar
        assert "count" in info.class_vars
        assert "count" not in info.instance_fields

    def test_optional_field(self):
        class Model:
            name: Optional[str]

        info = inspect_class(Model)
        assert info.fields["name"].is_optional

    def test_fields_with_metadata(self):
        @dataclasses.dataclass
        class Tag:
            label: str

        t = Tag(label="important")

        class Model:
            x: Annotated[int, t]
            y: str

        info = inspect_class(Model)
        tagged = info.fields_with_metadata(Tag)
        assert "x" in tagged
        assert "y" not in tagged

    def test_follow_mro(self):
        class Base:
            x: Annotated[int, "base x"]

        class Child(Base):
            y: Annotated[str, "child y"]

        info = inspect_class(Child, follow_mro=True)
        assert "x" in info.fields
        assert "y" in info.fields
        assert info.fields["x"].annotation.metadata == ["base x"]

    def test_field_base_type(self):
        class Model:
            x: Annotated[Optional[int], "meta"]

        info = inspect_class(Model)
        # base_type debería ser Optional[int] (sin el Annotated)
        base = info.fields["x"].base_type
        assert typing.get_origin(base) is Union


# ===========================================================================
# inspect_func
# ===========================================================================

class TestInspectFunc:
    def test_basic_function(self):
        def foo(x: Annotated[int, "x param"], y: str) -> bool: ...

        sig = inspect_func(foo)
        assert "x" in sig.params
        assert "y" in sig.params
        assert sig.params["x"].annotation.is_annotated
        assert sig.params["x"].metadata == ["x param"]
        assert sig.return_annotation is not None
        assert sig.return_annotation.raw is bool

    def test_no_annotations(self):
        def foo(x, y): ...

        sig = inspect_func(foo)
        assert "x" in sig.params
        assert sig.params["x"].annotation is None

    def test_default_values(self):
        def foo(x: int, y: str = "default"): ...

        sig = inspect_func(foo)
        assert not sig.params["x"].has_default
        assert sig.params["y"].has_default
        assert sig.params["y"].default == "default"

    def test_return_annotated(self):
        def foo() -> Annotated[int, "result"]: ...

        sig = inspect_func(foo)
        assert sig.return_annotation is not None
        assert sig.return_annotation.is_annotated
        assert sig.return_annotation.metadata == ["result"]

    def test_params_with_metadata(self):
        @dataclasses.dataclass
        class Doc:
            text: str

        d = Doc(text="hello")

        def foo(x: Annotated[int, d], y: str): ...

        sig = inspect_func(foo)
        params = sig.params_with_metadata(Doc)
        assert "x" in params
        assert "y" not in params

    def test_keyword_only(self):
        def foo(x: int, *, y: Annotated[str, "kw"]): ...

        sig = inspect_func(foo)
        assert sig.params["y"].kind == "KEYWORD_ONLY"
        assert sig.params["y"].metadata == ["kw"]

    def test_positional_params(self):
        def foo(a: int, b: str, *, c: bool): ...

        sig = inspect_func(foo)
        pos = sig.positional_params
        assert "a" in pos and "b" in pos
        assert "c" not in pos

    def test_classmethod(self):
        class Foo:
            @classmethod
            def create(cls, x: Annotated[int, "x"]) -> "Foo": ...

        sig = inspect_func(Foo.create)
        # cls no debe aparecer
        assert "cls" not in sig.params
        assert "x" in sig.params

    def test_lambda_no_annotations(self):
        f = lambda x, y: x + y

        sig = inspect_func(f)
        assert "x" in sig.params
        assert sig.params["x"].annotation is None


# ===========================================================================
# Funciones de conveniencia del módulo
# ===========================================================================

class TestModuleFunctions:
    def test_get_annotated_metadata(self):
        assert get_annotated_metadata(Annotated[int, "a", "b"]) == ["a", "b"]
        assert get_annotated_metadata(int) == []

    def test_strip_annotated(self):
        assert strip_annotated(Annotated[int, "meta"]) is int
        assert strip_annotated(int) is int

    def test_strip_nested_annotated(self):
        tp = Annotated[Annotated[int, "inner"], "outer"]
        # base_type atraviesa todos los niveles
        result = strip_annotated(tp)
        assert result is int

    def test_inspect_type_union(self):
        node = inspect_type(Union[int, str, None])
        assert node.is_nullable
        assert node.kind == TypeKind.UNION

    def test_inspect_type_literal(self):
        node = inspect_type(Literal["a", "b"])
        assert node.is_literal
        assert "a" in node.literal_values


# ===========================================================================
# Casos edge y escenarios avanzados
# ===========================================================================

class TestEdgeCases:
    def test_annotated_with_no_extra_metadata(self):
        # Annotated con solo un argumento extra es válido
        tp = Annotated[int, None]
        node = TypeNode.from_type(tp)
        assert node.is_annotated
        assert node.metadata == [None]

    def test_deeply_nested_type(self):
        tp = Annotated[
            dict[str, list[Optional[Annotated[int, "deep"]]]],
            "top"
        ]
        node = TypeNode.from_type(tp)
        assert node.is_annotated
        annotated_nodes = node.find_annotated()
        assert len(annotated_nodes) == 2  # top + deep

    def test_union_with_annotated_preserves_meta(self):
        tp = Union[Annotated[int, "int_meta"], Annotated[str, "str_meta"]]
        node = TypeNode.from_type(tp)
        assert node.kind == TypeKind.UNION
        metas = [a.metadata[0] for a in node.args if a.is_annotated]
        assert "int_meta" in metas
        assert "str_meta" in metas

    def test_empty_class(self):
        class Empty: pass

        info = inspect_class(Empty)
        assert info.fields == {}

    def test_class_with_only_classvars(self):
        class Config:
            MAX: ClassVar[int] = 100
            NAME: ClassVar[str] = "app"

        info = inspect_class(Config)
        assert all(f.is_classvar for f in info.fields.values())
        assert info.instance_fields == {}

    def test_typealiastype(self):
        MyType = typing.TypeAliasType("MyType", Annotated[int, "alias"])
        node = TypeNode.from_type(MyType)
        # El inner debe ser el Annotated
        assert node.inner is not None
        assert node.inner.is_annotated

    def test_is_evaluable(self):
        from typespec.resolver import AnnotationResolver

        class Good:
            x: int

        class Bad:
            pass
        Bad.__annotations__ = {"x": "NonExistentType12345"}

        r = AnnotationResolver()
        assert r.is_evaluable(Good)
        # Bad puede fallar o no según fallbacks; simplemente no debe lanzar
        result = r.is_evaluable(Bad)
        assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
