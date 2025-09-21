"""Tkinter-based GUI implementation for zinfo.

This module provides a Tkinter-specific implementation of the AbstractUI interface.
"""

from __future__ import annotations

import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional, List

from . import (
    AbstractUI,
    AbstractProgressDialog,
    ScanConfig,
    QueryFilter,
    ScanProgressCallback,
    ProgressCallback,
)
from .app import ZinfoApp
from .tk_components import ZinfoTable, show_scan_dialog, show_query_dialog
from zinfo.core.models import ResourceMetadata

logger = logging.getLogger(__name__)


class TkProgressDialog(AbstractProgressDialog):
    """Tk implementation of progress dialog."""

    def __init__(self, root: tk.Tk, title: str, message: str):
        self.root = root
        self.top = tk.Toplevel(root)
        self.top.title(title)
        self.top.transient(root)
        self.top.grab_set()
        self._cancelled = False

        self.label = ttk.Label(self.top, text=message, padding=(10, 10))
        self.label.pack(fill="x")

        self.progress = ttk.Progressbar(self.top, mode="determinate", length=300)
        self.progress.pack(fill="x", padx=10, pady=(0, 10))
        self.progress["value"] = 0
        self.progress["maximum"] = 1

        self.btn_frame = ttk.Frame(self.top)
        self.btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.cancel_btn = ttk.Button(self.btn_frame, text="Close", command=self._on_close)
        self.cancel_btn.pack(side="right")

        # Center dialog
        self.top.update_idletasks()
        w = self.top.winfo_width()
        h = self.top.winfo_height()
        x = (self.top.winfo_screenwidth() // 2) - (w // 2)
        y = (self.top.winfo_screenheight() // 2) - (h // 2)
        self.top.geometry(f"{w}x{h}+{x}+{y}")

    def _on_close(self) -> None:
        self._cancelled = True
        self.top.destroy()

    def update_progress(self, current: int, total: int, message: str = "") -> None:
        if message:
            self.label.configure(text=message)
        total = max(1, total)
        self.progress["maximum"] = total
        self.progress["value"] = current
        self.top.update_idletasks()

    def close(self) -> None:
        try:
            self.top.destroy()
        except Exception:
            pass

    def is_cancelled(self) -> bool:
        return self._cancelled


class ZinfoTkApp(AbstractUI):
    """Tk-based implementation of the zinfo UI."""

    def __init__(self, app_name: str = "zInfo"):
        """Initialize the Tk UI implementation.

        Args:
            app_name: Name of the application
        """
        self.app_name = app_name
        self.root: Optional[tk.Tk] = None
        self.main_frame: Optional[ttk.Frame] = None
        self.zinfo_app: Optional[ZinfoApp] = None

        # Progress callbacks
        self.scan_progress_callback: Optional[ScanProgressCallback] = None
        self.query_progress_callback: Optional[ProgressCallback] = None

        # UI components
        self.scan_button: Optional[ttk.Button] = None
        self.query_button: Optional[ttk.Button] = None
        self.results_table: Optional[ZinfoTable] = None
        self.status_var: Optional[tk.StringVar] = None
        self.status_label: Optional[ttk.Label] = None

    def startup(self) -> None:
        """Start up the Tk application."""
        self.root = tk.Tk()
        self.root.title(self.app_name)

        # Main container
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Toolbar
        toolbar = ttk.Frame(self.main_frame)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        toolbar.columnconfigure(0, weight=1)

        # Use explicit font configuration for individual widgets
        large_font = ("TkDefaultFont", 12)
        
        self.scan_button = ttk.Button(toolbar, text="Scan Directory", command=self._on_scan_pressed)
        self.scan_button.grid(row=0, column=0, padx=(0, 5), sticky="w")

        self.query_button = ttk.Button(toolbar, text="Query Projects", command=self._on_query_pressed)
        self.query_button.grid(row=0, column=1, padx=(0, 5), sticky="w")

        settings_button = ttk.Button(toolbar, text="Settings", command=self._on_settings_pressed)
        settings_button.grid(row=0, column=2, padx=(0, 5), sticky="w")

        about_button = ttk.Button(toolbar, text="About", command=self._on_about_pressed)
        about_button.grid(row=0, column=3, padx=(0, 5), sticky="w")

        # Results area
        results_label = ttk.Label(self.main_frame, text="Query Results:", font=("TkDefaultFont", 14, "bold"))
        results_label.grid(row=1, column=0, sticky="w", pady=(5, 2))

        self.results_table = ZinfoTable(self.main_frame)
        self.results_table.widget().grid(row=2, column=0, sticky="nsew")
        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var, relief="sunken", font=("TkDefaultFont", 12))
        self.status_label.grid(row=3, column=0, sticky="ew", pady=(5, 0))

        # Initialize zinfo app
        self.zinfo_app = ZinfoApp(self)

        # Set up status
        self._update_status("Ready")

    def _update_status(self, message: str) -> None:
        """Update the status bar message."""
        if self.status_var is not None:
            self.status_var.set(message)

    # AbstractUI implementation
    def show_main_window(self) -> None:
        """Show the main application window."""
        if self.root:
            self.root.mainloop()

    def show_scan_dialog(self, config: ScanConfig) -> Optional[ScanConfig]:
        """Show scan configuration dialog."""
        if not self.root:
            return None
        return show_scan_dialog(self.root, config)

    def show_query_dialog(self, filter_config: QueryFilter) -> Optional[QueryFilter]:
        """Show query filter dialog."""
        if not self.root:
            return None
        return show_query_dialog(self.root, filter_config)

    def show_results_table(self, results: List["ResourceMetadata"]) -> None:
        """Display results in a table format."""
        if self.results_table:
            self.results_table.set_data(results)

    def show_progress_dialog(self, title: str, message: str) -> AbstractProgressDialog:
        """Show a progress dialog."""
        if not self.root:
            raise RuntimeError("Tk root not initialized")
        return TkProgressDialog(self.root, title, message)

    def show_error_message(self, title: str, message: str) -> None:
        """Show an error message dialog."""
        if self.root:
            messagebox.showerror(title, message, parent=self.root)

    def show_info_message(self, title: str, message: str) -> None:
        """Show an information message dialog."""
        if self.root:
            messagebox.showinfo(title, message, parent=self.root)

    def show_confirmation_dialog(self, title: str, message: str) -> bool:
        """Show a confirmation dialog."""
        if not self.root:
            return False
        return messagebox.askyesno(title, message, parent=self.root)

    def set_scan_progress_callback(self, callback: ScanProgressCallback) -> None:
        """Set callback for scan progress updates."""
        self.scan_progress_callback = callback

    def set_query_progress_callback(self, callback: ProgressCallback) -> None:
        """Set callback for query progress updates."""
        self.query_progress_callback = callback

    # Button handlers
    def _on_scan_pressed(self) -> None:
        """Handle scan button press."""
        if self.zinfo_app is None or self.root is None:
            return

        # Show scan configuration dialog
        config = ScanConfig(
            root_path=Path("."),  # Default to current directory
            max_depth=5,
            cache_path=Path("zinfo.db"),
        )

        updated_config = self.show_scan_dialog(config)
        if updated_config:
            # Disable scan button during operation
            if self.scan_button:
                self.scan_button.config(state="disabled")
            self._update_status("Scanning...")

            # Show progress dialog on main thread
            progress_dialog = self.show_progress_dialog("Scanning", f"Scanning {updated_config.root_path}...")

            def scan_thread():
                if self.zinfo_app is None or self.root is None:
                    return
                    
                try:
                    # Initialize cache if not already done
                    if self.zinfo_app.cache is None:
                        self.zinfo_app.initialize_cache(updated_config.cache_path)

                    # Create scanner (no GUI operations here)
                    from zinfo.core.scanner import ZinfoScanner
                    scanner = ZinfoScanner(
                        base_dir=updated_config.root_path,
                        cache=self.zinfo_app.cache,
                        max_depth=updated_config.max_depth
                    )

                    # Run scan (core logic only, no GUI)
                    result = scanner.scan()

                    # Schedule GUI updates on main thread
                    def _update_success():
                        try:
                            progress_dialog.update_progress(100, 100, "Scan completed")
                            progress_dialog.close()

                            # Show results
                            if result.errors:
                                error_msg = f"Scan completed with {len(result.errors)} errors:\n"
                                error_msg += "\n".join(f"• {error}" for error in result.errors[:5])
                                if len(result.errors) > 5:
                                    error_msg += f"\n... and {len(result.errors) - 5} more errors"
                                self.show_error_message("Scan Completed with Errors", error_msg)

                            success_msg = f"Scan completed successfully!\n"
                            success_msg += f"Found {result.total_items_found} projects in {result.total_dirs_scanned} directories"
                            self.show_info_message("Scan Completed", success_msg)

                            # Update results table
                            if result.items:
                                self.show_results_table(result.items)

                        finally:
                            if self.scan_button:
                                self.scan_button.config(state="normal")
                            self._update_status("Ready")

                    if self.root:
                        self.root.after(0, _update_success)

                except Exception as e:
                    logger.error(f"Error during scan: {e}")
                    error_str = str(e)
                    def _update_error():
                        try:
                            progress_dialog.close()
                        except:
                            pass
                        self.show_error_message("Scan Error", f"An error occurred during scanning:\n{error_str}")
                        if self.scan_button:
                            self.scan_button.config(state="normal")
                        self._update_status("Ready")
                    if self.root:
                        self.root.after(0, _update_error)

            thread = threading.Thread(target=scan_thread, daemon=True)
            thread.start()

    def _on_query_pressed(self) -> None:
        """Handle query button press."""
        if self.zinfo_app is None or self.root is None:
            return

        if self.zinfo_app.cache is None:
            self.show_error_message("No Cache", "No cache available. Please run a scan first.")
            return

        # Show query filter dialog
        filter_config = QueryFilter()

        updated_filter = self.show_query_dialog(filter_config)
        if updated_filter:
            # Disable query button during operation
            if self.query_button:
                self.query_button.config(state="disabled")
            self._update_status("Querying...")

            # Show progress dialog on main thread
            progress_dialog = self.show_progress_dialog("Querying", "Searching resources...")

            def query_thread():
                if self.zinfo_app is None or self.root is None or self.zinfo_app.cache is None:
                    return
                    
                try:
                    # Parse dates (no GUI operations)
                    after_date = None
                    before_date = None

                    if updated_filter.after_date:
                        from zinfo.core.cache import parse_date
                        after_date = parse_date(updated_filter.after_date)

                    if updated_filter.before_date:
                        from zinfo.core.cache import parse_date
                        before_date = parse_date(updated_filter.before_date)

                    # Run search (core logic only, no GUI)
                    results = self.zinfo_app.cache.search_resources(
                        title=updated_filter.title,
                        author=updated_filter.author,
                        metadata_type=updated_filter.metadata_type,
                        limit=updated_filter.limit,
                        after_date=after_date,
                        before_date=before_date,
                        date_field=updated_filter.date_field
                    )

                    # Schedule GUI updates on main thread
                    def _update_success():
                        try:
                            progress_dialog.update_progress(100, 100, f"Found {len(results)} results")
                            progress_dialog.close()
                            self.show_results_table(results)
                        finally:
                            if self.query_button:
                                self.query_button.config(state="normal")
                            self._update_status("Ready")

                    if self.root:
                        self.root.after(0, _update_success)

                except Exception as e:
                    logger.error(f"Error during query: {e}")
                    error_str = str(e)
                    def _update_error():
                        try:
                            progress_dialog.close()
                        except:
                            pass
                        self.show_error_message("Query Error", f"An error occurred during query:\n{error_str}")
                        if self.query_button:
                            self.query_button.config(state="normal")
                        self._update_status("Ready")
                    if self.root:
                        self.root.after(0, _update_error)

            thread = threading.Thread(target=query_thread, daemon=True)
            thread.start()

    def _on_settings_pressed(self) -> None:
        """Handle settings button press."""
        if self.zinfo_app:
            self.zinfo_app.show_settings_dialog()

    def _on_about_pressed(self) -> None:
        """Handle about button press."""
        if self.zinfo_app:
            self.zinfo_app.show_about_dialog()
