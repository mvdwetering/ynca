# Copilot Instructions

## Commands

```bash
# Setup
python3 -m venv venv && source ./venv/bin/activate
pip install -e .[dev]

# Run all tests with coverage + mypy
./coverage.sh

# Run a single test file
pytest tests/test_zone.py

# Run a single test
pytest tests/test_zone.py::test_function_name

# Lint
ruff check src/ tests/
ruff format src/ tests/

# Type check
mypy src/
```

## Architecture

This is a Python library (`ynca`) for controlling Yamaha AV receivers via the YNCA serial/IP protocol.

**Core layers:**

- `YncaConnection` (`connection.py`) — low-level: sends/receives raw YNCA protocol messages (`@SUBUNIT:FUNCTION=VALUE`), handles throttling and keep-alive
- `SubunitBase` (`subunit.py`) — mid-level: base class for all subunits; owns `function_handlers` dict (keyed by YNCA function name), manages initialization via GET requests + `SYS:VERSION` sync, dispatches update callbacks
- `YncaApi` (`api.py`) — top-level: discovers available subunits, exposes them as typed attributes (e.g., `api.main`, `api.sys`)

**Subunit/Function descriptor pattern:**
Each YNCA function on a subunit is a class-level descriptor (`FunctionMixinBase` subclass from `function.py`). Reading an attribute returns the cached value from `function_handlers`; writing sends a PUT command. `__set_name__` uppercases the attribute name to derive the YNCA function name (overridable via `name_override`).

Available mixins: `EnumFunctionMixin`, `StrFunctionMixin`, `IntFunctionMixin`, `FloatFunctionMixin`, `EnumOrFloatFunctionMixin`, `EnumOrIntFunctionMixin`, `TimedeltaFunctionMixin`.

Subunits live in `src/ynca/subunits/`. Shared capabilities (playback controls, metadata fields, etc.) are composed in as mixins defined in `src/ynca/subunits/__init__.py`.

## Key Conventions

**Adding a new YNCA command:**

1. Add a `FunctionMixin` attribute to the appropriate subunit class in `src/ynca/subunits/`
2. If the value is multi-valued, add an `Enum` to `src/ynca/enums.py`
3. Export the new type from `src/ynca/__init__.py` (both import and `__all__`)
4. Add a test in `tests/`; coverage must remain at 100%
5. Keep attributes/enums alphabetically ordered

**Enums always have an `UNKNOWN` sentinel:**

```python
@unique
class ExBass(StrEnum):
    AUTO = "Auto"
    OFF = "Off"
    UNKNOWN = UNKNOWN_STRING

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)
```

Use individual enums per function even when values overlap — receiver models differ.

**API design rules:**

- GET+PUT functions → readable/writable attribute
- PUT-only functions → method (e.g., `playback(Playback.PLAY)`)
- Action functions → method with `_up`/`_down` suffix (e.g., `vol_up(step)`)
- Attribute names follow YNCA names in lowercase; use `name_override` for invalid Python identifiers (e.g., `2CHDECODER` → attribute `twochdecoder` with `name_override="2CHDECODER"`)

**`init=` parameter:** When a single GET command triggers responses for multiple functions (e.g., `BASIC`, `METAINFO`), set `init="BASIC"` on those attributes to avoid redundant initialization requests.

**Converters** (`converters.py`) handle string↔Python-type translation for YNCA protocol values. Each `FunctionMixin` takes a `converter` argument:

| Converter | Python type | Notes |
| --- | --- | --- |
| `StrConverter(min_len, max_len)` | `str` | Optional length validation |
| `IntConverter(to_str)` | `int` | Optional custom serializer |
| `FloatConverter(to_str)` | `float` | Use `number_to_string_with_stepsize` helper for stepped values (e.g., volume, frequency) |
| `EnumConverter(datatype)` | `Enum` | Maps string ↔ enum `.value` |
| `TimedeltaOrNoneConverter` | `timedelta \| None` | Parses `MM:SS` format |
| `MultiConverter([...])` | first match | Tries converters in order; use when a value can be either a number or an enum (e.g., volume presets) |

Converters must be stateless. Custom `to_str` lambdas are passed to `FloatConverter`/`IntConverter` when the format isn't plain `str()`, e.g.:

```python
FloatConverter(to_str=lambda v: number_to_string_with_stepsize(v, 2, 0.2))
```

**Testing pattern:**

Tests use `YncaConnectionMock` (from `tests/mock_yncaconnection.py`) and a `connection` pytest fixture from `conftest.py`. Responses are set up as a sequential list of `(request, [responses])` tuples in `get_response_list` before calling `subunit.initialize()`.

```python
connection.get_response_list = [
    (("MAIN", "AVAIL"), [("MAIN", "AVAIL", "Ready")]),
    (("MAIN", "BASIC"), [("MAIN", "PWR", "On"), ...]),
    (("SYS", "VERSION"), [("SYS", "VERSION", "1.0")]),
]
main = Main(connection)
main.initialize()
```

`UNKNOWN_STRING` constant (from `enums.py`) is used as the sentinel value for all unknown enum entries.
