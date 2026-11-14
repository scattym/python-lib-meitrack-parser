# Meitrack Parser — Baseline Scores Report

**Date:** 2026-11-07  
**Target Codebase:** `<repo>/meitrack`  
**Package:** `meitrackparser` (v`2.11.dev0`)  
**Python Runtime:** Python 3.14.9 (Linux x86_64)  
**Analysis Virtualenv:** `<workspace>/.venv`  

---

## Executive Summary & Scorecard

| Pillar | Baseline Metric / Score | Status / Health | Key Findings |
|---|---|---|---|
| **1. Correctness** | **Score: 72 / 100** (Moderate) | 🟡 In-Progress | • `licenseparser` installed from Git (`https://github.com/scattym/python-lib-license-parser`).<br>• `pytest` runs cleanly: **80 passed in 0.28s**, **51% baseline line coverage** (1,963 statements, 960 missed).<br>• 11 `mypy` type check errors in `event.py` `@singledispatch` handlers.<br>• Bandit found 0 security issues.<br>• Verified functional bugs to address: hardcoded analogue inputs (`common.py:422`), OTA little-endian vs big-endian spec contradiction (`FC2`), empty `command_A10.py` stub. |
| **2. Simplification** | **Score: 58 / 100** (Moderate) | ⚠️ Needs Refactoring | • 219 `ruff` lint violations across 31 files.<br>• 30 of 31 source files fail `ruff format`.<br>• Radon maintainability index (MI) dips as low as 30.73 (`command/__init__.py`) and 44.36 (`command/common.py`).<br>• 3 functions at Cyclomatic Complexity rank C (CC: 11), 8 at rank B (CC: 7–10).<br>• Legacy Python 2/3 compatibility shims (`s2b`, `b2s`, manual byte encoding/decoding) clutter the API. |
| **3. Speed & Throughput** | **Score: 78 / 100** (Acceptable Baseline) | 🟢 Good Baseline | • AAA standard telemetry throughput: **~45,816 msg/s** (latency mean: 21.27 µs, p95: 21.77 µs).<br>• AAA taxi telemetry (event 109): **~35,977 msg/s** (latency mean: 27.10 µs, p95: 56.72 µs).<br>• Heartbeat control packet: **~570,388 msg/s** (latency mean: 1.56 µs).<br>• Multi-packet stream framing: **~11,924 streams/s** (latency mean: 81.98 µs). |

---

## 1. Correctness Analysis

### 1.1 Type Checking (`mypy`)
- **Command:** `mypy meitrack`
- **Result:** **12 errors in 2 files** (31 source files checked).

| File | Line | Error Code | Description |
|---|---|---|---|
| `meitrack/command/common.py` | 8 | `import-not-found` | Cannot find implementation or library stub for module named `license.cardreader` |
| `meitrack/command/event.py` | 172 | `return-value` | Incompatible return value type (got `Any \| None`, expected `str`) |
| `meitrack/command/event.py` | 176 | `misc` | Dispatch type `str` must be subtype of fallback function first argument `int` |
| `meitrack/command/event.py` | 176 | `return` | Missing return statement in `@singledispatch` handler |
| `meitrack/command/event.py` | 191 | `misc` | Dispatch type `bytes` must be subtype of fallback function first argument `int` |
| `meitrack/command/event.py` | 191 | `return` | Missing return statement in `@singledispatch` handler |
| `meitrack/command/event.py` | 222 | `misc` | Dispatch type `str` must be subtype of fallback function first argument `int` |
| `meitrack/command/event.py` | 222 | `return` | Missing return statement in `@singledispatch` handler |
| `meitrack/command/event.py` | 230 | `return-value` | Incompatible return value type (got `int`, expected `str`) |
| `meitrack/command/event.py` | 236 | `misc` | Dispatch type `bytes` must be subtype of fallback function first argument `int` |
| `meitrack/command/event.py` | 236 | `return` | Missing return statement in `@singledispatch` handler |
| `meitrack/command/event.py` | 244 | `return-value` | Incompatible return value type (got `int`, expected `str`) |

