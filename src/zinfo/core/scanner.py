"""Base directory scanner functionality.

Provides the core scanning logic used by different metadata providers.
"""
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Type, TYPE_CHECKING
import logging
from abc import ABC, abstractmethod

from .models import ResourceMetadata, ScanResult

if TYPE_CHECKING:
    from .cache import Cache

logger = logging.getLogger(__name__)

class BaseScanner(ABC):
    """Abstract base scanner class."""
    
    def __init__(
        self,
        base_dir: Path,
        cache: Optional['Cache'] = None,
        recursive: bool = True
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
                paths = list(self.base_dir.glob('**/*'))
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
            total_items_found=len(items)
        )
        
        # Cache results if cache is available
        if self.cache:
            try:
                self.cache.store_scan_result(result)
            except Exception as e:
                logger.error(f"Error caching results: {str(e)}")
        
        return result
