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
- When you discover an issue, immediately update `tickets/` with your findings using a subagent. When the issue is resolved, update `tickets/` and mark closed.
- When the tests pass, update `tickets/`, then add changed code and ticket with "git add -A" via bash, then do a "git commit" with a message that describes the changes you made to the code. After the commit, do a "git push" to push the changes to the remote repository.

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
