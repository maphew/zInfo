import os
import tempfile
from pathlib import Path
from datetime import datetime
import pytest
from starlette.testclient import TestClient
from zinfo.ui.fh_ui import app
from zinfo.core.cache import Cache
from zinfo.core.models import ResourceMetadata

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
def seeded_cache(temp_db):
    """Create a cache with seeded sample data."""
    cache = Cache(temp_db)

    resource1 = ResourceMetadata(
        id="test/resource1",
        title="Test Resource 1",
        link="file://test1.txt",
        contact="test1@example.com",
        metadata_type="resource",
        last_indexed=datetime.now(),
    )

    resource2 = ResourceMetadata(
        id="test/resource2",
        title="Test Resource 2",
        link="file://test2.txt",
        contact="test2@example.com",
        metadata_type="resource",
        last_indexed=datetime.now(),
    )

    cache.store_resource(resource1)
    cache.store_resource(resource2)

    return cache

def test_index_empty(temp_db):
    """Test index with no resources."""
    old_env = os.environ.get("ZINFO_DB_PATH")
    os.environ["ZINFO_DB_PATH"] = str(temp_db)

    try:
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert "zInfo UI" in response.text
        assert "No cached resources found" in response.text
    finally:
        if old_env is not None:
            os.environ["ZINFO_DB_PATH"] = old_env
        else:
            os.environ.pop("ZINFO_DB_PATH", None)

def test_index_with_resources(seeded_cache, temp_db):
    """Test index with seeded resources."""
    old_env = os.environ.get("ZINFO_DB_PATH")
    os.environ["ZINFO_DB_PATH"] = str(temp_db)

    try:
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert "zInfo UI" in response.text
        assert "Test Resource 1" in response.text
        assert "Test Resource 2" in response.text
        assert "<table" in response.text  # Check for table element
        assert "Title" in response.text  # Header
        assert "Type" in response.text
        assert "ID" in response.text
        assert "Path" in response.text
    finally:
        if old_env is not None:
            os.environ["ZINFO_DB_PATH"] = old_env
        else:
            os.environ.pop("ZINFO_DB_PATH", None)
