"""Toga-specific UI components for zinfo.

This module contains reusable Toga UI components that implement the abstract interfaces.
"""

import toga
from toga.style import Pack
from toga.style.pack import ROW, COLUMN
from pathlib import Path
from typing import Optional, List, Any
import threading

from zinfo.core.models import ResourceMetadata
from . import ScanConfig, QueryFilter


class ZinfoTable:
    """A table widget for displaying ResourceMetadata objects."""

    def __init__(self, style: Pack = None):
        """Initialize the table widget.

        Args:
            style: Toga style for the table
        """
        self.table = toga.Table(
            headings=["ID", "Title", "Contact", "Type", "Last Modified"],
            style=style or Pack(flex=1)
        )
        self._data: List[ResourceMetadata] = []

    def set_data(self, data: List[ResourceMetadata]) -> None:
        """Set the data to display in the table.

        Args:
            data: List of ResourceMetadata objects to display
        """
        self._data = data
        self._refresh_table()

    def _refresh_table(self) -> None:
        """Refresh the table display with current data."""
        # Clear existing rows
        self.table.data = []

        # Add data rows
        for item in self._data:
            # Truncate long fields for display
            id_short = item.id[:30] + "..." if len(item.id) > 33 else item.id
            title_short = item.title[:35] + "..." if len(item.title) > 38 else item.title
            contact_short = item.contact[:25] + "..." if len(item.contact) > 28 else item.contact

            row = [
                id_short,
                title_short,
                contact_short,
                item.metadata_type,
                item.last_modified.strftime("%Y-%m-%d %H:%M") if item.last_modified else "N/A"
            ]
            self.table.data.append(row)

    def get_selected_items(self) -> List[ResourceMetadata]:
        """Get the currently selected items."""
        # For now, return empty list - Toga table selection would need to be implemented
        return []

    def refresh(self) -> None:
        """Refresh the table display."""
        self._refresh_table()

    def set_filter(self, filter_text: str) -> None:
        """Apply a filter to the table data."""
        # For now, just refresh - filtering would need to be implemented
        self._refresh_table()


def show_scan_dialog(app: toga.App, config: ScanConfig) -> Optional[ScanConfig]:
    """Show a scan configuration dialog.

    Args:
        app: The Toga application instance
        config: Current scan configuration

    Returns:
        Updated configuration or None if cancelled
    """
    # Create dialog
    dialog = toga.Selection(
        title="Scan Configuration",
        message="Configure scan parameters:",
        style=Pack(padding=20)
    )

    # Root path selection
    root_input = toga.TextInput(
        value=str(config.root_path),
        placeholder="Enter root directory path",
        style=Pack(flex=1)
    )

    # Max depth selection
    depth_input = toga.NumberInput(
        value=config.max_depth,
        min_value=1,
        max_value=10,
        step=1,
        style=Pack(width=100)
    )

    # Cache path selection
    cache_input = toga.TextInput(
        value=str(config.cache_path) if config.cache_path else "zinfo.db",
        placeholder="Enter cache database path",
        style=Pack(flex=1)
    )

    # Create content box
    content = toga.Box(
        style=Pack(direction=COLUMN, padding=10)
    )

    content.add(toga.Label("Root Directory:", style=Pack(padding=(0, 5))))
    content.add(root_input)

    content.add(toga.Label("Max Depth:", style=Pack(padding=(10, 5, 0, 5))))
    content.add(depth_input)

    content.add(toga.Label("Cache Database:", style=Pack(padding=(10, 5, 0, 5))))
    content.add(cache_input)

    # Show dialog
    if app.main_window:
        result = app.main_window.dialog(
            toga.QuestionDialog(
                title="Scan Configuration",
                message="Configure scan parameters:",
                content=content,
                yes_button="Start Scan",
                no_button="Cancel"
            )
        )

        if result:
            try:
                root_path = Path(root_input.value)
                if not root_path.exists():
                    app.error_dialog("Invalid Path", f"Root directory does not exist: {root_path}")
                    return None

                return ScanConfig(
                    root_path=root_path,
                    max_depth=int(depth_input.value),
                    cache_path=Path(cache_input.value)
                )
            except Exception as e:
                app.error_dialog("Configuration Error", f"Invalid configuration: {str(e)}")
                return None

    return None


def show_query_dialog(app: toga.App, filter_config: QueryFilter) -> Optional[QueryFilter]:
    """Show a query filter dialog.

    Args:
        app: The Toga application instance
        filter_config: Current filter configuration

    Returns:
        Updated filter configuration or None if cancelled
    """
    # Create dialog content
    content = toga.Box(
        style=Pack(direction=COLUMN, padding=10)
    )

    # Title filter
    title_input = toga.TextInput(
        value=filter_config.title or "",
        placeholder="Filter by title",
        style=Pack(flex=1)
    )

    # Author filter
    author_input = toga.TextInput(
        value=filter_config.author or "",
        placeholder="Filter by author",
        style=Pack(flex=1)
    )

    # Type filter
    type_input = toga.TextInput(
        value=filter_config.metadata_type or "",
        placeholder="Filter by type",
        style=Pack(flex=1)
    )

    # Limit filter
    limit_input = toga.NumberInput(
        value=filter_config.limit or 50,
        min_value=1,
        max_value=1000,
        step=10,
        style=Pack(width=100)
    )

    # Add fields to content
    content.add(toga.Label("Title:", style=Pack(padding=(0, 5))))
    content.add(title_input)

    content.add(toga.Label("Author:", style=Pack(padding=(10, 5, 0, 5))))
    content.add(author_input)

    content.add(toga.Label("Type:", style=Pack(padding=(10, 5, 0, 5))))
    content.add(type_input)

    content.add(toga.Label("Limit:", style=Pack(padding=(10, 5, 0, 5))))
    content.add(limit_input)

    # Show dialog
    if app.main_window:
        result = app.main_window.dialog(
            toga.QuestionDialog(
                title="Query Filters",
                message="Configure query filters:",
                content=content,
                yes_button="Search",
                no_button="Cancel"
            )
        )

        if result:
            return QueryFilter(
                title=title_input.value if title_input.value else None,
                author=author_input.value if author_input.value else None,
                metadata_type=type_input.value if type_input.value else None,
                limit=int(limit_input.value) if limit_input.value else None
            )

    return None
