"""Tests for NullUI implementation."""

import logging
from pathlib import Path
from unittest.mock import patch
from typing import List

import pytest

from zinfo.ui.null_ui import NullUI, NullProgressDialog
from zinfo.ui import ScanConfig, QueryFilter
from zinfo.core.models import ResourceMetadata


@pytest.fixture
def null_ui() -> NullUI:
    """Provide a NullUI instance for testing."""
    return NullUI()


@pytest.fixture
def sample_scan_config() -> ScanConfig:
    """Sample scan configuration."""
    return ScanConfig(root_path=Path("/test"), max_depth=3)


@pytest.fixture
def sample_query_filter() -> QueryFilter:
    """Sample query filter."""
    return QueryFilter(title="test", limit=10)


@pytest.fixture
def sample_results() -> List[ResourceMetadata]:
    """Sample results."""
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


def test_null_ui_initialization(null_ui: NullUI):
    """Test NullUI initialization."""
    assert null_ui.scan_progress_callback is None
    assert null_ui.query_progress_callback is None
    assert null_ui.zinfo_app is None


def test_show_main_window_noop(null_ui: NullUI):
    """Test show_main_window does nothing."""
    # Should not raise any exception
    null_ui.show_main_window()


def test_show_scan_dialog_returns_none(null_ui: NullUI, sample_scan_config: ScanConfig):
    """Test show_scan_dialog returns None (cancelled)."""
    result = null_ui.show_scan_dialog(sample_scan_config)
    assert result is None


def test_show_query_dialog_returns_none(null_ui: NullUI, sample_query_filter: QueryFilter):
    """Test show_query_dialog returns None (cancelled)."""
    result = null_ui.show_query_dialog(sample_query_filter)
    assert result is None


def test_show_results_table_noop(null_ui: NullUI, sample_results: List[ResourceMetadata]):
    """Test show_results_table does nothing."""
    null_ui.show_results_table(sample_results)


def test_show_progress_dialog_returns_null_progress_dialog(null_ui: NullUI):
    """Test show_progress_dialog returns NullProgressDialog instance."""
    result = null_ui.show_progress_dialog("Title", "Message")
    assert isinstance(result, NullProgressDialog)


def test_show_error_message_logs_warning(null_ui: NullUI, caplog):
    """Test show_error_message logs as warning."""
    with caplog.at_level(logging.WARNING):
        null_ui.show_error_message("Error Title", "Error Message")

    assert "Error Title: Error Message" in caplog.text
    assert caplog.records[0].levelname == "WARNING"


def test_show_info_message_logs_info(null_ui: NullUI, caplog):
    """Test show_info_message logs as info."""
    with caplog.at_level(logging.INFO):
        null_ui.show_info_message("Info Title", "Info Message")

    assert "Info Title: Info Message" in caplog.text
    assert caplog.records[0].levelname == "INFO"


def test_show_confirmation_dialog_returns_false(null_ui: NullUI):
    """Test show_confirmation_dialog always returns False."""
    result = null_ui.show_confirmation_dialog("Title", "Message")
    assert result is False


def test_set_scan_progress_callback(null_ui: NullUI):
    """Test setting scan progress callback."""
    def callback(dirs_scanned: int, items_found: int, current_path: str):
        pass

    null_ui.set_scan_progress_callback(callback)
    assert null_ui.scan_progress_callback is callback


def test_set_query_progress_callback(null_ui: NullUI):
    """Test setting query progress callback."""
    def callback(current: int, total: int, message: str):
        pass

    null_ui.set_query_progress_callback(callback)
    assert null_ui.query_progress_callback is callback


def test_startup_initializes_app(null_ui: NullUI):
    """Test startup method initializes zinfo_app."""
    null_ui.startup()
    assert null_ui.zinfo_app is not None
    # Note: We can't easily test the app creation without mocking, but at least check it's set


class TestNullProgressDialog:
    """Tests for NullProgressDialog."""

    def test_update_progress_noop(self):
        """Test update_progress does nothing."""
        dialog = NullProgressDialog()
        dialog.update_progress(1, 10, "Test")

    def test_close_noop(self):
        """Test close does nothing."""
        dialog = NullProgressDialog()
        dialog.close()

    def test_is_cancelled_always_false(self):
        """Test is_cancelled always returns False."""
        dialog = NullProgressDialog()
        assert dialog.is_cancelled() is False
