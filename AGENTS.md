# AGENTS.md
## 1. Project Context & Purpose
**Primary Reference:** Read the file `ai_context/0-Architecture.md` to understand the full architectural context of the project, including design decisions, technology choices, and future plans. This will help you make informed suggestions and maintain consistency with the overall project vision.
**Important:** Project-specific details in `ai_context/0-Architecture.md` take precedence over generic standards in this AGENTS.md file. Always consult the architecture document first for project-specific implementations, patterns, and decisions.

---
## 2. Directory Structure & Architecture
Strictly adhere to the **Standard Python Project Layout** (using the `src` layout pattern). When creating new files or suggesting refactors, use the following logic:
* **`/`**: Main application and library code.
    * The subdirectory name here should match the primary package name.
    * Business logic, storage adapters, and domain models reside here.
* **`tests/`**: Test suite.
    * Test files must mirror the directory structure of `src/` to separate application code from test code.
* **`scripts/`**: Companion scripts, utility executables, and CLI entry points.
* **`ai_context/`**: Dedicated directory for all AI-generated documentation, plans, and architectural decisions.
* **`api/`**: OpenAPI/Swagger specs, JSON schema files, or protocol definition files.

---
## 3. Python Coding Standards
### General Style
* **Formatting:** All code must adhere to PEP 8 standards. Use `black` for formatting and `isort` for import sorting.
* **Linting:** Use `ruff` or `flake8` to maintain standardisation and code quality.
* **Type Hinting:** Use standard Python type hints (`typing` module or built-ins) for all function arguments and return types. 
* **Naming:**
    * Use `snake_case` for variables, functions, and module names.
    * Use `PascalCase` for class names.
    * Use `UPPER_SNAKE_CASE` for module-level constants.

### Error Handling
* **Explicit Handling:** Catch specific exceptions rather than using a bare `except:`.
* **Custom Exceptions:** Define custom exception classes inheriting from `Exception` for domain-specific, actionable failure states.
* **Raising Errors:** Provide clear, informative error messages when raising exceptions. Ensure exceptions do not leak sensitive infrastructure details to user-facing APIs.

### Concurrency
* **Async I/O:** Use `asyncio` for network-bound operations or I/O-heavy workloads where non-blocking execution is required.
* **Thread/Process Pools:** Use `concurrent.futures` when handling CPU-bound tasks or when interacting with strict synchronous libraries.
* **Safety:** Use standard synchronisation primitives (e.g., `asyncio.Lock`, `threading.Lock`) when managing shared state.

### Testing
* **Framework:** Use `pytest` for all unit and integration testing.
* **Style:** Utilise fixtures for setup and teardown. Parameterise tests to efficiently validate multiple inputs against expected outputs.
* **Location:** Place test files in the `tests/` directory, mapping directly to the module they test (e.g., `src/module/foo.py` is tested by `tests/module/test_foo.py`).

---
## 4. Technology Stack & Dependencies
* **Python Version:** 3.11+ (minimum)
* **Dependency Management:** Use `pyproject.toml` (via standard tooling like Poetry, pip-tools, or Hatch) to manage dependencies.
* **Configuration:** `argparse` or `click` for CLI tools + environment variables.
  * Environment variables use uppercase with underscores.
  * **Priority:** Environment variables first, then CLI parameters (CLI overrides env vars).
* **CLI Tools for Libraries:** Build companion CLI tools to exercise libraries and backends.
  * **Purpose:** Troubleshooting, debugging, and validating library behaviour.
  * **External API Libraries:** Create CLI tools that use the library to call external APIs.
  * **Internal APIs:** Create CLI tools that exercise the same backend libraries as the API, allowing execution of core logic without the HTTP layer.
  * Store CLI tools in the `scripts/` directory.
* **Logging:** Standard `logging` module or structured loggers like `structlog`.
  * Usage must be structured JSON in production environments.
  * **Log Levels:** Logging must strictly use user-defined log levels (e.g., set via configuration files or environment variables) to determine output verbosity. Do not hardcode internal log level overrides.
  * Include context fields (timestamps, module names, execution IDs).
  * **Operational Endpoints:** Minimise logging on health and metrics endpoints unless failures occur or the user-defined level explicitly demands high verbosity.
* **HTTP Framework:** `FastAPI` (or equivalent standard ASGI frameworks).
  * Use standard middleware patterns for cross-cutting concerns.
* **Metrics:** `prometheus_client`
  * Expose a `/metrics` endpoint.
  * Use standard metric types (Counter, Gauge, Histogram).
* **Versioning & Release Management:** Automated via `zest.releaser`.
  * Use semantic versioning (MAJOR.MINOR.PATCH).
  * Rely entirely on `zest.releaser` commands (e.g., `fullrelease`) to manage git tagging, version bumping, and repository pushes. 
