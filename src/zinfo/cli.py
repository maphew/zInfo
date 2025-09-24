import click
import logging
import json
from pathlib import Path
from typing import Optional, List

from zinfo.core.scanner import ZinfoScanner
from zinfo.core.cache import Cache, parse_date
from zinfo.core.models import ScanResult, ResourceMetadata


@click.group()
def main():
    """Zinfo: Interface for interesting folders in the filesystem."""
    pass


@main.command()
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path("."),
    help="Root directory to scan.",
)
@click.option("--depth", type=int, default=5, help="Maximum scan depth.")
@click.option(
    "--cache-db",
    type=click.Path(path_type=Path),
    default=Path("zinfo.db"),
    help="Path to SQLite cache database.",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging.")
def scan(root: Path, depth: int, cache_db: Path, verbose: bool):
    """Scan for zinfo.txt metadata files and build/update index."""
    if verbose:
        logging.basicConfig(level=logging.INFO)
        logging.info(f"Scanning {root} to depth {depth}, cache: {cache_db}")

    cache = Cache(cache_db)
    scanner = ZinfoScanner(root, cache, max_depth=depth)
    result: ScanResult = scanner.scan()

    click.echo(
        f"Scan completed in {(result.end_time - result.start_time).total_seconds():.2f}s:\n"
        f"  - {result.total_items_found} projects found\n"
        f"  - {result.total_dirs_scanned} directories scanned"
    )

    if result.errors:
        click.echo(f"\nErrors ({len(result.errors)}):")
        for error in result.errors:
            click.echo(f"  - {error}")

    if result.items:
        click.echo("\nFound projects:")
        for item in result.items:
            team_info = f" | Team: {item.team}" if item.team else ""
            click.echo(f"  - {item.title} ({item.location}){team_info}")
    else:
        click.echo("No projects found.")


@main.command()
@click.option(
    "--cache-db",
    type=click.Path(path_type=Path),
    default=Path("zinfo.db"),
    help="Path to SQLite cache database.",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging.")
@click.option("--title", "-t", help="Filter by title (partial match).")
@click.option("--author", "-a", help="Filter by author (searches in team field).")
@click.option("--shortname", "-s", help="Filter by shortname (partial match).")
@click.option("--client", "-C", help="Filter by client (partial match).")
@click.option("--team", "-m", help="Filter by team (partial match).")
@click.option("--dir-id", "-d", help="Filter by dir_id (partial match).")
@click.option("--type", "-T", "metadata_type", help="Filter by metadata type.")
@click.option("--limit", "-l", type=int, help="Limit number of results.")
@click.option("--format", "-f", type=click.Choice(["table", "detailed", "json"]),
              default="table", help="Output format.")
@click.option("--all", "-A", "show_all", is_flag=True,
              help="Show all resources (ignore other filters).")
@click.option("--count", "-c", is_flag=True, help="Show only count of matching resources.")
@click.option("--id", "-i", help="Get specific resource by ID.")
@click.option("--after", help="Filter resources after this date (YYYY, YYYY-MM, or YYYY-MM-DD).")
@click.option("--before", help="Filter resources before this date (YYYY, YYYY-MM, or YYYY-MM-DD).")
@click.option("--date-field", default="created",
              help="Date field to filter on (created, updated, last_modified, last_indexed).")
def query(
    cache_db: Path,
    verbose: bool,
    title: Optional[str],
    author: Optional[str],
    shortname: Optional[str],
    client: Optional[str],
    team: Optional[str],
    dir_id: Optional[str],
    metadata_type: Optional[str],
    limit: Optional[int],
    format: str,
    show_all: bool,
    count: bool,
    id: Optional[str],
    after: Optional[str],
    before: Optional[str],
    date_field: str
):
    """Query the index with flexible filtering and display options."""
    if verbose:
        logging.basicConfig(level=logging.INFO)
        logging.info(f"Querying cache: {cache_db}")

    cache = Cache(cache_db)

    # Check if database exists and has data
    if not cache_db.exists():
        click.echo(f"Error: Cache database '{cache_db}' does not exist.")
        click.echo("Run 'zinfo scan' first to create the database.")
        return

    total_count = cache.get_resource_count()
    if total_count == 0:
        click.echo("No resources found in cache. Run 'zinfo scan' first.")
        return

    # Parse date parameters
    after_date = parse_date(after) if after else None
    before_date = parse_date(before) if before else None

    if after and not after_date:
        click.echo(f"Error: Invalid date format for --after: {after}")
        click.echo("Use formats like: 2024, 2024-01, 2024-01-15")
        return

    if before and not before_date:
        click.echo(f"Error: Invalid date format for --before: {before}")
        click.echo("Use formats like: 2024, 2024-01, 2024-01-15")
        return

    # Handle specific ID query
    if id:
        resource = cache.get_resource(id)
        if resource:
            _display_resources([resource], format, verbose)
        else:
            click.echo(f"No resource found with ID: {id}")
        return

    # Handle count-only query
    if count:
        if show_all:
            click.echo(f"Total resources: {total_count}")
        else:
            # Count with filters
            results, _ = cache.search_resources(
                title=title,
                author=author,
                shortname=shortname,
                client=client,
                team=team,
                metadata_type=metadata_type,
                dir_id=dir_id,
                limit=None
            )
            click.echo(f"Matching resources: {len(results)}")
        return

    # Build search criteria
    if show_all:
        title = author = metadata_type = None
        limit = limit or 50  # Default limit for "all" to avoid overwhelming output

    results, _ = cache.search_resources(
        title=title,
        author=author,
        shortname=shortname,
        client=client,
        team=team,
        metadata_type=metadata_type,
        dir_id=dir_id,
        limit=limit,
        after_date=after_date,
        before_date=before_date,
        date_field=date_field
    )

    if not results:
        if show_all:
            click.echo("No resources found in cache.")
        else:
            click.echo("No resources match the specified criteria.")
        return

    _display_resources(results, format, verbose)


def _display_resources(resources: List[ResourceMetadata], format: str, verbose: bool):
    """Display resources in the specified format."""
    if format == "json":
        # JSON output
        data = []
        for resource in resources:
            resource_dict = {
                "dir_id": resource.dir_id,
                "dir_path": resource.dir_path,
                "title": resource.title,
                "shortname": resource.shortname,
                "summary": resource.summary,
                "client": resource.client,
                "team": resource.team,
                "contact_email": resource.contact_email,
                "location": resource.location,
                "metadata_type": resource.metadata_type,
                "last_modified": resource.last_modified.isoformat() if resource.last_modified else None,
                "last_indexed": resource.last_indexed.isoformat() if resource.last_indexed else None,
                "optional_fields": resource.optional_fields,
                "custom_fields": resource.custom_fields
            }
            data.append(resource_dict)
        click.echo(json.dumps(data, indent=2))

    elif format == "detailed":
        # Detailed text output
        for i, resource in enumerate(resources, 1):
            click.echo(f"\n--- Resource {i} ---")

            # Required fields
            click.echo("Required Fields:")
            click.echo(f"  Dir ID: {resource.dir_id}")
            click.echo(f"  Title: {resource.title}")
            click.echo(f"  Shortname: {resource.shortname}")
            click.echo(f"  Summary: {resource.summary}")
            click.echo(f"  Client: {resource.client}")
            click.echo(f"  Team: {resource.team}")
            click.echo(f"  Contact Email: {resource.contact_email}")
            click.echo(f"  Location: {resource.location}")

            # System fields
            click.echo("System Fields:")
            click.echo(f"  Dir Path: {resource.dir_path}")
            click.echo(f"  Type: {resource.metadata_type}")
            if resource.last_modified:
                click.echo(f"  Last Modified: {resource.last_modified}")
            if resource.last_indexed:
                click.echo(f"  Last Indexed: {resource.last_indexed}")

            # Optional fields
            if resource.optional_fields:
                click.echo("Optional Fields:")
                for key, value in resource.optional_fields.items():
                    click.echo(f"  {key}: {value}")

            # Custom fields
            if resource.custom_fields:
                click.echo("Custom Fields:")
                for key, value in resource.custom_fields.items():
                    click.echo(f"  {key}: {value}")

    else:  # table format (default)
        # Table header
        click.echo("Dir ID      Title                          Shortname    Client              Location")
        click.echo("-" * 100)

        # Table rows
        for resource in resources:
            dir_id_short = resource.dir_id[:10] + "..." if len(resource.dir_id) > 13 else resource.dir_id
            title_short = resource.title[:30] + "..." if len(resource.title) > 33 else resource.title
            shortname_short = resource.shortname[:12] + "..." if len(resource.shortname) > 15 else resource.shortname
            client_short = resource.client[:18] + "..." if len(resource.client) > 21 else resource.client
            location_short = resource.location[:20] + "..." if len(resource.location) > 23 else resource.location

            # Use string formatting for table columns
            row = "{:<13} {:<33} {:<15} {:<21} {:<23}".format(
                dir_id_short, title_short, shortname_short, client_short, location_short
            )
            click.echo(row)

    if verbose:
        click.echo(f"\nDisplayed {len(resources)} resource(s)")


if __name__ == "__main__":
    main()
