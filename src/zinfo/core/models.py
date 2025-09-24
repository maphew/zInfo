"""Core data models for zinfo.

These models represent the fundamental data structures used throughout the application.
They provide a common interface for different metadata providers and output generators.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List


@dataclass
class ResourceMetadata:
    """Metadata for zInfo project resources."""

    # System fields (computed)
    dir_id: str  # 6+ char hash
    dir_path: str  # fully resolved path

    # Required fields
    title: str  # soft max 50
    shortname: str  # soft max 15
    summary: str  # soft max 150
    client: str
    team: str  # semicolon-delimited
    contact_email: str
    location: str  # relative path to zinfo file

    # System timestamps
    last_modified: Optional[datetime] = None
    last_indexed: Optional[datetime] = None
    metadata_type: str = "zinfo_project"

    # Optional structured fields
    optional_fields: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class ScanResult:
    """Results from a directory scan."""

    items: List[ResourceMetadata]
    errors: List[str]
    start_time: datetime
    end_time: datetime
    total_dirs_scanned: int
    total_items_found: int
