Comprehensive plan to add a FastHTML UI to zInfo

Objective
Deliver a minimal, server-rendered FastHTML UI that:
- Lists cached resources with filters.
- Shows resource details.
- Provides a simple in-app scan trigger.
- Adheres to existing architecture and tests-per-iteration.
- Updates tickets upon issue discovery/resolution, and commits+pushes only after green tests.
- Defers complexity; reuse existing modules.

Scope and constraints
- UI stack: [python.fast_app()](reference/llms-ctx.txt:57) + HTMX defaults, Pico CSS on; return pages with [python.Titled()](reference/llms-ctx.txt:39), forms via [python.Form()](reference/llms-ctx.txt:258), inputs via [python.Input()](reference/llms-ctx.txt:260), buttons via [python.Button()](reference/llms-ctx.txt:232), serve with [python.serve()](reference/llms-ctx.txt:71).
- Reuse: [src/zinfo/core/cache.py](src/zinfo/core/cache.py), [src/zinfo/core/scanner.py](src/zinfo/core/scanner.py), [src/zinfo/core/models.py](src/zinfo/core/models.py). Keep CLI untouched ([src/zinfo/cli.py](src/zinfo/cli.py)).
- UI complements existing NullUI ([src/zinfo/ui/null_ui.py](src/zinfo/ui/null_ui.py)); headless remains default.
- Testing per iteration using [python.TestClient()](reference/llms-ctx.txt:271).
- Ticketing: new epic ticket [tickets/006-fasthtml-ui.md](tickets/006-fasthtml-ui.md); subagent updates on discovery+closure; commit after tests pass.

Files to add
- [src/zinfo/ui/fh_ui.py](src/zinfo/ui/fh_ui.py): FastHTML app, routes, small runner.
- [tests/ui/test_fh_ui.py](tests/ui/test_fh_ui.py): route tests with [python.TestClient()](reference/llms-ctx.txt:271).
- [tickets/006-fasthtml-ui.md](tickets/006-fasthtml-ui.md): epic tracking UI iterations and issues.
- Optional CLI runner entry (later): add console_script in [pyproject.toml](pyproject.toml) pointing to fh_ui runner.

Iterative delivery

Iteration 0 — Scaffolding and smoke test
- Implement:
  - [src/zinfo/ui/fh_ui.py](src/zinfo/ui/fh_ui.py): create app via [python.fast_app()](reference/llms-ctx.txt:57); define @rt index route returning [python.Titled()](reference/llms-ctx.txt:39) “zInfo UI” with placeholder content; expose run() that calls [python.serve()](reference/llms-ctx.txt:71) (no side effects on import).
- Tests:
  - GET “/” returns 200 and includes “zInfo UI”.
- Tickets:
  - Create [tickets/006-fasthtml-ui.md](tickets/006-fasthtml-ui.md); log any startup issues (Open → Closed upon fix).
- VCS:
  - After green tests: git add -A; git commit “006: FastHTML UI scaffolding and smoke test”; git push.

Iteration 1 — Read-only browse (list all cached resources)
- Implement:
  - In index handler, open cache via [src/zinfo/core/cache.py](src/zinfo/core/cache.py) default path and fetch all resources (reuse existing method; if missing, implement the smallest addition to cache API).
  - Render a simple table: columns [title, type, id, path]. Use semantic FTs in a [python.Container()](reference/llms-ctx.txt:1709).
- Tests:
  - Use temp cache fixture (pattern from tests/core) and verify rows render.
- Tickets:
  - If cache lacks “get_all_resources”, open sub-issue under 006 and minimally add it; mark Closed after tests.
- VCS:
  - Commit “006: List cached resources on index; tests”.

Iteration 2 — Filtering (title, author, type, id)
- Implement:
  - Add a [python.Form()](reference/llms-ctx.txt:258) with inputs for title, author, type, id.
  - Create “/search” route that reads query args, calls cache’s query API (aligned with CLI), returns:
    - Full page (non-HX) via [python.Titled()](reference/llms-ctx.txt:39).
    - Partial table (HX) for in-place swap using hx_target/hx_swap (see HTMX attributes in [reference/llms-ctx.txt:804](reference/llms-ctx.txt:804)).
- Tests:
  - Seed varied data; GET with HX-Request header returns filtered rows only; non-HX request returns full page.
- Tickets:
  - If a needed cache filter is missing, open a sub-issue, implement minimal filter, test, close.
- VCS:
  - Commit “006: Query filters + HTMX partial results; tests”.

Iteration 3 — Resource details drawer
- Implement:
  - “/detail?id=…” returns a panel with title, type, link, contact, doc_dir.
  - In results table, make title a link/button with hx_get to detail route, hx_target="#detail", hx_swap="innerHTML".
- Tests:
  - HX request returns only the details fragment; non-HX returns full [python.Titled()](reference/llms-ctx.txt:39).
- Tickets:
  - Note any link/contact formatting deltas; reference [tickets/004-link-contact-utilities.md](tickets/004-link-contact-utilities.md) and [tickets/005-doc-directory-detection.md](tickets/005-doc-directory-detection.md).
- VCS:
  - Commit “006: Details drawer via HTMX; tests”.

