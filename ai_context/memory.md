# Project Memory

Maintained per AGENTS.md section 7. Read this and [0-Architecture.md](0-Architecture.md) first each session.

## Status (2026-11-14)

- Branch `refactor/phase-1-correctness`; phases 1-3 complete.
- 169 tests passing, mypy clean, ruff clean.
- Docs (`ai_context/`, CHANGELOG Unreleased) written; not committed.

## Decisions

- Flat `meitrack/` package, not `src/` layout (deliberate; AGENTS.md deviation).
- ruff replaces black/isort (deliberate).
- Missing command fields raise `AttributeError`; direction auto-detected; `StreamParser` and `CommandBuilder` added as public API.
- Benchmarks: baseline -> phase3c, e.g. AAA_TAXI 28,988 -> 54,583 msg/s, stream framing 11,181 -> 15,215 streams/s. Later ~2% stream speed-up is noise.

## Commits (newest first, this refactor)

- `c71dca6` feat(api): add fluent CommandBuilder and meitrack_cli script
- `d8adc1a` Add AGENTS.md file
- `1e78a0f` feat(stream): stateful StreamParser; offset-based framing
- `755eda2` perf(core): remove deepcopy in AAA, C-level sum in calc_signature
- `96ada45` feat(api): AttributeError for missing fields, typed telemetry, auto direction
- `b8ab88b` refactor(core): simplification, dedupe boilerplate, ruff formatting
- `28562cb` test(core): unit test suite (92% coverage)
- `31d4f01` fix(core): decouple license import, analogue bug, OTA endianness, A10 command

## Pending / next steps

1. Commit the new `ai_context/` files and CHANGELOG entry.
2. Open PR for `refactor/phase-1-correctness`.
3. Deploy / release 2.11 after review.
4. Fix `setup.py` (fails `ruff format`).
5. Optional: extend `CommandBuilder`, add benchmark regression gate.

## Documentation references

- [0-Architecture.md](0-Architecture.md)
- `../../knowledge/*.md` (protocol, OTA, events, commands, architecture, API ergonomics)
- `../../analysis/refactor_plan.md`, `baseline_scores.md`, `step_verification_phase1.md`, `benchmark_*.json`

## Session log

- 2026-11-14: wrote 0-Architecture.md, memory.md, CHANGELOG Unreleased entry. No code changes.
