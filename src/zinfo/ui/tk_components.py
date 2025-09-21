"""Tkinter-specific UI components for zinfo.

This module contains reusable Tk UI components that implement the abstract interfaces.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, simpledialog, filedialog, messagebox
from pathlib import Path
from typing import Optional, List, Dict

from zinfo.core.models import ResourceMetadata
from . import ScanConfig, QueryFilter


class ZinfoTable:
    """A table widget for displaying ResourceMetadata objects using ttk.Treeview."""

    def __init__(self, parent: tk.Widget | None = None):
        """Initialize the table widget.

        Args:
            parent: Tk parent widget (Frame/Window). If None, a new Frame will be created lazily.
        """
        self.parent = parent
        self.frame: Optional[tk.Frame] = None
        self.tree: Optional[ttk.Treeview] = None
        self._data: List[ResourceMetadata] = []
        self._row_map: Dict[str, ResourceMetadata] = {}

        if self.parent is not None:
            self._create_widgets(self.parent)

    def widget(self) -> tk.Widget:
        """Return the top-level widget (Frame) for packing/placing into layouts."""
        if self.frame is None:
            if self.parent is None:
                raise RuntimeError("ZinfoTable requires a parent widget")
            self._create_widgets(self.parent)
        return self.frame  # type: ignore[return-value]

    def _create_widgets(self, parent: tk.Widget) -> None:
        self.frame = tk.Frame(parent)
        columns = ("id", "title", "contact", "type", "lastmod")
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings", height=12)

        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Title")
        self.tree.heading("contact", text="Contact")
        self.tree.heading("type", text="Type")
        self.tree.heading("lastmod", text="Last Modified")

        # Reasonable default widths
        self.tree.column("id", width=250, anchor="w")
        self.tree.column("title", width=260, anchor="w")
        self.tree.column("contact", width=200, anchor="w")
        self.tree.column("type", width=100, anchor="w")
        self.tree.column("lastmod", width=140, anchor="w")

        vsb = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

    def set_data(self, data: List[ResourceMetadata]) -> None:
        """Set the data to display in the table.

        Args:
            data: List of ResourceMetadata objects to display
        """
        self._data = list(data)
        self._refresh_table()

    def _refresh_table(self) -> None:
        """Refresh the table display with current data."""
        if self.tree is None:
            return

        # Clear existing rows
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self._row_map.clear()

        # Add data rows
        for item in self._data:
            # Truncate long fields for display to align with Toga behavior
            id_val = item.id or ""
            title_val = item.title or ""
            contact_val = item.contact or ""
            id_short = (id_val[:30] + "...") if len(id_val) > 33 else id_val
            title_short = (title_val[:35] + "...") if len(title_val) > 38 else title_val
            contact_short = (contact_val[:25] + "...") if len(contact_val) > 28 else contact_val
            lastmod = item.last_modified.strftime("%Y-%m-%d %H:%M") if item.last_modified else "N/A"

            values = (id_short, title_short, contact_short, item.metadata_type, lastmod)
            iid = self.tree.insert("", "end", values=values)
            self._row_map[iid] = item

    def get_selected_items(self) -> List[ResourceMetadata]:
        """Get the currently selected items."""
        if self.tree is None:
            return []
        selected = []
        for iid in self.tree.selection():
            meta = self._row_map.get(iid)
            if meta is not None:
                selected.append(meta)
        return selected

    def refresh(self) -> None:
        """Refresh the table display."""
        self._refresh_table()

    def set_filter(self, filter_text: str) -> None:
        """Apply a filter to the table data. Currently a no-op; just refresh."""
        # Placeholder for future filtering
        self._refresh_table()


def show_scan_dialog(root: tk.Misc, config: ScanConfig) -> Optional[ScanConfig]:
    """Show a scan configuration dialog.

    A minimal implementation using standard dialogs:
    - Ask for root directory via filedialog.askdirectory
    - Ask for max depth via simpledialog.askinteger
    - Ask for cache path via simpledialog.askstring
    """
    # Root directory
    initialdir = str(config.root_path) if config.root_path else "."
    root_path_str = filedialog.askdirectory(parent=root, initialdir=initialdir, title="Select Root Directory")
    if not root_path_str:
        return None

    # Max depth
    try:
        default_depth = int(config.max_depth or 5)
    except Exception:
        default_depth = 5
    depth = simpledialog.askinteger("Max Depth", "Enter maximum scan depth (1-10):",
                                    initialvalue=default_depth, minvalue=1, maxvalue=10, parent=root)
    if depth is None:
        return None

    # Cache path
    default_cache = str(config.cache_path) if config.cache_path else "zinfo.db"
    cache_path_str = simpledialog.askstring("Cache Database", "Enter cache database path:",
                                            initialvalue=default_cache, parent=root)
    if cache_path_str is None:
        return None

    # Validate root exists
    root_path = Path(root_path_str)
    if not root_path.exists():
        messagebox.showerror("Invalid Path", f"Root directory does not exist: {root_path}", parent=root)
        return None

    return ScanConfig(
        root_path=root_path,
        max_depth=int(depth),
        cache_path=Path(cache_path_str) if cache_path_str else None,
    )


def show_query_dialog(root: tk.Misc, filter_config: QueryFilter) -> Optional[QueryFilter]:
    """Show a query filter dialog using simple dialogs."""
    title = simpledialog.askstring("Title Filter", "Filter by title:",
                                   initialvalue=filter_config.title or "", parent=root)
    if title is None:
        return None

    author = simpledialog.askstring("Author Filter", "Filter by author:",
                                    initialvalue=filter_config.author or "", parent=root)
    if author is None:
        return None

    mtype = simpledialog.askstring("Type Filter", "Filter by type:",
                                   initialvalue=filter_config.metadata_type or "", parent=root)
    if mtype is None:
        return None

    try:
        default_limit = int(filter_config.limit or 50)
    except Exception:
        default_limit = 50

    limit = simpledialog.askinteger("Limit", "Maximum results:",
                                    initialvalue=default_limit, minvalue=1, maxvalue=1000, parent=root)
    if limit is None:
        return None

    return QueryFilter(
        title=title or None,
        author=author or None,
        metadata_type=mtype or None,
        limit=int(limit),
        after_date=filter_config.after_date,
        before_date=filter_config.before_date,
        date_field=filter_config.date_field,
    )
