# zInfo

**An index/catalogue system for projects in the file system**

zInfo is a command-line tool that scans directory trees to locate and index "interesting folders" by reading project metadata files. It provides a searchable, filterable interface to your project ecosystem, making it easy to discover and manage projects across your filesystem no matter where they are. No longer do you need to have all your projects co-located in a single 'Projects' folder tree.

## Features

- **Modular Architecture**: Extensible scanner system supporting multiple metadata formats
- **SQLite Caching**: Persistent indexing with fast lookups and incremental updates
- **CLI Interface**: Simple command-line interface for scanning and querying
- **Web UI**: FastHTML-based web interface for browsing, searching, filtering, and in-app scanning
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

# Filter by author (searches in team field)
zinfo query --author "jonah"

# Filter by shortname
zinfo query --shortname "web"

# Filter by client
zinfo query --client "Dept"

# Filter by team
zinfo query --team "matt"

# Filter by directory ID
zinfo query --dir-id "abc123"

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

## Web UI

zInfo provides a complete web-based interface built with FastHTML for browsing, searching, filtering, and managing your project index.

### Running the Web UI

Launch the web interface:

```bash
# Start the web server
zinfo-web

# Access at http://localhost:5001 by default
```

The web UI provides the same powerful querying capabilities as the CLI, with an intuitive graphical interface for discovery and management.

For detailed UI documentation and features, see [`src/zinfo/ui/README.md`](src/zinfo/ui/README.md).

## Configuration

### Metadata File Format

zInfo currently supports `zinfo.txt` metadata files. The format uses simple key-value pairs:

```
title: My Project
shortname: my-project
summary: A brief description of what this project does
description: A more detailed explanation of the project's purpose and goals
team: Jane Doe <jane@example.ca> @janedoe; Sam Gamgee, @samwise;
date_started: 2024-01-15
date_updated: 2024-09-21
client: Dept of Environment
client_contact: project-lead@example-org.net
status: Complete
```

#### Metadata Fields

**System** (in db, not in zinfo.txt)
- `dir_id`: unique id computed at scan time from project folder, hashed into 6 or more characters. Not editable.
- `dir_path`: fully resolved path to zinfo file's `location`

**Required**
- `title`: Project or product name (soft max 50 chars)
- `shortname`: nickname, for casual use, files & folders, quick typing (soft max 15 chars)
- `summary`: Short description (soft max 150 chars)
- `client`: Sponsoring organization or person, who deliverables go to
- `team`: Primary author(s) or team lead(s), semicolon-delimited list
    - `contact_email`: email address of team lead/author
- `location`: path to where the project zinfo file lives
  
Soft max: after this limit chararcters might be muted, elided, or not shown in the UI.

**Optional**
- `other_id`: Project or product ID in your other system(s), omma separated
- `description`: Detailed description (max chars?)
- `contact_handle:`: social nickname or handle, e.g. @samwise
- `related_projects`: related project names or IDs
    - `--> name`: this project depends or is child of 'name'
    - `<-- name`: 'name' depends or is child of this project
    - `name`: 'name' is related to this project
- `links`: url or file system links
- `date_started`: project began on this date (all dates are ISO)
- `date_updated`: date of latest significant milestone
- `client_contact`: Client contact name(s)
    - `client_email`: email address of client
    - `client_handle`: social nickname or handle, e.g. @jwhale
- `status`: Pending, In-progress, On-hold, Complete, Shelved, Perpetual
    - `progress`: 0-100%
- `priority`: 1 - 4 (low, medium, high, critical)
- `comment`: notes

**Custom**
- Any additional key-value pairs you need, `key: value`


### Scan Parameters

- `--root`: Directory to start scanning from (default: current directory)
- `--depth`: How deep to traverse the folder tree (default: 5)
- `--cache-db`: SQLite database file location (default: zinfo.db)
- `--verbose`: Enable detailed logging

### Query Parameters

- `--cache-db`: SQLite database file location (default: zinfo.db)
- `--verbose`: Enable detailed logging
- `--title`, `-t`: Filter by title (partial match)
- `--author`, `-a`: Filter by author (searches in team field)
- `--shortname`, `-s`: Filter by shortname (partial match)
- `--client`, `-C`: Filter by client (partial match)
- `--team`, `-m`: Filter by team (partial match)
- `--dir-id`, `-d`: Filter by dir_id (partial match)
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
│   ├── fh_ui.py        # FastHTML web UI
│   ├── main.py         # NullUI entry point
│   ├── null_ui.py      # Headless UI implementation
│   ├── static/         # Static assets
│   │   └── script.js   # HTMX scripts
│   └── README.md       # UI documentation
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
