# Enhancement Ticket: Doc Directory Detection

## Summary
Add automatic detection and linking of Doc/ subdirectories, replicating the documentation directory functionality from legacy `envapplist.py` and `envmapplist.py` scripts.

## Background
The legacy scripts automatically detect and create links to `Doc/` subdirectories within project folders, providing easy access to project documentation. This functionality needs to be integrated into the new scanner architecture.

## Example Input/Output

**Project Structure:**
```
projects/
├── app1/
│   ├── appinfo.txt
│   └── Doc/
│       ├── readme.txt
│       └── user_guide.pdf
└── app2/
    ├── appinfo.txt
    └── (no Doc directory)
```

**Expected ResourceMetadata:**
```python
# For app1
ResourceMetadata(
    id="projects/app1",
    title="Application 1",
    link="setup.bat",
    contact="support@gov.yk.ca",
    doc_dir=Path("projects/app1/Doc"),  # Detected automatically
    metadata_type="appinfo_app",
    extra={}
)

# For app2
ResourceMetadata(
    id="projects/app2",
    title="Application 2",
    link="install.exe",
    contact="dev@gov.yk.ca",
    doc_dir=None,  # No Doc directory present
    metadata_type="appinfo_app",
    extra={}
)
```

## Current Impact
- **Users affected**: All users who need documentation links in exports
- **Current workaround**: Manual documentation path specification
- **Data loss risk**: Documentation directories not automatically linked
- **Integration gap**: Missing automatic documentation discovery

## Rationale for Deferral
- **Priority**: Medium - useful but not critical functionality
- **Complexity**: Low - simple directory existence check
- **Dependencies**: None - can be implemented independently
- **Migration path**: Enhances scanner functionality with minimal effort

## Design Sketch

### Architecture Integration
```
Scanner.extract_metadata()
    ↓
DocDetector (utility)
    ↓
- detect_doc_dir()
- create_doc_link()
```

### Implementation Plan
1. Create `DocDetector` utility class
2. Integrate into existing scanner implementations
3. Add automatic Doc/ directory detection
4. Generate appropriate file:// links for HTML export
5. Handle missing Doc/ directories gracefully

### Code Structure
```python
class DocDetector:
    def __init__(self):
        pass

    def detect_doc_dir(self, project_path: Path) -> Optional[Path]:
        """Detect Doc/ subdirectory in project path."""
        doc_dir = project_path / 'Doc'
        if doc_dir.exists() and doc_dir.is_dir():
            return doc_dir
        return None

    def create_doc_link(self, doc_dir: Path, base_path: Optional[Path] = None) -> str:
        """Create HTML link for Doc directory."""
        if base_path:
            # Convert to file:// URL relative to base path
            file_url = f"file:///{(base_path / doc_dir).as_posix()}"
        else:
            # Use absolute path
            file_url = f"file:///{doc_dir.as_posix()}"

        # Display Windows-style path for readability
        win_path = str(doc_dir).replace('/', '\\')
        return f'<a href="{file_url}">{win_path}</a>'

# Integration in scanner
def extract_metadata(self, path: Path) -> Optional[ResourceMetadata]:
    # ... existing parsing logic ...

    doc_dir = self.doc_detector.detect_doc_dir(path.parent)

    return ResourceMetadata(
        # ... other fields ...
        doc_dir=doc_dir,
        # ... other fields ...
    )
```

## Dependencies/Blockers
- **Dependencies**: None (uses standard library)
- **Blockers**: None
- **Related**: Used by HTML export (ticket #003), enhances scanners (tickets #001, #002)

## Acceptance Criteria
- [ ] `DocDetector` utility class created with proper interface
- [ ] Automatic detection of Doc/ subdirectories in project folders
- [ ] Graceful handling when Doc/ directory is missing
- [ ] Integration with existing scanner implementations
- [ ] File:// link generation for HTML export
- [ ] Windows path display compatibility
- [ ] Cross-platform path handling
- [ ] Unit tests for directory detection logic
- [ ] Integration tests with scanner functionality

## Testing Strategy
- Unit tests for Doc/ directory detection
- Edge case tests for missing directories
- Cross-platform tests for path handling
- Integration tests with scanner implementations
- Mock tests for file system operations

## Migration Notes
- Enhances existing scanner functionality
- Provides automatic documentation linking
- No breaking changes to current functionality
- Improves user experience with minimal effort
