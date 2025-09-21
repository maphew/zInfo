"""Test suite for Toga UI components."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from zinfo.ui.toga_components import ZinfoTable, show_scan_dialog, show_query_dialog
from zinfo.core.models import ResourceMetadata
from zinfo.ui import ScanConfig, QueryFilter


class TestZinfoTable:
    """Test the ZinfoTable component."""

    def test_table_initialization(self):
        """Test table initialization."""
        table = ZinfoTable()
        assert table.table is not None
        assert len(table._data) == 0

    def test_set_data(self):
        """Test setting table data."""
        table = ZinfoTable()

        # Create sample data
        data = [
            ResourceMetadata(
                id="test1",
                title="Test Project 1",
                link="file://test1.txt",
                contact="test@example.com"
            ),
            ResourceMetadata(
                id="test2",
                title="Test Project 2",
                link="file://test2.txt",
                contact="test2@example.com"
            )
        ]

        table.set_data(data)
        assert len(table._data) == 2
        assert table._data[0].id == "test1"
        assert table._data[1].id == "test2"

    def test_refresh_table(self):
        """Test table refresh functionality."""
        table = ZinfoTable()

        # Add some data
        data = [ResourceMetadata(
            id="test1",
            title="Test Project",
            link="file://test.txt",
            contact="test@example.com"
        )]
        table.set_data(data)

        # Refresh should not raise errors
        table.refresh()

    def test_get_selected_items(self):
        """Test getting selected items (currently returns empty list)."""
        table = ZinfoTable()
        selected = table.get_selected_items()
        assert selected == []

    def test_set_filter(self):
        """Test setting filter (currently just refreshes)."""
        table = ZinfoTable()
        table.set_filter("test filter")
        # Should not raise errors


class TestDialogs:
    """Test dialog functionality."""

    @patch('zinfo.ui.toga_components.toga')
    def test_show_scan_dialog(self, mock_toga):
        """Test scan dialog creation."""
        # Mock the app and main window
        mock_app = Mock()
        mock_window = Mock()
        mock_app.main_window = mock_window

        # Mock the dialog response
        mock_window.dialog.return_value = True

        # Create config
        config = ScanConfig(
            root_path=Path("/test"),
            max_depth=3,
            cache_path=Path("test.db")
        )

        # This should not raise errors
        result = show_scan_dialog(mock_app, config)
        assert result is None  # Dialog not fully implemented in test

    @patch('zinfo.ui.toga_components.toga')
    def test_show_query_dialog(self, mock_toga):
        """Test query dialog creation."""
        # Mock the app and main window
        mock_app = Mock()
        mock_window = Mock()
        mock_app.main_window = mock_window

        # Mock the dialog response
        mock_window.dialog.return_value = True

        # Create filter config
        filter_config = QueryFilter(
            title="test",
            author="test author"
        )

        # This should not raise errors
        result = show_query_dialog(mock_app, filter_config)
        assert result is None  # Dialog not fully implemented in test

    @patch('zinfo.ui.toga_components.toga')
    def test_dialog_without_main_window(self, mock_toga):
        """Test dialog behavior when no main window exists."""
        mock_app = Mock()
        mock_app.main_window = None

        config = ScanConfig(root_path=Path("/test"))

        # Should not raise errors
        result = show_scan_dialog(mock_app, config)
        assert result is None
