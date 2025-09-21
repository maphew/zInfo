# zInfo GUI

A graphical user interface for the zInfo project indexing system, designed with a framework-agnostic interface to support multiple UI toolkits. Currently, it defaults to Tkinter, with optional support for Toga.

## Features

- **Scan Interface**: Configure and run directory scans with progress indicators
- **Query Interface**: Search and filter indexed projects with advanced filtering options
- **Results Display**: View results in sortable tables with detailed project information
- **Error Handling**: User-friendly error messages and notifications
- **Settings Management**: Configure scan parameters and application preferences
- **Cross-Platform**: Works on Windows, macOS, and Linux (Tkinter is generally pre-installed)

## Architecture

The GUI follows a modular architecture with clean separation of concerns:

### Layers

1. **UI Layer** (`tk_app.py`, `tk_components.py` for Tkinter; `toga_app.py`, `toga_components.py` for Toga): Framework-specific UI components
2. **Interface Layer** (`__init__.py`): Abstract interfaces for framework-agnostic design
3. **Application Layer** (`app.py`): Business logic and coordination
4. **Core Layer**: Existing zinfo functionality (models, scanner, cache)

### Key Components

- `ZinfoTkApp`: Main Tkinter application implementing the AbstractUI interface
- `ZinfoTogaApp`: (Optional) Toga application implementing the AbstractUI interface
- `ZinfoApp`: Application controller coordinating UI and core functionality
- `ZinfoTable`: Custom table widget for displaying project metadata (Tkinter and Toga versions)
- `TkProgressDialog`: Progress dialog implementation for Tkinter
- `TogaProgressDialog`: (Optional) Progress dialog implementation for Toga

## Usage

### Running the GUI

The GUI now defaults to Tkinter.

```bash
# Install core dependencies (tkinter is usually built-in)
uv sync

# Run the GUI application (defaults to Tkinter)
uv run zinfo-gui

# To run with Toga (if installed as an optional dependency):
# 1. Install Toga:
uv sync -E toga
# 2. Run with explicit selection:
ZINFO_GUI=toga uv run zinfo-gui
# Or using the --gui flag:
uv run zinfo-gui --gui toga

# You can also specify a cache database path:
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
2. Implement framework-specific versions (e.g., in `tk_components.py` or `toga_components.py`)
3. Use the component in the respective framework's app (e.g., `tk_app.py` or `toga_app.py`)

### Framework Migration

To migrate to a different UI framework or add a new one:

1. Create new implementation of `AbstractUI` interface
2. Implement required components (tables, dialogs, forms)
3. Update `main.py` to include the new framework in the selection logic
4. No changes needed to application logic or core functionality

### Testing

```bash
# Run all tests (Toga tests will be skipped if Toga is not installed)
uv run pytest

# Run only Tkinter GUI tests
uv run pytest tests/ui/test_tk_components.py

# Run only Toga GUI tests (requires Toga installed: uv sync -E toga)
uv run pytest -m toga tests/ui/test_toga_components.py
```

## Dependencies

- **Tkinter**: Standard Python GUI toolkit (usually built-in)
- **Toga** (Optional): Cross-platform GUI framework (requires `uv sync -E toga`)
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

1. **Tkinter not found**: Ensure your Python installation includes Tkinter. On some Linux systems, it might require a separate package (e.g., `python3-tk`).
2. **Toga import errors**: If you explicitly select Toga but it's not installed, ensure you run `uv sync -E toga`.
3. **Database Errors**: Check file permissions and path validity.
4. **UI Freezing**: Long operations run in background threads to keep UI responsive.

### Debug Mode

Enable debug logging by setting the environment variable:

```bash
export ZINFO_DEBUG=1
uv run zinfo-gui
```

## Contributing

When contributing to the GUI:

1. Follow the modular architecture patterns.
2. Implement both abstract interfaces and concrete implementations.
3. Add appropriate error handling and user feedback.
4. Include accessibility features where applicable.
5. Write tests for new components.

## Future Enhancements

- [ ] Additional UI frameworks (PyQt, Kivy, Dear PyGui)
- [ ] Advanced filtering and sorting options
- [ ] Export functionality (CSV, JSON, HTML)
- [ ] Drag-and-drop file operations
- [ ] Keyboard shortcuts and hotkeys
- [ ] Customizable themes and styling
- [ ] Plugin architecture for additional scanners
