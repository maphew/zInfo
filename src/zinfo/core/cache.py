"""SQLite cache management for zinfo.

Provides caching functionality to store scan results and metadata,
enabling faster lookups and change detection.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import json
import logging

from .models import ResourceMetadata, ScanResult

logger = logging.getLogger(__name__)


def adapt_datetime(dt):
    """Convert datetime to string for SQLite."""
    return dt.isoformat() if dt else None


def convert_datetime(s):
    """Convert string from SQLite to datetime."""
    return datetime.fromisoformat(s.decode()) if s else None


sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("TIMESTAMP", convert_datetime)


class Cache:
    """SQLite-based cache for scan results."""

    def __init__(self, db_path: Path, timeout: float = 30.0):
        """Initialize cache with database path."""
        self.db_path = db_path
        self.timeout = timeout
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(
            self.db_path, timeout=self.timeout, detect_types=sqlite3.PARSE_DECLTYPES
        )
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS resources (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    link TEXT NOT NULL,
                    contact TEXT NOT NULL,
                    doc_dir TEXT,
                    metadata_type TEXT NOT NULL,
                    last_modified TIMESTAMP,
                    last_indexed TIMESTAMP NOT NULL,
                    extra JSON
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    total_dirs_scanned INTEGER NOT NULL,
                    total_items_found INTEGER NOT NULL,
                    errors JSON
                )
            """
            )
            conn.commit()
        finally:
            conn.close()

    def store_resource(self, resource: ResourceMetadata):
        """Store or update a resource in the cache."""
        conn = sqlite3.connect(
            self.db_path, timeout=self.timeout, detect_types=sqlite3.PARSE_DECLTYPES
        )
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO resources
                (id, title, link, contact, doc_dir, metadata_type,
                 last_modified, last_indexed, extra)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    resource.id,
                    resource.title,
                    resource.link,
                    resource.contact,
                    str(resource.doc_dir) if resource.doc_dir else None,
                    resource.metadata_type,
                    resource.last_modified,
                    resource.last_indexed or datetime.now(),
                    json.dumps(resource.extra) if resource.extra else None,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def store_scan_result(self, result: ScanResult):
        """Store scan results and update all resources."""
        conn = sqlite3.connect(
            self.db_path, timeout=self.timeout, detect_types=sqlite3.PARSE_DECLTYPES
        )
        try:
            # Store all resources first
            for item in result.items:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO resources
                    (id, title, link, contact, doc_dir, metadata_type,
                     last_modified, last_indexed, extra)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        item.id,
                        item.title,
                        item.link,
                        item.contact,
                        str(item.doc_dir) if item.doc_dir else None,
                        item.metadata_type,
                        item.last_modified,
                        item.last_indexed or datetime.now(),
                        json.dumps(item.extra) if item.extra else None,
                    ),
                )

            # Store scan metadata
            conn.execute(
                """
                INSERT INTO scans
                (start_time, end_time, total_dirs_scanned,
                 total_items_found, errors)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    result.start_time,
                    result.end_time,
                    result.total_dirs_scanned,
                    result.total_items_found,
                    json.dumps(result.errors),
                ),
            )

            conn.commit()
        finally:
            conn.close()

    def get_resource(self, id: str) -> Optional[ResourceMetadata]:
        """Retrieve a resource by ID."""
        conn = sqlite3.connect(
            self.db_path, timeout=self.timeout, detect_types=sqlite3.PARSE_DECLTYPES
        )
        try:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM resources WHERE id = ?", (id,)).fetchone()

            if row:
                return self._row_to_resource(row)
            return None
        finally:
            conn.close()

    def get_resources_by_type(self, metadata_type: str) -> List[ResourceMetadata]:
        """Retrieve all resources of a specific type."""
        conn = sqlite3.connect(
            self.db_path, timeout=self.timeout, detect_types=sqlite3.PARSE_DECLTYPES
        )
        try:
            conn.row_factory = sqlite3.Row
            resources = []
            for row in conn.execute(
                "SELECT * FROM resources WHERE metadata_type = ?", (metadata_type,)
            ):
                resources.append(self._row_to_resource(row))
            return resources
        finally:
            conn.close()

    def get_latest_scan(self) -> Optional[ScanResult]:
        """Get the most recent scan result."""
        conn = sqlite3.connect(
            self.db_path, timeout=self.timeout, detect_types=sqlite3.PARSE_DECLTYPES
        )
        try:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT * FROM scans
                ORDER BY start_time DESC
                LIMIT 1
            """
            ).fetchone()

            if row:
                return ScanResult(
                    items=self.get_resources_by_type("resource"),
                    errors=json.loads(row["errors"]),
                    start_time=row["start_time"],
                    end_time=row["end_time"],
                    total_dirs_scanned=row["total_dirs_scanned"],
                    total_items_found=row["total_items_found"],
                )
            return None
        finally:
            conn.close()

    @staticmethod
    def _row_to_resource(row: sqlite3.Row) -> ResourceMetadata:
        """Convert a database row to a ResourceMetadata object."""
        return ResourceMetadata(
            id=row["id"],
            title=row["title"],
            link=row["link"],
            contact=row["contact"],
            doc_dir=Path(row["doc_dir"]) if row["doc_dir"] else None,
            metadata_type=row["metadata_type"],
            last_modified=row["last_modified"],
            last_indexed=row["last_indexed"],
            extra=json.loads(row["extra"]) if row["extra"] else None,  # type: ignore
        )
