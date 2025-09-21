# zInfo

**An index/catalogue system for projects in the file system**

zInfo is a command-line tool that scans directory trees to locate and index "interesting folders" by reading project metadata files. It provides a searchable, filterable interface to your project ecosystem, making it easy to discover and manage projects across your filesystem.

## Features

- **Modular Architecture**: Extensible scanner system supporting multiple metadata formats
- **SQLite Caching**: Persistent indexing with fast lookups and incremental updates
- **CLI Interface**: Simple command-line interface for scanning and querying
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Metadata Extraction**: Parses project metadata from text files
- **Error Handling**: Robust error collection and reporting

## Installation

```bash
# Using uv (recommended)
uv tool install -e .

# Or using pip
pip install -e .
```

## Quick Start

### Scanning Projects

Scan a directory tree for projects with metadata files:

```bash
# Scan current directory with default depth (5 levels)
zinfo scan

# Scan specific directory with custom depth
zinfo scan --root /path/to/projects --depth 3

# Enable verbose logging
zinfo scan --verbose
```

### Querying the Index

Search and filter indexed projects:

```bash
# List all indexed projects
zinfo query

# Filter by title (partial match)
zinfo query --title "web"

# Filter by author
zinfo query --author "john"

# Filter by date range
zinfo query --after 2024-01-01 --before 2024-12-31
```

## Configuration

### Metadata File Format

zInfo currently supports `zinfo.txt` metadata files. The format uses simple key-value pairs:

```
title: My Project
summary: A brief description of what this project does
description: A more detailed explanation of the project's purpose and goals
authors: John Doe <john@example.com>, @johndoe
date_started: 2024-01-15
last_update: 2024-09-21
client: Example Corp
contact: project-lead@example.com
```

**Supported Fields:**
- `title` (required): Project name (max 100 chars)
- `summary`: Short description (max 200 chars)
- `description`: Detailed description (max 1000 chars)
- `authors`: Semicolon-delimited list with email/GitHub handles
- `date_started`: ISO date when project began
- `last_update`: ISO date of significant updates
- `client`: Sponsoring organization
- `contact`: Main contact person(s)
- Custom fields: Any additional key-value pairs you need

### Scan Parameters

- `--root`: Directory to start scanning from (default: current directory)
- `--depth`: How deep to traverse the folder tree (default: 5)
- `--cache`: SQLite database file location (default: zinfo.db)
- `--verbose`: Enable detailed logging

## Migration from Legacy Scripts

### Legacy Script Removal

The legacy HTML generation scripts (`envapplist.py` and `envmapplist.py`) have been removed and replaced with the new modular CLI architecture. This change provides:

- **Better maintainability**: Modular, testable code structure
- **Enhanced functionality**: SQLite caching and extensible metadata support
- **Improved performance**: Efficient scanning and querying
- **Better error handling**: Comprehensive error reporting

### Migration Guide

**Before (Legacy):**
```bash
python src/v.01/envapplist.py --root \\server\share\projects
```

**After (New CLI):**
```bash
zinfo scan --root /path/to/projects --depth 5
```

### Future Enhancements

The following features from the legacy scripts are planned for future releases:

- **Multiple Metadata Formats**: Support for `appinfo.txt` and `project.ini` formats (see [enhancement ticket #001](tickets/001-appinfo-scanner.md) and [#002](tickets/002-project-ini-scanner.md))
- **HTML Export**: Web-friendly export functionality with styled tables (see [enhancement ticket #003](tickets/003-html-export.md))
- **Link Utilities**: Enhanced file:// URL generation and contact normalization (see [enhancement ticket #004](tickets/004-link-contact-utilities.md))
- **Documentation Detection**: Automatic linking to Doc/ subdirectories (see [enhancement ticket #005](tickets/005-doc-directory-detection.md))

## Architecture

zInfo follows a modular architecture with clean separation of concerns:

- **CLI Layer**: Command-line interface using Click framework
- **Scanner Layer**: Abstract base classes for metadata extraction
- **Cache Layer**: SQLite-based persistence for scan results
- **Model Layer**: Dataclasses representing resources and scan outcomes

For detailed architecture information, see [ARCHITECTURE.md](.kilocode/rules/memory-bank/architecture.md).

## Development

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd zinfo

# Install with uv (recommended)
uv tool install -e .

# Run tests
uv run pytest

# Run with verbose logging
zinfo scan --verbose
```

### Project Structure

```
src/zinfo/
├── cli.py              # Command-line interface
├── core/
│   ├── models.py       # Data models and dataclasses
│   ├── scanner.py      # Scanner implementations
│   └── cache.py        # SQLite caching layer
tests/                  # Test suite
tickets/                # Enhancement tickets
```

## Contributing

1. Check existing [enhancement tickets](tickets/) for planned features
2. Follow the modular architecture patterns
3. Add comprehensive tests for new functionality
4. Update documentation for any changes

## License

[Add license information here]

## Changelog

For detailed change history, see [CHANGELOG.md](CHANGELOG.md).
