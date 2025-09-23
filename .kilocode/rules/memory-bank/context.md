# Project Context

## Current Work Focus
- Core CLI implementation completed with scanning and querying functionality.
- SQLite caching system implemented with search capabilities.
- Comprehensive error handling and logging throughout the system.
- **GUI implementation completed** with NullUI for headless/CLI-only usage.
- **FastHTML UI MVP completed**: Full browseable, filterable, searchable interface with in-app scan trigger.
- **Pagination implemented** for /index and /search routes with HTMX dynamic loading, page/limit parameters, and validation.

## Recent Changes
- Completed removal of legacy HTML generation scripts (envapplist.py, envmapplist.py) and migration to modular scanner architecture.
- Added pytest-based unit tests for scanner functionality.
- Defined dataclasses for metadata and scan results.
- Completed transition to UV for env and package management; tests now run cleanly with all imports resolved.
- **Implemented query command** with filtering by title, author, type, and ID.
- Added multiple output formats (table, detailed, JSON) for different use cases.
- Enhanced cache layer with advanced search methods and improved test coverage (96% for cache.py).
- **Implemented NullUI** for headless/CLI-only usage as the default GUI implementation.
- **Removed Tkinter-specific GUI implementation** (tk_app.py, tk_components.py, test_tk_components.py).
- **Removed Toga-specific GUI implementation** (toga_app.py, toga_components.py, test_toga_components.py) and updated main.py to use NullUI as the default.
- Removed debug_gui_test.py and cleaned up framework selection mechanism in main.py to explicitly default to NullUI.
- **Implemented new UI layout for FastHTML UI**: Restructured with CSS Grid, compact scan form in upper right, centered search form, enhanced styling with professional color scheme, card-based design, and responsive layout for mobile/tablet/desktop.
- **Implemented in-memory caching for FastHTML UI database queries** with TTL (30s for index, 10s for search) and cache invalidation on scan operations.
- Refactored FastHTML UI to use constants for hardcoded values (scan profiles, depths, pagination defaults, cache TTLs, etc.).
- **Created comprehensive security documentation** for FastHTML UI explaining authentication, access control, input validation, path traversal prevention, and deployment considerations.

## Next Steps
- Add project initiation tools to create boilerplate folders and metadata files.
- Extend scanner to support additional metadata formats (e.g., appinfo.txt, project.ini) - see enhancement tickets 001, 002.
- Enhance caching with incremental updates and change detection.
- Implement HTML export functionality - see enhancement ticket 003.
- Add link and contact utilities - see enhancement ticket 004.
- Add documentation directory detection - see enhancement ticket 005.
