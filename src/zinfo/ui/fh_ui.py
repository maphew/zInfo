from fasthtml.common import *
from starlette.responses import HTMLResponse
from fasthtml.common import Toast, to_xml
from pathlib import Path
from zinfo.core.cache import Cache
from zinfo.core.scanner import ZinfoScanner
import os
import uvicorn
import click

app, rt = fast_app(htmx=True, pico=True)
setup_toasts(app)

@app.exception_handler(404)
def not_found(request, exc):
    content = to_xml(Titled("404 - Page Not Found", Container(H1("404"), P("The page you requested was not found."))))
    return HTMLResponse(content)

@rt("/")
def index():
    import logging
    logging.info("Rendering index: search_form defined first, then scan_form. Container order: scan_form, search_form")
    db_path = os.getenv("ZINFO_DB_PATH", "zinfo.db")
    cache = Cache(Path(db_path))
    resources = cache.get_all_resources()

    # Search form with labels
    search_form = Form(
        Fieldset(
            Legend("Search Resources"),
            Div(
                Label("Title", Input(name="title", placeholder="Search by title")),
                cls="form-group"
            ),
            Div(
                Label("Author", Input(name="author", placeholder="Search by author")),
                cls="form-group"
            ),
            Div(
                Label("Type", Input(name="type", placeholder="Search by type")),
                cls="form-group"
            ),
            Div(
                Label("ID", Input(name="id", placeholder="Search by ID")),
                cls="form-group"
            ),
            Button("Search", type="submit")
        ),
        hx_get="/search",
        hx_target="#results",
        hx_swap="innerHTML",
        cls="search-form"
    )
    # Compact scan form with horizontal layout
    scan_form = Form(
        Div(
            Label("Directory", Input(id="root", name="root", placeholder="~/", required=True, aria_describedby="root-help", cls="compact-input")),
            Label("Profile", Select(
                Option("Quick", value="quick"),
                Option("Standard", value="standard"),
                Option("Deep", value="deep"),
                Option("Custom", value="custom"),
                id="profile", name="profile", onchange="updateProfile()", cls="compact-select"
            )),
            Input(id="custom_depth", name="custom_depth", type="number", min="1", max="10", placeholder="Depth", style="display:none;", aria_describedby="depth-help", cls="compact-input"),
            Button("Scan", type="submit", id="scan-btn", disabled=True, hx_post="/scan", hx_target="#scan-status", hx_swap="innerHTML", cls="compact-btn"),
            cls="scan-form-row"
        ),
        Div(id="scan-status", cls="status-text"),
        Div(
            Div(id="scan-errors", cls="error-messages", style="display:none;"),
            Div(id="scan-success", cls="success-messages", style="display:none;"),
            id="scan-results", cls="scan-results"
        ),
        id="scan-form",
        onsubmit="return validateScanForm()",
        cls="compact-scan-form"
    )

    if not resources:
        results_div = Div(P("No cached resources found."), id="results")
    else:
        table_rows = [
            Tr(
                Td(A(resource.title, hx_get=f"/detail?id={resource.id}", hx_target="#detail", hx_swap="innerHTML")),
                Td(resource.metadata_type),
                Td(resource.id),
                Td(resource.link)
            ) for resource in resources
        ]

        table = Table(
            Thead(Tr(Th("Title"), Th("Type"), Th("ID"), Th("Path"))),
            Tbody(*table_rows)
        )
        results_div = Div(table, id="results")

    return Titled("zInfo",
        P("Scan directories for project metadata files and browse indexed resources"),
        Style("""
            .main-grid {
                display: grid;
                grid-template-areas:
                    "header"
                    "main";
                gap: 1rem;
                min-height: 100vh;
            }
            .header-area {
                grid-area: header;
                display: grid;
                grid-template-columns: 1fr auto;
                align-items: start;
                gap: 1rem;
                padding: 1rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .search-centered {
                justify-self: center;
                max-width: 600px;
            }
            .scan-right {
                justify-self: end;
            }
            .main-content {
                grid-area: main;
                padding: 1rem;
            }
            .search-form {
                background: white;
                padding: 1.5rem;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                border: 1px solid #e1e5e9;
            }
            .search-form fieldset {
                border: none;
                padding: 0;
                margin: 0;
            }
            .search-form .form-group {
                margin-bottom: 1rem;
            }
            .search-form label {
                display: block;
                font-weight: 600;
                color: #374151;
                margin-bottom: 0.5rem;
            }
            .search-form input {
                width: 100%;
                padding: 0.5rem;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                font-size: 1rem;
            }
            .search-form button {
                background: #3b82f6;
                color: white;
                padding: 0.75rem 1.5rem;
                border: none;
                border-radius: 4px;
                font-size: 1rem;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            .search-form button:hover {
                background: #2563eb;
            }
            .compact-scan-form {
                background: white;
                padding: 1rem;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                border: 1px solid #e1e5e9;
            }
            .scan-form-row {
                display: flex;
                gap: 0.5rem;
                align-items: end;
                flex-wrap: wrap;
            }
            .compact-input, .compact-select {
                padding: 0.5rem;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                font-size: 0.9rem;
            }
            .compact-input {
                flex: 1;
                min-width: 120px;
            }
            .compact-select {
                min-width: 100px;
            }
            .compact-btn {
                background: #10b981;
                color: white;
                padding: 0.5rem 1rem;
                border: none;
                border-radius: 4px;
                font-size: 0.9rem;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            .compact-btn:hover:not(:disabled) {
                background: #059669;
            }
            .compact-btn:disabled {
                background: #9ca3af;
                cursor: not-allowed;
            }
            .status-text {
                margin-top: 0.5rem;
                font-size: 0.9rem;
                color: #6b7280;
            }
            .results-card {
                background: white;
                padding: 1.5rem;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                border: 1px solid #e1e5e9;
                margin-bottom: 1rem;
            }
            .results-card table {
                width: 100%;
                border-collapse: collapse;
            }
            .results-card th, .results-card td {
                padding: 0.75rem;
                text-align: left;
                border-bottom: 1px solid #e5e7eb;
            }
            .results-card th {
                background: #f9fafb;
                font-weight: 600;
                color: #374151;
            }
            .results-card a {
                color: #3b82f6;
                text-decoration: none;
            }
            .results-card a:hover {
                text-decoration: underline;
            }
            .detail-card {
                background: white;
                padding: 1.5rem;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                border: 1px solid #e1e5e9;
                margin-top: 1rem;
            }
            .error-messages {
                color: #dc2626;
                background: #fef2f2;
                padding: 0.5rem;
                border-radius: 4px;
                border: 1px solid #fecaca;
            }
            .success-messages {
                color: #16a34a;
                background: #f0fdf4;
                padding: 0.5rem;
                border-radius: 4px;
                border: 1px solid #bbf7d0;
            }
            @media (max-width: 768px) {
                .main-grid {
                    grid-template-areas:
                        "header"
                        "main";
                }
                .header-area {
                    grid-template-columns: 1fr;
                    gap: 1rem;
                }
                .search-centered {
                    justify-self: stretch;
                }
                .scan-right {
                    justify-self: stretch;
                }
                .scan-form-row {
                    flex-direction: column;
                    align-items: stretch;
                }
                .compact-input, .compact-select {
                    width: 100%;
                }
            }
            @media (min-width: 769px) and (max-width: 1024px) {
                .header-area {
                    gap: 0.5rem;
                }
                .search-centered {
                    max-width: 500px;
                }
            }
        """),
        Div(
            Div(
                Div(search_form, cls="search-centered"),
                Div(scan_form, cls="scan-right"),
                cls="header-area"
            ),
            Div(
                Div(results_div, cls="results-card"),
                Div(id="detail", cls="detail-card"),
                cls="main-content"
            ),
            cls="main-grid"
        ),
        Script("""
            function updateProfile() {
                const profile = document.getElementById('profile').value;
                const customInput = document.getElementById('custom_depth');
                if (profile === 'custom') {
                    customInput.style.display = 'block';
                    customInput.required = true;
                } else {
                    customInput.style.display = 'none';
                    customInput.required = false;
                }
                validateScanForm();
            }

            function validateScanForm() {
                const root = document.getElementById('root').value.trim();
                const profile = document.getElementById('profile').value;
                const customDepth = document.getElementById('custom_depth');
                const btn = document.getElementById('scan-btn');
                const errors = document.getElementById('scan-errors');

                let isValid = root !== '';
                if (profile === 'custom') {
                    isValid = isValid && customDepth.value && parseInt(customDepth.value) >= 1;
                }

                btn.disabled = !isValid;

                if (!isValid) {
                    errors.textContent = 'Please fill in all required fields.';
                    errors.style.display = 'block';
                } else {
                    errors.style.display = 'none';
                }

                return isValid;
            }

            document.getElementById('root').addEventListener('input', validateScanForm);
            document.getElementById('custom_depth').addEventListener('input', validateScanForm);

            // Initial validation
            validateScanForm();
        """)
    )

