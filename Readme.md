# zInfo

**An index/catalogue system for projects in the file system**

zInfo is a command-line tool that scans directory trees to locate and index "interesting folders" by reading project metadata files. It provides a searchable, filterable interface to your project ecosystem, making it easy to discover and manage projects across your filesystem no matter where they are. No longer do you need to have all your projects co-located in a single 'Projects' folder tree.

## Features

- **Modular Architecture**: Extensible scanner system supporting multiple metadata formats
- **SQLite Caching**: Persistent indexing with fast lookups and incremental updates
- **CLI Interface**: Simple command-line interface for scanning and querying
- **UI Framework**: Extensible UI framework with NullUI for headless usage
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

Search and filter indexed projects with flexible options:

```bash
# List all indexed projects (table format)
zinfo query

# List all projects (limited to avoid overwhelming output)
zinfo query --all --limit 50

# Filter by title (partial match)
zinfo query --title "web"

# Filter by author (searches in extra fields and contact)
zinfo query --author "jonah"

# Filter by metadata type
zinfo query --type "zinfo_project"

# Get specific project by ID
zinfo query --id "path/to/project/zinfo.txt"

# Different output formats
zinfo query --format table          # Default table format
zinfo query --format detailed       # Detailed information
zinfo query --format json           # JSON output for scripting

# Count matching projects
zinfo query --count                 # Show total count
zinfo query --title "web" --count   # Count matching filter

# Limit results
zinfo query --limit 10

# Combine filters
zinfo query --title "analysis" --author "matt" --format detailed

# Filter by date range (supports partial dates: YYYY, YYYY-MM, YYYY-MM-DD)
zinfo query --after 2024-01 --before 2024-12
zinfo query --after 2024-01-01 --before 2024-12-31

# Filter by different date fields
zinfo query --after 2024-01 --date-field created
zinfo query --after 2024-01 --date-field last_modified

# Combine date filtering with other filters
zinfo query --after 2024-01 --title "Research" --format table --limit 5
```

## UI Framework

zInfo provides a headless UI framework designed for CLI-only usage and as a foundation for future GUI implementations:

### Running the GUI

```bash
# Launch the GUI application (headless mode)
zinfo-gui

# Launch with specific cache database
zinfo-gui /path/to/cache.db
```

### UI Features

- **Headless Operation**: No-op implementations for all UI operations
- **CLI Integration**: Seamless fallback for command-line environments
- **Error Logging**: User-friendly error messages logged to console
- **Testing Support**: Suitable for automated testing and CI/CD pipelines
- **Extensibility**: Abstract interfaces ready for future GUI framework integrations

### UI Architecture

The UI follows a modular architecture with abstract interfaces:

- **Framework-Agnostic Layer**: Abstract interfaces for UI operations
- **NullUI Implementation**: Headless/no-op implementation for CLI usage
- **Application Controller**: Coordinates UI and core functionality

For detailed UI documentation, see [UI README](src/zinfo/ui/README.md).

## Configuration

### Metadata File Format

zInfo currently supports `zinfo.txt` metadata files. The format uses simple key-value pairs:

```
title: My Project
shortname: my-project
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
- `shortname`: nickname, for casual use, quick typing (max 20 chars)
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
- `--cache-db`: SQLite database file location (default: zinfo.db)
- `--verbose`: Enable detailed logging

### Query Parameters

- `--cache-db`: SQLite database file location (default: zinfo.db)
- `--verbose`: Enable detailed logging
- `--title`, `-t`: Filter by title (partial match)
- `--author`, `-a`: Filter by author (searches in extra fields and contact)
- `--type`, `-T`: Filter by metadata type
- `--limit`, `-l`: Limit number of results
- `--format`, `-f`: Output format (table, detailed, json)
- `--all`, `-A`: Show all resources (ignore other filters)
- `--count`, `-c`: Show only count of matching resources
- `--id`, `-i`: Get specific resource by ID
- `--after`: Filter resources after this date (YYYY, YYYY-MM, or YYYY-MM-DD)
- `--before`: Filter resources before this date (YYYY, YYYY-MM, or YYYY-MM-DD)
- `--date-field`: Date field to filter on (created, updated, last_modified, last_indexed)

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
├── ui/                 # User interface framework
│   ├── __init__.py     # Abstract UI interfaces
│   ├── app.py          # Application controller
│   ├── main.py         # GUI entry point
│   ├── null_ui.py      # Headless UI implementation
│   └── README.md       # GUI documentation
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
