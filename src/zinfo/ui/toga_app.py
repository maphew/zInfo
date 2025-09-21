"""Toga-based GUI implementation for zinfo.

This module provides a Toga-specific implementation of the AbstractUI interface.
"""

import toga
from toga.style import Pack
from toga.style.pack import ROW, COLUMN
from pathlib import Path
from typing import Optional, List, Callable, Any
import threading
import logging

from . import AbstractUI, AbstractProgressDialog, ScanConfig, QueryFilter, ScanProgressCallback, ProgressCallback
from .app import ZinfoApp
from .toga_components import ZinfoTable
from zinfo.core.models import ResourceMetadata

logger = logging.getLogger(__name__)


class TogaProgressDialog(AbstractProgressDialog):
    """Toga implementation of progress dialog."""

    def __init__(self, app: toga.App, title: str, message: str):
        self.app = app
        self.dialog = toga.ProgressDialog(title=title, message=message)
        self._cancelled = False

    def update_progress(self, current: int, total: int, message: str = "") -> None:
        """Update progress information."""
        if message:
            self.dialog.message = message
        self.dialog.progress = current / total if total > 0 else 0

    def close(self) -> None:
        """Close the progress dialog."""
        self.dialog.close()

    def is_cancelled(self) -> bool:
        """Check if the user has cancelled the operation."""
        return self._cancelled


