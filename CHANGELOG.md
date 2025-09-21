# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.io/spec/v2.0.0.html).

## [Unreleased]

### Added
- Modular scanner architecture with `BaseScanner` abstract base class
- SQLite caching system for persistent indexing
- CLI commands for scan and query operations using Click framework
- Comprehensive test suite with pytest
- Support for `zinfo.txt` metadata format with key-value parsing
- Dataclasses for metadata and scan result models
- **Advanced query command** with flexible filtering options (title, author, type, ID)
- **Multiple output formats** for query results (table, detailed, JSON)
- **Date range filtering** with support for partial dates (YYYY, YYYY-MM, YYYY-MM-DD)
- **Flexible date parsing** utilities for various date formats and metadata fields
- **Interactive query features** including count-only mode and result limiting

### Removed
- Legacy HTML generation scripts (`envapplist.py`, `envmapplist.py`)
- Manual HTML table generation code
- Legacy metadata parsing logic
- Direct file system manipulation scripts

### Migration Notes
- **For users of legacy scripts**: The functionality has been migrated to the new CLI-based architecture
- **New commands**: Use `zinfo scan --root <path> --depth <n>` instead of running legacy Python scripts
- **Query command**: The query command is now fully implemented with advanced filtering and multiple output formats
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
