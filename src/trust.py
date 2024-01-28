# %%
from functools import cached_property as cached_property_std

from typing import (
    Any,
    dataclass_transform,
    get_type_hints,
)


@dataclass_transform()
class TrustMetaclass(type):
    """
    Metaclass for Trust classes.

    This metaclass is responsible for handling the creation of Trust classes.
    It performs checks on the base classes and sets the appropriate slots based on the class attributes.

    Attributes:
        type_hints: A cached property that returns the type hints for the class.

    Args:
        name (str): The name of the class.
        bases (tuple[type, ...]): The base classes of the class.
        namespace (dict[str, Any]): The namespace of the class.
        weak_refs (bool | Undefined, optional): Flag indicating whether weak references are enabled. Defaults to Undefined.
        dynamic_attrs (bool | Undefined, optional): Flag indicating whether dynamic properties are enabled. Defaults to Undefined.

    Raises:
        TypeError: If __slots__ is defined in the namespace of the class.

    Returns:
        The created class.
    """

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        weak_refs: bool | None = None,
        dynamic_attrs: bool | None = None,
    ):
        has_weak_references = False
        has_dynamic_properties = False

        for base in bases:
            if not isinstance(base, TrustMetaclass):
                raise TypeError(
                    f"Invalid base class: `{base.__qualname__}`."
                    f"All base classes must be Trust classes."
                )

            if "__weakref__" in base.__slots__:
                has_weak_references = True

                if weak_refs is False:
                    raise TypeError(
                        f"Cannot disable `weak_refs`. "
                        f"`weak_references` are enabled in base class {base.__qualname__}. You cannot disable them in a subclass."
                    )

            if "__dict__" in base.__slots__:
                has_dynamic_properties = True

                if dynamic_attrs is False:
                    raise TypeError(
                        f"Cannot disable `dynamic_attrs`. "
                        f"`dynamic_attrs` are enabled in base class {base.__qualname__}. You cannot disable them in a subclass."
                    )

        if "__slots__" in namespace:
            raise TypeError("You cannot define __slots__ in a Trust class.")

        # cls = type.__new__(mcs, name, bases, {})

        fields = namespace.get("__annotations__", {})

        defaults = []
        for field in fields:
            if not field in namespace:
                assert (
                    len(defaults) == 0
                ), f"no default field {field} followed by default field"
                continue

            defaults.append(namespace.pop(field))

        slots = []

        if not has_weak_references and weak_refs is True:
            slots.append("__weakref__")

        if not has_dynamic_properties and dynamic_attrs is True:
            slots.append("__dict__")

        slots += fields  # TODO: discard ClassVars fields without evaluation

        slots += [
            f"_cached_{nm}"
            for nm, item in namespace.items()
            if isinstance(item, cached_property_std)
        ]

        namespace["__slots__"] = tuple(slots)
        namespace["__defaults__"] = tuple(defaults)

        return type.__new__(mcs, name, bases, namespace)

    # @cached_property_std
    @property
    def fields(self):
        return get_type_hints(self)


class cached_property(cached_property_std):
    """
    A decorator that converts a method into a read-only cached property.
    The property value is computed once and then stored as a regular attribute
    on the instance. Subsequent accesses to the property will return the cached value
    instead of recomputing it.
    """

    def __set_name__(self, owner, name):
        super().__set_name__(owner, name)
        self.attrname = f"_cached_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.attrname is None:
            raise TypeError(
                "Cannot use cached_property instance without calling __set_name__ on it."
            )

        descriptor = getattr(owner, self.attrname)

        try:
            return descriptor.__get__(instance, owner)
        except AttributeError:
            pass

        val = self.func(instance)
        descriptor.__set__(instance, val)
        return val


@dataclass_transform()
class Trust(
    metaclass=TrustMetaclass,
    weak_refs=False,
    dynamic_attrs=False,
):
    """Base class for trust objects."""
