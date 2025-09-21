"""Test suite for Tkinter UI components."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import tkinter as tk

# Skip tests if tkinter is not available (e.g., in a headless environment)
pytest.importorskip("tkinter")

from zinfo.core.models import ResourceMetadata
from zinfo.ui import ScanConfig, QueryFilter
from zinfo.ui.tk_components import ZinfoTable, show_scan_dialog, show_query_dialog


class TestZinfoTable:
    """Test the ZinfoTable component."""

    @pytest.fixture
    def root(self):
        """Fixture for a Tk root window."""
        root = tk.Tk()
        yield root
        root.destroy()

    def test_table_initialization(self, root):
        """Test table initialization."""
        table = ZinfoTable(parent=root)
        assert table.tree is not None
        assert len(table._data) == 0

    def test_set_data(self, root):
        """Test setting table data."""
        table = ZinfoTable(parent=root)

        # Create sample data
        data = [
            ResourceMetadata(
                id="test1",
                title="Test Project 1",
                link="file://test1.txt",
                contact="test@example.com",
                metadata_type="zinfo_project",
            ),
            ResourceMetadata(
                id="test2",
                title="Test Project 2",
                link="file://test2.txt",
                contact="test2@example.com",
                metadata_type="zinfo_project",
            ),
        ]

        table.set_data(data)
        assert len(table._data) == 2
        assert table._data[0].id == "test1"
        assert table._data[1].id == "test2"
        # Check if data is in the treeview
        children = table.tree.get_children()
        assert len(children) == 2
        assert table.tree.item(children[0])["values"][1] == "Test Project 1"

    def test_refresh_table(self, root):
        """Test table refresh functionality."""
        table = ZinfoTable(parent=root)
        data = [
            ResourceMetadata(
                id="test1",
                title="Test Project",
                link="file://test.txt",
                contact="test@example.com",
                metadata_type="zinfo_project",
            )
        ]
        table.set_data(data)
        assert len(table.tree.get_children()) == 1
        table.refresh()
        assert len(table.tree.get_children()) == 1 # Should not raise errors and still have data

    def test_get_selected_items(self, root):
        """Test getting selected items."""
        table = ZinfoTable(parent=root)
        data = [
            ResourceMetadata(
                id="test1",
                title="Test Project 1",
                link="file://test1.txt",
                contact="test@example.com",
                metadata_type="zinfo_project",
            )
        ]
        table.set_data(data)
        children = table.tree.get_children()
        table.tree.selection_set(children[0])
        
        selected = table.get_selected_items()
        assert len(selected) == 1
        assert selected[0].id == "test1"


@patch("zinfo.ui.tk_components.filedialog")
@patch("zinfo.ui.tk_components.simpledialog")
class TestDialogs:
    """Test dialog functionality."""

    def test_show_scan_dialog(self, mock_simpledialog, mock_filedialog, tmp_path):
        """Test scan dialog creation and returning a config."""
        mock_root = Mock()
        mock_filedialog.askdirectory.return_value = str(tmp_path)
        mock_simpledialog.askinteger.return_value = 4
        mock_simpledialog.askstring.return_value = "test_cache.db"
        
        config = ScanConfig(root_path=Path("."), max_depth=5, cache_path=Path("zinfo.db"))
        
        result = show_scan_dialog(mock_root, config)

        assert isinstance(result, ScanConfig)
        assert result.root_path == tmp_path
        assert result.max_depth == 4
        assert result.cache_path == Path("test_cache.db")

    def test_show_scan_dialog_cancel(self, mock_simpledialog, mock_filedialog):
        """Test scan dialog cancellation."""
        mock_root = Mock()
        mock_filedialog.askdirectory.return_value = "" # User cancels
        config = ScanConfig(root_path=Path("."))
        
        result = show_scan_dialog(mock_root, config)
        assert result is None

    def test_show_query_dialog(self, mock_simpledialog, mock_filedialog):
        """Test query dialog creation and returning a filter."""
        mock_root = Mock()
        mock_simpledialog.askstring.side_effect = ["my title", "my author", "my type"]
        mock_simpledialog.askinteger.return_value = 100

        filter_config = QueryFilter()
        result = show_query_dialog(mock_root, filter_config)

        assert isinstance(result, QueryFilter)
        assert result.title == "my title"
        assert result.author == "my author"
        assert result.metadata_type == "my type"
        assert result.limit == 100

    def test_show_query_dialog_cancel(self, mock_simpledialog, mock_filedialog):
        """Test query dialog cancellation."""
        mock_root = Mock()
        mock_simpledialog.askstring.return_value = None # User cancels
        
        filter_config = QueryFilter()
        result = show_query_dialog(mock_root, filter_config)
        assert result is None
