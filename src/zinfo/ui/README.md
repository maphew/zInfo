# zInfo GUI

A graphical user interface for the zInfo project indexing system, built with the Toga framework for cross-platform compatibility.

## Features

- **Scan Interface**: Configure and run directory scans with progress indicators
- **Query Interface**: Search and filter indexed projects with advanced filtering options
- **Results Display**: View results in sortable tables with detailed project information
- **Error Handling**: User-friendly error messages and notifications
- **Settings Management**: Configure scan parameters and application preferences
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Architecture

The GUI follows a modular architecture with clean separation of concerns:

### Layers

1. **UI Layer** (`toga_app.py`, `toga_components.py`): Toga-specific UI components
2. **Interface Layer** (`__init__.py`): Abstract interfaces for framework-agnostic design
3. **Application Layer** (`app.py`): Business logic and coordination
4. **Core Layer**: Existing zinfo functionality (models, scanner, cache)

### Key Components

- `ZinfoTogaApp`: Main Toga application implementing the AbstractUI interface
- `ZinfoApp`: Application controller coordinating UI and core functionality
- `ZinfoTable`: Custom table widget for displaying project metadata
- `TogaProgressDialog`: Progress dialog implementation

## Usage

### Running the GUI

```bash
# Install dependencies
uv sync

# Run the GUI application
uv run zinfo-gui

# Or run with specific cache database
uv run zinfo-gui /path/to/cache.db
```

### Using the Interface

1. **Scan Directory**: Click "Scan Directory" to configure and run a scan
2. **Query Projects**: Click "Query Projects" to search and filter results
3. **View Results**: Results are displayed in the table below the toolbar
4. **Settings**: Click "Settings" to configure application preferences
5. **About**: Click "About" for application information

## Development

### Adding New UI Components

1. Create abstract interface in `__init__.py`
2. Implement Toga-specific version in `toga_components.py`
3. Use the component in `toga_app.py`

### Framework Migration

To migrate to a different UI framework:

1. Create new implementation of `AbstractUI` interface
2. Implement required components (tables, dialogs, forms)
3. Update imports in `main.py`
4. No changes needed to application logic or core functionality

### Testing

```bash
# Run GUI tests
uv run pytest tests/ui/

# Run all tests
uv run pytest
```

## Dependencies

- **Toga**: Cross-platform GUI framework
- **zinfo**: Core project indexing functionality
- **Python 3.11+**: Minimum Python version

## Configuration

The GUI supports the following configuration options:

- **Cache Database**: Path to SQLite database for storing scan results
- **Scan Parameters**: Root directory, max depth, and other scan options
- **Query Filters**: Title, author, type, date range, and limit options
- **UI Preferences**: Window size, theme, and display options

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure Toga is properly installed with `uv sync`
2. **Database Errors**: Check file permissions and path validity
3. **UI Freezing**: Long operations run in background threads to keep UI responsive

### Debug Mode

Enable debug logging by setting the environment variable:

```bash
export ZINFO_DEBUG=1
uv run zinfo-gui
```

## Contributing

When contributing to the GUI:

1. Follow the modular architecture patterns
2. Implement both abstract interfaces and concrete implementations
3. Add appropriate error handling and user feedback
4. Include accessibility features where applicable
5. Write tests for new components

## Future Enhancements

- [ ] Additional UI frameworks (PyQt, Kivy, Dear PyGui)
- [ ] Advanced filtering and sorting options
- [ ] Export functionality (CSV, JSON, HTML)
- [ ] Drag-and-drop file operations
- [ ] Keyboard shortcuts and hotkeys
- [ ] Customizable themes and styling
- [ ] Plugin architecture for additional scanners
