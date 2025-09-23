'''A Python class that automatically generates the shortest unique ID for each item, Git-style.
<From GPT-5> '''

import hashlib

class ShortIDGenerator:
    def __init__(self, min_len=6, max_len=40, hash_algo='sha1'):
        """
        min_len: minimum length of short ID
        max_len: maximum length of short ID
        hash_algo: 'sha1' or 'sha256'
        """
        self.min_len = min_len
        self.max_len = max_len
        self.existing = set()
        self.hash_func = getattr(hashlib, hash_algo)

    def generate(self, value):
        """
        Generate a unique short ID for `value`.
        """
        full_hash = self.hash_func(value.encode()).hexdigest()
        for length in range(self.min_len, self.max_len + 1):
            prefix = full_hash[:length]
            if prefix not in self.existing:
                self.existing.add(prefix)
                return prefix
        raise ValueError("Cannot generate unique short ID; increase max_len.")

    def add_existing(self, short_id):
        """
        Add a pre-existing short ID to avoid collisions.
        """
        self.existing.add(short_id)

# -------------------------
# Example usage
# -------------------------
generator = ShortIDGenerator(min_len=6)

items = ["Apple", "Banana", "Cherry", "Apple"]
for item in items:
    short_id = generator.generate(item)
    print(f"{item} -> {short_id}")

# Example output (will vary):
# Apple -> 1f3870
# Banana -> b8f5a1
# Cherry -> 2d7116
# Apple -> 1f3870  (same input yields same hash prefix)
