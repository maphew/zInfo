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
        title="Python Project",
        link="file://test1.txt",
        contact="alice@example.com",
        metadata_type="project",
        last_indexed=datetime.now(),
        extra={"authors": ["Alice Smith"]}
    )

    resource2 = ResourceMetadata(
        id="test/resource2",
        title="JavaScript App",
        link="file://test2.txt",
        contact="bob@example.com",
        metadata_type="app",
        last_indexed=datetime.now(),
        extra={"authors": ["Bob Johnson"]}
    )

    resource3 = ResourceMetadata(
        id="docs/manual",
        title="User Manual",
        link="file://manual.pdf",
        contact="charlie@example.com",
        metadata_type="document",
        last_indexed=datetime.now(),
        extra={"authors": ["Charlie Brown", "Alice Smith"]}
    )

    resource4 = ResourceMetadata(
        id="web/site",
        title="Website",
        link="file://site.html",
        contact="diana@example.com",
        metadata_type="web",
        last_indexed=datetime.now(),
        extra={"authors": ["Diana Prince"]}
    )

    cache.store_resource(resource1)
    cache.store_resource(resource2)
    cache.store_resource(resource3)
    cache.store_resource(resource4)

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

def test_search_htmx_request(seeded_cache, temp_db):
    """Test GET /search with HX-Request header returns filtered rows only."""
    old_env = os.environ.get("ZINFO_DB_PATH")
    os.environ["ZINFO_DB_PATH"] = str(temp_db)

    try:
        client = TestClient(app)
        response = client.get("/search?title=Python", headers={"HX-Request": "true"})
        assert response.status_code == 200
        assert "Python Project" in response.text
        assert "JavaScript App" not in response.text
        assert "User Manual" not in response.text
        assert "Website" not in response.text
        assert "<table" in response.text
        assert "zInfo UI" not in response.text  # Should not return full page
    finally:
        if old_env is not None:
            os.environ["ZINFO_DB_PATH"] = old_env
        else:
            os.environ.pop("ZINFO_DB_PATH", None)

def test_search_non_htmx_request(seeded_cache, temp_db):
    """Test non-HX request returns full page."""
    old_env = os.environ.get("ZINFO_DB_PATH")
    os.environ["ZINFO_DB_PATH"] = str(temp_db)

    try:
        client = TestClient(app)
        response = client.get("/search?type=project")
        assert response.status_code == 200
        assert "Python Project" in response.text  # type=project
        assert "JavaScript App" not in response.text  # type=app
        assert "User Manual" not in response.text  # type=document
        assert "Website" not in response.text  # type=web
        assert "<table" in response.text
        assert "zInfo UI" in response.text  # Should return full page
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
        assert "Python Project" in response.text
        assert "JavaScript App" in response.text
        assert "User Manual" in response.text
        assert "Website" in response.text
        assert "<table" in response.text  # Check for table element
        assert "Title" in response.text  # Header
        assert "Type" in response.text
        assert "ID" in response.text
        assert "Path" in response.text
        assert '<form' in response.text  # Check for form
        assert 'hx-get="/search"' in response.text  # Check for HTMX attributes
        assert 'id="results"' in response.text  # Check for results div
    finally:
        if old_env is not None:
            os.environ["ZINFO_DB_PATH"] = old_env
        else:
            os.environ.pop("ZINFO_DB_PATH", None)
