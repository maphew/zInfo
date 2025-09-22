from fasthtml.common import *
from pathlib import Path
from zinfo.core.cache import Cache
import os

app, rt = fast_app(htmx=True, pico=True)

@rt("/")
def index():
    db_path = os.getenv("ZINFO_DB_PATH", "zinfo.db")
    cache = Cache(Path(db_path))
    resources = cache.get_all_resources()

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
                Td(resource.title),
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

    return Titled("zInfo UI", Container(form, results_div))

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
                Td(resource.title),
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

def run():
    serve()
