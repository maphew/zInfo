# Project Context

## Current Work Focus
- Implementing the core CLI for scanning directories and extracting metadata from zinfo.txt files.
- Building SQLite caching for persistent indexing.
- Basic error handling and logging in place.

## Recent Changes
- Completed removal of legacy HTML generation scripts (envapplist.py, envmapplist.py) and migration to modular scanner architecture.
- Added pytest-based unit tests for scanner functionality.
- Defined dataclasses for metadata and scan results.
- Completed transition to UV for env and package management; tests now run cleanly with all imports resolved.

## Next Steps
- Complete the query command with filtering by title, author, date.
- Add project initiation tools to create boilerplate folders and metadata files.
- Build a browseable, filterable UI.
- Extend scanner to support additional metadata formats (e.g., appinfo.txt, project.ini) - see enhancement tickets 001, 002.
- Enhance caching with incremental updates and change detection.
- Implement HTML export functionality - see enhancement ticket 003.
- Add link and contact utilities - see enhancement ticket 004.
- Add documentation directory detection - see enhancement ticket 005.
