"""Main application layer for zinfo GUI.

This module contains the main application logic that coordinates between
the UI layer and the core zinfo functionality.
"""

import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from zinfo.core.scanner import ZinfoScanner
from zinfo.core.cache import Cache
from zinfo.core.models import ResourceMetadata, ScanResult

from . import AbstractUI, ScanConfig, QueryFilter, ScanProgressCallback, ProgressCallback

logger = logging.getLogger(__name__)


class ZinfoApp:
    """Main application controller for zinfo GUI."""

    def __init__(self, ui: AbstractUI):
        """Initialize the application with a UI implementation.

        Args:
            ui: The UI implementation to use
        """
        self.ui = ui
        self.cache: Optional[Cache] = None
        self.scanner: Optional[ZinfoScanner] = None
        self._scan_in_progress = False
        self._query_in_progress = False

        # Set up progress callbacks
        self.ui.set_scan_progress_callback(self._on_scan_progress)
        self.ui.set_query_progress_callback(self._on_query_progress)

    def initialize_cache(self, cache_path: Optional[Path] = None) -> None:
        """Initialize the cache with the specified path.

        Args:
            cache_path: Path to the cache database. If None, uses default.
        """
        if cache_path is None:
            cache_path = Path("zinfo.db")

        self.cache = Cache(cache_path)
        logger.info(f"Initialized cache at {cache_path}")

    def get_cache_path(self) -> Optional[Path]:
        """Get the current cache path."""
        return self.cache.db_path if self.cache else None

    def run_scan(self, config: ScanConfig) -> bool:
        """Run a scan with the given configuration.

        Args:
            config: Scan configuration

        Returns:
            True if scan completed successfully, False otherwise
        """
        if self._scan_in_progress:
            logger.warning("Scan already in progress")
            return False

        try:
            self._scan_in_progress = True

            # Initialize cache if not already done
            if self.cache is None:
                self.initialize_cache(config.cache_path)

            # Create scanner
            self.scanner = ZinfoScanner(
                base_dir=config.root_path,
                cache=self.cache,
                max_depth=config.max_depth
            )

            # Show progress dialog
            progress_dialog = self.ui.show_progress_dialog(
                "Scanning", f"Scanning {config.root_path}..."
            )

            try:
                # Run scan
                result = self.scanner.scan()

                # Update progress dialog
                progress_dialog.update_progress(100, 100, "Scan completed")

                # Show results
                if result.errors:
                    error_msg = f"Scan completed with {len(result.errors)} errors:\n"
                    error_msg += "\n".join(f"• {error}" for error in result.errors[:5])
                    if len(result.errors) > 5:
                        error_msg += f"\n... and {len(result.errors) - 5} more errors"
                    self.ui.show_error_message("Scan Completed with Errors", error_msg)

                success_msg = f"Scan completed successfully!\n"
                success_msg += f"Found {result.total_items_found} projects in {result.total_dirs_scanned} directories"
                self.ui.show_info_message("Scan Completed", success_msg)

                return True

            finally:
                progress_dialog.close()
                self._scan_in_progress = False

        except Exception as e:
            logger.error(f"Error during scan: {e}")
            self.ui.show_error_message("Scan Error", f"An error occurred during scanning:\n{str(e)}")
            self._scan_in_progress = False
            return False

    def run_query(self, filter_config: QueryFilter) -> List[ResourceMetadata]:
        """Run a query with the given filter configuration.

        Args:
            filter_config: Query filter configuration

        Returns:
            List of matching resources
        """
        if self._query_in_progress:
            logger.warning("Query already in progress")
            return []

        if self.cache is None:
            self.ui.show_error_message("No Cache", "No cache available. Please run a scan first.")
            return []

        try:
            self._query_in_progress = True

            # Show progress dialog
            progress_dialog = self.ui.show_progress_dialog("Querying", "Searching resources...")

            try:
                # Parse dates
                after_date = None
                before_date = None

                if filter_config.after_date:
                    from zinfo.core.cache import parse_date
                    after_date = parse_date(filter_config.after_date)

                if filter_config.before_date:
                    from zinfo.core.cache import parse_date
                    before_date = parse_date(filter_config.before_date)

                # Run search
                results = self.cache.search_resources(
                    title=filter_config.title,
                    author=filter_config.author,
                    metadata_type=filter_config.metadata_type,
                    limit=filter_config.limit,
                    after_date=after_date,
                    before_date=before_date,
                    date_field=filter_config.date_field
                )

                # Update progress
                progress_dialog.update_progress(100, 100, f"Found {len(results)} results")

                return results

            finally:
                progress_dialog.close()
                self._query_in_progress = False

        except Exception as e:
            logger.error(f"Error during query: {e}")
            self.ui.show_error_message("Query Error", f"An error occurred during query:\n{str(e)}")
            self._query_in_progress = False
            return []

    def get_resource_count(self) -> int:
        """Get the total number of resources in the cache."""
        if self.cache is None:
            return 0
        return self.cache.get_resource_count()

    def get_latest_scan(self) -> Optional[ScanResult]:
        """Get the most recent scan result."""
        if self.cache is None:
            return None
        return self.cache.get_latest_scan()

    def _on_scan_progress(self, dirs_scanned: int, items_found: int, current_path: str) -> None:
        """Handle scan progress updates."""
        # This method can be overridden by subclasses to provide custom progress handling
        logger.debug(f"Scan progress: {dirs_scanned} dirs, {items_found} items, current: {current_path}")

    def _on_query_progress(self, current: int, total: int, message: str) -> None:
        """Handle query progress updates."""
        # This method can be overridden by subclasses to provide custom progress handling
        logger.debug(f"Query progress: {current}/{total} - {message}")

    def show_about_dialog(self) -> None:
        """Show the about dialog."""
        about_text = """zInfo GUI

A graphical interface for the zinfo project indexing system.

This application allows you to:
• Scan directories for project metadata files
• Query and filter indexed projects
• View detailed project information
• Manage scan configurations

Built with modular architecture for easy UI framework swapping."""

        self.ui.show_info_message("About zInfo GUI", about_text)

    def show_settings_dialog(self) -> None:
        """Show the settings dialog."""
        # This would be implemented with actual settings management
        self.ui.show_info_message("Settings", "Settings dialog not yet implemented.")
