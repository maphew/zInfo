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
import re

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


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string supporting multiple formats and partial dates.

    Supports formats like:
    - 2024 (year only)
    - 2024-01 (year-month)
    - 2024-01-15 (full date)
    - 2024-01-15 14:30 (date with time)
    """
    if not date_str or not date_str.strip():
        return None

    date_str = date_str.strip()

    # Handle year only (YYYY)
    if re.match(r'^\d{4}$', date_str):
        return datetime(int(date_str), 1, 1)

    # Handle year-month (YYYY-MM)
    if re.match(r'^\d{4}-\d{2}$', date_str):
        year, month = map(int, date_str.split('-'))
        return datetime(year, month, 1)

    # Handle full date (YYYY-MM-DD)
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        year, month, day = map(int, date_str.split('-'))
        return datetime(year, month, day)

    # Handle date with time (YYYY-MM-DD HH:MM or YYYY-MM-DD HH:MM:SS)
    if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}', date_str):
        parts = date_str.split()
        date_part = parts[0]
        time_part = parts[1]

        year, month, day = map(int, date_part.split('-'))
        hour, minute = map(int, time_part.split(':'))

        # Handle optional seconds
        second = 0
        if len(time_part.split(':')) > 2:
            second = int(time_part.split(':')[2])

        return datetime(year, month, day, hour, minute, second)

    # Try standard datetime parsing as fallback
    try:
        return datetime.fromisoformat(date_str.replace(' ', 'T'))
    except ValueError:
        logger.warning(f"Could not parse date: {date_str}")
        return None


def extract_date_from_metadata(optional_fields: Optional[dict], date_field: str) -> Optional[datetime]:
    """Extract and parse date from metadata optional_fields."""
    if not optional_fields or date_field not in optional_fields:
        return None

    date_value = optional_fields[date_field]
    if isinstance(date_value, str):
        return parse_date(date_value)
    elif isinstance(date_value, (int, float)):
        # Handle Unix timestamps
        try:
            return datetime.fromtimestamp(date_value)
        except (OSError, ValueError):
            return None

    return None


class Cache:
    """SQLite-based cache for scan results."""

    def __init__(self, db_path: Path, timeout: float = 30.0):
        """Initialize cache with database path."""
        self.db_path = db_path
        self.timeout = timeout
        self._init_db()

    def _init_db(self):
        """Initialize database schema if not already initialized."""
        conn = sqlite3.connect(
            self.db_path, timeout=self.timeout, detect_types=sqlite3.PARSE_DECLTYPES
        )
        try:
            # Check if schema is already initialized
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_versions'")
            if cursor.fetchone():
                # Schema already exists, don't reinitialize
                return

            # Drop existing tables for clean break (only if we're initializing fresh)
            conn.execute("DROP TABLE IF EXISTS resources")
            conn.execute("DROP TABLE IF EXISTS scans")
            conn.execute("DROP TABLE IF EXISTS schema_versions")

            # Create new resources table with updated schema
            conn.execute(
                """
                CREATE TABLE resources (
                    -- System fields
                    dir_id TEXT PRIMARY KEY,
                    dir_path TEXT NOT NULL,

                    -- Required fields
                    title TEXT NOT NULL,
                    shortname TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    client TEXT NOT NULL,
                    team TEXT NOT NULL,
                    contact_email TEXT NOT NULL,
                    location TEXT NOT NULL,

                    -- System timestamps
                    last_modified TIMESTAMP,
                    last_indexed TIMESTAMP NOT NULL,
                    metadata_type TEXT NOT NULL,

                    -- JSON fields for structured optional/custom data
                    optional_fields JSON,
                    custom_fields JSON
                )
            """
            )

            # Recreate scans table (keeping existing structure)
            conn.execute(
                """
                CREATE TABLE scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    total_dirs_scanned INTEGER NOT NULL,
                    total_items_found INTEGER NOT NULL,
                    errors JSON
                )
            """
            )

            # Create schema version tracking table
            conn.execute(
                """
                CREATE TABLE schema_versions (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP NOT NULL
                )
            """
            )

            # Record schema version 1
            conn.execute(
                "INSERT INTO schema_versions (version, applied_at) VALUES (1, ?)",
                (datetime.now(),)
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
                (dir_id, dir_path, title, shortname, summary, client, team,
                 contact_email, location, last_modified, last_indexed,
                 metadata_type, optional_fields, custom_fields)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    resource.dir_id,
                    resource.dir_path,
                    resource.title,
                    resource.shortname,
                    resource.summary,
                    resource.client,
                    resource.team,
                    resource.contact_email,
                    resource.location,
                    resource.last_modified,
                    resource.last_indexed or datetime.now(),
                    resource.metadata_type,
                    json.dumps(resource.optional_fields) if resource.optional_fields else None,
                    json.dumps(resource.custom_fields) if resource.custom_fields else None,
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
                    (dir_id, dir_path, title, shortname, summary, client, team,
                     contact_email, location, last_modified, last_indexed,
                     metadata_type, optional_fields, custom_fields)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        item.dir_id,
                        item.dir_path,
                        item.title,
                        item.shortname,
                        item.summary,
                        item.client,
                        item.team,
                        item.contact_email,
                        item.location,
                        item.last_modified,
                        item.last_indexed or datetime.now(),
                        item.metadata_type,
                        json.dumps(item.optional_fields) if item.optional_fields else None,
                        json.dumps(item.custom_fields) if item.custom_fields else None,
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

    def get_resource(self, dir_id: str) -> Optional[ResourceMetadata]:
        """Retrieve a resource by dir_id."""
        conn = sqlite3.connect(
            self.db_path, timeout=self.timeout, detect_types=sqlite3.PARSE_DECLTYPES
        )
        try:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM resources WHERE dir_id = ?", (dir_id,)).fetchone()

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
                    items=self.get_resources_by_type("zinfo_project"),
                    errors=json.loads(row["errors"]),
                    start_time=row["start_time"],
                    end_time=row["end_time"],
                    total_dirs_scanned=row["total_dirs_scanned"],
                    total_items_found=row["total_items_found"],
                )
            return None
        finally:
            conn.close()

    def search_resources(
        self,
        title: Optional[str] = None,
        author: Optional[str] = None,
        shortname: Optional[str] = None,
        client: Optional[str] = None,
        team: Optional[str] = None,
        metadata_type: Optional[str] = None,
        dir_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        after_date: Optional[datetime] = None,
        before_date: Optional[datetime] = None,
        date_field: str = "created"  # Field to use for date filtering: created, updated, last_modified, last_indexed
    ) -> tuple[List[ResourceMetadata], int]:
        """Search resources with flexible filtering options."""
        conn = sqlite3.connect(
            self.db_path, timeout=self.timeout, detect_types=sqlite3.PARSE_DECLTYPES
        )
        try:
            conn.row_factory = sqlite3.Row

            # Build query dynamically
            query_parts = ["SELECT * FROM resources WHERE 1=1"]
            params = []

            if title:
                query_parts.append("AND title LIKE ?")
                params.append(f"%{title}%")

            if author:
                query_parts.append("AND team LIKE ?")
                params.append(f"%{author}%")

            if shortname:
                query_parts.append("AND shortname LIKE ?")
                params.append(f"%{shortname}%")

            if client:
                query_parts.append("AND client LIKE ?")
                params.append(f"%{client}%")

            if team:
                query_parts.append("AND team LIKE ?")
                params.append(f"%{team}%")

            if metadata_type:
                query_parts.append("AND metadata_type = ?")
                params.append(metadata_type)

            if dir_id:
                query_parts.append("AND dir_id LIKE ?")
                params.append(f"%{dir_id}%")

            # Search in JSON fields for optional/custom data
            if author or title or shortname or client or team:
                search_terms = []
                search_params = []
                if author:
                    search_terms.append("(optional_fields LIKE ? OR custom_fields LIKE ?)")
                    search_params.extend([f"%{author}%", f"%{author}%"])
                if title:
                    search_terms.append("(optional_fields LIKE ? OR custom_fields LIKE ?)")
                    search_params.extend([f"%{title}%", f"%{title}%"])
                if shortname:
                    search_terms.append("(optional_fields LIKE ? OR custom_fields LIKE ?)")
                    search_params.extend([f"%{shortname}%", f"%{shortname}%"])
                if client:
                    search_terms.append("(optional_fields LIKE ? OR custom_fields LIKE ?)")
                    search_params.extend([f"%{client}%", f"%{client}%"])
                if team:
                    search_terms.append("(optional_fields LIKE ? OR custom_fields LIKE ?)")
                    search_params.extend([f"%{team}%", f"%{team}%"])

                if search_terms:
                    query_parts.append(f"OR ({' OR '.join(search_terms)})")
                    params.extend(search_params)

            # Handle date filtering
            if after_date or before_date:
                if date_field in ["last_modified", "last_indexed"]:
                    # Use database datetime fields
                    if after_date:
                        query_parts.append(f"AND {date_field} >= ?")
                        params.append(after_date)
                    if before_date:
                        query_parts.append(f"AND {date_field} <= ?")
                        params.append(before_date)
                else:
                    # Use metadata fields from JSON optional_fields
                    # This requires a more complex query since we need to parse JSON
                    if after_date:
                        query_parts.append(f"AND (optional_fields->>'{date_field}' IS NOT NULL AND datetime(optional_fields->>'{date_field}') >= ?)")
                        params.append(after_date.isoformat())
                    if before_date:
                        query_parts.append(f"AND (optional_fields->>'{date_field}' IS NOT NULL AND datetime(optional_fields->>'{date_field}') <= ?)")
                        params.append(before_date.isoformat())

            query_parts.append("ORDER BY last_indexed DESC")

            if limit:
                query_parts.append("LIMIT ?")
                params.append(limit)

            if offset:
                query_parts.append("OFFSET ?")
                params.append(offset)

            query = " ".join(query_parts)
            logger.debug(f"Executing search query: {query} with params: {params}")

            # Build count query (without ORDER BY, LIMIT, OFFSET)
            order_by_index = query_parts.index("ORDER BY last_indexed DESC")
            count_query = " ".join(query_parts[:order_by_index]).replace("SELECT * ", "SELECT COUNT(*) ", 1)
            params_count = params
            if offset:
                params_count = params[:-1]  # remove offset
            if limit:
                params_count = params_count[:-1]  # remove limit

            total_count = conn.execute(count_query, params_count).fetchone()[0]

            resources = []
            for row in conn.execute(query, params):
                resource = self._row_to_resource(row)

                # Additional filtering for metadata date fields (since JSON parsing in SQL is limited)
                if date_field not in ["last_modified", "last_indexed"]:
                    if after_date or before_date:
                        metadata_date = extract_date_from_metadata(resource.optional_fields, date_field)
                        if metadata_date:
                            if after_date and metadata_date < after_date:
                                continue
                            if before_date and metadata_date > before_date:
                                continue

                resources.append(resource)

            return resources, total_count
        finally:
            conn.close()

    def get_all_resources(self, limit: Optional[int] = None, offset: Optional[int] = None) -> tuple[List[ResourceMetadata], int]:
        """Get all resources in the cache with optional pagination."""
        conn = sqlite3.connect(
            self.db_path, timeout=self.timeout, detect_types=sqlite3.PARSE_DECLTYPES
        )
        try:
            conn.row_factory = sqlite3.Row

            # Get total count
            total_count = conn.execute("SELECT COUNT(*) FROM resources").fetchone()[0]

            # Build query with pagination
            query = "SELECT * FROM resources ORDER BY last_indexed DESC"
            params = []
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            if offset:
                query += " OFFSET ?"
                params.append(offset)

            resources = []
            for row in conn.execute(query, params):
                resources.append(self._row_to_resource(row))
            return resources, total_count
        finally:
            conn.close()

    def get_resource_count(self) -> int:
        """Get total count of resources in the cache."""
        conn = sqlite3.connect(
            self.db_path, timeout=self.timeout, detect_types=sqlite3.PARSE_DECLTYPES
        )
        try:
            return conn.execute("SELECT COUNT(*) FROM resources").fetchone()[0]
        finally:
            conn.close()

    @staticmethod
    def _row_to_resource(row: sqlite3.Row) -> ResourceMetadata:
        """Convert a database row to a ResourceMetadata object."""
        return ResourceMetadata(
            dir_id=row["dir_id"],
            dir_path=row["dir_path"],
            title=row["title"],
            shortname=row["shortname"],
            summary=row["summary"],
            client=row["client"],
            team=row["team"],
            contact_email=row["contact_email"],
            location=row["location"],
            last_modified=row["last_modified"],
            last_indexed=row["last_indexed"],
            metadata_type=row["metadata_type"],
            optional_fields=json.loads(row["optional_fields"]) if row["optional_fields"] else None,
            custom_fields=json.loads(row["custom_fields"]) if row["custom_fields"] else None,
        )
