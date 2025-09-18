# Project Context

## Current Work Focus
- Implementing the core CLI for scanning directories and extracting metadata from zinfo.txt files.
- Building SQLite caching for persistent indexing.
- Basic error handling and logging in place.

## Recent Changes
- Migrated from standalone HTML generation scripts (envapplist.py, envmapplist.py) to a modular scanner architecture.
- Added pytest-based unit tests for scanner functionality.
- Defined dataclasses for metadata and scan results.
- Completed transition to UV for env and package management; tests now run cleanly with all imports resolved.

## Next Steps
- Complete the query command with filtering by title, author, date.
- Add project initiation tools to create boilerplate folders and metadata files.
- Build a browseable, filterable UI.
- Extend scanner to support additional metadata formats (e.g., appinfo.txt, project.ini).
- Enhance caching with incremental updates and change detection.