Iteration 4 — Minimal in-app scan trigger
- Implement:
  - Add “/scan” route with root, depth params (defaults match CLI). Call scan flow in [src/zinfo/core/scanner.py](src/zinfo/core/scanner.py) and persist via [src/zinfo/core/cache.py](src/zinfo/core/cache.py).
  - On success, return updated table or HTMX redirect via [python.HtmxResponseHeaders()](reference/llms-ctx.txt:382).
  - Provide small scan form on index.
- Tests:
  - Create temp directory with sample metadata; POST “/scan”, then GET “/” shows new entries.
- Tickets:
  - Record discrepancies with CLI options/signatures; close after alignment.
- VCS:
  - Commit “006: In-app scan (sync) with refresh; tests”.

Iteration 5 — Toasts and basic errors
- Implement:
  - Enable toasts with [python.setup_toasts()](reference/llms-ctx.txt:437); scan route adds success/error toasts and returns FT components.
  - Add 404 handler returning [python.Titled()](reference/llms-ctx.txt:39) error page.
- Tests:
  - Bad root path yields error toast; 404 returns expected content.
- Tickets:
  - Capture edge cases; close with fixes.
- VCS:
  - Commit “006: Toasts + 404 handler; tests”.

Iteration 6 — CLI entrypoint for UI
- Implement:
  - Add console_script entry in [pyproject.toml](pyproject.toml) (e.g., “zinfo-web”) pointing to a run() in [src/zinfo/ui/fh_ui.py](src/zinfo/ui/fh_ui.py) that calls [python.serve()](reference/llms-ctx.txt:71).
- Tests:
  - Import check for run symbol (no side effects unless invoked).
- Tickets:
  - Mark MVP complete with notes and follow-ups.
- VCS:
  - Commit “006: zinfo-web entrypoint; MVP complete; tests”.

Testing discipline
- Per iteration, add tests first or alongside changes using [python.TestClient()](reference/llms-ctx.txt:271).
- Run full test suite after each iteration to catch regressions.

Ticketing discipline (subagent usage)
- Create [tickets/006-fasthtml-ui.md](tickets/006-fasthtml-ui.md) with a checklist:
  - [ ] Iteration 0 Scaffolding
  - [ ] Iteration 1 Browse
  - [ ] Iteration 2 Filter
  - [ ] Iteration 3 Details
  - [ ] Iteration 4 Scan
  - [ ] Iteration 5 Toasts/Errors
  - [ ] Iteration 6 CLI entry
- For each discovered issue:
  - Log immediately under 006 with “Open” status, concise cause, impacted files, minimal fix.
  - After fix and green tests, mark “Closed” with one-line resolution and commit hash.
- Cross-link related enhancement tickets:
  - Link/contact utilities → [tickets/004-link-contact-utilities.md](tickets/004-link-contact-utilities.md).
  - Doc directory detection → [tickets/005-doc-directory-detection.md](tickets/005-doc-directory-detection.md).
  - HTML export (future) → [tickets/003-html-export.md](tickets/003-html-export.md).

Commit and push policy
- Only after tests pass and ticket updates are written:
  - git add -A
  - git commit -m "006: <iteration summary>; refs #006"
  - git push

Minimal UI surface (MVP)
- Index ("/"):
  - [python.Titled()](reference/llms-ctx.txt:39) “zInfo”.
  - Filter form (title, author, type, id) [python.Form()](reference/llms-ctx.txt:258)/[python.Input()](reference/llms-ctx.txt:260)/[python.Button()](reference/llms-ctx.txt:232) with HTMX submit updating results Div id="results".
  - Results table within Div id="results".
  - Details panel Div id="detail".
  - Scan form (root, depth) posting to “/scan”.
- Detail route ("/detail"): Returns panel (FT partial for HX; full page for non-HX).

Defer and avoid over-engineering
- No [python.APIRouter()](reference/llms-ctx.txt:393) until route count requires it.
- No WebSockets [reference/llms-ctx.txt:497](reference/llms-ctx.txt:497) or SSE [reference/llms-ctx.txt:473](reference/llms-ctx.txt:473) initially.
- No MonsterUI; Pico CSS defaults suffice for MVP.
- Synchronous scan; consider async/background later.
- Use only necessary changes; prefer single-file UI module.

Risks and mitigations
- Scan blocking: keep default depth small; advise CLI for large scans; later consider background/SSE.
- Cache path divergence: reuse the same DB location as CLI defaults to avoid multiple caches.
- Path/link rendering: MVP displays plain text; advanced formatting deferred to [tickets/004-link-contact-utilities.md](tickets/004-link-contact-utilities.md) and [tickets/005-doc-directory-detection.md](tickets/005-doc-directory-detection.md).
- Security/escaping: rely on FT escaping; avoid raw HTML unless using Safe/NotStr per [reference/llms-ctx.txt:316](reference/llms-ctx.txt:316).

Readiness
- Plan aligns with existing architecture ([src/zinfo/cli.py](src/zinfo/cli.py), [src/zinfo/core/*](src/zinfo/core/), [src/zinfo/ui/*](src/zinfo/ui/)).
- Each step is test-backed, with disciplined ticket updates and clean commits.
- No actions performed; execution will begin only upon approval.
