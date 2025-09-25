---------

**Plan Completed** 2025-09-23  
commit: 016f71f4bed5a707c273a24536f48cc3ca6dab42

---------

# zInfo Metadata Format Restructure Plan

## Overview
This plan restructures the zInfo system to implement the new metadata format specification defined in @/Readme.md section "Metadata File Format" (lines 128-284). The changes involve a complete database schema redesign, model updates, scanner modifications, and UI enhancements.

## Current State Analysis

### Database Schema (Current)
```sql
CREATE TABLE resources (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    contact TEXT NOT NULL,
    doc_dir TEXT,
    metadata_type TEXT NOT NULL,
    last_modified TIMESTAMP,
    last_indexed TIMESTAMP NOT NULL,
    extra JSON
)
```

### ResourceMetadata Model (Current)
- Basic fields: id, title, link, contact, doc_dir, last_modified, last_indexed, metadata_type
- Everything else stored in `extra` dict

### Key Issues to Address
1. No dir_id generation
2. Missing required field validation
3. Current structure doesn't match new specification
4. UI doesn't display new structured fields properly

## New Requirements

### Field Categories
1. **System Fields (computed at scan time):**
   - `dir_id`: Unique 6+ character hash of project folder
   - `dir_path`: Fully resolved path to directory containing zinfo file

2. **Required Fields (must be present in zinfo.txt):**
   - `title`: Project name (soft max 50 chars)
   - `shortname`: Nickname (soft max 15 chars)  
   - `summary`: Short description (soft max 150 chars)
   - `client`: Sponsoring organization/person
   - `team`: Primary author(s), semicolon-delimited
   - `contact_email`: Team lead/author email
   - `location`: Path to zinfo file

3. **Optional Fields:**
   - Various metadata like dates, status, links, etc.

4. **Custom Fields:**
   - Any additional key-value pairs

## Implementation Plan

### Phase 1: Core Data Structure Changes

#### 1.1 Update ResourceMetadata Model
**File:** `src/zinfo/core/models.py`

**Changes:**
- Replace current model with new structure matching specification
- Add system fields: dir_id, dir_path
- Add all required fields as first-class attributes
- Keep optional fields in structured extra dict
- Remove old link/contact fields entirely

**New Model Structure:**
```python
@dataclass
class ResourceMetadata:
    # System fields (computed)
    dir_id: str  # 6+ char hash
    dir_path: str  # fully resolved path
    
    # Required fields
    title: str  # soft max 50
    shortname: str  # soft max 15
    summary: str  # soft max 150
    client: str
    team: str  # semicolon-delimited
    contact_email: str
    location: str  # relative path to zinfo file
    
    # System timestamps
    last_modified: Optional[datetime] = None
    last_indexed: Optional[datetime] = None
    metadata_type: str = "zinfo_project"
    
    # Optional structured fields
    optional_fields: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None
```

#### 1.2 Implement dir_id Generation
**File:** `src/zinfo/core/id_generator.py` (new)

**Implementation:**
- Adapt `generate_id.py` ShortIDGenerator for directory path hashing
- Use directory path (not file path) as hash input
- Generate unique 6+ character IDs
- Handle collisions by extending length

#### 1.3 Create New Database Schema
**File:** `src/zinfo/core/cache.py`

**New Schema:**
```sql
CREATE TABLE resources (
    -- System fields
    dir_id TEXT PRIMARY KEY,
    dir_path TEXT NOT NULL,
    
    -- Required fields  
    title TEXT NOT NULL,
    shortname TEXT NOT NULL,
    summary TEXT NOT NULL,
    client TEXT NOT NULL,
    team TEXT NOT NULL,
    contact_email TEXT NOT NULL,
    location TEXT NOT NULL,
    
    -- System timestamps
    last_modified TIMESTAMP,
    last_indexed TIMESTAMP NOT NULL,
    metadata_type TEXT NOT NULL,
    
    -- JSON fields for structured optional/custom data
    optional_fields JSON,
    custom_fields JSON
)
```

**Migration Strategy:**
- Drop existing tables (fresh start as agreed)
- Create new schema on first scan
- Add schema version tracking for future migrations

### Phase 2: Scanner Updates

#### 2.1 Update ZinfoScanner
**File:** `src/zinfo/core/scanner.py`

**Key Changes:**
1. **Required Field Validation:**
   - Check for presence of all required fields
   - Skip files missing required fields with detailed warnings
   - Log validation errors for user review

2. **Field Parsing:**
   - Parse and categorize fields into required/optional/custom buckets
   - Handle team field parsing (semicolon-delimited)
   - Extract contact_email from team or standalone field

3. **dir_id Generation:**
   - Generate unique dir_id for each project directory
   - Use directory path as hash input
   - Store mapping for collision detection

4. **Enhanced Metadata Extraction:**
   ```python
   def extract_metadata(self, path: Path) -> Optional[ResourceMetadata]:
       # Parse all fields from zinfo.txt
       fields = self._parse_zinfo_file(path)
       
       # Validate required fields
       if not self._validate_required_fields(fields):
           return None  # Skip with warning
           
       # Generate dir_id
       dir_id = self.id_generator.generate(str(path.parent))
       
       # Categorize fields
       required = self._extract_required_fields(fields)
       optional = self._extract_optional_fields(fields)  
       custom = self._extract_custom_fields(fields)
       
       # Build ResourceMetadata
       return ResourceMetadata(
           dir_id=dir_id,
           dir_path=str(path.parent.resolve()),
           **required,
           optional_fields=optional,
           custom_fields=custom,
           last_modified=datetime.fromtimestamp(path.stat().st_mtime),
           last_indexed=datetime.now()
       )
   ```

