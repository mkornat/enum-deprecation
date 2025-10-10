
# 🧩 Enum-Deprecation

[![PyPI](https://img.shields.io/pypi/v/enum-deprecation.svg)](https://pypi.org/project/enum-deprecation/)
[![Python Versions](https://img.shields.io/pypi/pyversions/enum-deprecation.svg)](https://pypi.org/project/enum-deprecation/)
[![License](https://img.shields.io/pypi/l/enum-deprecation.svg)](https://github.com/yourname/enum-deprecation/blob/main/LICENSE)
[![Tests](https://github.com/yourname/enum-deprecation/actions/workflows/tests.yml/badge.svg)](https://github.com/yourname/enum-deprecation/actions)

> Add **deprecation warnings** to your Python `Enum` members —
> works for all Enum subclasses (`Enum`, `IntEnum`, `StrEnum`, or your own mixins).

---

## ✨ Features

* ✅ Works with `Enum`, `IntEnum`, `StrEnum`, or any custom subclass
* ⚙️ Emits `DeprecationWarning` when deprecated members are accessed:

  * by attribute: `MyEnum.OLD`
  * by name: `MyEnum["OLD"]`
  * by value: `MyEnum(value)`
* 🧾 Fully type-checked (`mypy --strict`) and tested on **Python 3.11 – 3.13**
* 🧱 Compatible with **SQLAlchemy** enums
* 🛡 Zero runtime dependencies

---

## 📦 Installation

```bash
pip install enum-deprecation
```

Python ≥ 3.11 is required (because of `StrEnum` support and `typing.Self`).

---

## 🧠 Usage

```python
from enum import Enum, IntEnum, StrEnum, auto
from enum_deprecation import allow_deprecation, deprecated
import warnings

warnings.simplefilter("default")  # enable DeprecationWarnings for demo


# --- Basic Enum --------------------------------------------------------------

class MyEnum(Enum, metaclass=allow_deprecation):
    A = auto()
    OLD = deprecated()        # auto value, but deprecated
    B = auto()
    OLD2 = deprecated(42)     # explicit value
    OLD3 = deprecated("X", msg_tpl="{attr} will go away soon")


print(MyEnum.A)
print(MyEnum.OLD)     # emits a DeprecationWarning
print(MyEnum["OLD"])  # warning again
print(MyEnum(42))     # warning for explicit value
```

---

### 💡 Works with `StrEnum`, `IntEnum`, and custom mixins

```python
class MyStrEnum(StrEnum, metaclass=allow_deprecation):
    OK = "ok"
    OLD = deprecated("deprecated")  # string value
```

```python
class MyIntEnum(IntEnum, metaclass=allow_deprecation):
    NEW = 1
    OLD = deprecated(2)
```

---

### ⚙️ Custom deprecation messages

```python
class Status(Enum, metaclass=allow_deprecation):
    ACTIVE = 1
    LEGACY = deprecated(2, msg_tpl="Status {attr} is legacy")
```

You can format `{attr}` anywhere in the message template.

---

## 🧩 How it works

The metaclass `allow_deprecation` wraps `EnumMeta` and:

1. Records all members defined as `deprecated(...)`.
2. Replaces `deprecated(auto)` with the proper sentinel so `auto()` still works.
3. Emits a `DeprecationWarning` whenever those members are retrieved via attribute, name, or value lookup.

It’s completely transparent to the rest of the `enum` machinery — the resulting class is still a regular `Enum` subclass.

---

## 🧰 SQLAlchemy compatibility

The resulting enums can be used directly with SQLAlchemy:

```python
from sqlalchemy import Enum as SAEnum, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase): ...

class Thing(Base):
    __tablename__ = "thing"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[MyEnum] = mapped_column(SAEnum(MyEnum, name="status_enum"))
```

⚠️ Note: accessing deprecated enum values during ORM loading will emit warnings.
If you wish to suppress them during DB round-trip, wrap with a small
`TypeDecorator` that uses `MyEnum.__members__` directly.

---

## 🧪 Testing

```bash
tox           # runs tests under Python 3.11–3.13
pytest -v     # run in the current environment
mypy .        # type checking
```

---

## 🧾 License

MIT License © 2025 Marcin Kornat

---

## 🧭 Links

* 📘 PyPI: [https://pypi.org/project/enum-deprecation/](https://pypi.org/project/enum-deprecation/)
* 🧑‍💻 Source: [https://github.com/yourname/enum-deprecation](https://github.com/yourname/enum-deprecation)
* 🧪 Tests & CI: see `.github/workflows/tests.yml`

---

Would you like me to include a **short “Development / Contributing”** section (for running tests, lint, etc.) and a **“Changelog”** stub for PyPI’s long description?
