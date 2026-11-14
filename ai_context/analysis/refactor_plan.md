# Meitrack Parser — Architecture & Refactoring Plan

**Target Codebase:** `<repo>/meitrack`  
**Author:** Refactoring Software Engineer  
**Date:** 2026-11-07  
**Guiding Directives:**  
1. **Correctness (Highest Priority):** Zero tolerance for breaking protocol edge cases, packet framing, or specification contracts.
2. **Simplification (Medium Priority):** Reduce cognitive load, eliminate dead code, decompose high-CC functions, and modernize Python 2 idioms to Python 3.
3. **Speed / Performance (Lowest Priority):** Preserve or improve the baseline throughput (>35k–45k msg/s) with verified benchmarks.

---

## 1. Executive Refactoring Strategy

The baseline audit revealed that while the `meitrackparser` package has high raw parsing throughput, its correctness and maintainability are critically impaired:
- It crashes upon import in any clean environment lacking the unfulfillable `licenseparser` package.
- It contains verified protocol bugs (hardcoded analogue telemetry values, OTA big-endian vs little-endian inversion).
- It lacks any dedicated unit test suite in `tests/`, relying solely on doctests that fail to run out-of-the-box.
- Core modules have dangerously low maintainability indices (as low as 30.73) and 219 lint violations.

The refactoring will be executed in three phased, test-driven cycles:
1. **Phase 1: Correctness Hardening & Test Harness Foundation**
2. **Phase 2: Architectural Simplification & Modernization**
3. **Phase 3: Stream Framing Optimization & Performance Verification**

---

## 2. Phase 1: Correctness Hardening (Highest Priority)

### 1.1 Decouple Proprietary `license` Dependency
- **Current State:** `from license.cardreader import License` at line 8 of `meitrack/command/common.py` raises `ModuleNotFoundError` during module import.
- **Root Cause:** `licenseparser` is an external/proprietary dependency that cannot be fetched from PyPI.
- **Refactoring Solution:**
  - Introduce an abstraction layer / conditional import in `meitrack/command/common.py`:
    ```python
    try:
        from license.cardreader import License
    except ImportError:
        License = None
    ```
  - In `Command.get_license_data()`:
    ```python
    def get_license_data(self):
        rfid = self.field_dict.get("rfid")
        if not rfid:
            return None
        if License is None:
            logger.warning("licenseparser is not installed; returning raw rfid payload")
            return rfid
        return License(rfid)
    ```
  - This allows the entire package, doctests, and test suites to function cleanly in standard environments while remaining 100% backward-compatible when `licenseparser` is present.

### 1.2 Fix Hardcoded Analogue Pin Telemetry Bug
- **Current State (`meitrack/command/common.py:422`):**
  ```python
  if self.field_dict.get("analog_input_value"):
      return meitrack_analogue_pins_to_dict(b"0000|0000|0000|018D|0579")  # BUG
  ```
- **Refactoring Solution:**
  - Pass the actual live telemetry string:
    ```python
    analog_val = self.field_dict.get("analog_input_value")
    if analog_val:
        return meitrack_analogue_pins_to_dict(analog_val)
    return {}
    ```

### 1.3 Fix OTA Protocol Endianness Defect
- **Current State:**
  - In `meitrack/firmware_update.py` and `meitrack/command/command_FC2.py`, byte conversion for `INDEX`, `Data length`, and `OTA data checksum` uses `byteorder='big'`.
- **Specification (`MEITRACK_OTA_Protocol_V1.0`):**
  - Section 3.2 explicitly specifies **little-endian** for multi-byte numeric fields in OTA command handshakes.
- **Refactoring Solution:**
  - Align `FC2` serialization and parsing to little-endian:
    `int.from_bytes(data, byteorder='little')` and `val.to_bytes(length, byteorder='little')`.

### 1.4 Resolve `mypy` Static Typing Errors
- **Current State:** 12 typing errors across `meitrack/command/event.py` and `meitrack/command/common.py`.
- **Refactoring Solution:**
  - Correct the `@singledispatch` type hierarchy in `meitrack/command/event.py`:
    - Ensure base function accepts `object` or `Any` before dispatching to `int`, `str`, `bytes`.
    - Provide explicit return types and handle non-matching cases.
    - Annotate return values (`str | None`, `int | None`).
  - Target: **0 mypy errors** across all 31 source files.

### 1.5 Implement Missing `command_A10.py`
- **Current State:** `meitrack/command/command_A10.py` is a 3-line docstring with no class. `command_to_object.py` maps `b"A10"` to `class: None`.
- **Refactoring Solution:**
  - Implement `LocationQueryCommand` subclassing `Command` according to protocol specification (A10 uplink/downlink format).
  - Register `LocationQueryCommand` in `COMMAND_LIST`.

### 1.6 Create Comprehensive Unit & Regression Test Suite
- **Current State:** No `tests/` directory exists.
- **Refactoring Solution:**
  - Create `<repo>/tests/`:
    - `test_gprs_protocol.py`: Test packet framing (`@@`, `$$`), length validation, checksum calculation (`calc_signature`), direction parsing.
    - `test_command_aaa.py`: Test all telemetry event code variations (event 35 standard, event 37 RFID, event 39 photo, event 50/51 temperature, event 109 taxi meter).
    - `test_analogue_digital_pins.py`: Verify pin status unpacking and voltage calculation.
    - `test_ota_update.py`: Test firmware update state machine (FC0 through FC7).
    - `test_file_transfer.py`: Chunk aggregation for D00 and directory listing for D01.
  - Target: **>85% statement coverage** across all modules with 100% green tests.