@rt("/search")
def search(request, title: str = "", author: str = "", type: str = "", id: str = ""):
    db_path = os.getenv("ZINFO_DB_PATH", "zinfo.db")
    cache = Cache(Path(db_path))

    # Filter out empty strings
    search_params = {}
    if title.strip():
        search_params['title'] = title.strip()
    if author.strip():
        search_params['author'] = author.strip()
    if type.strip():
        search_params['metadata_type'] = type.strip()
    if id.strip():
        search_params['id'] = id.strip()

    resources = cache.search_resources(**search_params)

    if not resources:
        content = P("No matching resources found.")
    else:
        table_rows = [
            Tr(
                Td(A(resource.title, hx_get=f"/detail?id={resource.id}", hx_target="#detail", hx_swap="innerHTML")),
                Td(resource.metadata_type),
                Td(resource.id),
                Td(resource.link)
            ) for resource in resources
        ]

        table = Table(
            Thead(Tr(Th("Title"), Th("Type"), Th("ID"), Th("Path"))),
            Tbody(*table_rows)
        )
        content = table

    # Check if this is an HTMX request
    if request.headers.get("HX-Request"):
        return content
    else:
        return Titled("zInfo UI", Container(content))

@rt("/detail")
def detail(request, id: str):
    db_path = os.getenv("ZINFO_DB_PATH", "zinfo.db")
    cache = Cache(Path(db_path))
    resource = cache.get_resource(id)

    if not resource:
        content = P("Resource not found.")
    else:
        panel = Div(
            H3(resource.title),
            P(f"Type: {resource.metadata_type}"),
            P(f"Link: {resource.link}"),
            P(f"Contact: {resource.contact}"),
            P(f"Doc Dir: {resource.doc_dir}"),
            id="detail-panel"
        )
        content = panel

    if request.headers.get("HX-Request"):
        return content
    else:
        return Titled("zInfo UI - Detail", Container(content))

