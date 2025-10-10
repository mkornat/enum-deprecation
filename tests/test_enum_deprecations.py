import warnings

from enum import Enum, IntEnum, StrEnum, auto
from typing import Callable, TypeVar
from warnings import WarningMessage

from enum_deprecation._enum_deprecation import allow_deprecation, deprecated

T = TypeVar("T")


def run_with_warnings(fn: Callable[[], T]) -> tuple[T, list[WarningMessage]]:
    """Run `fn` with DeprecationWarnings captured; return (result, warnings)."""
    rec: list[WarningMessage]
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always", DeprecationWarning)
        result = fn()
    return result, rec


def warning_messages(records: list[WarningMessage]) -> list[str]:
    return [
        str(w.message) for w in records if issubclass(w.category, DeprecationWarning)
    ]


def test_attribute_access_warns_on_deprecated_member() -> None:
    class MyEnum(Enum, metaclass=allow_deprecation):
        EN_A = auto()
        EN_B = deprecated()
        EN_C = auto()

    def work() -> None:
        _m = MyEnum.EN_B

    _, rec = run_with_warnings(work)
    msgs = warning_messages(rec)
    assert len(msgs) == 1
    assert "EN_B" in msgs[0]


def test_attribute_access_does_not_warn_on_non_deprecated() -> None:
    class MyEnum(Enum, metaclass=allow_deprecation):
        EN_A = auto()
        EN_B = deprecated()
        EN_C = auto()

    def work() -> None:
        _a = MyEnum.EN_A
        _c = MyEnum.EN_C

    _, rec = run_with_warnings(work)
    msgs = warning_messages(rec)
    assert msgs == []


def test_name_lookups_warns_and_return_member() -> None:
    class MyEnum(Enum, metaclass=allow_deprecation):
        EN_A = auto()
        EN_B = deprecated()
        EN_C = auto()

    def work() -> MyEnum:
        _m = MyEnum["EN_B"]
        return _m

    member, rec = run_with_warnings(work)
    msgs = warning_messages(rec)
    assert len(msgs) == 1
    assert "EN_B" in msgs[0]
    assert isinstance(member, MyEnum)
    assert member.name == "EN_B"


def test_value_lookup_warns_and_returns_member() -> None:
    class MyEnum(Enum, metaclass=allow_deprecation):
        EN_A = auto()
        EN_B = deprecated()
        EN_C = auto()

    value = MyEnum.EN_B.value

    def work() -> MyEnum:
        _m = MyEnum(value)
        return _m

    member, rec = run_with_warnings(work)
    msgs = warning_messages(rec)
    assert len(msgs) == 1
    assert "EN_B" in msgs[0]
    assert member is MyEnum.EN_B


def test_multiple_accesses_warn_each_time() -> None:
    class MyEnum(Enum, metaclass=allow_deprecation):
        EN_A = auto()
        EN_B = deprecated()
        EN_C = auto()

    def work() -> None:
        _1 = MyEnum.EN_B
        _2 = MyEnum.EN_B
        _3 = MyEnum["EN_B"]
        _4 = MyEnum(MyEnum.EN_B.value)

    _, rec = run_with_warnings(work)
    msgs = warning_messages(rec)
    assert len(msgs) == 5


def test_strenum_explicit_value_deprecated_warns() -> None:
    class MyStrEnum(StrEnum, metaclass=allow_deprecation):
        OK = "OK"
        OLD = deprecated("OLD")

    def work() -> tuple[MyStrEnum, MyStrEnum, MyStrEnum]:
        m1 = MyStrEnum.OLD
        m2 = MyStrEnum["OLD"]
        m3 = MyStrEnum("OLD")
        return m1, m2, m3

    (m1, m2, m3), rec = run_with_warnings(work)
    msgs = warning_messages(rec)
    assert len(msgs) == 3
    assert all("OLD" in s for s in msgs)
    assert m1 is m2 is m3 is MyStrEnum.OLD
    assert m1.value == "OLD"


def test_strenum_auto_deprecated_warns() -> None:
    class MyStrEnum(StrEnum, metaclass=allow_deprecation):
        A = auto()
        B = deprecated()
        C = auto()

    def work() -> tuple[MyStrEnum, MyStrEnum, MyStrEnum]:
        m1 = MyStrEnum.B
        m2 = MyStrEnum["B"]
        m3 = MyStrEnum("b")
        return m1, m2, m3

    (m1, m2, m3), rec = run_with_warnings(work)
    msgs = warning_messages(rec)
    assert len(msgs) == 3
    assert all("B" in s for s in msgs)
    assert m1 is m2 is m3 is MyStrEnum.B
    assert m1.value == "b"


def test_intenum_auto_and_explicit_deprecated_warns() -> None:
    class MyIntEnum(IntEnum, metaclass=allow_deprecation):
        A = auto()  # -> 1
        B = deprecated()  # -> 2 (deprecated)
        C = auto()  # -> 3
        D = deprecated(10)  # explicit value

    def work() -> tuple[MyIntEnum, MyIntEnum, MyIntEnum, MyIntEnum]:
        b1 = MyIntEnum.B
        b2 = MyIntEnum["B"]
        b3 = MyIntEnum(MyIntEnum.B)  # value-lookup using member
        d = MyIntEnum(10)
        return b1, b2, b3, d

    (b1, b2, b3, d), rec = run_with_warnings(work)
    msgs = warning_messages(rec)
    assert len(msgs) == 5
    text = "".join(msgs)
    assert "B" in text and "D" in text
    assert int(b1) == 2 and int(b2) == 2 and int(b3) == 2 and int(d) == 10


def test_custom_message_template_is_used() -> None:
    class MyEnum(Enum, metaclass=allow_deprecation):
        A = auto()
        OLD = deprecated(msg_tpl="X-{attr}-Y")
        C = auto()

    def work() -> None:
        _ = MyEnum.OLD

    _, rec = run_with_warnings(work)
    msgs = warning_messages(rec)
    assert msgs == ["X-OLD-Y"]


def test_internal_attribute_access_does_not_warn() -> None:
    class MyEnum(Enum, metaclass=allow_deprecation):
        A = auto()
        B = deprecated()
        C = auto()

    def work() -> None:
        m = MyEnum.__members__  # type: ignore[assignment]
        _ = m.get("A")
        _map = MyEnum._member_map_  # type: ignore[attr-defined]
        _ = _map.get("B")
        _dep = getattr(MyEnum, "__deprecated_map__", {})
        _ = _dep.keys()

    _, rec = run_with_warnings(work)
    msgs = warning_messages(rec)
    assert msgs == []


def test_printing_class_and_non_deprecated_member_no_warn() -> None:
    class MyEnum(Enum, metaclass=allow_deprecation):
        A = auto()
        B = deprecated()
        C = auto()

    def work() -> None:
        _s1 = repr(MyEnum)
        _s2 = str(MyEnum.A)
        # accessing MyEnum.B would warn; we intentionally avoid it

    _, rec = run_with_warnings(work)
    msgs = warning_messages(rec)
    assert msgs == []
