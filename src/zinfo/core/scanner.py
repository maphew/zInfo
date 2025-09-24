"""Base directory scanner functionality.

Provides the core scanning logic used by different metadata providers.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING
import logging
from abc import ABC, abstractmethod
import os

from .models import ResourceMetadata, ScanResult
from .id_generator import DirIDGenerator

if TYPE_CHECKING:
    from .cache import Cache

logger = logging.getLogger(__name__)


class BaseScanner(ABC):
    """Abstract base scanner class."""

    def __init__(
        self, base_dir: Path, cache: Optional["Cache"] = None, recursive: bool = True
    ):
        """Initialize scanner with base directory and options.

        Args:
            base_dir: Root directory to scan
            cache: Optional cache instance for storing results
            recursive: Whether to scan subdirectories
        """
        self.base_dir = Path(base_dir)
        self.cache = cache
        self.recursive = recursive

    @abstractmethod
    def can_handle_file(self, path: Path) -> bool:
        """Check if this scanner can handle the given file."""
        pass

    @abstractmethod
    def extract_metadata(self, path: Path) -> Optional[ResourceMetadata]:
        """Extract metadata from a file."""
        pass

    def scan(self) -> ScanResult:
        """Scan directory for metadata files.

        Returns:
            ScanResult containing found items and scan statistics
        """
        start_time = datetime.now()
        items: List[ResourceMetadata] = []
        errors: List[str] = []
        dirs_scanned = 0

        try:
            if not self.base_dir.exists():
                raise FileNotFoundError(f"Directory does not exist: {self.base_dir}")

            if not self.base_dir.is_dir():
                raise NotADirectoryError(f"Path is not a directory: {self.base_dir}")

            # Keep track of directories we've seen
            seen_dirs = set()

            # Use .glob() if recursive, otherwise .iterdir()
            if self.recursive:
                paths = list(self.base_dir.glob("**/*"))
            else:
                paths = list(self.base_dir.iterdir())

            for path in paths:
                if path.is_dir():
                    if self.recursive and path != self.base_dir:
                        seen_dirs.add(path)
                    continue

                if not self.can_handle_file(path):
                    continue

                try:
                    if metadata := self.extract_metadata(path):
                        items.append(metadata)
                except Exception as e:
                    error_msg = f"Error processing {path}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)

            # Count all directories we've seen
            dirs_scanned = len(seen_dirs)

        except Exception as e:
            error_msg = f"Error scanning directory {self.base_dir}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)

        result = ScanResult(
            items=items,
            errors=errors,
            start_time=start_time,
            end_time=datetime.now(),
            total_dirs_scanned=dirs_scanned,
            total_items_found=len(items),
        )

        # Cache results if cache is available
        if self.cache:
            try:
                self.cache.store_scan_result(result)
            except Exception as e:
                logger.error(f"Error caching results: {str(e)}")

        return result


class ZinfoScanner(BaseScanner):
    """Concrete scanner for zinfo.txt metadata files."""

    def __init__(
        self,
        base_dir: Path,
        cache: Optional["Cache"] = None,
        max_depth: int = 5,
        recursive: bool = True,
    ):
        super().__init__(base_dir, cache, recursive)
        self.max_depth = max_depth
        self.id_generator = DirIDGenerator()

    def can_handle_file(self, path: Path) -> bool:
        """Check if file is zinfo.txt."""
        return path.name.lower() == "zinfo.txt"

    def _parse_zinfo_file(self, path: Path) -> dict:
        """Parse zinfo.txt file into key-value dictionary."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()[:50]  # First 50 lines as spec

            meta = {}
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    meta[key.strip().lower()] = value.strip()
            return meta
        except Exception as e:
            logger.error(f"Failed to parse {path}: {e}")
            return {}

    def _validate_required_fields(self, fields: dict, path: Path) -> bool:
        """Validate presence of required fields."""
        required = ["title", "shortname", "summary", "client", "team", "contact_email", "location"]
        missing = [f for f in required if f not in fields or not fields[f]]
        if missing:
            logger.warning(f"Skipping {path}: missing required fields: {', '.join(missing)}")
            return False
        return True

    def _extract_required_fields(self, fields: dict) -> dict:
        """Extract required fields from parsed fields."""
        required_keys = ["title", "shortname", "summary", "client", "team", "contact_email", "location"]
        return {k: fields[k] for k in required_keys}

    def _extract_optional_fields(self, fields: dict) -> dict:
        """Extract optional fields from parsed fields."""
        # For now, no specific optional fields defined, return empty
        return {}

    def _extract_custom_fields(self, fields: dict) -> dict:
        """Extract custom fields from parsed fields."""
        required_keys = {"title", "shortname", "summary", "client", "team", "contact_email", "location"}
        return {k: v for k, v in fields.items() if k not in required_keys}

    def extract_metadata(self, path: Path) -> Optional[ResourceMetadata]:
        """Parse zinfo.txt into ResourceMetadata with validation and categorization."""
        try:
            fields = self._parse_zinfo_file(path)

            if not fields:  # No valid keys
                return None

            # Check for ignore
            if fields.get("do_not_index", "").lower() == "true":
                return None

            # Validate required fields
            if not self._validate_required_fields(fields, path):
                return None

            # Generate dir_id
            dir_id = self.id_generator.generate(str(path.parent))

            # Categorize fields
            required = self._extract_required_fields(fields)
            optional = self._extract_optional_fields(fields)
            custom = self._extract_custom_fields(fields)

            # Build ResourceMetadata
            rel_path = path.relative_to(self.base_dir)
            return ResourceMetadata(
                dir_id=dir_id,
                dir_path=str(path.parent.resolve()),
                **required,
                last_modified=datetime.fromtimestamp(path.stat().st_mtime),
                last_indexed=datetime.now(),
                optional_fields=optional or None,
                custom_fields=custom or None,
            )

        except Exception as e:
            logger.error(f"Failed to extract metadata from {path}: {e}")
            return None

    def scan(self) -> ScanResult:
        """Scan with max_depth limit using os.walk."""
        start_time = datetime.now()
        items: List[ResourceMetadata] = []
        errors: List[str] = []
        dirs_scanned = 0

        try:
            if not self.base_dir.exists():
                raise FileNotFoundError(f"Directory does not exist: {self.base_dir}")

            if not self.base_dir.is_dir():
                raise NotADirectoryError(f"Path is not a directory: {self.base_dir}")

            # Use os.walk with maxdepth
            for root, dirs, files in os.walk(str(self.base_dir), topdown=True):
                current_depth = len(Path(root).relative_to(self.base_dir).parts)
                if current_depth > self.max_depth:
                    dirs[:] = []  # Prune deeper dirs
                    continue

                dirs_scanned += 1
                root_path = Path(root)

                for file in files:
                    path = root_path / file
                    if not self.can_handle_file(path):
                        continue

                    try:
                        if metadata := self.extract_metadata(path):
                            items.append(metadata)
                    except Exception as e:
                        error_msg = f"Error processing {path}: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)

        except Exception as e:
            error_msg = f"Error scanning directory {self.base_dir}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)

        result = ScanResult(
            items=items,
            errors=errors,
            start_time=start_time,
            end_time=datetime.now(),
            total_dirs_scanned=dirs_scanned,
            total_items_found=len(items),
        )

        if self.cache:
            try:
                self.cache.store_scan_result(result)
            except Exception as e:
                logger.error(f"Error caching results: {e}")

        return result
