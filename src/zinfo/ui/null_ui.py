"""Null UI implementation for headless/CLI-only usage.

This module provides a no-op implementation of the AbstractUI interface,
suitable for testing and environments where no GUI framework is available.
"""

import logging
from pathlib import Path
from typing import Optional, List

from . import AbstractUI, AbstractProgressDialog, ScanConfig, QueryFilter, ScanProgressCallback, ProgressCallback
from zinfo.core.models import ResourceMetadata

logger = logging.getLogger(__name__)


class NullProgressDialog(AbstractProgressDialog):
    """No-op implementation of progress dialog for headless usage."""

    def update_progress(self, current: int, total: int, message: str = "") -> None:
        """Update progress information (no-op)."""
        pass

    def close(self) -> None:
        """Close the progress dialog (no-op)."""
        pass

    def is_cancelled(self) -> bool:
        """Check if cancelled (always False for headless)."""
        return False


class NullUI(AbstractUI):
    """Headless/no-op implementation of the UI interface.

    This implementation provides no-op methods for all UI operations,
    making it suitable for CLI-only usage and testing scenarios.
    """

    def __init__(self):
        """Initialize the null UI."""
        self.scan_progress_callback: Optional[ScanProgressCallback] = None
        self.query_progress_callback: Optional[ProgressCallback] = None
        self.zinfo_app = None

    def startup(self) -> None:
        """Initialize the UI (no-op for headless)."""
        from .app import ZinfoApp
        self.zinfo_app = ZinfoApp(self)

    def show_main_window(self) -> None:
        """Show the main application window (no-op)."""
        pass

    def show_scan_dialog(self, config: ScanConfig) -> Optional[ScanConfig]:
        """Show scan configuration dialog (returns None to indicate cancelled)."""
        return None

    def show_query_dialog(self, filter_config: QueryFilter) -> Optional[QueryFilter]:
        """Show query filter dialog (returns None to indicate cancelled)."""
        return None

    def show_results_table(self, results: List[ResourceMetadata]) -> None:
        """Display results in a table format (no-op)."""
        pass

    def show_progress_dialog(self, title: str, message: str) -> AbstractProgressDialog:
        """Show a progress dialog (returns null progress dialog)."""
        return NullProgressDialog()

    def show_error_message(self, title: str, message: str) -> None:
        """Show an error message (logs as warning)."""
        logger.warning(f"{title}: {message}")

    def show_info_message(self, title: str, message: str) -> None:
        """Show an information message (logs as info)."""
        logger.info(f"{title}: {message}")

    def show_confirmation_dialog(self, title: str, message: str) -> bool:
        """Show a confirmation dialog (always returns False)."""
        return False

    def set_scan_progress_callback(self, callback: ScanProgressCallback) -> None:
        """Set callback for scan progress updates."""
        self.scan_progress_callback = callback

    def set_query_progress_callback(self, callback: ProgressCallback) -> None:
        """Set callback for query progress updates."""
        self.query_progress_callback = callback
