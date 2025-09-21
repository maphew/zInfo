"""User Interface layer for zinfo.

This module provides a framework-agnostic interface for GUI operations,
allowing easy swapping between different UI frameworks like Toga, PyQt, Kivy, etc.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List, Callable, Any, Protocol
from dataclasses import dataclass

from zinfo.core.models import ResourceMetadata, ScanResult


@dataclass
class ScanConfig:
    """Configuration for scan operations."""
    root_path: Path
    max_depth: int = 5
    cache_path: Optional[Path] = None


@dataclass
class QueryFilter:
    """Filter criteria for queries."""
    title: Optional[str] = None
    author: Optional[str] = None
    metadata_type: Optional[str] = None
    limit: Optional[int] = None
    after_date: Optional[str] = None
    before_date: Optional[str] = None
    date_field: str = "created"


class ProgressCallback(Protocol):
    """Protocol for progress reporting callbacks."""
    def __call__(self, current: int, total: int, message: str) -> None: ...


class ScanProgressCallback(Protocol):
    """Protocol for scan-specific progress callbacks."""
    def __call__(self, dirs_scanned: int, items_found: int, current_path: str) -> None: ...


class AbstractUI(ABC):
    """Abstract base class for UI implementations."""

    @abstractmethod
    def show_main_window(self) -> None:
        """Show the main application window."""
        pass

    @abstractmethod
    def show_scan_dialog(self, config: ScanConfig) -> Optional[ScanConfig]:
        """Show scan configuration dialog and return updated config or None if cancelled."""
        pass

    @abstractmethod
    def show_query_dialog(self, filter_config: QueryFilter) -> Optional[QueryFilter]:
        """Show query filter dialog and return updated filter or None if cancelled."""
        pass

    @abstractmethod
    def show_results_table(self, results: List[ResourceMetadata]) -> None:
        """Display results in a table format."""
        pass

    @abstractmethod
    def show_progress_dialog(self, title: str, message: str) -> 'AbstractProgressDialog':
        """Show a progress dialog and return a progress dialog instance."""
        pass

    @abstractmethod
    def show_error_message(self, title: str, message: str) -> None:
        """Show an error message dialog."""
        pass

    @abstractmethod
    def show_info_message(self, title: str, message: str) -> None:
        """Show an information message dialog."""
        pass

    @abstractmethod
    def show_confirmation_dialog(self, title: str, message: str) -> bool:
        """Show a confirmation dialog and return True if confirmed."""
        pass

    @abstractmethod
    def set_scan_progress_callback(self, callback: ScanProgressCallback) -> None:
        """Set callback for scan progress updates."""
        pass

    @abstractmethod
    def set_query_progress_callback(self, callback: ProgressCallback) -> None:
        """Set callback for query progress updates."""
        pass


class AbstractProgressDialog(ABC):
    """Abstract base class for progress dialogs."""

    @abstractmethod
    def update_progress(self, current: int, total: int, message: str = "") -> None:
        """Update progress information."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the progress dialog."""
        pass

    @abstractmethod
    def is_cancelled(self) -> bool:
        """Check if the user has cancelled the operation."""
        pass


class AbstractTableWidget(ABC):
    """Abstract base class for table widgets."""

    @abstractmethod
    def set_data(self, data: List[ResourceMetadata]) -> None:
        """Set the data to display in the table."""
        pass

    @abstractmethod
    def get_selected_items(self) -> List[ResourceMetadata]:
        """Get the currently selected items."""
        pass

    @abstractmethod
    def refresh(self) -> None:
        """Refresh the table display."""
        pass

    @abstractmethod
    def set_filter(self, filter_text: str) -> None:
        """Apply a filter to the table data."""
        pass


class AbstractFormWidget(ABC):
    """Abstract base class for form widgets."""

    @abstractmethod
    def get_field_value(self, field_name: str) -> Any:
        """Get the value of a form field."""
        pass

    @abstractmethod
    def set_field_value(self, field_name: str, value: Any) -> None:
        """Set the value of a form field."""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate the form data."""
        pass

    @abstractmethod
    def get_all_values(self) -> dict:
        """Get all form field values as a dictionary."""
        pass
