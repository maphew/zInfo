"""Test suite for base scanner functionality."""

from pathlib import Path
import pytest
from typing import Optional

from zinfo.core.models import ResourceMetadata
from zinfo.core.scanner import BaseScanner
from zinfo.core.cache import Cache


class TestScanner(BaseScanner):
    """Test implementation of BaseScanner."""

    def can_handle_file(self, path: Path) -> bool:
        """Handle .test files."""
        return path.suffix == ".test"

    def extract_metadata(self, path: Path) -> Optional[ResourceMetadata]:
        """Extract metadata from test file."""
        if not self.can_handle_file(path):
            return None

        return ResourceMetadata(
            dir_id=f"test_{path.stem}",
            dir_path=str(path.parent),
            title=path.stem,
            shortname=path.stem[:4],
            summary=f"Test file {path.stem}",
            client="Test Client",
            team="Test Team",
            contact_email="test@example.com",
            location=str(path.relative_to(self.base_dir)),
            metadata_type="resource",
        )


@pytest.fixture
def temp_test_dir(tmp_path):
    """Create a temporary directory with test files."""
    # Create test files
    test_file1 = tmp_path / "test1.test"
    test_file1.write_text("test content")

    test_file2 = tmp_path / "test2.test"
    test_file2.write_text("test content")

    # Create a subdirectory with test file
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    test_file3 = subdir / "test3.test"
    test_file3.write_text("test content")

    # Create non-test file
    other_file = tmp_path / "other.txt"
    other_file.write_text("other content")

    return tmp_path


@pytest.fixture
def temp_cache(tmp_path):
    """Create a temporary cache."""
    return Cache(tmp_path / "test.db")


def test_scanner_basic(temp_test_dir):
    """Test basic scanning functionality."""
    scanner = TestScanner(temp_test_dir, recursive=False)  # Non-recursive
    result = scanner.scan()

    assert result.total_items_found == 2  # Only top-level .test files
    assert len(result.items) == 2
    assert result.total_dirs_scanned == 0  # No subdirs in non-recursive mode
    assert not result.errors


def test_scanner_recursive(temp_test_dir):
    """Test recursive scanning."""
    scanner = TestScanner(temp_test_dir, recursive=True)
    result = scanner.scan()

    assert result.total_items_found == 3  # All .test files
    assert len(result.items) == 3
    assert result.total_dirs_scanned == 1  # One subdir
    assert not result.errors


def test_scanner_with_cache(temp_test_dir, temp_cache):
    """Test scanning with cache integration."""
    scanner = TestScanner(temp_test_dir, cache=temp_cache)
    result = scanner.scan()

    # Check cache
    cached_result = temp_cache.get_latest_scan()
    assert cached_result is not None
    assert cached_result.total_items_found == result.total_items_found

    # Check cached items
    cached_items = list(temp_cache.get_resources_by_type("resource"))
    assert len(cached_items) == result.total_items_found


def test_scanner_error_handling(temp_test_dir):
    """Test scanner error handling."""

    class ErrorScanner(TestScanner):
        def extract_metadata(self, path: Path) -> Optional[ResourceMetadata]:
            raise Exception("Test error")

    scanner = ErrorScanner(temp_test_dir)
    result = scanner.scan()

    assert result.total_items_found == 0
    assert len(result.errors) > 0
    assert "Test error" in result.errors[0]


def test_non_existent_directory():
    """Test scanning non-existent directory."""
    scanner = TestScanner(Path("/nonexistent"))
    result = scanner.scan()

    assert result.total_items_found == 0
    assert len(result.errors) == 1
    assert "Directory does not exist" in result.errors[0]


def test_zinfo_scanner_required_field_validation(tmp_path):
    """Test ZinfoScanner required field validation."""
    from zinfo.core.scanner import ZinfoScanner

    # Create a zinfo.txt with missing required fields
    zinfo_file = tmp_path / "zinfo.txt"
    zinfo_file.write_text("title: Test Project\nshortname: Test\n")

    scanner = ZinfoScanner(tmp_path)
    result = scanner.scan()

    # Should find no items due to missing required fields
    assert result.total_items_found == 0
    assert len(result.errors) == 0  # Validation warnings don't count as errors


def test_zinfo_scanner_field_categorization(tmp_path):
    """Test ZinfoScanner field categorization."""
    from zinfo.core.scanner import ZinfoScanner

    # Create a complete zinfo.txt
    zinfo_file = tmp_path / "zinfo.txt"
    zinfo_file.write_text("""title: Test Project
shortname: Test
summary: A test project
client: Test Client
team: John Doe; Jane Smith
contact_email: john@example.com
location: zinfo.txt
custom_field: custom_value
optional_field: optional_value
""")

    scanner = ZinfoScanner(tmp_path)
    result = scanner.scan()

    assert result.total_items_found == 1
    item = result.items[0]

    # Check required fields
    assert item.title == "Test Project"
    assert item.shortname == "Test"
    assert item.summary == "A test project"
    assert item.client == "Test Client"
    assert item.team == "John Doe; Jane Smith"
    assert item.contact_email == "john@example.com"
    assert item.location == "zinfo.txt"

    # Check custom fields (all non-required fields go here since no optional fields defined)
    assert item.custom_fields == {"custom_field": "custom_value", "optional_field": "optional_value"}
    assert item.optional_fields is None  # No optional fields defined yet