### 1.2 Security Audit (`bandit`)
- **Command:** `bandit -r meitrack -f json`
- **Result:** **0 issues identified** across 4,813 lines of code (0 High, 0 Medium, 0 Low).

### 1.3 Test Suite & Code Coverage (`pytest`, `coverage`)
- **Execution with `licenseparser` Installed:**
  - Installed directly from `git+https://github.com/scattym/python-lib-license-parser`.
  - `pytest` runs cleanly without collection errors: **80 tests passed** in 0.28s (0 failures, 1 warning).
  - Code Coverage: **51%** (Total statements: 1,963, Missed: 960).
  - Coverage Breakdown by Core Module:
    - `meitrack/build_message.py`: 93% (235 stmts, 16 missed)
    - `meitrack/command/__init__.py`: 88% (136 stmts, 16 missed)
    - `meitrack/command/command_to_object.py`: 71% (34 stmts, 10 missed)
    - `meitrack/command/command_D01.py`: 60% (15 stmts, 6 missed)
    - `meitrack/command/command_D00.py`: 50% (48 stmts, 24 missed)
    - `meitrack/command/command_FC0`–`FC7`: 45%–63%
    - `meitrack/command/common.py`: 43% (219 stmts, 125 missed)
    - `meitrack/firmware_update.py`: 44% (230 stmts, 128 missed)
    - `meitrack/gprs_protocol.py`: 41% (174 stmts, 103 missed)
    - `meitrack/command/command_AAA.py`: 35% (51 stmts, 33 missed)
    - `meitrack/command/command_C91.py`: 32% (31 stmts, 21 missed)
    - `meitrack/command/command_A13.py`: 33% (30 stmts, 20 missed)
    - `meitrack/command/command_E91.py`: 32% (31 stmts, 21 missed)
    - `meitrack/stub_processor.py`: 24% (58 stmts, 44 missed)
    - `meitrack/file_download.py`: 23% (119 stmts, 92 missed)
    - `meitrack/file_list.py`: 14% (153 stmts, 132 missed)
  - Critical Gap: There are **no unit test files** in the repository (no `tests/` directory); the library relies entirely on docstring doctests and exploratory scripts inside `if __name__ == '__main__':` blocks.

### 1.4 Known Defects & Specification Discrepancies
*(Audited against `/knowledge/codebase_architecture_and_dependencies.md` and official Meitrack protocol specs)*:
1. **Hardcoded Analogue Pin Value (`meitrack/command/common.py:422`):**
   ```python
   # CURRENT BUG:
   def get_analogue_pin_states(self):
       if self.field_dict.get("analog_input_value"):
           return meitrack_analogue_pins_to_dict(b"0000|0000|0000|018D|0579")  # HARDCODED!
   ```
   Completely discards live device telemetry.
2. **Missing `command_A10.py` Implementation:**
   File contains only 3 lines of docstring; `COMMAND_LIST` in `command_to_object.py` maps `b"A10"` to `class: None`.
3. **OTA Endianness Violation (`command_FC2.py` / `firmware_update.py`):**
   Official `MEITRACK_OTA_Protocol_V1.0` stipulates that `INDEX`, `Data length`, and `OTA data checksum` in `FC2` packets are transmitted **little-endian**. Codebase transmits them as **big-endian** (`to_bytes(4, byteorder='big')`).
4. **Hard Dependency on Unfulfillable `licenseparser` Package:**
   `from license.cardreader import License` at module top-level in `common.py` bricks standard imports if this proprietary dependency is absent. Should be guarded or abstracted.
5. **Dozens of Unmapped Commands:**
   Over 40 commands (A11, A12, A14–A73, B05–B99, C01–C49, D10–D16, F01–F11) in `command_to_object.py` default to `None` class, producing generic unstructured dicts.

---

## 2. Simplification Analysis

