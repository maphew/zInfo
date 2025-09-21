"""Test suite for SQLite cache functionality."""

from datetime import datetime
from pathlib import Path
import pytest
import tempfile

from zinfo.core.models import ResourceMetadata, ScanResult
from zinfo.core.cache import Cache


@pytest.fixture
def temp_db():
    """Create a temporary database file."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    yield db_path

    try:
        db_path.unlink()
    except PermissionError:
        pass  # Ignore Windows file locking issues


@pytest.fixture
def cache(temp_db):
    """Create a Cache instance with temporary database."""
    return Cache(temp_db)


@pytest.fixture
def sample_resource():
    """Create a sample resource for testing."""
    return ResourceMetadata(
        id="test/resource1",
        title="Test Resource",
        link="file://test.txt",
        contact="test@example.com",
        doc_dir=Path("/test/docs"),
        last_modified=datetime.now(),
        last_indexed=datetime.now(),
        extra={"key": "value"},
    )


@pytest.fixture
def sample_scan_result(sample_resource):
    """Create a sample scan result for testing."""
    return ScanResult(
        items=[sample_resource],
        errors=["Test error"],
        start_time=datetime.now(),
        end_time=datetime.now(),
        total_dirs_scanned=10,
        total_items_found=1,
    )


def test_cache_init(cache):
    """Test cache initialization creates tables."""
    assert cache.db_path.exists()


def test_store_resource(cache, sample_resource):
    """Test storing and retrieving a resource."""
    cache.store_resource(sample_resource)
    retrieved = cache.get_resource(sample_resource.id)

    assert retrieved is not None
    assert retrieved.id == sample_resource.id
    assert retrieved.title == sample_resource.title
    assert retrieved.link == sample_resource.link
    assert retrieved.contact == sample_resource.contact
    assert retrieved.doc_dir == sample_resource.doc_dir
    assert retrieved.extra == sample_resource.extra


def test_store_scan_result(cache, sample_scan_result):
    """Test storing and retrieving scan results."""
    cache.store_scan_result(sample_scan_result)
    latest = cache.get_latest_scan()

    assert latest is not None
    assert len(latest.items) == 1
    assert latest.total_dirs_scanned == sample_scan_result.total_dirs_scanned
    assert latest.total_items_found == sample_scan_result.total_items_found
    assert latest.errors == sample_scan_result.errors


def test_get_resources_by_type(cache, sample_resource):
    """Test retrieving resources by type."""
    cache.store_resource(sample_resource)

    resources = list(cache.get_resources_by_type("resource"))
    assert len(resources) == 1
    assert resources[0].id == sample_resource.id


def test_resource_not_found(cache):
    """Test retrieving non-existent resource."""
    assert cache.get_resource("nonexistent") is None


def test_latest_scan_not_found(cache):
    """Test retrieving latest scan when none exists."""
    assert cache.get_latest_scan() is None


def test_update_existing_resource(cache, sample_resource):
    """Test updating an existing resource."""
    cache.store_resource(sample_resource)

    # Modify and store again
    updated_resource = ResourceMetadata(
        id=sample_resource.id,  # Same ID
        title="Updated Title",
        link=sample_resource.link,
        contact=sample_resource.contact,
    )
    cache.store_resource(updated_resource)

    # Retrieve and verify
    retrieved = cache.get_resource(sample_resource.id)
    assert retrieved is not None
    assert retrieved.title == "Updated Title"
