import click
import logging
from pathlib import Path

from zinfo.core.scanner import ZinfoScanner
from zinfo.core.cache import Cache
from zinfo.core.models import ScanResult


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
            extra_info = (
                f" | Authors: {item.extra.get('authors', 'N/A')}"
                if item.extra and item.extra.get("authors")
                else ""
            )
            click.echo(f"  - {item.title} ({item.link}){extra_info}")
    else:
        click.echo("No projects found.")


@main.command()
def query():
    """Query the index (stub - implement filtering later)."""
    click.echo("Query command: Not fully implemented yet.")
    click.echo("Load cache and query by title/author/date.")


if __name__ == "__main__":
    main()
