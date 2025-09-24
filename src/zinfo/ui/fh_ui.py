from fasthtml.common import *
from pathlib import Path
from zinfo.core.cache import Cache
from zinfo.core.scanner import ZinfoScanner
import os
import re
import logging
import time
from typing import Any, Tuple, List, Optional
import click

# Constants
# Scan profiles define preset depth levels for directory scanning
SCAN_PROFILES = {'quick', 'standard', 'deep', 'custom'}
# Depth mappings for each scan profile (quick=1 level, standard=3, deep=5)
PROFILE_DEPTHS = {"quick": 1, "standard": 3, "deep": 5}
# Default pagination settings
DEFAULT_PAGE = 1
DEFAULT_LIMIT = 50
# Maximum allowed limit for pagination to prevent excessive memory usage
MAX_LIMIT = 1000
# TTL for index page cache in seconds (30s balances freshness with performance)
INDEX_CACHE_TTL = 30
# TTL for search results cache in seconds (shorter due to dynamic queries)
SEARCH_CACHE_TTL = 10
# Default scan depth when no profile specified
DEFAULT_DEPTH = 5
# Maximum allowed scan depth to prevent runaway scans
MAX_DEPTH = 10
# Maximum length for search parameters to prevent abuse
MAX_SEARCH_PARAM_LENGTH = 100
# Regex pattern for validating search parameters (alphanumeric, spaces, hyphens, underscores, dots)
SEARCH_PARAM_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_.]*$')
# Default server binding settings
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 5001
# Default SQLite database path (can be overridden via ZINFO_DB_PATH env var)
DEFAULT_DB_PATH = "zinfo.db"



