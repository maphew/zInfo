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
    """Base metadata for any indexed resource."""

    id: str  # Unique identifier (e.g., relative path)
    title: str
    link: str
    contact: str
    doc_dir: Optional[Path] = None
    last_modified: Optional[datetime] = None
    last_indexed: Optional[datetime] = None
    metadata_type: str = "resource"  # For polymorphic handling
    extra: Optional[Dict[str, Any]] = None  # Additional metadata fields


@dataclass
class ScanResult:
    """Results from a directory scan."""

    items: List[ResourceMetadata]
    errors: List[str]
    start_time: datetime
    end_time: datetime
    total_dirs_scanned: int
    total_items_found: int
