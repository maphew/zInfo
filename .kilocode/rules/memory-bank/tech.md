# Technologies and Setup

## Technologies Used
- **Language**: Python 3.11+
- **CLI Framework**: Click for command-line interface
- **GUI Framework**: Toga for cross-platform graphical interface
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

## Technical Constraints
- **Platform**: Primarily Windows-focused (UNC paths, file:/// links in legacy), but uses pathlib for cross-platform compatibility
- **Metadata Formats**: Currently zinfo.txt (key-value); extensible via BaseScanner subclasses
- **Performance**: Depth-limited traversal (default 5); suitable for large filesystems but not real-time
- **No External APIs**: Standalone tool, no cloud dependencies

## Dependencies
From pyproject.toml:
- click (CLI)
- toga (GUI, version >=0.4.0)
- pytest, pytest-cov (testing)

Runtime: Standard library (datetime, json, os, logging, sqlite3)

## Tool Usage Patterns
- **Logging**: BasicConfig for INFO level; logger per module
- **Testing**: Fixtures for temp dirs/cache; unit tests for scanner extraction, caching, error handling
- **Error Handling**: Collect in lists, log without halting; robust path/file checks
- **Extensibility**: ABC for scanners; JSON for flexible metadata/errors in DB
- **Build**: pyproject.toml with setuptools backend; pixi for reproducible env (conda-forge, win-64)
