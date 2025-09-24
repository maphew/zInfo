# zInfo UI

A modular user interface system for zInfo, providing both a headless NullUI implementation for CLI-only environments and a complete FastHTML-based web interface for browsing, searching, filtering, and managing project indexes. The architecture supports clean separation between UI and business logic with extensible framework integration.

## Features

- **Web Interface**: Complete FastHTML-based web UI for browsing, searching, and filtering projects
- **In-App Scanning**: Trigger directory scans directly from the web interface
- **Responsive Design**: Mobile-friendly interface with card-based layouts
- **HTMX Integration**: Dynamic updates without full page reloads
- **Pico CSS Styling**: Clean, professional interface with no custom CSS
- **Pagination**: Efficient browsing of large project indexes
- **Framework Agnostic**: Pluggable architecture supporting multiple UI frameworks
- **Headless Support**: NullUI implementation for CLI-only environments
- **Error Handling**: User-friendly error messages and notifications
- **Extensible**: Easy to add new UI frameworks via abstract interfaces

## Architecture

The GUI follows a modular architecture with clean separation of concerns:

### Layers

1. **Web UI Layer** (`fh_ui.py`): FastHTML-based web interface with HTMX and Pico CSS
2. **Headless UI Layer** (`null_ui.py`): NullUI implementation for CLI-only environments
3. **Interface Layer** (`__init__.py`): Abstract base classes and protocols for framework-agnostic design
4. **Application Layer** (`app.py`): Business logic and coordination between UI and core
5. **Core Layer**: Existing zinfo functionality (models, scanner, cache)

### Key Components

- **`fh_ui.py`**: FastHTML web application with routes for browsing, searching, and scanning
- **`AbstractUI`**: Abstract base class defining the UI interface
- **`AbstractProgressDialog`**: Interface for progress dialog components
- **`AbstractTableWidget`**: Interface for table display components
- **`AbstractFormWidget`**: Interface for form input components
- **`NullUI`**: Headless implementation for CLI-only usage
- **`ZinfoApp`**: Application controller coordinating UI and core functionality
- **`static/script.js`**: HTMX scripts for dynamic web interactions

## Usage

### Running the Web UI

The primary user interface is the FastHTML-based web application:

```bash
# Install dependencies
uv sync

# Start the web server
uv run zinfo-web

# Access at http://localhost:5001 by default
```

### Running the Headless GUI

For CLI-only environments, the NullUI implementation is available:

```bash
# Run the headless GUI application
uv run zinfo-gui

# Specify a cache database path:
uv run zinfo-gui /path/to/cache.db
```

### Web UI Features

The FastHTML web interface provides:

1. **Browse Projects**: View all indexed projects in a paginated, card-based layout
2. **Search and Filter**: Real-time search with filters for title, client, team, and more
3. **In-App Scanning**: Configure and trigger directory scans with progress feedback
4. **Project Details**: View detailed information for individual projects
5. **Responsive Design**: Works on desktop, tablet, and mobile devices

### NullUI Behavior

The NullUI implementation provides headless operation for CLI environments:

- Scan and query dialogs return `None` (cancelled)
- Results tables and progress dialogs are no-op
- Error/info messages are logged
- Confirmation dialogs always return `False`

This allows the core application logic to run without a graphical interface, suitable for CLI automation and testing.

## Development

### Architecture Overview

The UI system is built around abstract base classes that define the interface any UI framework must implement:

- **`AbstractUI`**: Main UI interface with methods for windows, dialogs, and messaging
- **`AbstractProgressDialog`**: Progress reporting interface
- **`AbstractTableWidget`**: Data display interface
- **`AbstractFormWidget`**: Form input interface

### Current Implementation

- **`fh_ui.py`**: Complete FastHTML web application with idiomatic patterns
- **`NullUI`**: Headless implementation for CLI/testing environments
- **`ZinfoApp`**: Application controller that coordinates UI and core logic
- **`static/script.js`**: HTMX scripts for dynamic interactions

### Adding New UI Frameworks

For detailed instructions on adding new UI frameworks, see [`DEVELOPER_GUIDE.md`](DEVELOPER_GUIDE.md).

### Testing

```bash
# Run all UI tests
uv run pytest tests/ui/

# Run FastHTML web UI tests
uv run pytest tests/ui/test_fh_ui.py

# Run abstract interface contract tests
uv run pytest tests/ui/test_abstract_ui.py

# Run NullUI implementation tests
uv run pytest tests/ui/test_null_ui.py
```

## Dependencies

- **zinfo**: Core project indexing functionality
- **Python 3.11+**: Minimum Python version
- **FastHTML**: Web framework for the web UI (python-fasthtml)
- **UI Frameworks**: None required for NullUI (framework-agnostic)

Future native UI framework implementations may add dependencies:
- Tkinter (usually built-in with Python)
- PyQt6/PySide6 for Qt-based interfaces
- Toga for cross-platform native widgets
- Kivy for touch interfaces
- etc.

## Configuration

The UI system supports the following configuration options:

- **Cache Database**: Path to SQLite database for storing scan results
- **Scan Parameters**: Root directory, max depth, and other scan options
- **Query Filters**: Title, author, type, date range, and limit options
- **UI Framework**: Selection of UI implementation (future enhancement)

## Troubleshooting

### Common Issues

1. **Web UI Not Starting**: Ensure FastHTML is installed and port 5001 is available
2. **NullUI Behavior**: Headless implementation - dialogs return None/cancelled
3. **Database Errors**: Check file permissions and path validity for cache database
4. **Import Errors**: Ensure all dependencies are installed via `uv sync`
5. **Scan Not Working**: Verify zinfo scan has been run first to populate the database

### Debug Mode

Enable debug logging by setting the environment variable:

```bash
export ZINFO_DEBUG=1
uv run zinfo-gui
```

## Contributing

When contributing to the GUI system:

1. Follow the abstract interface patterns defined in `__init__.py`
2. Implement all required abstract methods
3. Add comprehensive tests following the NullUI test patterns
4. Update documentation in both README and DEVELOPER_GUIDE
5. Consider framework-specific best practices and platform conventions
6. Ensure thread-safety for long-running operations

## Future Enhancements

- [x] FastHTML web UI implementation (completed)
- [ ] Implement concrete native UI frameworks (Tkinter, Qt, Toga, etc.)
- [ ] Advanced filtering and sorting in web UI
- [ ] Export functionality (CSV, JSON, HTML)
- [ ] Drag-and-drop file operations
- [ ] Keyboard shortcuts and hotkeys
- [ ] Customizable themes and styling
- [ ] Settings persistence and management
- [ ] Plugin architecture for additional UI frameworks
- [ ] Accessibility features (screen reader support, keyboard navigation)
- [ ] Internationalization (i18n) support