### 2.1 Code Volume & Size Breakdown (`radon raw`, `lizard`)
- **Total Lines of Code (LOC):** 5,794
- **Source Lines of Code (SLOC):** 3,164
- **Logical Lines of Code (LLOC):** 2,317
- **Non-comment Lines of Code (NLOC):** 2,837
- **Comment Lines:** 150 (single: 93, docstrings/multi: 1,704)
- **Blank Lines:** 833
- **Total Functions/Methods:** 223 across 31 files
- **Average Function NLOC:** 9.2 lines

### 2.2 Cyclomatic Complexity (`radon cc`, `lizard`)
- **Average Cyclomatic Complexity:** **2.448 (Rank A)**
- **Functions with Elevated Complexity (Rank B & C):**

| Module | Function / Method | Radon CC | Lizard CCN | Token Count | Risk Category |
|---|---|---|---|---|---|
| `meitrack/firmware_update.py` | `FirmwareUpdate.parse_response` | 11 (C) | 11 | 209 | High branching in OTA packet response state machine |
| `meitrack/file_list.py` | `gprs_file_list_as_str` | 11 (C) | 11 | 193 | Redundant string concatenations and loop branching |
| `meitrack/gprs_protocol.py` | `parse_data_payload` | 11 (C) | 11 | 326 | Complex message framing delimiter extraction |
| `meitrack/command/__init__.py` | `stc_set_fatigue_driving_alert` | 10 (B) | 10 | 112 | Repetitive manual boundary validation |
| `meitrack/command/__init__.py` | `stc_set_idle_alert_time` | 10 (B) | 10 | 111 | Repetitive manual boundary validation |
| `meitrack/file_list.py` | `FileListing.add_packet` | 9 (B) | 9 | 175 | Nested sequence handling |
| `meitrack/command/common.py` | `Command.parse_payload` | 7 (B) | 7 | 199 | Dynamic field assignment loop |
| `meitrack/firmware_update.py` | `FirmwareUpdate.return_next_payload` | 7 (B) | 7 | 125 | Chunking logic |
| `meitrack/command/__init__.py` | `stc_set_speeding_alert` | 7 (B) | 7 | 95 | Redundant boundary validation |
| `meitrack/gprs_protocol.py` | `main` | 7 (B) | 7 | 882 | 381-line monolithic test script inside module |
| `meitrack/stub_processor.py` | `request_to_response` | 6 (B) | 6 | 157 | Ad-hoc dict matching |

### 2.3 Maintainability Index (`radon mi`)
The Maintainability Index identifies code areas vulnerable to technical debt and high cognitive load:

| Maintainability Index | Modules | Assessment |
|---|---|---|
| **< 40 (Poor)** | `meitrack/command/__init__.py` (**30.73**) | Dense command helper functions with duplicated string interpolation and manual checks. |
| **40 – 55 (Moderate / Fragile)** | `meitrack/command/common.py` (**44.36**)<br>`meitrack/firmware_update.py` (**49.05**)<br>`meitrack/gprs_protocol.py` (**50.11**)<br>`meitrack/file_list.py` (**51.41**) | High coupling, complex state handling, legacy byte string manipulations. |
| **56 – 75 (Good)** | `meitrack/file_download.py` (62.31)<br>`meitrack/stub_processor.py` (64.77)<br>`meitrack/build_message.py` (62.78)<br>`meitrack/command/command_FC1.py` (64.74)<br>`meitrack/command/command_AAA.py` (71.00) | Moderate structure, minor redundancy. |
| **> 75 (Excellent)** | Individual command files (`FC0`–`FC7`, `A13`, `C91`, `E91`, `D00`, `D01`) and helpers (`common.py`, `devices.py`, `error.py`) | Simple single-purpose classes. |