### Phase 3: Database Layer Updates

#### 3.1 Update Cache Class
**File:** `src/zinfo/core/cache.py`

**Changes:**
1. **Schema Migration:**
   - Implement new table creation
   - Add schema version tracking
   - Clean break from old schema

2. **CRUD Operations:**
   - Update all database operations for new schema
   - Store required fields as columns
   - Serialize optional/custom fields as JSON
   - Update search functionality for new structure

3. **Search Enhancements:**
   - Search across required fields directly
   - Search in JSON fields for optional/custom data
   - Add shortname, client, team search capabilities

### Phase 4: UI Updates

#### 4.1 Update FastHTML UI
**File:** `src/zinfo/ui/fh_ui.py`

**Display Changes:**
1. **Resource Table:**
   - Show: title, shortname, client, dir_id, location
   - Update column headers and data extraction
   - Add client filtering

2. **Detail Panel:**
   - Display all required fields prominently  
   - Show optional fields in organized sections
   - Display custom fields separately
   - Format team members properly (semicolon parsing)
   - Show system fields (dir_id, dir_path)

3. **Search Form:**
   - Add shortname search field
   - Add client search field  
   - Add team member search
   - Update backend search integration

4. **Validation Display:**
   - Show validation errors from scanner
   - Highlight missing required fields
   - Provide guidance for fixing invalid files

### Phase 5: CLI Updates

#### 5.1 Update Query Command
**File:** `src/zinfo/cli.py`

**Changes:**
1. **Query Options:**
   - Add --shortname filter
   - Add --client filter  
   - Add --team filter
   - Update --author to search team field
   - Add --dir-id for direct lookup

2. **Output Formats:**
   - Update table format for new fields
   - Update detailed format with structured display
   - Update JSON format for new schema

### Phase 6: Testing & Validation

#### 6.1 Update Test Suite
**Files:** `tests/core/test_*.py`

**Changes:**
1. **Model Tests:**
   - Test new ResourceMetadata structure
   - Test field validation
   - Test dir_id generation

2. **Scanner Tests:**
   - Test required field validation
   - Test field categorization
   - Test with sample files from fake-home/

3. **Cache Tests:**
   - Test new schema operations
   - Test search functionality
   - Test JSON field handling

4. **Integration Tests:**
   - Full scan with fake-home/ samples
   - UI rendering with new data structure
   - CLI query operations

#### 6.2 Sample File Validation
**Files:** `fake-home/*/zinfo.txt`

**Validation Steps:**
1. Test scanner against all sample files
2. Verify required field extraction
3. Confirm optional/custom field categorization
4. Validate dir_id generation uniqueness
5. Test UI display with real data

## Implementation Sequence

### Day 1: Core Data Structure
1. ✅ Create detailed plan (this document)
2. Update ResourceMetadata model
3. Implement dir_id generation
4. Create new database schema
5. Update basic cache operations

### Day 2: Scanner & Validation  
1. Update ZinfoScanner with field validation
2. Implement required field checking
3. Add enhanced error reporting
4. Test against sample files

### Day 3: UI & Search
1. Update FastHTML UI for new fields
2. Enhance search functionality  
3. Update detail display
4. Add validation error display

### Day 4: CLI & Testing
1. Update CLI query commands
2. Update all test cases
3. Full integration testing
4. Documentation updates

## Risk Mitigation

### Data Loss Prevention
- Clean break approach means fresh scans required
- Provide clear migration instructions
- Keep old code in git history for reference

### Validation Robustness  
- Comprehensive field validation with clear error messages
- Graceful handling of malformed files
- Detailed logging for troubleshooting

### Performance Considerations
- Maintain cache TTL optimizations
- Efficient JSON field queries
- Index critical search fields

## Success Criteria

1. **Functional Requirements:**
   - ✅ All required fields properly validated and stored
   - ✅ dir_id generation working with collision handling  
   - ✅ UI displays new field structure correctly
   - ✅ Search works across all new fields
   - ✅ CLI queries support new field filters

2. **Quality Requirements:**
   - ✅ All existing tests pass with new structure
   - ✅ Sample files from fake-home/ scan successfully
   - ✅ Error handling provides clear guidance
   - ✅ Performance maintains current levels

3. **User Experience:**
   - ✅ Clear validation error messages for missing required fields
   - ✅ Intuitive field organization in UI
   - ✅ Smooth transition with minimal learning curve
   - ✅ Enhanced search capabilities improve discoverability

## Questions for Implementation

1. **Team Field Parsing:** Should we parse email addresses from team field or require separate contact_email?
   - **Decision:** Require separate contact_email field for clarity

2. **Optional Field Organization:** How to group optional fields in UI?
   - **Suggestion:** Create logical sections (Project Info, Contacts, Dates, Technical, etc.)

3. **Custom Field Validation:** Any restrictions on custom field names/values?
   - **Suggestion:** Allow alphanumeric + underscore/dash for field names

4. **Search Prioritization:** Should required fields have higher search ranking?
   - **Suggestion:** Yes, weight required field matches higher in search results
