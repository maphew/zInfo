# Enhancement Ticket: project.ini Format Support

## Summary
Add scanner support for the legacy `project.ini` format used by map projects, fixing the broken implementation in `envmapplist.py` and integrating it into the new modular architecture.

## Background
The legacy `envmapplist.py` script attempts to process `project.ini` files but has a critical bug - it reads the file as plain text lines instead of using ConfigParser. The correct format uses INI structure with `[Project]` sections.

## Example Input/Output

**Input (project.ini):**
```ini
[Project]
title = Yukon Wildlife Habitat Mapping
link = maps/wildlife_habitat.mxd
contact = env-geo-unit@gov.yk.ca
description = Comprehensive wildlife habitat mapping project
```

**Expected Output (ResourceMetadata):**
```python
ResourceMetadata(
    id="projects/wildlife_mapping",
    title="Yukon Wildlife Habitat Mapping",
    link="maps/wildlife_habitat.mxd",
    contact="env-geo-unit@gov.yk.ca",
    doc_dir=Path("projects/wildlife_mapping/Doc"),
    metadata_type="project_ini",
    extra={
        "description": "Comprehensive wildlife habitat mapping project"
    }
)
```

## Current Impact
- **Users affected**: Geomatics unit and map project stakeholders
- **Current workaround**: Broken legacy script requires manual fixes
- **Data loss risk**: Map projects using `project.ini` format cannot be properly indexed
- **Bug severity**: High - legacy script produces incorrect output

## Rationale for Deferral
- **Priority**: High - fixes broken functionality from legacy migration
- **Complexity**: Medium - requires ConfigParser integration
- **Dependencies**: None - can be implemented independently
- **Migration path**: Fixes existing broken functionality

## Design Sketch

### Architecture Integration
```
CLI (scan command)
    ↓
Scanner Registry
    ↓
ProjectIniScanner (new)
    ↓
BaseScanner.extract_metadata()
    ↓
ConfigParser.read()
    ↓
ResourceMetadata
    ↓
Cache.store_scan_result()
```

### Implementation Plan
1. Create `ProjectIniScanner` class extending `BaseScanner`
2. Implement `can_handle_file()` to detect `project.ini` files
3. Implement `extract_metadata()` using ConfigParser for `[Project]` section
4. Add scanner registration to CLI
5. Update tests with sample `project.ini` fixtures
6. Fix the bug in legacy script logic

### Code Structure
```python
import configparser

class ProjectIniScanner(BaseScanner):
    def can_handle_file(self, path: Path) -> bool:
        return path.name.lower() == 'project.ini'

    def extract_metadata(self, path: Path) -> Optional[ResourceMetadata]:
        try:
            config = configparser.ConfigParser()
            config.read(path)

            if not config.has_section('Project'):
                return None

            section = config['Project']
            title = section.get('title', path.parent.name)
            link = section.get('link', '')
            contact = section.get('contact', '')

            # Handle link formatting (file:// vs http)
            # Handle contact normalization (@gov.yk.ca fallback)
            # Check for Doc/ directory
            # Extract additional fields to extra dict

            return ResourceMetadata(...)
        except Exception as e:
            logger.error(f"Failed to parse project.ini {path}: {e}")
            return None
```

## Dependencies/Blockers
- **Dependencies**: None (uses standard library ConfigParser)
- **Blockers**: None
- **Related**: Links to HTML export functionality (ticket #003)

## Acceptance Criteria
- [ ] `ProjectIniScanner` class created and extends `BaseScanner`
- [ ] Scanner correctly parses `[Project]` section using ConfigParser
- [ ] Scanner handles missing sections gracefully
- [ ] Scanner integrates with existing scan command
- [ ] Unit tests pass with sample fixtures
- [ ] Additional INI fields are preserved in `extra` dict
- [ ] Scanner respects case-insensitive section names
- [ ] Error handling for malformed INI files
- [ ] Fixes the bug present in legacy `envmapplist.py`

## Testing Strategy
- Unit tests for ConfigParser integration
- Integration tests with CLI scan command
- Sample `project.ini` files in test fixtures
- Error handling tests for malformed INI files
- Edge case tests for missing sections/fields

## Migration Notes
- Fixes broken functionality from legacy migration
- Existing `envmapplist.py` users get working replacement
- No breaking changes to current functionality
- Enables proper indexing of map projects
