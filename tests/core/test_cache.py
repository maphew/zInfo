"""Test suite for SQLite cache functionality."""

from datetime import datetime
from pathlib import Path
import pytest
import tempfile

from zinfo.core.models import ResourceMetadata, ScanResult
from zinfo.core.cache import Cache, parse_date, extract_date_from_metadata


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
        dir_id="test123",
        dir_path="/test/path",
        title="Test Resource",
        shortname="Test",
        summary="A test resource",
        client="Test Client",
        team="Test Team",
        contact_email="test@example.com",
        location="zinfo.txt",
        last_modified=datetime.now(),
        last_indexed=datetime.now(),
        optional_fields={"key": "value"},
        custom_fields={"custom": "data"},
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
    retrieved = cache.get_resource(sample_resource.dir_id)

    assert retrieved is not None
    assert retrieved.dir_id == sample_resource.dir_id
    assert retrieved.title == sample_resource.title
    assert retrieved.shortname == sample_resource.shortname
    assert retrieved.summary == sample_resource.summary
    assert retrieved.client == sample_resource.client
    assert retrieved.team == sample_resource.team
    assert retrieved.contact_email == sample_resource.contact_email
    assert retrieved.location == sample_resource.location
    assert retrieved.optional_fields == sample_resource.optional_fields
    assert retrieved.custom_fields == sample_resource.custom_fields


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

    resources = list(cache.get_resources_by_type("zinfo_project"))
    assert len(resources) == 1
    assert resources[0].dir_id == sample_resource.dir_id


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
        dir_id=sample_resource.dir_id,  # Same dir_id
        dir_path=sample_resource.dir_path,
        title="Updated Title",
        shortname=sample_resource.shortname,
        summary=sample_resource.summary,
        client=sample_resource.client,
        team=sample_resource.team,
        contact_email=sample_resource.contact_email,
        location=sample_resource.location,
    )
    cache.store_resource(updated_resource)

    # Retrieve and verify
    retrieved = cache.get_resource(sample_resource.dir_id)
    assert retrieved is not None
    assert retrieved.title == "Updated Title"


def test_search_resources_by_title(cache, sample_resource):
    """Test searching resources by title."""
    cache.store_resource(sample_resource)

    # Search by title
    results, _ = cache.search_resources(title="Test")
    assert len(results) == 1
    assert results[0].dir_id == sample_resource.dir_id

    # Search with no matches
    results, _ = cache.search_resources(title="Nonexistent")
    assert len(results) == 0


def test_search_resources_by_author(cache, sample_resource):
    """Test searching resources by author."""
    # Add author to team field
    resource_with_author = ResourceMetadata(
        dir_id="test456",
        dir_path="/test/path2",
        title="Resource with Author",
        shortname="Auth",
        summary="Resource with author",
        client="Test Client",
        team="John Doe",
        contact_email="test@example.com",
        location="zinfo.txt",
        optional_fields={"authors": "John Doe"}
    )
    cache.store_resource(resource_with_author)

    # Search by author (in team field)
    results, _ = cache.search_resources(author="John")
    assert len(results) == 1
    assert results[0].dir_id == "test456"

    # Search by team field directly
    results, _ = cache.search_resources(team="Doe")
    assert len(results) == 1
    assert results[0].dir_id == "test456"


def test_get_all_resources(cache, sample_resource):
    """Test getting all resources."""
    cache.store_resource(sample_resource)

    resources, _ = cache.get_all_resources()
    assert len(resources) == 1
    assert resources[0].dir_id == sample_resource.dir_id


def test_get_resource_count(cache, sample_resource):
    """Test getting resource count."""
    assert cache.get_resource_count() == 0

    cache.store_resource(sample_resource)
    assert cache.get_resource_count() == 1


def test_parse_date():
    """Test date parsing with various formats."""
    from datetime import datetime

    # Test year only
    assert parse_date("2024") == datetime(2024, 1, 1)

    # Test year-month
    assert parse_date("2024-01") == datetime(2024, 1, 1)

    # Test full date
    assert parse_date("2024-01-15") == datetime(2024, 1, 15)

    # Test date with time
    assert parse_date("2024-01-15 14:30") == datetime(2024, 1, 15, 14, 30)

    # Test ISO format
    assert parse_date("2024-01-15T14:30:00") == datetime(2024, 1, 15, 14, 30)

    # Test invalid date
    assert parse_date("invalid") is None
    assert parse_date("") is None
    assert parse_date(None) is None


def test_extract_date_from_metadata():
    """Test extracting dates from metadata."""
    from datetime import datetime

    # Test with valid date
    metadata = {"created": "2024-01-15"}
    assert extract_date_from_metadata(metadata, "created") == datetime(2024, 1, 15)

    # Test with year only
    metadata = {"created": "2024"}
    assert extract_date_from_metadata(metadata, "created") == datetime(2024, 1, 1)

    # Test with missing field
    assert extract_date_from_metadata(metadata, "missing") is None

    # Test with None metadata
    assert extract_date_from_metadata(None, "created") is None


def test_search_resources_with_date_filtering(cache):
    """Test searching resources with date filtering."""
    from datetime import datetime

    # Create resources with different dates
    resource1 = ResourceMetadata(
        dir_id="test111",
        dir_path="/test/path1",
        title="Resource 1",
        shortname="Res1",
        summary="First resource",
        client="Client A",
        team="Team A",
        contact_email="test@example.com",
        location="zinfo.txt",
        last_modified=datetime(2024, 1, 15),
        last_indexed=datetime.now(),
        optional_fields={"created": "2024-01-15"}
    )

    resource2 = ResourceMetadata(
        dir_id="test222",
        dir_path="/test/path2",
        title="Resource 2",
        shortname="Res2",
        summary="Second resource",
        client="Client B",
        team="Team B",
        contact_email="test@example.com",
        location="zinfo.txt",
        last_modified=datetime(2024, 6, 15),
        last_indexed=datetime.now(),
        optional_fields={"created": "2024-06-15"}
    )

    cache.store_resource(resource1)
    cache.store_resource(resource2)

    # Test filtering by metadata date (created)
    after_date = datetime(2024, 3, 1)
    results, _ = cache.search_resources(after_date=after_date, date_field="created")
    assert len(results) == 1
    assert results[0].dir_id == "test222"

    # Test filtering by database date (last_modified)
    results, _ = cache.search_resources(after_date=after_date, date_field="last_modified")
    assert len(results) == 1
    assert results[0].dir_id == "test222"

    # Test date range filtering
    before_date = datetime(2024, 3, 1)
    results, _ = cache.search_resources(
        after_date=datetime(2024, 1, 1),
        before_date=before_date,
        date_field="created"
    )
    assert len(results) == 1
    assert results[0].dir_id == "test111"