### 2.4 Code Quality & Lint Violations (`ruff`)
- **Total Issues Found:** **219 errors** (70 auto-fixable safely, 90 with unsafe fixes).
- **Formatting Status:** **30 of 31 source files** require formatting according to PEP 8 / Ruff standard.
- **Key Violation Categories:**
  - `UP031` / `UP032`: Obsolete percent formatting (`%b`, `%s`) instead of f-strings or format specifiers.
  - `ISC004`: Dangerous unparenthesized multi-line implicit string concatenation in list/dict literals.
  - `RUF012`: Mutable class attributes (`request_field_names = [...]`, `field_names = [...]`) without `typing.ClassVar`.
  - `I001`: Unsorted and unformatted import blocks across all files.
  - `N999`: Non-standard module names (`command_A10`, `command_AAA`, etc.).
  - `EXE001`: Shebang in non-executable library modules.

---

## 3. Speed & Performance Analysis

### 3.1 Benchmark Methodology
- Harness: `<workspace>/scripts/benchmark_parser.py`
- Samples Tested:
  - `AAA_TAXI` (250 bytes): Real-world taxi meter telemetry packet (Event 109 from `README.md`).
  - `AAA_STANDARD` (166 bytes): Periodic tracking packet (Event 35).
  - `AAA_RFID` (308 bytes): Magnetic / RFID driver license card report (Event 37).
  - `A11_HEARTBEAT` (33 bytes): Uplink / Downlink heartbeat control frame.
  - `Stream Framing`: Multi-packet continuous byte stream (757 bytes) parsed via `parse_data_payload()`.
- Iterations: 10,000 runs per packet (1,000 warmup); 5,000 runs for stream framing.

### 3.2 Benchmark Baseline Results

```text
---------------------------------------------------------------------------------------------------------------
MEITRACK PARSER BENCHMARK RESULTS (BASELINE)
---------------------------------------------------------------------------------------------------------------
Packet Type      |  Bytes | Iterations | Throughput (msg/s) |  Mean (µs) |   p50 (µs) |   p95 (µs) |   p99 (µs)
---------------------------------------------------------------------------------------------------------------
AAA_TAXI         |    250 |     10,000 |           35,977.3 |      27.10 |      22.23 |      56.72 |     102.17
AAA_STANDARD     |    166 |     10,000 |           45,816.5 |      21.27 |      20.96 |      21.77 |      25.98
AAA_RFID         |    308 |     10,000 |           45,241.9 |      21.54 |      21.39 |      21.89 |      24.91
A11_HEARTBEAT    |     33 |     10,000 |          570,387.8 |       1.56 |       1.56 |       1.60 |       1.63
---------------------------------------------------------------------------------------------------------------
Stream Framing   |    757 |      5,000 |           11,923.5 |      81.98 |      81.24 |      85.23 |      99.50
---------------------------------------------------------------------------------------------------------------
```

### 3.3 Performance Hotspots Identified
1. **Dynamic Field Assignment Overhead in `Command.parse_payload` (`common.py`):**
   Iterating over field names and running dictionary insertions takes ~21–27 µs per message.
2. **String / Byte Conversion & Delimiter Scanning in `parse_data_payload` (`gprs_protocol.py`):**
   Stream framing incurs ~82 µs per multi-packet buffer due to repeated `payload.find()` scans and substring slicing.
3. **Dynamic Taxi Meter Sub-parsing:**
   In `AAA_TAXI`, p99 latency reaches 102 µs due to conditional dispatch and extra nested parsing of taxi meter sub-fields.

---

## 4. Overall Baseline Summary

The codebase has strong algorithmic foundations and high raw throughput (>35k–45k telemetry packets/sec), but suffers from critical **Correctness** and **Maintainability** liabilities:
1. **Correctness Deficit:** The library cannot be cleanly imported or tested out-of-the-box due to the hard `license` dependency, has 12 type errors, lacks a dedicated test suite, and contains verified functional bugs (hardcoded analogue values, OTA endianness mismatch).
2. **Maintenance Drag:** Low Maintainability Index in core modules (30.73 in `command/__init__.py`), 219 lint issues, and duplicate validation routines.
3. **Execution Readiness:** The reusable benchmark tool `<workspace>/scripts/benchmark_parser.py` and baseline data `<workspace>/analysis/benchmark_baseline.json` provide a reliable gate to ensure future refactorings improve simplicity without regressing correctness or throughput.
