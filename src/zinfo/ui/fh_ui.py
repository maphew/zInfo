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
    db_path = os.getenv("ZINFO_DB_PATH", "zinfo.db")
    cache = Cache(Path(db_path))
    resources = cache.get_all_resources()

    # Scan form with redesigned inputs
    scan_form = Form(
        Fieldset(
            Legend("Scan Configuration"),
            Div(
                Label("Target Directory", Input(id="root", name="root", placeholder="~/", required=True, aria_describedby="root-help")),
                Small("Enter the root directory to scan. Examples: . (current), /home/projects, C:\\Projects", id="root-help"),
                cls="form-group"
            ),
            Div(
                Label("Scan Profile", Select(
                    Option("Quick", value="quick"),
                    Option("Standard", value="standard"),
                    Option("Deep", value="deep"),
                    Option("Custom", value="custom"),
                    id="profile", name="profile", onchange="updateProfile()"
                )),
                Small("Quick: 1 level deep, Standard: 3 levels, Deep: 5 levels, Custom: specify depth", id="profile-help"),
                cls="form-group"
            ),
            Div(
                Label("Custom Depth", Input(id="custom_depth", name="custom_depth", type="number", min="1", max="10", style="display:none;", aria_describedby="depth-help"),
                Small("Specify scan depth (1-10 levels)", id="depth-help"),
                cls="form-group", id="custom-depth-group",
                style="display:none;"
            ),
        ),
        Button("Start Scan", type="submit", id="scan-btn", disabled=True, hx_post="/scan", hx_target="#results", hx_swap="innerHTML"),
        Small("Button enabled when target directory and scan profile have been set", id="scan-help"),
        Div(
            Div(
                id="scan-errors", cls="error-messages", style="display:none;"
            ),
            Div(
                id="scan-success", cls="success-messages", style="display:none;"
            ),
            id="scan-results",
            cls="scan-results"
        ),
        cls="form-group",
        id="scan-form",
        onsubmit="return validateScanForm()"
    ))
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
        Container(
            scan_form,
            search_form,
            results_div,
            Div(id="detail"),
            Script("""
                function updateProfile() {
                    const profile = document.getElementById('profile').value;
                    const customGroup = document.getElementById('custom-depth-group');
                    const customInput = document.getElementById('custom_depth');
                    if (profile === 'custom') {
                        customGroup.style.display = 'block';
                        customInput.style.display = 'block';
                        customInput.required = true;
                    } else {
                        customGroup.style.display = 'none';
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
    else:
        toast_msg = f"Scan completed successfully, found {result.total_items_found} resources"
        toast_type = "success"

    return content, Toast(toast_msg, typ=toast_type)

@click.command()
@click.option('--host', default='0.0.0.0', help='Host to bind the server to.')
@click.option('--port', default=5001, type=int, help='Port to bind the server to.')
@click.option('--reload/--no-reload', default=True, is_flag=True, help='Enable live reload')
def run(host, port, reload):
    """Start the zInfo FastHTML web UI server."""
    uvicorn.run('zinfo.ui.fh_ui:app', host=host, port=port, reload=reload)
