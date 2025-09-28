"""Contract tests for AbstractUI interface implementations.

These tests validate that any UI implementation conforms to the AbstractUI interface
by ensuring all abstract methods are implemented and callable.
"""

import pytest
from pathlib import Path
from typing import List

from zinfo.ui import AbstractUI, ScanConfig, QueryFilter
from zinfo.ui.null_ui import NullUI
from zinfo.core.models import ResourceMetadata


@pytest.fixture
def ui_instance() -> AbstractUI:
    """Provide a UI instance for contract testing."""
    return NullUI()


@pytest.fixture
def sample_scan_config() -> ScanConfig:
    """Sample scan configuration for testing."""
    return ScanConfig(root_path=Path("/test"), max_depth=3)


@pytest.fixture
def sample_query_filter() -> QueryFilter:
    """Sample query filter for testing."""
    return QueryFilter(title="test", limit=10)


@pytest.fixture
def sample_results() -> List[ResourceMetadata]:
    """Sample resource metadata results for testing."""
    return [
        ResourceMetadata(
            dir_id="test/resource1",
            dir_path="/test/resource1",
            title="Test Resource",
            shortname="Test",
            summary="A test resource",
            client="Test Client",
            team="Test Team",
            contact_email="test@example.com",
            location="zinfo.txt",
        )
    ]


def test_show_main_window_contract(ui_instance: AbstractUI):
    """Test that show_main_window method is implemented and callable."""
    # Should not raise NotImplementedError
    ui_instance.show_main_window()


def test_show_scan_dialog_contract(ui_instance: AbstractUI, sample_scan_config: ScanConfig):
    """Test that show_scan_dialog method is implemented and callable."""
    result = ui_instance.show_scan_dialog(sample_scan_config)
    # Result should be Optional[ScanConfig]
    assert result is None or isinstance(result, ScanConfig)


def test_show_query_dialog_contract(ui_instance: AbstractUI, sample_query_filter: QueryFilter):
    """Test that show_query_dialog method is implemented and callable."""
    result = ui_instance.show_query_dialog(sample_query_filter)
    # Result should be Optional[QueryFilter]
    assert result is None or isinstance(result, QueryFilter)


def test_show_results_table_contract(ui_instance: AbstractUI, sample_results: List[ResourceMetadata]):
    """Test that show_results_table method is implemented and callable."""
    ui_instance.show_results_table(sample_results)


def test_show_progress_dialog_contract(ui_instance: AbstractUI):
    """Test that show_progress_dialog method is implemented and callable."""
    from zinfo.ui import AbstractProgressDialog
    result = ui_instance.show_progress_dialog("Test Title", "Test Message")
    assert isinstance(result, AbstractProgressDialog)


def test_show_error_message_contract(ui_instance: AbstractUI):
    """Test that show_error_message method is implemented and callable."""
    ui_instance.show_error_message("Error Title", "Error Message")


def test_show_info_message_contract(ui_instance: AbstractUI):
    """Test that show_info_message method is implemented and callable."""
    ui_instance.show_info_message("Info Title", "Info Message")


def test_show_confirmation_dialog_contract(ui_instance: AbstractUI):
    """Test that show_confirmation_dialog method is implemented and callable."""
    result = ui_instance.show_confirmation_dialog("Confirm Title", "Confirm Message")
    assert isinstance(result, bool)


def test_set_scan_progress_callback_contract(ui_instance: AbstractUI):
    """Test that set_scan_progress_callback method is implemented and callable."""
    def dummy_callback(dirs_scanned: int, items_found: int, current_path: str):
        pass
    ui_instance.set_scan_progress_callback(dummy_callback)


def test_set_query_progress_callback_contract(ui_instance: AbstractUI):
    """Test that set_query_progress_callback method is implemented and callable."""
    def dummy_callback(current: int, total: int, message: str):
        pass
    ui_instance.set_query_progress_callback(dummy_callback)

def test_progress_dialog_contract(ui_instance: AbstractUI):
    """Test that progress dialog methods are implemented and callable."""
    from zinfo.ui import AbstractProgressDialog
    progress_dialog = ui_instance.show_progress_dialog("Test", "Testing")

    # Test update_progress
    progress_dialog.update_progress(1, 10, "Testing")

    # Test close
    progress_dialog.close()

    # Test is_cancelled
    result = progress_dialog.is_cancelled()
    assert isinstance(result, bool)
