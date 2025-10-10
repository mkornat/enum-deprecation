import warnings

from enum import Enum, EnumMeta, FlagBoundary, _EnumDict, auto
from typing import TYPE_CHECKING, Any, Optional, Type, Union, overload

try:
    from typing import Never
except ImportError:
    from typing_extensions import Never

if TYPE_CHECKING:
    from enum import _EnumNames  # type: ignore[attr-defined]

_MISSING = object()


class deprecated(auto):
    """
    Marker to declare an enum member as deprecated.

    Usages:
      - auto value (works for Enum/IntEnum/StrEnum/etc.):
          FOO = deprecated()
      - explicit underlying value:
          BAR = deprecated("bar")                 # value="bar"
          BAZ = deprecated(value=123)            # value=123
      - with a custom message:
          OLD = deprecated(msg_tpl="Member {attr} is old")
          X   = deprecated("X", msg_tpl="Don't use {attr}")
    """

    def __init__(self, value=_MISSING, *, msg_tpl: Optional[str] = None) -> None:
        super().__init__()

        _default_tpl: str = (
            "The enum member {attr} is deprecated and will be removed in the future."
        )
        self._has_explicit_value = value is not _MISSING
        self._explicit_value = value if self._has_explicit_value else None
        if msg_tpl is None:
            msg_tpl = _default_tpl
        self._deprecation_msg_tpl = msg_tpl

    def __repr__(self) -> str:
        return self._deprecation_msg_tpl


class allow_deprecation(EnumMeta):
    """
    Metaclass that:
      1) remembers which names were declared with `deprecated(...)`
      2) emits a DeprecationWarning when those members are accessed by:
         - attribute (MyEnum.BAR)
         - name lookup (MyEnum["BAR"])
         - value lookup (MyEnum(<value>))
    Works for Enum and all Enum subclasses (IntEnum, StrEnum, etc.).
    """

    @classmethod
    def __prepare__(mcls, name: str, bases: tuple[type, ...], **kw: Any) -> _EnumDict:
        ns = super().__prepare__(name, bases, **kw)

        Base = ns.__class__

        class TrackingDict(Base):  # type: ignore[misc]
            def __init__(self) -> None:
                super().__init__()
                self._deprecated_map: dict[str, str] = {}

            def __setitem__(self, key: str, value: Any) -> None:
                if isinstance(value, deprecated):
                    self._deprecated_map[key] = value._deprecation_msg_tpl
                    if value._has_explicit_value:
                        value = value._explicit_value
                    else:
                        value = auto()
                return super().__setitem__(key, value)

        ns.__class__ = TrackingDict
        if not hasattr(ns, "_deprecated_map"):
            ns._deprecated_map = {}
        return ns

    def __new__(
        mcls: type["allow_deprecation"],
        cls_name: str,
        bases: tuple[type, ...],
        classdict: "_EnumDict",
        *,
        boundary: Union[FlagBoundary, None] = None,
        _simple: bool = False,
        **kwds: Any,
    ) -> "allow_deprecation":
        # StrEnum auto() special case
        try:
            from enum import StrEnum
        except ImportError:
            StrEnum = None
        is_strenum = StrEnum is not None and any(
            isinstance(b, type) and issubclass(b, StrEnum) for b in bases
        )
        if is_strenum and "_generate_next_value_" not in classdict:
            # Make auto() return the member name
            def _gen(name: str, start: int, count: int, last_values: list[Any]) -> str:
                return name

            classdict["_generate_next_value_"] = _gen

        cls = super().__new__(
            mcls,
            cls_name,
            bases,
            classdict,
            boundary=boundary,
            _simple=_simple,
            **kwds,
        )
        dep_map = getattr(classdict, "_deprecated_map", {})
        type.__setattr__(cls, "__deprecated_map__", dict(dep_map))
        return cls

    # Attribute access: MyEnum.BAR
    def __getattribute__(cls, name: str) -> Any:
        if name.startswith("_") or name in ("__members__", "__deprecated_map__"):
            return type.__getattribute__(cls, name)
        attr = super().__getattribute__(name)
        try:
            dep_map: dict[str, str] = type.__getattribute__(cls, "__deprecated_map__")
        except AttributeError:
            return attr
        if isinstance(attr, cls) and attr.name in dep_map:
            warnings.warn(
                dep_map[attr.name].format(attr=attr.name),
                DeprecationWarning,
                stacklevel=2,
            )
        return attr

    @overload
    def __getitem__(self, item: str) -> Never: ...

    @overload
    def __getitem__(self, item: Any) -> Never: ...

    # Name lookup: MyEnum["BAR"]
    def __getitem__(self, name: str) -> Any:
        member: Any = super().__getitem__(name)  # type: ignore[no-untyped-call]
        dep_map = type.__getattribute__(self, "__deprecated_map__") or {}
        if name in dep_map:
            warnings.warn(
                dep_map[name].format(attr=name),
                DeprecationWarning,
                stacklevel=2,
            )
        return member

    @overload
    def __call__(cls, value: Any, names: None = ...) -> Never: ...

    @overload
    def __call__(
        cls,
        value: str,
        names: "_EnumNames",
        *,
        module: Union[str, None] = ...,
        qualname: Union[str, None] = ...,
        type: Union[type, None] = ...,
        start: int = ...,
        boundary: Union[Any, None] = ...,
    ) -> Type[Enum]: ...

    # Value lookup: MyEnum(<value>)
    def __call__(cls, value: Any, names: Any = None, *args: Any, **kwargs: Any) -> Any:
        if isinstance(names, tuple) and args and isinstance(args[0], dict):
            return super().__call__(value, names, *args, **kwargs)

        if names is None:
            res = super().__call__(value)
            try:
                dep_map = type.__getattribute__(cls, "__deprecated_map__")
            except AttributeError:
                return res
            name = getattr(res, "name", None)
            if name in dep_map:
                warnings.warn(
                    dep_map[name].format(attr=name),
                    DeprecationWarning,
                    stacklevel=2,
                )
            return res

        return super().__call__(value, names, *args, **kwargs)
