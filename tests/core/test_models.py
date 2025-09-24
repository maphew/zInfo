"""Test suite for core data models."""

from datetime import datetime
from pathlib import Path

from zinfo.core.models import ResourceMetadata, ScanResult
from zinfo.core.id_generator import DirIDGenerator


def test_resource_metadata_basic():
    """Test basic ResourceMetadata creation and attributes."""
    metadata = ResourceMetadata(
        dir_id="test123",
        dir_path="/test/path",
        title="Test Resource",
        shortname="Test",
        summary="A test resource",
        client="Test Client",
        team="Test Team",
        contact_email="test@example.com",
        location="zinfo.txt",
    )

    assert metadata.dir_id == "test123"
    assert metadata.dir_path == "/test/path"
    assert metadata.title == "Test Resource"
    assert metadata.shortname == "Test"
    assert metadata.summary == "A test resource"
    assert metadata.client == "Test Client"
    assert metadata.team == "Test Team"
    assert metadata.contact_email == "test@example.com"
    assert metadata.location == "zinfo.txt"
    assert metadata.metadata_type == "zinfo_project"
    assert metadata.optional_fields is None
    assert metadata.custom_fields is None


def test_resource_metadata_with_optional():
    """Test ResourceMetadata with optional fields."""
    now = datetime.now()
    optional_fields = {"created": "2024-01-15"}
    custom_fields = {"custom": "value"}

    metadata = ResourceMetadata(
        dir_id="test123",
        dir_path="/test/path",
        title="Test Resource",
        shortname="Test",
        summary="A test resource",
        client="Test Client",
        team="Test Team",
        contact_email="test@example.com",
        location="zinfo.txt",
        last_modified=now,
        last_indexed=now,
        optional_fields=optional_fields,
        custom_fields=custom_fields,
    )

    assert metadata.last_modified == now
    assert metadata.last_indexed == now
    assert metadata.optional_fields == optional_fields
    assert metadata.custom_fields == custom_fields


def test_resource_metadata_field_validation():
    """Test ResourceMetadata field validation."""
    # Test required fields are present
    metadata = ResourceMetadata(
        dir_id="test123",
        dir_path="/test/path",
        title="Test Resource",
        shortname="Test",
        summary="A test resource",
        client="Test Client",
        team="Test Team",
        contact_email="test@example.com",
        location="zinfo.txt",
    )

    # All required fields should be strings
    assert isinstance(metadata.title, str)
    assert isinstance(metadata.shortname, str)
    assert isinstance(metadata.summary, str)
    assert isinstance(metadata.client, str)
    assert isinstance(metadata.team, str)
    assert isinstance(metadata.contact_email, str)
    assert isinstance(metadata.location, str)

    # System fields
    assert isinstance(metadata.dir_id, str)
    assert isinstance(metadata.dir_path, str)


def test_dir_id_generation():
    """Test dir_id generation for ResourceMetadata."""
    generator = DirIDGenerator()

    # Generate dir_id for a test path
    test_path = "/test/project/path"
    dir_id = generator.generate(test_path)

    assert isinstance(dir_id, str)
    assert len(dir_id) >= 6  # Should be 6+ characters

    # Same path with new generator should generate same dir_id
    generator2 = DirIDGenerator()
    dir_id2 = generator2.generate(test_path)
    assert dir_id == dir_id2

    # Different path should generate different dir_id
    different_path = "/different/path"
    dir_id3 = generator.generate(different_path)
    assert dir_id != dir_id3


def test_scan_result():
    """Test ScanResult creation and attributes."""
    start_time = datetime.now()
    end_time = datetime.now()

    metadata = ResourceMetadata(
        dir_id="test123",
        dir_path="/test/path",
        title="Test Resource",
        shortname="Test",
        summary="A test resource",
        client="Test Client",
        team="Test Team",
        contact_email="test@example.com",
        location="zinfo.txt",
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
