"""Test suite for base scanner functionality."""
from datetime import datetime
from pathlib import Path
import pytest
from typing import Optional

from zinfo.core.models import ResourceMetadata, ScanResult
from zinfo.core.scanner import BaseScanner
from zinfo.core.cache import Cache

class TestScanner(BaseScanner):
    """Test implementation of BaseScanner."""
    
    def can_handle_file(self, path: Path) -> bool:
        """Handle .test files."""
        return path.suffix == '.test'
    
    def extract_metadata(self, path: Path) -> Optional[ResourceMetadata]:
        """Extract metadata from test file."""
        if not self.can_handle_file(path):
            return None
        
        return ResourceMetadata(
            id=str(path.relative_to(self.base_dir)),
            title=path.stem,
            link=str(path),
            contact="test@example.com"
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
