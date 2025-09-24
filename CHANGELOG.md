# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.io/spec/v2.0.0.html).

## [Unreleased]

### Added
- **FastHTML Web UI**: Complete web-based interface for browsing, searching, filtering, and managing project indexes
- **In-App Scanning**: Trigger directory scans directly from the web interface
- **Pagination**: Efficient browsing of large project indexes with HTMX dynamic loading
- **Responsive Design**: Mobile-friendly interface with card-based layouts and Pico CSS styling
- **In-Memory Caching**: Performance optimization for web UI database queries with TTL-based cache invalidation
- **Advanced Query Filters**: New CLI options for shortname, client, team, and dir_id filtering
- **Modular scanner architecture** with `BaseScanner` abstract base class
- **SQLite caching system** for persistent indexing
- **CLI commands** for scan and query operations using Click framework
- **Comprehensive test suite** with pytest
- **Support for `zinfo.txt` metadata format** with key-value parsing
- **Dataclasses for metadata and scan result models**
- **Advanced query command** with flexible filtering options (title, author, type, ID)
- **Multiple output formats** for query results (table, detailed, JSON)
- **Date range filtering** with support for partial dates (YYYY, YYYY-MM, YYYY-MM-DD)
- **Flexible date parsing** utilities for various date formats and metadata fields
- **Interactive query features** including count-only mode and result limiting
- **NullUI implementation** for headless/CLI-only environments
- **Security documentation** for FastHTML UI explaining authentication, access control, and deployment considerations

### Changed
- **UI Architecture**: Transitioned from planned native GUI frameworks to FastHTML web UI as primary interface
- **FastHTML UI Refactoring**: Removed all custom styling in favor of exclusive Pico CSS framework usage
- **Query Command**: Enhanced with additional filter options (shortname, client, team, dir_id)
- **Development Setup**: Migrated to UV for environment and dependency management
- **Testing**: Improved test coverage (96% for cache.py) with comprehensive unit tests

### Removed
- **Tkinter-specific GUI implementation** (`tk_app.py`, `tk_components.py`, `test_tk_components.py`)
- **Toga-specific GUI implementation** (`toga_app.py`, `toga_components.py`, `test_toga_components.py`)
- **Legacy HTML generation scripts** (`envapplist.py`, `envmapplist.py`)
- **Manual HTML table generation code**
- **Legacy metadata parsing logic**
- **Direct file system manipulation scripts**
- **Debug GUI test script** (`debug_gui_test.py`)

### Fixed
- **FastHTML UI Layout**: Restructured with CSS Grid, compact scan form, and professional color scheme
- **Exception Handling**: Improved error handling throughout the system with comprehensive logging
- **Path Handling**: Enhanced cross-platform path support with pathlib

### Migration Notes
- **For users of legacy scripts**: The functionality has been migrated to the new CLI-based architecture
- **New commands**: Use `zinfo scan --root <path> --depth <n>` instead of running legacy Python scripts
- **Query command**: The query command now includes additional filter options for enhanced searching
- **Web UI**: Primary interface is now the web UI accessible via `zinfo-web` command
- **Date filtering**: New `--after` and `--before` options support flexible date ranges and partial dates
- **Metadata format**: Currently supports `zinfo.txt` format; additional formats (`appinfo.txt`, `project.ini`) planned for future releases
- **HTML export**: Legacy HTML export functionality will be reimplemented in a future release (see enhancement ticket #003)

## [0.1.0] - 2024-09-21

### Added
- Initial modular scanner architecture
- Basic CLI structure with Click
- SQLite caching implementation
- Core models and scanner classes
- Unit test framework setup

### Migration from Legacy
- Legacy scripts removed in favor of modular architecture
- Enhanced error handling and logging
- Improved extensibility for future metadata formats
