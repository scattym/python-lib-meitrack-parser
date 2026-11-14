# Meitrack Parser — Architecture

Python library for parsing and building Meitrack GPRS protocol packets (`$$...*CS\r\n`), including OTA firmware and file-transfer helpers. Branch: `refactor/phase-1-correctness`.

## Module map

| Module | Role |
| --- | --- |
| `meitrack/__init__.py` | Public facade: `GPRS`, `parse_data_payload`, `calc_signature`, `StreamParser`, `CommandBuilder` |
| `meitrack/gprs_protocol.py` | `GPRS` packet object, framing, checksum (`calc_signature`), `parse_data_payload` |
| `meitrack/stream.py` | `StreamParser`: stateful byte-stream framer (`feed`, `buffered`, `reset`) |
| `meitrack/command_builder.py` | `CommandBuilder`: fluent builder (`with_imei`, `with_direction`, `with_data_identifier`, `request_location`, `format_sdcard`, ...) |
| `meitrack/command/` | Per-command classes (AAA, A10, ...) |
| `meitrack/build_message.py`, `fromdevice.py` | Outbound / inbound message helpers |
| `meitrack/event.py`, `devices.py` | Event-code and device-type tables |
| `meitrack/file_download.py`, `file_list.py`, `firmware_update.py` | File transfer and OTA |
| `meitrack/stub_processor.py`, `common.py`, `error.py` | Stub server helpers, shared utils, errors |
| `scripts/meitrack_cli.py`, `scripts/mtparse` | CLI tools |

## Data flow

```text
raw bytes -> StreamParser.feed() / parse_data_payload()   (framing)
          -> GPRS packet (direction auto-detected, signature checked)
          -> command object (meitrack/command/*; typed telemetry properties)
reverse:  CommandBuilder -> command object -> GPRS -> bytes
```

## Public API

- `GPRS`, `parse_data_payload`, `calc_signature` (facade exports since phase 2).
- `StreamParser` and `CommandBuilder` (phase 3).
- Missing command fields raise `AttributeError` (via `__getattr__`) instead of returning silent defaults.
- Typed telemetry properties on commands; packet direction is auto-detected.

## Decisions and rationale

- **Phase 1 correctness**: decoupled the proprietary license import, fixed analogue pin telemetry bug, corrected OTA endianness, added A10 command, mypy clean, test suite at 92% coverage.
- **Phase 2 simplification**: complexity Rank C -> A/B, ruff cleanup, dead code removed, facade exports added.
- **Phase 3 ergonomics/speed**: `AttributeError` semantics, direction auto-detect, `deepcopy` removed in AAA command, `calc_signature` uses C-level `sum()`, offset-based stream scanning, `StreamParser`, `CommandBuilder`, CLI.
- **Deliberate deviations from AGENTS.md**: flat `meitrack/` package rather than `src/` layout (avoids breaking existing imports and packaging); `ruff` used for lint and format instead of black/isort (single tool, faster).

## Quality gates

- 169 tests passing (pytest); `mypy` clean; `ruff` clean.
- Tools live in `<workspace>/.venv/bin/`.

## Performance (from `analysis/benchmark_*.json`; baseline vs phase3c, Python 3.14.9)

| Benchmark | Baseline msg/s | Phase 3c msg/s |
| --- | --- | --- |
| AAA_TAXI (250 B) | 28,988 | 54,583 |
| AAA_STANDARD (166 B) | 46,597 | 57,328 |
| AAA_RFID (308 B) | 43,295 | 55,775 |
| A11_HEARTBEAT (33 B) | 480,846 | 557,949 |
| stream framing (757 B), streams/s | 11,181 | 15,215 |

Intermediate runs (phase3a/3b) are in the same directory. Single-machine runs; treat small deltas as noise. A later stream-framing speed-up of about 2% is within noise.

## Limitations and known leftovers

- `setup.py` fails `ruff format`.
- Packaging is still flat/legacy (`setup.py`, `setup.cfg`).
- `CommandBuilder` covers only a subset of commands (location, delete file, format SD, restart GSM/GPS, tracking interval, output pin).
- Benchmarks are not gated in CI.

## Future plans

- Review and merge PR #1; then release 3.0.
- Format `setup.py`; consider moving to `pyproject.toml`-only packaging.
- Extend `CommandBuilder` to more commands; add perf regression gate.

## Related documents (relative to repo root, `../knowledge` and `../analysis`)

- [Codebase architecture and dependencies](knowledge/codebase_architecture_and_dependencies.md)
- [API ergonomics recommendations](knowledge/api_ergonomics_and_architecture_recommendations.md)
- [Protocol spec](knowledge/meitrack_protocol_spec.md), [OTA](knowledge/meitrack_ota_protocol.md), [event codes](knowledge/meitrack_event_codes.md), [commands](knowledge/meitrack_commands_reference.md), [peripherals](knowledge/peripherals_and_custom_features.md)
- [Refactor plan](analysis/refactor_plan.md), [baseline scores](analysis/baseline_scores.md), [phase 1 verification](analysis/step_verification_phase1.md)
- Benchmarks: `analysis/benchmark_baseline.json` ... `benchmark_phase3c.json`
- [memory.md](memory.md)
