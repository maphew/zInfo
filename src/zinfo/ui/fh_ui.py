from fasthtml.common import *
from starlette.responses import HTMLResponse
from fasthtml.common import Toast, to_xml
from pathlib import Path
from zinfo.core.cache import Cache
from zinfo.core.scanner import ZinfoScanner
import os

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

    scan_form = Form(
        Input(name="root", placeholder="Root directory", value="."),
        Input(name="depth", type="number", value=5),
        Button("Scan", type="submit"),
        hx_post="/scan",
        hx_target="#results",
        hx_swap="innerHTML"
    )

    form = Form(
        Input(name="title", placeholder="Title"),
        Input(name="author", placeholder="Author"),
        Input(name="type", placeholder="Type"),
        Input(name="id", placeholder="ID"),
        Button("Search", type="submit"),
        hx_get="/search",
        hx_target="#results",
        hx_swap="innerHTML"
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

    return Titled("zInfo UI", Container(scan_form, form, results_div, Div(id="detail")))

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
def scan(root: str = ".", depth: int = 5):
    db_path = os.getenv("ZINFO_DB_PATH", "zinfo.db")
    cache = Cache(Path(db_path))

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

def run():
    serve()
