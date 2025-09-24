"""Directory ID generator for zInfo project directories.

Generates unique short IDs for directory paths using hash prefixes,
with collision handling by extending length.
"""

import hashlib


class DirIDGenerator:
    """Generates unique short IDs for directory paths.

    Uses SHA-1 hashing of directory paths to create unique identifiers
    starting at 6 characters, extending length on collisions.
    """

    def __init__(self, min_len=6, max_len=40, hash_algo='sha1'):
        """
        Initialize the directory ID generator.

        Args:
            min_len: Minimum length of generated IDs (default: 6)
            max_len: Maximum length of generated IDs (default: 40)
            hash_algo: Hash algorithm to use ('sha1' or 'sha256')
        """
        self.min_len = min_len
        self.max_len = max_len
        self.existing = set()
        self.hash_func = getattr(hashlib, hash_algo)

    def generate(self, dir_path: str) -> str:
        """
        Generate a unique short ID for the given directory path.

        Args:
            dir_path: The directory path string to hash

        Returns:
            A unique short ID string

        Raises:
            ValueError: If unable to generate unique ID within max_len
        """
        full_hash = self.hash_func(dir_path.encode()).hexdigest()
        for length in range(self.min_len, self.max_len + 1):
            prefix = full_hash[:length]
            if prefix not in self.existing:
                self.existing.add(prefix)
                return prefix
        raise ValueError("Cannot generate unique directory ID; increase max_len.")

    def add_existing(self, dir_id: str):
        """
        Add a pre-existing directory ID to avoid collisions.

        Args:
            dir_id: The existing directory ID to register
        """
        self.existing.add(dir_id)
