# Enhancement Ticket: Link Formatting and Contact Normalization Utilities

## Summary
Create utility classes for link formatting and contact normalization, extracting reusable logic from legacy scripts for file:// link handling and @gov.yk.ca contact fallback behavior.

## Background
The legacy scripts contain sophisticated logic for:
- Converting relative paths to file:// URLs with Windows compatibility
- Normalizing contact emails with service desk fallback
- Handling HTTP vs file:// link detection
- Cross-platform path conversion

## Example Input/Output

**Link Formatting Examples:**
```python
# HTTP links (unchanged)
formatter.format_link("https://example.com/app")  # "https://example.com/app"

# Relative file paths (converted to file://)
formatter.format_link("setup.bat")  # "file:///C:/projects/app1/setup.bat"

# Windows path handling
formatter.format_link("\\\\server\\app\\setup.bat")  # "file://server/app/setup.bat"
```

**Contact Normalization Examples:**
```python
# Gov contacts (unchanged)
normalizer.normalize_contact("user@gov.yk.ca")  # "user@gov.yk.ca"

# Non-gov contacts (fallback to service desk)
normalizer.normalize_contact("external@contractor.com")
# "service.desk@gov.yk.ca?Subject=Environment Application: App Title"
```

## Current Impact
- **Users affected**: All users requiring proper link formatting in exports
- **Current workaround**: Manual link formatting in export code
- **Data loss risk**: Incorrect links in HTML exports
- **Code duplication**: Link/contact logic scattered across components

## Rationale for Deferral
- **Priority**: High - foundational utilities needed by multiple components
- **Complexity**: Low - utility functions with clear interfaces
- **Dependencies**: None - can be implemented independently
- **Migration path**: Enables consistent link/contact handling across all exporters

## Design Sketch

### Architecture Integration
```
Multiple Components
    ↓
LinkFormatter (utility)
    ↓
- format_link()
- is_http_link()
- to_file_url()

ContactNormalizer (utility)
    ↓
- normalize_contact()
- is_gov_contact()
- create_service_desk_link()
```

### Implementation Plan
1. Create `LinkFormatter` utility class
2. Create `ContactNormalizer` utility class
3. Implement Windows path compatibility
4. Add cross-platform file:// URL generation
5. Support mailto link generation with subjects
6. Add comprehensive unit tests

### Code Structure
```python
class LinkFormatter:
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path

    def format_link(self, link: str, project_path: Path) -> str:
        """Format link for HTML output with proper URL encoding."""
        if self.is_http_link(link):
            return f'<a href="{link}">{link}</a>'

        # Convert relative path to file:// URL
        if self.base_path:
            full_path = self.base_path / project_path / link
        else:
            full_path = project_path / link

        file_url = self.to_file_url(full_path)
        win_path = str(full_path).replace('/', '\\')
        return f'<a href="{file_url}">{win_path}</a>'

    def is_http_link(self, link: str) -> bool:
        return link.startswith(('http://', 'https://'))

    def to_file_url(self, path: Path) -> str:
        """Convert pathlib Path to file:// URL."""
        return f"file:///{path.as_posix()}"

class ContactNormalizer:
    def __init__(self, service_desk_email: str = "service.desk@gov.yk.ca"):
        self.service_desk_email = service_desk_email

    def normalize_contact(self, contact: str, project_title: str) -> str:
        """Normalize contact email with service desk fallback."""
        if not contact:
            return self.service_desk_email

        if self.is_gov_contact(contact):
            return f'<a href="mailto:{contact}?Subject={project_title}" target="_top">{contact}</a>'

        # Non-gov contact - route through service desk
        subject = f"Environment Application: {project_title}"
        return f'<a href="mailto:{self.service_desk_email}?Subject={subject}" target="_top">{contact}</a>'

    def is_gov_contact(self, contact: str) -> bool:
        return 'gov.yk.ca' in contact.lower()
```

## Dependencies/Blockers
- **Dependencies**: None (uses standard library)
- **Blockers**: None
- **Related**: Required by HTML export (ticket #003), used by scanners (tickets #001, #002)

## Acceptance Criteria
- [ ] `LinkFormatter` utility class created with proper interface
- [ ] `ContactNormalizer` utility class created with proper interface
- [ ] HTTP link detection and formatting works correctly
- [ ] File path to file:// URL conversion handles Windows paths
- [ ] Cross-platform compatibility maintained
- [ ] Contact normalization applies @gov.yk.ca fallback correctly
- [ ] Service desk email integration with subject lines
- [ ] Comprehensive unit tests for edge cases
- [ ] Integration tests with HTML export functionality

## Testing Strategy
- Unit tests for all utility methods
- Edge case tests for malformed URLs/paths
- Cross-platform tests for path handling
- Integration tests with HTML export
- Mock tests for Windows-specific behavior

## Migration Notes
- Extracted from legacy script logic
- Provides consistent behavior across all components
- Enables proper HTML export functionality
- Supports future export formats requiring links