@rt("/scan", methods=["POST"])
def scan(root: str = ".", profile: str = "standard", custom_depth: Optional[int] = None):
    db_path = os.getenv("ZINFO_DB_PATH", "zinfo.db")
    cache = Cache(Path(db_path))

    # Determine depth based on profile
    if profile == "custom":
        depth = custom_depth if custom_depth is not None else 5
    else:
        depth_map = {"quick": 1, "standard": 3, "deep": 5}
        depth = depth_map.get(profile, 5)

    scanner = ZinfoScanner(Path(root), cache, max_depth=depth)
    result = scanner.scan()

    # Return updated table content
    resources = cache.get_all_resources()

    if not resources:
        content = P("No cached resources found.")
    else:
        table_rows = [
            Tr(
                Td(A(resource.title, hx_get=f"/detail?id={resource.id}", hx_target="#detail", hx_swap="innerHTML")),
                Td(resource.metadata_type),
                Td(resource.id),
                Td(resource.link)
            ) for resource in resources
        ]

        table = Table(
            Thead(Tr(Th("Title"), Th("Type"), Th("ID"), Th("Path"))),
            Tbody(*table_rows)
        )
        content = table

    # Add toast based on scan result
    if result.errors:
        toast_msg = f"Scan completed with {len(result.errors)} errors"
        toast_type = "error"
        status_msg = f"Scan completed with {len(result.errors)} errors, found {result.total_items_found} resources"
    else:
        toast_msg = f"Scan completed successfully, found {result.total_items_found} resources"
        toast_type = "success"
        status_msg = toast_msg

    status_div = Div(status_msg, id="scan-status")
    results_div = Div(content, id="results", hx_swap_oob="innerHTML")

    return status_div, results_div, Toast(toast_msg, typ=toast_type)

@click.command()
@click.option('--host', default='0.0.0.0', help='Host to bind the server to.')
@click.option('--port', default=5001, type=int, help='Port to bind the server to.')
@click.option('--reload/--no-reload', default=True, is_flag=True, help='Enable live reload')
def run(host, port, reload):
    """Start the zInfo FastHTML web UI server."""
    uvicorn.run('zinfo.ui.fh_ui:app', host=host, port=port, reload=reload)
