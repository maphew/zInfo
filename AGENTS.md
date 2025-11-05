# zInfo Agent Commands & Guidelines

## Build/Lint/Test Commands

- **Install dev dependencies**: `uv pip install -e ".[dev]"` or `pip install -e ".[dev]"`
- **Run all tests**: `uv run pytest` or `pytest`
- **Run single test**: `uv run pytest tests/path/to/test.py::TestClass::test_method`
- **Run tests with coverage**: `uv run pytest --cov=zinfo`
- **Lint code**: `uv run ruff check .`
- **Fix lint issues**: `uv run ruff check --fix .`
- **Format code**: `uv run black .`
- **Type check**: `uv run mypy src/`

## Architecture

zInfo is a modular Python CLI tool with SQLite caching and FastHTML web UI for indexing project metadata from filesystem directories.

**Core Components**:
- `src/zinfo/cli.py`: Click-based CLI commands (scan, query)
- `src/zinfo/core/models.py`: Dataclasses for ResourceMetadata and ScanResult
- `src/zinfo/core/scanner.py`: BaseScanner ABC and ZinfoScanner implementation
- `src/zinfo/core/cache.py`: SQLite persistence layer with JSON serialization
- `src/zinfo/ui/`: FastHTML web interface and NullUI headless implementation

**Database**: SQLite (zinfo.db) with resources and scans tables
**Metadata Format**: zinfo.txt files with key-value pairs
**UI Framework**: FastHTML with Pico CSS, HTMX for interactivity

## Code Style Guidelines

**Imports**: Standard library first, then third-party, then local imports (alphabetical within groups)
**Types**: Use type hints throughout, prefer `typing` module for complex types
**Dataclasses**: Use dataclasses for data models (ResourceMetadata, ScanResult)
**Error Handling**: Collect errors in ScanResult without halting operations
**Naming**: snake_case for variables/functions, PascalCase for classes
**Docstrings**: Use triple quotes with brief description
**Testing**: pytest with fixtures, comprehensive coverage required
**Formatting**: black (line length 88), ruff for linting
**Paths**: Use pathlib.Path for cross-platform compatibility

## FastHTML Patterns

- Use `fast_app()` with exception handlers as parameters (not decorators)
- Use `serve()` function for startup (not manual uvicorn)
- Return FT components directly (no manual `to_xml()` or `HTMLResponse`)
- Use Pico CSS exclusively (no custom CSS)
- Use `fasthtml.common` imports instead of redundant Starlette imports
- Server startup function named `run_server()`
