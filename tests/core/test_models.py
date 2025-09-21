"""Test suite for core data models."""

from datetime import datetime
from pathlib import Path

from zinfo.core.models import ResourceMetadata, ScanResult


def test_resource_metadata_basic():
    """Test basic ResourceMetadata creation and attributes."""
    metadata = ResourceMetadata(
        id="test/path",
        title="Test Resource",
        link="file://test.txt",
        contact="test@example.com",
    )

    assert metadata.id == "test/path"
    assert metadata.title == "Test Resource"
    assert metadata.link == "file://test.txt"
    assert metadata.contact == "test@example.com"
    assert metadata.doc_dir is None
    assert metadata.metadata_type == "resource"
    assert metadata.extra is None


def test_resource_metadata_with_optional():
    """Test ResourceMetadata with optional fields."""
    now = datetime.now()
    doc_dir = Path("/test/docs")
    extra = {"key": "value"}

    metadata = ResourceMetadata(
        id="test/path",
        title="Test Resource",
        link="file://test.txt",
        contact="test@example.com",
        doc_dir=doc_dir,
        last_modified=now,
        last_indexed=now,
        extra=extra,
    )

    assert metadata.doc_dir == doc_dir
    assert metadata.last_modified == now
    assert metadata.last_indexed == now
    assert metadata.extra == extra


def test_scan_result():
    """Test ScanResult creation and attributes."""
    start_time = datetime.now()
    end_time = datetime.now()

    metadata = ResourceMetadata(
        id="test/path",
        title="Test Resource",
        link="file://test.txt",
        contact="test@example.com",
    )

    result = ScanResult(
        items=[metadata],
        errors=["Test error"],
        start_time=start_time,
        end_time=end_time,
        total_dirs_scanned=10,
        total_items_found=1,
    )

    assert len(result.items) == 1
    assert result.items[0] == metadata
    assert len(result.errors) == 1
    assert result.errors[0] == "Test error"
    assert result.start_time == start_time
    assert result.end_time == end_time
    assert result.total_dirs_scanned == 10
    assert result.total_items_found == 1
