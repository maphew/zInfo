# Enhancement Ticket: appinfo.txt Format Support

## Summary
Add scanner support for the legacy `appinfo.txt` format used by environment applications, enabling migration from the standalone `envapplist.py` script to the new modular architecture.

## Background
The legacy `envapplist.py` script processes `appinfo.txt` files with a simple 3-line format:
```
Title of Application
setup.bat
contact@domain.com
```

This format is used by environment system applications and needs to be supported in the new scanner architecture.

## Example Input/Output

**Input (appinfo.txt):**
```
Environment Data Viewer
setup.bat
env-support@gov.yk.ca
```

**Expected Output (ResourceMetadata):**
```python
ResourceMetadata(
    id="apps/dataviewer",
    title="Environment Data Viewer",
    link="setup.bat",
    contact="env-support@gov.yk.ca",
    doc_dir=Path("apps/dataviewer/Doc"),
    metadata_type="appinfo_app",
    extra={}
)
```

## Current Impact
- **Users affected**: Environment system administrators and users who rely on the legacy HTML generation
- **Current workaround**: Must maintain separate `envapplist.py` script alongside new zinfo system
- **Data loss risk**: Projects using `appinfo.txt` format are not indexed by the new system

## Rationale for Deferral
- **Priority**: Medium - existing zinfo.txt format covers most use cases
- **Complexity**: Low - straightforward format parsing
- **Dependencies**: None - can be implemented independently
- **Migration path**: Enables gradual migration from legacy scripts

## Design Sketch

### Architecture Integration
```
CLI (scan command)
    ↓
Scanner Registry
    ↓
AppInfoScanner (new)
    ↓
BaseScanner.extract_metadata()
    ↓
ResourceMetadata
    ↓
Cache.store_scan_result()
```

### Implementation Plan
1. Create `AppInfoScanner` class extending `BaseScanner`
2. Implement `can_handle_file()` to detect `appinfo.txt` files
3. Implement `extract_metadata()` to parse 3-line format
4. Add scanner registration to CLI
5. Update tests with sample `appinfo.txt` fixtures

### Code Structure
```python
class AppInfoScanner(BaseScanner):
    def can_handle_file(self, path: Path) -> bool:
        return path.name.lower() == 'appinfo.txt'

    def extract_metadata(self, path: Path) -> Optional[ResourceMetadata]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()[:3]  # First 3 lines
                if len(lines) < 3:
                    return None

                title, link, contact = lines
                # Handle link formatting (file:// vs http)
                # Handle contact normalization (@gov.yk.ca fallback)
                # Check for Doc/ directory

                return ResourceMetadata(...)
        except Exception as e:
            logger.error(f"Failed to parse appinfo.txt {path}: {e}")
            return None
```

## Dependencies/Blockers
- **Dependencies**: None
- **Blockers**: None
- **Related**: Links to HTML export functionality (ticket #003)

## Acceptance Criteria
- [ ] `AppInfoScanner` class created and extends `BaseScanner`
- [ ] Scanner correctly parses 3-line `appinfo.txt` format
- [ ] Scanner handles missing files gracefully
- [ ] Scanner integrates with existing scan command
- [ ] Unit tests pass with sample fixtures
- [ ] Link formatting utilities handle file:// and HTTP links
- [ ] Contact normalization applies @gov.yk.ca fallback
- [ ] Doc/ directory detection works correctly
- [ ] Scanner respects `do_not_index` equivalent behavior

## Testing Strategy
- Unit tests for format parsing edge cases
- Integration tests with CLI scan command
- Sample `appinfo.txt` files in test fixtures
- Error handling tests for malformed files

## Migration Notes
- Existing `envapplist.py` users can gradually migrate
- No breaking changes to current functionality
- HTML export will use same data once implemented