class TTLCache:
    """
    Simple in-memory cache with TTL (time-to-live) for performance optimization.

    This cache stores key-value pairs with automatic expiration based on time.
    Used to reduce database queries for frequently accessed data like index listings
    and search results. Thread-safety is not implemented as FastHTML is single-threaded.

    Design decision: Simple dict-based cache instead of external cache (Redis/memcached)
    to keep dependencies minimal and avoid complexity for a single-user application.
    """

    def __init__(self, ttl_seconds: int):
        """
        Initialize the cache with a TTL.

        Args:
            ttl_seconds: Time-to-live in seconds for cached items
        """
        self.ttl = ttl_seconds
        self.cache: dict[Any, Tuple[Any, float]] = {}

    def get(self, key: Any) -> Any:
        """
        Retrieve a value from cache if not expired.

        Args:
            key: Cache key to look up

        Returns:
            Cached value if found and not expired, None otherwise
        """
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                # Remove expired entry to prevent memory buildup
                del self.cache[key]
        return None

    def set(self, key: Any, value: Any) -> None:
        """
        Store a value in the cache with current timestamp.

        Args:
            key: Cache key
            value: Value to cache
        """
        self.cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cached entries. Used after data-modifying operations like scans."""
        self.cache.clear()


# Global cache instances
# Separate caches for index and search to allow different TTL policies
# Index cache has longer TTL since data changes less frequently
index_cache = TTLCache(INDEX_CACHE_TTL)  # Cache for main index page results
search_cache = TTLCache(SEARCH_CACHE_TTL)  # Cache for search results (shorter TTL due to dynamic queries)

def not_found(req, exc):
    return Titled("404 - Page Not Found", H1("404"), P("The page you requested was not found."))

def internal_error(req, exc):
    logging.error(f"Internal server error: {exc}", exc_info=True)
    return Titled("500 - Internal Server Error", H1("500"), P("An internal server error occurred. Please try again later."))

app, rt = fast_app(htmx=True, pico=True, exception_handlers={404: not_found, 500: internal_error})

# todo: remove this
# app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")


setup_toasts(app)

def validate_scan_params(root, profile, custom_depth):
    """
    Validate parameters for scan operations to prevent security issues and invalid inputs.

    Security: Restricts scan root to current working directory to prevent filesystem access
    outside the allowed scope. Prevents path traversal attacks.

    Args:
        root: Root directory path for scanning
        profile: Scan profile ('quick', 'standard', 'deep', 'custom')
        custom_depth: Custom depth when profile is 'custom'

    Raises:
        HTTPException: For invalid paths, profiles, or depths
    """
    # Validate root path - resolve to absolute path and check constraints
    try:
        root_path = Path(root).resolve()
    except Exception:
        raise HTTPException(400, "Invalid root path")
    cwd = Path.cwd()
    # Security check: prevent scanning outside current working directory
    if not str(root_path).startswith(str(cwd)):
        raise HTTPException(400, "Root path must be within current working directory")
    # Prevent path traversal attacks
    if '..' in root_path.parts:
        raise HTTPException(400, "Path traversal not allowed")

    # Validate profile against allowed set
    if profile not in SCAN_PROFILES:
        raise HTTPException(400, f"Invalid profile. Must be one of {SCAN_PROFILES}")

    # Validate custom_depth only when profile is custom
    if profile == 'custom':
        if custom_depth is None or not isinstance(custom_depth, int) or custom_depth <= 0:
            raise HTTPException(400, "custom_depth must be a positive integer when profile is custom")

def validate_search_params(query, search_title, search_shortname, search_client, search_team, search_author, search_type, search_dir_id):
    """
    Validate search parameters for length and character safety.

    Prevents abuse through overly long parameters and ensures only safe characters
    are used to avoid SQL injection or other issues.

    Args:
        query: Search query parameter
        search_title: Boolean flag for title field search
        search_shortname: Boolean flag for shortname field search
        search_client: Boolean flag for client field search
        search_team: Boolean flag for team field search
        search_author: Boolean flag for author field search
        search_type: Boolean flag for type field search
        search_dir_id: Boolean flag for dir_id field search

    Raises:
        HTTPException: For invalid parameter lengths or characters
    """
    # Validate query parameter
    if query:
        query = query.strip()
        if len(query) > MAX_SEARCH_PARAM_LENGTH:
            raise HTTPException(400, f"query must be {MAX_SEARCH_PARAM_LENGTH} characters or less")
        if not SEARCH_PARAM_PATTERN.match(query):
            raise HTTPException(400, "query contains invalid characters")

    # Validate boolean flags (should be 'true' or empty)
    boolean_params = {
        'search_title': search_title,
        'search_shortname': search_shortname,
        'search_client': search_client,
        'search_team': search_team,
        'search_author': search_author,
        'search_type': search_type,
        'search_dir_id': search_dir_id
    }

    for param, value in boolean_params.items():
        if value and value != 'true':
            raise HTTPException(400, f"{param} must be 'true' or empty")

def validate_detail_id(id_):
    """
    Validate resource ID parameter for detail view.

    Args:
        id_: Resource ID to validate

    Raises:
        HTTPException: If ID is empty or whitespace-only
    """
    if not id_ or not id_.strip():
        raise HTTPException(400, "id must be provided")

def validate_pagination_params(page: int, limit: int):
    """
    Validate pagination parameters to prevent invalid or abusive requests.

    Args:
        page: Page number (must be >= 1)
        limit: Items per page (must be between 1 and MAX_LIMIT)

    Raises:
        HTTPException: For invalid page or limit values
    """
    if page < 1:
        raise HTTPException(400, "page must be >= 1")
    if limit < 1 or limit > MAX_LIMIT:
        raise HTTPException(400, f"limit must be between 1 and {MAX_LIMIT}")

def render_pagination(current_page: int, limit: int, total_count: int, base_url: str, extra_params: str = ""):
    """
    Render HTMX-powered pagination controls for resource listings.

    Uses HTMX to dynamically load pages without full page refreshes.
    Only shows pagination if there are multiple pages.

    Args:
        current_page: Current page number
        limit: Items per page
        total_count: Total number of items
        base_url: Base URL for pagination links
        extra_params: Additional query parameters to preserve (e.g., search filters)

    Returns:
        HTML Div with pagination controls, or empty string if single page
    """
    total_pages = (total_count + limit - 1) // limit
    if total_pages <= 1:
        return ""

    prev_page = current_page - 1 if current_page > 1 else None
    next_page = current_page + 1 if current_page < total_pages else None

    pagination = Div()
    if prev_page:
        # HTMX GET request updates only the #results div
        pagination.append(Button("Previous", hx_get=f"{base_url}?page={prev_page}&limit={limit}{extra_params}", hx_target="#results", hx_swap="innerHTML"))
    pagination.append(Span(f"Page {current_page} of {total_pages}"))
    if next_page:
        pagination.append(Button("Next", hx_get=f"{base_url}?page={next_page}&limit={limit}{extra_params}", hx_target="#results", hx_swap="innerHTML"))
    return pagination

def build_resource_table(resources, total_count=None, page=DEFAULT_PAGE, limit=DEFAULT_LIMIT, base_url="/", extra_params="", no_resources_msg="No resources found."):
    """
    Build HTML table for displaying resources with optional pagination.

    Creates clickable titles that load details via HTMX, and includes pagination
    controls when there are multiple pages.

    Args:
        resources: List of ResourceMetadata objects to display
        total_count: Total count for pagination (None disables pagination)
        page: Current page number
        limit: Items per page
        base_url: Base URL for pagination links
        extra_params: Query parameters to preserve in pagination links
        no_resources_msg: Message to show when no resources found

    Returns:
        HTML table or message paragraph
    """
    if not resources:
        return P(no_resources_msg)

    # Build table rows with HTMX-powered detail links
    table_rows = [
        Tr(
            Td(A(resource.title, hx_get=f"/detail?id={resource.dir_id}", hx_target="#detail", hx_swap="innerHTML")),
            Td(resource.shortname),
            Td(resource.client),
            Td(resource.dir_id),
            Td(resource.location)
        ) for resource in resources
    ]

    table = Table(
        Thead(Tr(Th("Title"), Th("Shortname"), Th("Client"), Th("Dir ID"), Th("Location"))),
        Tbody(*table_rows)
    )

    # Add pagination only if we have total count and multiple pages
    if total_count is not None and total_count > limit:
        pagination = render_pagination(page, limit, total_count, base_url, extra_params)
        return Div(table, pagination)
    else:
        return table


@rt("/")
def index(page: int = DEFAULT_PAGE, limit: int = DEFAULT_LIMIT):
    """
    Main index page displaying paginated list of all resources.

    Renders the complete UI with search form, scan form, and resource table.
    Uses caching to improve performance for repeated requests.

    HTMX Behavior:
    - Full page load on initial request
    - Pagination handled by HTMX for dynamic updates

    Args:
        page: Page number for pagination (default: 1)
        limit: Number of items per page (default: 50, max: 1000)

    Returns:
        Complete HTML page with forms and resource listing
    """
    validate_pagination_params(page, limit)
    logging.info("Rendering index: search_form defined first, then scan_form. Container order: scan_form, search_form")
    db_path = os.getenv("ZINFO_DB_PATH", DEFAULT_DB_PATH)
    try:
        cache = Cache(Path(db_path))
        offset = (page - 1) * limit
        # Cache key includes pagination params for efficient lookups
        key = (page, limit)
        cached_result = index_cache.get(key)
        if cached_result:
            resources, total_count = cached_result
        else:
            # Fetch resources with pagination from database
            resources, total_count = cache.get_all_resources(limit=limit, offset=offset)
            # Cache the result to speed up subsequent identical requests
            index_cache.set(key, (resources, total_count))
    except Exception as e:
        logging.error(f"Error loading resources in index: {e}", exc_info=True)
        resources = []
        total_count = 0

    # Search form with single input and clickable field selection labels
    search_form = Form(
        Fieldset(
            Legend("Search Resources"),
            Input(name="query", placeholder="Enter search term...", required=True),
            Div(
                # Hidden checkboxes for form submission
                Input(type="checkbox", name="search_title", value="true", checked=True, id="search_title", style="display: none;"),
                Input(type="checkbox", name="search_shortname", value="true", checked=True, id="search_shortname", style="display: none;"),
                Input(type="checkbox", name="search_client", value="true", checked=True, id="search_client", style="display: none;"),
                Input(type="checkbox", name="search_team", value="true", checked=True, id="search_team", style="display: none;"),
                Input(type="checkbox", name="search_author", value="true", checked=True, id="search_author", style="display: none;"),
                Input(type="checkbox", name="search_type", value="true", checked=True, id="search_type", style="display: none;"),
                Input(type="checkbox", name="search_dir_id", value="true", checked=True, id="search_dir_id", style="display: none;"),
                # Clickable labels that control the hidden checkboxes
                # Note: Custom inline styles are used here to provide visual feedback for the clickable search field toggles.
                # This departs from idiomatic FastHTML's "exclusive use of Pico CSS without custom styling" because
                # the UX requires dynamic visual state changes (bold/color/background) that Pico doesn't provide out-of-the-box.
                # The JavaScript below handles the toggling of these styles and checkbox states.
                Div(
                    Label("Title", for_="search_title", style="font-weight: bold; color: #007acc; cursor: pointer; padding: 0.25rem 0.5rem; border-radius: 0.25rem; background-color: rgba(0, 122, 204, 0.1);"),
                    Label("Shortname", for_="search_shortname", style="font-weight: bold; color: #007acc; cursor: pointer; padding: 0.25rem 0.5rem; border-radius: 0.25rem; background-color: rgba(0, 122, 204, 0.1);"),
                    Label("Client", for_="search_client", style="font-weight: bold; color: #007acc; cursor: pointer; padding: 0.25rem 0.5rem; border-radius: 0.25rem; background-color: rgba(0, 122, 204, 0.1);"),
                    Label("Team", for_="search_team", style="font-weight: bold; color: #007acc; cursor: pointer; padding: 0.25rem 0.5rem; border-radius: 0.25rem; background-color: rgba(0, 122, 204, 0.1);"),
                    Label("Author", for_="search_author", style="font-weight: bold; color: #007acc; cursor: pointer; padding: 0.25rem 0.5rem; border-radius: 0.25rem; background-color: rgba(0, 122, 204, 0.1);"),
                    Label("Type", for_="search_type", style="font-weight: bold; color: #007acc; cursor: pointer; padding: 0.25rem 0.5rem; border-radius: 0.25rem; background-color: rgba(0, 122, 204, 0.1);"),
                    Label("Dir ID", for_="search_dir_id", style="font-weight: bold; color: #007acc; cursor: pointer; padding: 0.25rem 0.5rem; border-radius: 0.25rem; background-color: rgba(0, 122, 204, 0.1);"),
                    style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 1rem 0;"
                ),
                style="display: flex; flex-wrap: wrap; gap: 1rem; margin: 1rem 0;"
            ),
            Button("Search", type="submit")
        ),
        hx_get="/search",
        hx_target="#results",
        hx_swap="innerHTML"
    )
    # Scan form
    scan_form = Form(
        Fieldset(
            Legend("Scan Directory"),
            Label("Directory", Input(id="root", name="root", placeholder="~/", required=True, aria_describedby="root-help")),
            Label("Profile", Select(
                Option("Quick", value="quick"),
                Option("Standard", value="standard"),
                Option("Deep", value="deep"),
                Option("Custom", value="custom"),
                id="profile", name="profile", onchange="updateProfile()"
            )),
            Input(id="custom_depth", name="custom_depth", type="number", min="1", max=str(MAX_DEPTH), placeholder="Depth", aria_describedby="depth-help"),
            Button("Scan", type="submit", id="scan-btn", disabled=False, hx_post="/scan", hx_target="#scan-status", hx_swap="innerHTML"),
        ),
        Div(id="scan-status"),
        Div(
            Div(id="validation-errors"),
            Div(id="scan-errors"),
            Div(id="scan-success"),
            id="scan-results"
        ),
        id="scan-form",
        onsubmit="return validateScanForm()"
    )

    table_content = build_resource_table(resources, total_count, page, limit, "/", "", "No cached resources found.")
    results_div = Div(table_content, id="results")

    return Titled(
        "zInfo",
        P("Scan directories for project metadata files and browse indexed resources"),
        Grid(search_form, scan_form),
        Card(results_div),
        Card(Div(id="detail")),
        # JavaScript for clickable field selection labels
        Script("""
            function toggleFieldLabel(label, checkboxId) {
                const checkbox = document.getElementById(checkboxId);
                const isChecked = checkbox.checked;

                if (isChecked) {
                    // Disable field - muted styling
                    label.style.fontWeight = 'normal';
                    label.style.color = '#666';
                    label.style.backgroundColor = 'transparent';
                    checkbox.checked = false;
                } else {
                    // Enable field - bold/bright styling
                    label.style.fontWeight = 'bold';
                    label.style.color = '#007acc';
                    label.style.backgroundColor = 'rgba(0, 122, 204, 0.1)';
                    checkbox.checked = true;
                }
            }

            // Add click handlers to all field labels
            document.addEventListener('DOMContentLoaded', function() {
                const fieldLabels = [
                    { label: 'Title', checkbox: 'search_title' },
                    { label: 'Shortname', checkbox: 'search_shortname' },
                    { label: 'Client', checkbox: 'search_client' },
                    { label: 'Team', checkbox: 'search_team' },
                    { label: 'Author', checkbox: 'search_author' },
                    { label: 'Type', checkbox: 'search_type' },
                    { label: 'Dir ID', checkbox: 'search_dir_id' }
                ];

                fieldLabels.forEach(field => {
                    const labelElement = Array.from(document.querySelectorAll('label')).find(el =>
                        el.textContent.trim() === field.label
                    );
                    if (labelElement) {
                        labelElement.addEventListener('click', function(e) {
                            e.preventDefault();
                            toggleFieldLabel(this, field.checkbox);
                        });
                    }
                });
            });
        """)
    )

@rt("/search")
def search(request, query: str = "", search_title: str = "", search_shortname: str = "", search_client: str = "", search_team: str = "", search_author: str = "", search_type: str = "", search_dir_id: str = "", page: int = DEFAULT_PAGE, limit: int = DEFAULT_LIMIT):
    """
    Search resources using a single query term with field selection checkboxes.

    Filters resources based on provided search criteria. Uses caching to improve
    performance for repeated searches with same parameters.

    HTMX Behavior:
    - Returns only table content for dynamic updates when requested via HTMX
    - Returns full page for direct browser navigation

    Args:
        request: FastHTML request object (used to detect HTMX requests)
        query: Search term to look for
        search_title: Boolean flag to search in title field
        search_shortname: Boolean flag to search in shortname field
        search_client: Boolean flag to search in client field
        search_team: Boolean flag to search in team field
        search_author: Boolean flag to search in author field
        search_type: Boolean flag to search in type field
        search_dir_id: Boolean flag to search in dir_id field
        page: Page number for pagination
        limit: Number of results per page

    Returns:
        HTML content - table fragment for HTMX, full page otherwise
    """
    validate_search_params(query, search_title, search_shortname, search_client, search_team, search_author, search_type, search_dir_id)
    validate_pagination_params(page, limit)
    db_path = os.getenv("ZINFO_DB_PATH", DEFAULT_DB_PATH)
    try:
        cache = Cache(Path(db_path))

        # Check if any search fields are enabled
        enabled_fields = [search_title, search_shortname, search_client, search_team, search_author, search_type, search_dir_id]
        any_field_enabled = any(field == "true" for field in enabled_fields)

        # Build search parameters dict based on enabled fields
        search_params = {}
        if query.strip() and any_field_enabled:
            search_term = query.strip()

            # Only add fields to search if their corresponding checkbox is enabled
            if search_title == "true":
                search_params['title'] = search_term
            if search_shortname == "true":
                search_params['shortname'] = search_term
            if search_client == "true":
                search_params['client'] = search_term
            if search_team == "true":
                search_params['team'] = search_term
            if search_author == "true":
                search_params['author'] = search_term
            if search_type == "true":
                search_params['metadata_type'] = search_term
            if search_dir_id == "true":
                search_params['dir_id'] = search_term

        offset = (page - 1) * limit
        # Create cache key from sorted params to ensure consistent hashing
        search_key = tuple(sorted(search_params.items()))
        key = (search_key, page, limit)
        cached_result = search_cache.get(key)
        if cached_result:
            resources, total_count = cached_result
        else:
            # Perform database search with filters and pagination
            resources, total_count = cache.search_resources(limit=limit, offset=offset, **search_params)
            # Cache results for faster subsequent identical searches
            search_cache.set(key, (resources, total_count))
    except Exception as e:
        logging.error(f"Error searching resources: {e}", exc_info=True)
        content = P("An error occurred while searching. Please try again.")
    else:
        # Handle edge case where no search fields are enabled
        if query.strip() and not any_field_enabled:
            content = P("Please select at least one field to search in.")
        else:
            # Preserve search parameters in pagination links
            extra_params = f"&query={query}&search_title={search_title}&search_shortname={search_shortname}&search_client={search_client}&search_team={search_team}&search_author={search_author}&search_type={search_type}&search_dir_id={search_dir_id}"
            content = build_resource_table(resources, total_count, page, limit, "/search", extra_params, "No matching resources found.")

    # HTMX requests get only the content fragment, direct requests get full page
    if request.headers.get("HX-Request"):
        return content
    else:
        return Titled("zInfo UI", content)

@rt("/detail")
def detail(request, id: str):
    """
    Display detailed information for a specific resource.

    Retrieves and displays full metadata for a resource by ID.
    Used by HTMX links in resource tables.

    HTMX Behavior:
    - Returns detail panel fragment for dynamic updates
    - Returns full page for direct navigation

    Args:
        request: FastHTML request object (used to detect HTMX requests)
        id: Resource ID to retrieve details for

    Returns:
        HTML content - detail panel for HTMX, full page otherwise
    """
    validate_detail_id(id)
    db_path = os.getenv("ZINFO_DB_PATH", DEFAULT_DB_PATH)
    try:
        cache = Cache(Path(db_path))
        resource = cache.get_resource(id)
    except Exception as e:
        logging.error(f"Error retrieving resource {id}: {e}", exc_info=True)
        content = P("An error occurred while retrieving the resource.")
    else:
        if not resource:
            content = P("Resource not found.")
        else:
            # Display comprehensive resource metadata
            panel = Div(
                H3(resource.title),
                # Required fields prominently
                Fieldset(
                    Legend("Required Information"),
                    P(Strong("Shortname: "), resource.shortname),
                    P(Strong("Summary: "), resource.summary),
                    P(Strong("Client: "), resource.client),
                    P(Strong("Team: "), "; ".join(resource.team.split(";")) if resource.team else "None"),
                    P(Strong("Contact Email: "), resource.contact_email),
                    P(Strong("Location: "), resource.location)
                ),
                # System fields
                Fieldset(
                    Legend("System Information"),
                    P(Strong("Dir ID: "), resource.dir_id),
                    P(Strong("Dir Path: "), resource.dir_path),
                    P(Strong("Type: "), resource.metadata_type),
                    P(Strong("Last Modified: "), resource.last_modified.isoformat() if resource.last_modified else "Unknown"),
                    P(Strong("Last Indexed: "), resource.last_indexed.isoformat() if resource.last_indexed else "Unknown")
                ),
                # Optional fields organized
                resource.optional_fields and Fieldset(
                    Legend("Optional Information"),
                    *[P(Strong(f"{k.title()}: "), v) for k, v in resource.optional_fields.items()]
                ),
                # Custom fields separately
                resource.custom_fields and Fieldset(
                    Legend("Custom Fields"),
                    *[P(Strong(f"{k.title()}: "), v) for k, v in resource.custom_fields.items()]
                ),
                id="detail-panel"
            )
            content = panel

    # HTMX requests update the #detail div, direct requests show full page
    if request.headers.get("HX-Request"):
        return content
    else:
        return Titled("zInfo UI - Detail", content)

@rt("/scan", methods=["POST"])
def scan(root: str = ".", profile: str = "standard", custom_depth: Optional[int] = None):
    """
    Perform directory scan for project metadata files.

    Scans the specified directory tree for zinfo.txt files, extracts metadata,
    and updates the database. Invalidates caches to ensure fresh data display.

    HTMX Behavior:
    - Updates multiple page elements: status, results table, and shows toast
    - Uses hx_swap_oob for out-of-band updates to multiple targets

    Args:
        root: Root directory to scan (must be within current working directory)
        profile: Scan profile determining depth ('quick', 'standard', 'deep', 'custom')
        custom_depth: Custom scan depth when profile is 'custom'

    Returns:
        Tuple of (status_div, results_div, toast) for HTMX multi-target updates
    """
    validate_scan_params(root, profile, custom_depth)
    db_path = os.getenv("ZINFO_DB_PATH", DEFAULT_DB_PATH)
    try:
        cache = Cache(Path(db_path))

        # Map profile to actual depth value
        if profile == "custom":
            depth = custom_depth if custom_depth is not None else DEFAULT_DEPTH
        else:
            depth = PROFILE_DEPTHS.get(profile, DEFAULT_DEPTH)

        # Perform the scan operation
        scanner = ZinfoScanner(Path(root), cache, max_depth=depth)
        result = scanner.scan()

        # Clear caches since data has changed - ensures users see updated results immediately
        index_cache.clear()
        search_cache.clear()

        # Fetch updated resource list for display
        resources, _ = cache.get_all_resources()
    except Exception as e:
        logging.error(f"Error during scan: {e}", exc_info=True)
        status_div = Div("Scan failed due to an error.", id="scan-status")
        return status_div, Toast("Scan failed", typ="error")

    # Build updated results table
    content = build_resource_table(resources, no_resources_msg="No cached resources found.")

    # Generate appropriate messages based on scan outcome
    if result.errors:
        toast_msg = f"Scan completed with {len(result.errors)} errors"
        toast_type = "error"
        status_msg = f"Scan completed with {len(result.errors)} errors, found {result.total_items_found} resources"

        # Display validation errors with guidance
        error_details = []
        for error in result.errors:
            if "missing required field" in error.lower():
                error_details.append(Div(
                    H4("Missing Required Fields"),
                    P("The following zinfo.txt files are missing required fields:"),
                    Ul(*[Li(err) for err in result.errors if "missing required field" in err.lower()]),
                    P("Required fields are: title, shortname, summary, client, team, contact_email, location"),
                    P("Please add these fields to your zinfo.txt files and rescan.")
                ))
            else:
                error_details.append(P(error))

        validation_errors_div = Div(
            H3("Scan Validation Errors"),
            *error_details,
            id="validation-errors"
        )
    else:
        toast_msg = f"Scan completed successfully, found {result.total_items_found} resources"
        toast_type = "success"
        status_msg = toast_msg
        validation_errors_div = Div(id="validation-errors")  # Empty when no errors

    # Prepare HTMX response elements
    status_div = Div(status_msg, id="scan-status")
    # hx_swap_oob allows updating #results div even though it's not the main target
    results_div = Div(content, id="results", hx_swap_oob="innerHTML")
    # Update validation errors display
    validation_div = Div(validation_errors_div, id="validation-errors", hx_swap_oob="innerHTML")

    return status_div, results_div, validation_div, Toast(toast_msg, typ=toast_type)

def run_server(host=DEFAULT_HOST, port=DEFAULT_PORT, reload=True):
    """Start the zInfo FastHTML web UI server."""
    serve('zinfo.ui.fh_ui', app, host=host, port=port, reload=reload)

@click.command()
@click.option("--host", default=DEFAULT_HOST, help="Host to bind to")
@click.option("--port", type=int, default=DEFAULT_PORT, help="Port to bind to")
@click.option("--reload", is_flag=True, default=True, help="Enable live reload")
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
def run(host, port, reload, verbose):
    """Start the zInfo FastHTML web UI server."""
    if verbose:
        logging.basicConfig(level=logging.INFO)
    run_server(host=host, port=port, reload=reload)
