# zInfo Product Overview

## Why This Project Exists
zInfo is a tool designed to create an organized index or catalogue of projects and "interesting folders" scattered across a filesystem. In large organizations or personal workflows, important projects can be buried in directory trees, making discovery and management difficult. zInfo addresses this by automating the detection, metadata extraction, and indexing of these resources, enabling quick searching, browsing, and collaboration.

## Problems It Solves
- **Discovery Challenges**: Manually searching for projects across network shares, local drives, or cloud storage is time-consuming and error-prone.
- **Metadata Inconsistency**: Projects often lack standardized documentation, leading to lost context about authors, purposes, and statuses.
- **Maintenance Overhead**: Keeping an up-to-date inventory requires constant effort; zInfo automates rescans and caching to reduce this burden.
- **Collaboration Barriers**: Team members need easy access to project details like contacts, documentation, and last updates without deep filesystem knowledge.
- **Scalability Issues**: As file systems grow, traditional file explorers fall short; zInfo provides structured querying and filtering.

## How It Should Work
1. **Scanning**: zInfo walks a specified directory tree (with configurable depth) to locate metadata marker files (default: `zinfo.txt`). It parses these files for key-value pairs (e.g., title, summary, authors, dates).
2. **Metadata Extraction**: Supports flexible metadata fields, ignoring projects marked as private. Extracts structured data into a unified model (`ResourceMetadata`).
3. **Caching and Persistence**: Stores results in a SQLite database for fast lookups, tracking changes via timestamps, and enabling incremental updates.
4. **Indexing and Querying**: Builds a searchable index with both CLI-based output and a complete web interface providing browseable/filterable access via FastHTML.
5. **Project Initiation**: Tools to create new project folders with boilerplate metadata files.
6. **Extensibility**: Modular scanner architecture allows support for different metadata formats (e.g., integrating legacy `appinfo.txt` or `project.ini` parsers).

Workflow Example:
- Run `zinfo scan --root /projects --depth 5` to build/update the index.
- Query with `zinfo query --title "GIS"` to list matching projects with details.

## User Experience Goals
- **Simplicity**: Intuitive CLI commands with sensible defaults (e.g., current directory, depth 5). Verbose logging for transparency.
- **Reliability**: Robust error handling for invalid files/directories, with detailed reports. Caching ensures performance even on large scans.
- **Discoverability**: Output shows key info (title, path, authors) in a human-readable format. Future UI: Filterable tables, search by author/date/client.
- **Flexibility**: Configurable via options (root, depth, cache location). Supports UNC paths for network shares.
- **Low Friction**: Minimal setup; runs on standard Python environments. Encourages metadata adoption through easy project templating.
- **Transparency**: Logs scan stats (time, items found, errors) and metadata previews to build user trust.

zInfo aims to transform chaotic file systems into navigable knowledge bases, saving time and fostering better project management.