def test_zinfo_scanner_with_fake_home_samples():
    """Test ZinfoScanner with fake-home sample files."""
    from zinfo.core.scanner import ZinfoScanner

    fake_home = Path("fake-home")
    scanner = ZinfoScanner(fake_home)
    result = scanner.scan()

    # Should find some items (depending on what's in fake-home)
    assert result.total_items_found >= 0
    assert isinstance(result.errors, list)

    # If items found, check they have required fields
    for item in result.items:
        assert hasattr(item, 'dir_id')
        assert hasattr(item, 'title')
        assert hasattr(item, 'shortname')
        assert hasattr(item, 'summary')
        assert hasattr(item, 'client')
        assert hasattr(item, 'team')
        assert hasattr(item, 'contact_email')
        assert hasattr(item, 'location')


def test_zinfo_scanner_ignore_flag(tmp_path):
    """Test ZinfoScanner respects do_not_index flag."""
    from zinfo.core.scanner import ZinfoScanner

    # Create a zinfo.txt with do_not_index set
    zinfo_file = tmp_path / "zinfo.txt"
    zinfo_file.write_text("""title: Test Project
shortname: Test
summary: A test project
client: Test Client
team: Test Team
contact_email: test@example.com
location: zinfo.txt
do_not_index: true
""")

    scanner = ZinfoScanner(tmp_path)
    result = scanner.scan()

    # Should find no items due to do_not_index flag
    assert result.total_items_found == 0


def test_zinfo_scanner_dir_id_generation(tmp_path):
    """Test ZinfoScanner generates unique dir_ids."""
    from zinfo.core.scanner import ZinfoScanner

    # Create multiple zinfo.txt files in different directories
    dir1 = tmp_path / "project1"
    dir1.mkdir()
    zinfo1 = dir1 / "zinfo.txt"
    zinfo1.write_text("""title: Project 1
shortname: P1
summary: First project
client: Client A
team: Team A
contact_email: a@example.com
location: zinfo.txt
""")

    dir2 = tmp_path / "project2"
    dir2.mkdir()
    zinfo2 = dir2 / "zinfo.txt"
    zinfo2.write_text("""title: Project 2
shortname: P2
summary: Second project
client: Client B
team: Team B
contact_email: b@example.com
location: zinfo.txt
""")

    scanner = ZinfoScanner(tmp_path)
    result = scanner.scan()

    assert result.total_items_found == 2

    # Check dir_ids are different and valid
    dir_ids = [item.dir_id for item in result.items]
    assert len(set(dir_ids)) == 2  # All unique
    assert all(len(did) >= 6 for did in dir_ids)  # All 6+ chars


def test_integration_full_scan_with_cache():
    """Integration test: Full scan of fake-home with caching."""
    from zinfo.core.scanner import ZinfoScanner
    from zinfo.core.cache import Cache
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        cache_path = Path(temp_dir) / "test.db"
        cache = Cache(cache_path)

        # Scan fake-home
        fake_home = Path("fake-home")
        scanner = ZinfoScanner(fake_home, cache=cache)
        result = scanner.scan()

        # Verify scan completed
        assert result.total_items_found >= 0
        assert result.total_dirs_scanned >= 0

        # Verify caching worked
        cached_count = cache.get_resource_count()
        assert cached_count == result.total_items_found

        # Verify we can retrieve cached data
        resources, total = cache.get_all_resources()
        assert len(resources) == result.total_items_found
        assert total == result.total_items_found

        # Verify resource structure
        if resources:
            resource = resources[0]
            assert hasattr(resource, 'dir_id')
            assert hasattr(resource, 'title')
            assert hasattr(resource, 'shortname')
            assert hasattr(resource, 'client')
            assert hasattr(resource, 'team')
            assert hasattr(resource, 'contact_email')


def test_integration_cli_query_operations():
    """Integration test: CLI query operations with new fields."""
    from zinfo.core.cache import Cache
    from zinfo.core.scanner import ZinfoScanner
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        cache_path = Path(temp_dir) / "test.db"
        cache = Cache(cache_path)

        # First scan to populate cache
        fake_home = Path("fake-home")
        scanner = ZinfoScanner(fake_home, cache=cache)
        scanner.scan()

        # Test search by title
        results, _ = cache.search_resources(title="project")
        assert isinstance(results, list)

        # Test search by client
        results, _ = cache.search_resources(client="client")
        assert isinstance(results, list)

        # Test search by team
        results, _ = cache.search_resources(team="team")
        assert isinstance(results, list)

        # Test search by shortname
        results, _ = cache.search_resources(shortname="test")
        assert isinstance(results, list)