---

## 3. Phase 2: Simplification & Modernization (Medium Priority)

### 2.1 Modernize Python 2/3 Compatibility Shims
- **Current State:** Pervasive use of `s2b` and `b2s` helpers in `meitrack/common.py` that blindly call `.encode()` / `.decode()`.
- **Refactoring Solution:**
  - Modernize string/bytes boundary handling with explicit types.
  - Replace legacy `%b` and `%s` byte string formatting with Python 3 f-strings or clean byte concatenations.

### 2.2 Refactor Low-Maintainability Command Builders (`meitrack/command/__init__.py`)
- **Current State:** Maintainability Index is **30.73** (lowest in codebase). 28 functions have identical boilerplate for range validation and string interpolation (e.g., `stc_set_fatigue_driving_alert`, `stc_set_idle_alert_time`, `stc_set_speeding_alert`).
- **Refactoring Solution:**
  - Introduce reusable parameter validator helper:
    ```python
    def _validate_range(name: str, value: int, min_val: int, max_val: int) -> None:
        if value is None or not (min_val <= value <= max_val):
            raise GPRSParameterError(f"{name} must be between {min_val} and {max_val}. Was {value}")
    ```
  - This eliminates hundreds of duplicated lines, drops cyclomatic complexity from 10 to 1, and raises the MI to >70.

### 2.3 Decompose High-Complexity Methods
- **`FirmwareUpdate.parse_response` (CC: 11):**
  - Extract per-command handlers (`_handle_fc0`, `_handle_fc1`, `_handle_fc2`, etc.) into a dispatch dictionary.
- **`gprs_file_list_as_str` (CC: 11):**
  - Simplify loop with `b"|".join(filenames)` instead of manual string accumulation and edge-case slicing.
- **`parse_data_payload` (CC: 11):**
  - Split into:
    1. `_extract_next_frame(payload, prefix)`
    2. `_validate_frame_checksum(frame)`
    3. `_unpack_frame(frame, device_type)`

### 2.4 Eliminate 219 `ruff` Violations & Auto-Format
- Run `ruff check --fix` and resolve class attribute mutability (`typing.ClassVar` or immutable tuples).
- Enforce standard formatting across all 31 files via `ruff format meitrack`.

### 2.5 Clean Up Dead & Monolithic Script Code
- Remove unused 10-line stub `meitrack/fromdevice.py`.
- Move monolithic 380-line interactive test code in `meitrack/gprs_protocol.py:main` into dedicated tests or sample scripts.
- Populate `meitrack/__init__.py` with standard package exports (`__version__`, `GPRS`, `parse_data_payload`).

---

## 4. Phase 3: Speed & Stream Framing Optimization (Lowest Priority)

*Optimization will only be applied after Phase 1 and Phase 2 are verified green and tests are in place.*

### 3.1 Stream Framing Efficiency (`parse_data_payload`)
- **Current Bottleneck:** Stream framing throughput is ~11,924 streams/s (82 µs latency) due to repeated linear scanning of `payload.find()` and creating multiple intermediate byte slices.
- **Refactoring Solution:**
  - Use memoryview / slicing with indexed pointers instead of continually re-allocating `payload = payload[direction_start:]`.
  - Fast-path checksum verification using a lookup table or byte-level generator expression.

### 3.2 Field Parser Dispatch Optimization
- **Current Bottleneck:** `Command.parse_payload` dynamically iterates over lists of field names and does repeated dictionary lookups.
- **Refactoring Solution:**
  - Pre-allocate tuple layouts and map directly to structured objects or `NamedTuple` / `@dataclass(slots=True)` for standard events (`35`, `109`, `37`).

### 3.3 Performance Regression Gating
- Every optimization must be benchmarked against baseline figures using:
  ```bash
  python scripts/benchmark_parser.py -n 10000 -w 1000 -o analysis/benchmark_refactored.json
  ```
- **Gate:** No telemetry packet throughput may drop below the baseline (AAA_TAXI: ≥35.9k msg/s, AAA_STANDARD: ≥45.8k msg/s, Stream Framing: ≥11.9k streams/s).

---

## 5. Acceptance & Verification Gates

| Gate | Target / Threshold | Tool / Verification |
|---|---|---|
| **Type Safety** | 0 mypy errors | `mypy meitrack` |
| **Security** | 0 bandit issues | `bandit -r meitrack` |
| **Linting & Style** | 0 ruff errors, 100% formatted | `ruff check meitrack && ruff format --check meitrack` |
| **Test Execution** | 100% passing tests (unit + doctests) | `pytest` |
| **Code Coverage** | ≥85% statement coverage | `pytest --cov=meitrack --cov-report=term-missing` |
| **Maintainability** | Maintainability Index ≥ 65 across all files | `radon mi meitrack` |
| **Complexity** | 0 functions with Cyclomatic Complexity > 8 | `radon cc meitrack`, `lizard meitrack` |
| **Speed Throughput** | 0% regression vs baseline scores | `scripts/benchmark_parser.py` |