* **CHANGELOG.md Maintenance:**
  * Keep CHANGELOG.md updated with each release.
  * Follow [Keep a Changelog](https://keepachangelog.com/) format.
  * Document architectural changes and bug fixes (not low-level implementation details).
  * Categories: Added, Changed, Deprecated, Removed, Fixed, Security.
* **AWS Default Region:** `ap-southeast-2` (Sydney, Australia)
  * Use as default in all AWS SDK (`boto3`) configurations.
  * Allow override via environment variable or CLI flag.

---
## 4a. Docker Standards
* **Container Types:**
  * **Production (Slim):** Minimal images built from `python:<version>-slim`.
    * Install only runtime dependencies (no dev/test tools).
    * Non-root user (UID 1000).
  * **Debug:** Full-featured images for troubleshooting.
    * Includes shell (bash), curl, jq, and relevant development packages.
* **Dockerfile Standards:**
  * **Multi-stage builds:** Use a builder stage to compile wheels and process requirements, then copy artifacts to a clean final stage to reduce image size.
  * **Security:** Run as a non-root user.
  * **Location:** Store Dockerfiles in `dockerspecs/<service-name>/Dockerfile`.
* **Health Checks:**
  * Keep `HEALTHCHECK` directives lightweight, ideally calling a simple internal Python script or local endpoint without heavily taxing the container.

---
## 5. Interaction Guidelines for the Agent
1.  **Context Awareness:** Before suggesting changes, read `pyproject.toml` or `requirements.txt` to understand available dependencies. Do not introduce new third-party packages if the standard library suffices.
2.  **Refactoring:** If asked to refactor, ensure the public API surface remains unchanged unless explicitly instructed otherwise.
3.  **Code Generation:**
    * Always generate code with docstrings explaining *why*, not just *what*. Use standard formatting (e.g., Google or NumPy style) for class and function docstrings.

## 5a. HTTP Response Standards
**Health Check Endpoints:**
* `/health`, `/healthcheck`, `/healthz` - Liveness checks (return HTTP 200)
* `/ready`, `/readyz` - Readiness checks (return HTTP 200)
**Metrics Endpoint:**
* `/metrics` - Prometheus metrics endpoint.
**Version Endpoint:**
* `/version` - Return JSON payload containing current version and build data.

---
## 6. Generated Documentation & Artifacts
When asked to produce plans, summaries, post-mortems, or architectural documents:
1.  **Storage Location:** Save the file strictly in the `ai_context/` directory.
2.  **Naming Convention:** Prepend the filename with the ISO 8601 timestamp (Format: `YYYY-MM-DDTHH-MM-SS`) of the moment of generation.
    * *Example:* `2025-10-24T14-30-00_refactoring_plan.md`
    * *Example:* `2025-11-01T09-00-00_api_design_spec.md`
3.  **Format:** Ensure all generated files are valid Markdown.

Also maintain full context for the project, including:
* Architectural decisions
* Design documents
* Meeting notes
* Relevant research
* Any other artifacts that provide context for future maintainers
* Plans for future improvements or refactors
* Post-mortems for incidents or outages
* Rationale for major design decisions
* Summaries of complex features or modules
* Keep this documentation up-to-date with any changes made to the codebase.
* Use clear, descriptive filenames that reflect the content of the document.
* Ensure all documents are well-structured and easy to navigate.
* Link related documents where appropriate to provide a comprehensive understanding of the project.
* Regularly review and update the documentation to ensure its accuracy and relevance.
* Store these documents in the `ai_context/` directory for easy access and reference.

---
## 7. Memory & Context Maintenance
You are required to maintain a persistent history of our work in the file `ai_context/memory.md` (create it if it doesn't exist).
**File Location:** `ai_context/memory.md` (NOT in project root)

**Rules for every session:**
1.  **READ FIRST:** At the very beginning of every new session, you MUST read:
    * `ai_context/memory.md` - Understand project status, recent decisions, and last stopping point
    * `ai_context/0-Architecture.md` - Understand project-specific architecture and design decisions
    * Other relevant files under `ai_context/` for additional context
2.  **UPDATE LAST:** Before you finish your response or terminate the session, you MUST update `ai_context/memory.md` with:
    * A brief summary of what was accomplished in this session
    * Any architectural decisions made
    * The current state of pending tasks
    * What needs to be done next
    * Reference any new documentation files created
3.  **Cross-Session Consistency:** Use memory.md to ensure you do not repeat mistakes or lose context between invocations
4.  **Keep Current:** Update memory.md as work progresses, not just at session end
