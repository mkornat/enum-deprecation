import sys

from enum import Enum, EnumMeta, FlagBoundary, _EnumNames, auto
from typing import Any, Optional, Type, Union, overload

from typing_extensions import Never

class deprecated(auto):
    def __init__(self, value: Any = ..., *, msg_tpl: Optional[str] = ...) -> None: ...

class allow_deprecation(EnumMeta):
    def __new__(
        cls,
        cls_name: str,
        bases: tuple[type, ...],
        classdict: dict[str, object],
        **kwargs: object,
    ) -> "allow_deprecation": ...
    @classmethod
    def __getattribute__(cls, name: str) -> Any: ...
    def __getitem__(cls, name: str) -> Never: ...
    @overload
    def __call__(cls, value: Any, names: None = ...) -> Never: ...
    @overload
    def __call__(
        cls,
        value: str,
        names: _EnumNames,
        *,
        module: Union[str, None] = ...,
        qualname: Union[str, None] = ...,
        type: Union[type, None] = ...,
        start: int = ...,
        boundary: Union[FlagBoundary, None] = ...,
    ) -> Type[Enum]: ...
    if sys.version_info >= (3, 12):
        @overload
        def __call__(cls, value: Any, *values: Any) -> Never: ...

__all__ = ["deprecated", "allow_deprecation"]
