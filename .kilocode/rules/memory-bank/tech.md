# Technologies and Setup

## Technologies Used
- **Language**: Python 3.11+
- **CLI Framework**: Click for command-line interface
- **GUI Framework**: NullUI for headless/CLI-only usage
- **Web Framework**: FastHTML using idiomatic patterns - `fast_app()` with exception handlers, `serve()` function for startup, automatic FT component response conversion, exclusive Pico CSS styling (no custom CSS), reference manual: `/reference/llms-ctx.txt`
- **Database**: SQLite for caching and persistence
- **Data Structures**: dataclasses for models
- **File Handling**: pathlib for cross-platform paths
- **Testing**: pytest with fixtures and coverage
- **Environment & Dependency Management**: uv from Astral.sh

## Development Setup
- **Project Structure**: 
  - `src/zinfo/`: Main package with `__init__.py`, `cli.py`, `core/` (models, scanner, cache), legacy scripts
  - `tests/`: Pytest suite with `conftest.py` (fixtures), `core/` (unit tests), `fixtures/` (sample data)
- **Installation**: `uv tool install -e .` for editable install
- **Running**: `zinfo scan --root . --depth 5` (CLI entry via project.scripts in pyproject.toml)
- **Testing**: `uv run pytest` (pytest with coverage)
- **Database**: SQLite file (default: zinfo.db) created on first scan

## Tickets
- **Reporting:** Create a new markdown file in `tickets/` with a clear title, short summary, steps to reproduce, expected vs actual behavior, environment details, and any relevant logs or attachments. Use a subagent when needed to gather reproducer data or screenshots.
- **Triaging & Assigning:** Triage tickets promptly, add labels or priority.
- **Fixing & Verification:** Link the ticket to a branch or change. When a fix is implemented, update the ticket with a short description of the change and verification steps performed.
- **Commit & Push:** After local tests pass, stage changes with `git add -A`, commit with a descriptive message that references the ticket (e.g., "tickets/006: Fix FastHTML UI layout"), and push the branch (`git commit -m "..." && git push`).
- **Closing:** Once the change is pushed and any CI/tests pass, mark the ticket closed and add final verification notes (what was tested and by whom).
## Technical Constraints
- **Platform**: Primarily Windows-focused (UNC paths, file:/// links in legacy), but uses pathlib for cross-platform compatibility
- **Metadata Formats**: Currently zinfo.txt (key-value); extensible via BaseScanner subclasses
- **Performance**: Depth-limited traversal (default 5); suitable for large filesystems but not real-time
- **No External APIs**: Standalone tool, no cloud dependencies

## Dependencies
From pyproject.toml:
- click (CLI)
- pytest, pytest-cov (testing)
- fasthtml (web-ui)

Runtime: Standard library (datetime, json, os, logging, sqlite3)

## Tool Usage Patterns
- **Logging**: BasicConfig for INFO level; logger per module
- **Testing**: Fixtures for temp dirs/cache; unit tests for scanner extraction, caching, error handling
- **Error Handling**: Collect in lists, log without halting; robust path/file checks
- **Extensibility**: ABC for scanners; JSON for flexible metadata/errors in DB
- **Build**: pyproject.toml with setuptools backend; pixi for reproducible env (conda-forge, win-64)
