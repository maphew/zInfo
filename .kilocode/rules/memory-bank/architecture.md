# Architecture

## System Architecture
zInfo follows a modular architecture centered around scanning, metadata extraction, caching, and querying. The system is designed for extensibility, allowing easy addition of new metadata parsers while maintaining a clean separation of concerns.

High-level components:
- **CLI Layer**: Entry point using Click for commands like `scan` and `query`.
- **Scanner Layer**: Core logic for directory traversal and metadata extraction using abstract base classes.
- **Cache Layer**: SQLite-based persistence for scan results and metadata.
- **Model Layer**: Dataclasses representing resources and scan outcomes.
- **Output Layer**: Currently CLI echoes; extensible to UI (marimo) or HTML generation.

Data flow: CLI -> Scanner (with Cache) -> Models -> Cache -> Query/Output.

## Source Code Paths
- **Entry Point**: [`src/zinfo/cli.py`](src/zinfo/cli.py) - Defines `main` group and `scan`/`query` commands.
- **Core Models**: [`src/zinfo/core/models.py`](src/zinfo/core/models.py) - `ResourceMetadata` and `ScanResult` dataclasses.
- **Scanning**: [`src/zinfo/core/scanner.py`](src/zinfo/core/scanner.py) - `BaseScanner` (ABC) and `ZinfoScanner` implementation.
- **Caching**: [`src/zinfo/core/cache.py`](src/zinfo/core/cache.py) - SQLite cache implementation with resource and scan tables.

## Key Technical Decisions
- **Metadata Parsing**: Simple key-value parsing from first 50 lines of zinfo.txt (case-insensitive keys), with support for arbitrary fields in `extra` dict.
- **Traversal**: os.walk with depth pruning for efficiency; glob fallback in base scanner.
- **Persistence**: SQLite for local cache, using JSON for flexible fields and error lists; datetime adapters for proper handling.
- **Extensibility**: Abstract BaseScanner allows subclassing for new formats (e.g., INI, YAML); ResourceMetadata type field for polymorphism.
- **Error Handling**: Collect errors in ScanResult without halting scan; logging for diagnostics.
- **Platform**: Pathlib for cross-platform paths, but Windows-focused examples (UNC, file:/// links in legacy).

## Design Patterns
- **Abstract Factory/Strategy**: BaseScanner ABC for pluggable metadata extractors.
- **Repository**: Cache class as repository for CRUD on resources and scans.
- **Data Transfer Object**: ResourceMetadata and ScanResult for clean data passing.
- **Builder**: ScanResult construction aggregates items, stats, errors.

## Component Relationships
- CLI instantiates Scanner and Cache, passes Cache to Scanner for persistence.
- Scanner traverses dirs, extracts via extract_metadata -> Models, stores via Cache.
- Cache interacts with DB, serializes Models to rows (JSON for extra).
- Models are immutable dataclasses, used across layers.

## Critical Implementation Paths
- **Scan Flow**: cli.scan() -> ZinfoScanner.scan() -> os.walk -> extract_metadata (parse zinfo.txt) -> ResourceMetadata -> Cache.store_scan_result().
- **Query Flow**: cli.query() (stub) -> Cache.get_resources_by_type() -> filter/output.
- **Extending Parsers**: Subclass BaseScanner, override can_handle_file and extract_metadata, register in CLI.
- **Incremental Cache**: Future: Compare last_modified vs last_indexed to update only changed resources.