class ZinfoTogaApp(AbstractUI):
    """Toga-based implementation of the zinfo UI."""

    def __init__(self, app_name: str = "zInfo", app_id: str = "org.zinfo.gui"):
        """Initialize the Toga UI implementation.

        Args:
            app_name: Name of the application
            app_id: Unique application identifier
        """
        self.app_name = app_name
        self.app_id = app_id
        self.toga_app: Optional[toga.App] = None
        self.main_window: Optional[toga.MainWindow] = None
        self.zinfo_app: Optional[ZinfoApp] = None

        # Progress callbacks
        self.scan_progress_callback: Optional[ScanProgressCallback] = None
        self.query_progress_callback: Optional[ProgressCallback] = None

        # UI components
        self.scan_button: Optional[toga.Button] = None
        self.query_button: Optional[toga.Button] = None
        self.results_table: Optional[ZinfoTable] = None
        self.status_label: Optional[toga.Label] = None

    def startup(self) -> None:
        """Start up the Toga application."""
        self.toga_app = toga.App(
            formal_name=self.app_name,
            app_id=self.app_id,
            on_exit=self.shutdown
        )

        # Create main window
        self.main_window = toga.MainWindow(title=self.app_name)
        self.main_window.content = self._create_main_content()
        self.main_window.show()

        # Initialize zinfo app
        self.zinfo_app = ZinfoApp(self)

        # Set up status
        self._update_status("Ready")

    def _create_main_content(self) -> toga.Box:
        """Create the main window content."""
        # Create toolbar
        toolbar = self._create_toolbar()

        # Create main content area
        content_box = toga.Box(
            style=Pack(direction=COLUMN, padding=10)
        )

        # Status bar
        self.status_label = toga.Label(
            "Ready",
            style=Pack(padding=(5, 10), background_color="#f0f0f0")
        )

        # Add components to main box
        content_box.add(toolbar)
        content_box.add(toga.Divider())
        content_box.add(self._create_results_area())
        content_box.add(toga.Divider())
        content_box.add(self.status_label)

        return content_box

    def _create_toolbar(self) -> toga.Box:
        """Create the toolbar with action buttons."""
        toolbar = toga.Box(
            style=Pack(direction=ROW, padding=10, alignment="center")
        )

        # Scan button
        self.scan_button = toga.Button(
            "Scan Directory",
            on_press=self._on_scan_pressed,
            style=Pack(padding=10, margin=5)
        )

        # Query button
        self.query_button = toga.Button(
            "Query Projects",
            on_press=self._on_query_pressed,
            style=Pack(padding=10, margin=5)
        )

        # Settings button
        settings_button = toga.Button(
            "Settings",
            on_press=self._on_settings_pressed,
            style=Pack(padding=10, margin=5)
        )

        # About button
        about_button = toga.Button(
            "About",
            on_press=self._on_about_pressed,
            style=Pack(padding=10, margin=5)
        )

        toolbar.add(self.scan_button)
        toolbar.add(self.query_button)
        toolbar.add(settings_button)
        toolbar.add(about_button)

        return toolbar

    def _create_results_area(self) -> toga.Box:
        """Create the results display area."""
        results_box = toga.Box(
            style=Pack(direction=COLUMN, padding=10, flex=1)
        )

        # Results label
        results_label = toga.Label(
            "Query Results:",
            style=Pack(font_weight="bold", padding=(0, 0, 5, 0))
        )

        # Create table
        self.results_table = ZinfoTable(
            style=Pack(flex=1)
        )

        results_box.add(results_label)
        results_box.add(self.results_table)

        return results_box

    def _on_scan_pressed(self, widget: toga.Button) -> None:
        """Handle scan button press."""
        if self.zinfo_app is None:
            return

        # Show scan configuration dialog
        config = ScanConfig(
            root_path=Path("."),  # Default to current directory
            max_depth=5,
            cache_path=Path("zinfo.db")
        )

        updated_config = self.show_scan_dialog(config)
        if updated_config:
            # Disable scan button during operation
            self.scan_button.enabled = False
            self._update_status("Scanning...")

            # Run scan in background thread
            def scan_thread():
                try:
                    success = self.zinfo_app.run_scan(updated_config)
                    if success:
                        # Update results table with latest scan
                        latest_scan = self.zinfo_app.get_latest_scan()
                        if latest_scan and latest_scan.items:
                            self.show_results_table(latest_scan.items)
                finally:
                    # Re-enable button
                    self.scan_button.enabled = True
                    self._update_status("Ready")

            thread = threading.Thread(target=scan_thread, daemon=True)
            thread.start()

    def _on_query_pressed(self, widget: toga.Button) -> None:
        """Handle query button press."""
        if self.zinfo_app is None:
            return

        # Show query filter dialog
        filter_config = QueryFilter()

        updated_filter = self.show_query_dialog(filter_config)
        if updated_filter:
            # Disable query button during operation
            self.query_button.enabled = False
            self._update_status("Querying...")

            # Run query in background thread
            def query_thread():
                try:
                    results = self.zinfo_app.run_query(updated_filter)
                    self.show_results_table(results)
                finally:
                    # Re-enable button
                    self.query_button.enabled = True
                    self._update_status("Ready")

            thread = threading.Thread(target=query_thread, daemon=True)
            thread.start()

    def _on_settings_pressed(self, widget: toga.Button) -> None:
        """Handle settings button press."""
        if self.zinfo_app:
            self.zinfo_app.show_settings_dialog()

    def _on_about_pressed(self, widget: toga.Button) -> None:
        """Handle about button press."""
        if self.zinfo_app:
            self.zinfo_app.show_about_dialog()

    def _update_status(self, message: str) -> None:
        """Update the status bar message."""
        if self.status_label:
            self.status_label.text = message

    # AbstractUI implementation
    def show_main_window(self) -> None:
        """Show the main application window."""
        if self.toga_app:
            self.toga_app.main_loop()

    def show_scan_dialog(self, config: ScanConfig) -> Optional[ScanConfig]:
        """Show scan configuration dialog."""
        from .toga_components import show_scan_dialog
        return show_scan_dialog(self.toga_app, config)

    def show_query_dialog(self, filter_config: QueryFilter) -> Optional[QueryFilter]:
        """Show query filter dialog."""
        from .toga_components import show_query_dialog
        return show_query_dialog(self.toga_app, filter_config)

    def show_results_table(self, results: List['ResourceMetadata']) -> None:
        """Display results in a table format."""
        if self.results_table:
            self.results_table.set_data(results)

    def show_progress_dialog(self, title: str, message: str) -> AbstractProgressDialog:
        """Show a progress dialog."""
        if self.toga_app:
            return TogaProgressDialog(self.toga_app, title, message)
        else:
            raise RuntimeError("Toga app not initialized")

    def show_error_message(self, title: str, message: str) -> None:
        """Show an error message dialog."""
        if self.toga_app:
            self.toga_app.error_dialog(title, message)

    def show_info_message(self, title: str, message: str) -> None:
        """Show an information message dialog."""
        if self.toga_app:
            self.toga_app.info_dialog(title, message)

    def show_confirmation_dialog(self, title: str, message: str) -> bool:
        """Show a confirmation dialog."""
        if self.toga_app:
            return self.toga_app.confirm_dialog(title, message)
        return False

    def set_scan_progress_callback(self, callback: ScanProgressCallback) -> None:
        """Set callback for scan progress updates."""
        self.scan_progress_callback = callback

    def set_query_progress_callback(self, callback: ProgressCallback) -> None:
        """Set callback for query progress updates."""
        self.query_progress_callback = callback

    def shutdown(self, app: toga.App) -> bool:
        """Handle application shutdown."""
        logger.info("Shutting down zinfo GUI")
        return True
