"""Shared pytest fixtures."""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def test_data_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_metadata_dir(test_data_dir):
    """Create a directory with sample metadata files."""
    # Copy fixtures to test directory
    fixtures_dir = Path(__file__).parent / "fixtures"
    for fixture in fixtures_dir.glob("*"):
        if fixture.is_file():
            shutil.copy2(fixture, test_data_dir)
    return test_data_dir
