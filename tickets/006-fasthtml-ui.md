# 006 - FastHTML UI Implementation

## Epic Overview
Implement a FastHTML-based web UI for zInfo that provides browseable, filterable access to cached resources with in-app scan capabilities.

## Checklist
- [x] Iteration 0 Scaffolding
- [x] Iteration 1 Browse
- [x] Iteration 2 Filter
- [x] Iteration 3 Details
- [x] Iteration 4 Scan
- [x] Iteration 5 Toasts/Errors
- [x] Iteration 6 CLI entry

## Sub-issues
None yet.

## Notes
Iteration 0 completed: basic FastHTML app structure with index route and smoke test passing.
Started with Iteration 0: basic app structure and smoke test.
Iteration 1 completed: modified index route to display table of all cached resources with columns title, type, id, path. Added tests for empty and seeded cache scenarios.
Iteration 2 completed: added filtering functionality with form inputs for title, author, type, id. Created /search route that handles HTMX requests (partial table) and non-HTMX requests (full page). Updated tests with varied data and filtering scenarios.
Iteration 3 completed: Resource details drawer with HTMX. Added /detail route that returns panel with title, type, link, contact, doc_dir. HTMX links in table titles, detail div added. Tests for HX/non-HX requests added and passing. Note link/contact formatting deltas - reference tickets 004 and 005.
Iteration 4 completed: added /scan route with root and depth params (defaults match CLI), calling scan flow from scanner.py and persisting via cache, added scan form on index, and updated tests. No discrepancies with CLI options/signatures noted.
Iteration 5 completed: Added toast notifications for scan success/error, 404 error page. Edge cases: bad root path triggers error toast, invalid routes show 404 page.
Iteration 6 completed: Added console_script 'zinfo-web' pointing to run() in fh_ui.py. MVP complete with all core UI functionality implemented. Follow-ups: Add port/host configuration options to run() function for production deployment.
