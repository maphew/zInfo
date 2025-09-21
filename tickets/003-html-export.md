# Enhancement Ticket: HTML Export Functionality

## Summary
Add CLI command to export cached resources to styled HTML tables, replicating the HTML generation functionality from legacy `envapplist.py` and `envmapplist.py` scripts.

## Background
The legacy scripts generate styled HTML tables with project listings, including:
- Professional styling with headers and borders
- Clickable links for titles, contacts, and documentation
- JavaScript clipboard functionality
- Windows-specific path handling for file:// links
- Contact email integration with subject lines

## Example Input/Output

**CLI Invocation:**
```bash
zinfo export --format html --output projects.html --cache-db zinfo.db
```

**Generated HTML Output:**
```html
<HTML>
<body>
    <h1>Environment System List</h1>
    <h2>"setup.bat" links will only work using Internet Explorer.</h2>
    <table border="1" cellpadding="10">
        <tr>
            <td><a href="file:///C:/projects/app1/setup.bat">App Title 1</a></td>
            <td><a href="file:///C:/projects/app1/setup.bat">setup.bat</a></td>
            <td><a href="mailto:contact@gov.yk.ca?Subject=Environment Application: App Title 1">contact@gov.yk.ca</a></td>
            <td><a href="file:///C:/projects/app1/Doc">\\server\projects\app1\Doc</a></td>
        </tr>
    </table>
</body>
</HTML>
```

## Current Impact
- **Users affected**: All users who need HTML exports for sharing or web publishing
- **Current workaround**: Must maintain separate legacy scripts for HTML generation
- **Data loss risk**: Cached data cannot be exported to HTML format
- **Integration gap**: New scanner architecture lacks export capabilities

## Rationale for Deferral
- **Priority**: High - key functionality for data sharing and publishing
- **Complexity**: Medium - requires HTML template system and link formatting
- **Dependencies**: Requires scanner implementations (tickets #001, #002)
- **Migration path**: Enables complete migration from legacy scripts

## Design Sketch

### Architecture Integration
```
CLI (export command)
    ↓
Cache.load_resources()
    ↓
HTMLExporter
    ↓
LinkFormatter (utility)
    ↓
ContactNormalizer (utility)
    ↓
HTML Template
    ↓
Output File
```

### Implementation Plan
1. Create `HTMLExporter` class for HTML generation
2. Add `export` CLI command with format options
3. Implement HTML template with styling
4. Integrate link formatting utilities
5. Add contact normalization with mailto links
6. Support multiple output formats (future extensibility)

### Code Structure
```python
class HTMLExporter:
    def __init__(self, link_formatter: LinkFormatter, contact_normalizer: ContactNormalizer):
        self.link_formatter = link_formatter
        self.contact_normalizer = contact_normalizer

    def export(self, resources: List[ResourceMetadata], output_path: Path) -> None:
        html_content = self._generate_html(resources)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _generate_html(self, resources: List[ResourceMetadata]) -> str:
        # Generate styled HTML table
        # Use templates for maintainability
        # Include JavaScript for clipboard functionality
        pass

@click.command()
@click.option('--format', type=click.Choice(['html']), default='html')
@click.option('--output', '-o', type=click.Path(path_type=Path), required=True)
@click.option('--cache-db', type=click.Path(path_type=Path), default=Path('zinfo.db'))
def export(format: str, output: Path, cache_db: Path):
    """Export cached resources to various formats."""
    cache = Cache(cache_db)
    resources = cache.get_all_resources()

    if format == 'html':
        exporter = HTMLExporter(LinkFormatter(), ContactNormalizer())
        exporter.export(resources, output)
```

## Dependencies/Blockers
- **Dependencies**: Link formatting utilities (ticket #004), Contact normalization (ticket #004)
- **Blockers**: None
- **Related**: Requires scanner implementations (tickets #001, #002) for full functionality

## Acceptance Criteria
- [ ] `HTMLExporter` class created with proper architecture
- [ ] `export` CLI command added with format options
- [ ] HTML output matches legacy script styling and functionality
- [ ] Link formatting handles file:// and HTTP links correctly
- [ ] Contact normalization applies @gov.yk.ca fallback
- [ ] Doc/ directory links are generated correctly
- [ ] JavaScript clipboard functionality included
- [ ] Windows path handling for file:// links
- [ ] Cross-platform compatibility maintained
- [ ] Unit tests for HTML generation
- [ ] Integration tests with cached data

## Testing Strategy
- Unit tests for HTML generation with sample data
- Integration tests with actual cache database
- Cross-platform tests for path handling
- Edge case tests for missing data fields
- HTML validation tests

## Migration Notes
- Complete replacement for legacy HTML generation
- Maintains backward compatibility in output format
- Enables automation of HTML export process
- Supports future format extensions (JSON, CSV, etc.)
