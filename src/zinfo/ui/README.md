# zInfo GUI

A modular, framework-agnostic graphical user interface for the zInfo project indexing system. The architecture supports easy integration of new UI frameworks while maintaining clean separation between UI and business logic. Currently defaults to NullUI for headless/CLI-only usage.

## Features

- **Framework Agnostic**: Pluggable architecture supporting multiple UI frameworks
- **Scan Interface**: Configure and run directory scans with progress indicators
- **Query Interface**: Search and filter indexed projects with advanced filtering options
- **Results Display**: View results in sortable tables with detailed project information
- **Error Handling**: User-friendly error messages and notifications
- **Settings Management**: Configure scan parameters and application preferences
- **Extensible**: Easy to add new UI frameworks via abstract interfaces
- **Headless Support**: NullUI implementation for CLI-only environments

## Architecture

The GUI follows a modular architecture with clean separation of concerns:

### Layers

1. **UI Layer**: Framework-specific implementations (e.g., `null_ui.py` for headless)
2. **Interface Layer** (`__init__.py`): Abstract base classes and protocols for framework-agnostic design
3. **Application Layer** (`app.py`): Business logic and coordination between UI and core
4. **Core Layer**: Existing zinfo functionality (models, scanner, cache)

### Key Components

- **`AbstractUI`**: Abstract base class defining the UI interface
- **`AbstractProgressDialog`**: Interface for progress dialog components
- **`AbstractTableWidget`**: Interface for table display components
- **`AbstractFormWidget`**: Interface for form input components
- **`NullUI`**: Headless implementation for CLI-only usage
- **`ZinfoApp`**: Application controller coordinating UI and core functionality

## Usage

### Running the GUI

The GUI currently defaults to NullUI for headless/CLI-only usage. Future UI framework implementations can be added following the developer guide.

```bash
# Install core dependencies
uv sync

# Run the GUI application (currently defaults to NullUI - headless)
uv run zinfo-gui

# Future: Run with specific UI framework (when implemented)
# ZINFO_GUI=tkinter uv run zinfo-gui
# uv run zinfo-gui --gui qt

# Specify a cache database path:
uv run zinfo-gui /path/to/cache.db
```

### Current Behavior (NullUI)

Since the current implementation uses NullUI for headless operation:

- Scan and query dialogs return `None` (cancelled)
- Results tables and progress dialogs are no-op
- Error/info messages are logged
- Confirmation dialogs always return `False`

This allows the core application logic to run without a graphical interface, suitable for CLI automation and testing.

### Future GUI Usage

When GUI frameworks are implemented, the interface will provide:

1. **Scan Directory**: Configure and run directory scans with progress feedback
2. **Query Projects**: Search and filter indexed projects
3. **View Results**: Browse results in interactive tables
4. **Settings**: Configure application preferences
5. **About**: View application information

## Development

### Architecture Overview

The UI system is built around abstract base classes that define the interface any UI framework must implement:

- **`AbstractUI`**: Main UI interface with methods for windows, dialogs, and messaging
- **`AbstractProgressDialog`**: Progress reporting interface
- **`AbstractTableWidget`**: Data display interface
- **`AbstractFormWidget`**: Form input interface

### Current Implementation

- **`NullUI`**: Headless implementation for CLI/testing environments
- **`ZinfoApp`**: Application controller that coordinates UI and core logic

### Adding New UI Frameworks

For detailed instructions on adding new UI frameworks, see [`DEVELOPER_GUIDE.md`](DEVELOPER_GUIDE.md).

### Testing

```bash
# Run all UI tests
uv run pytest tests/ui/

# Run abstract interface contract tests
uv run pytest tests/ui/test_abstract_ui.py

# Run NullUI implementation tests
uv run pytest tests/ui/test_null_ui.py

# Future: Run framework-specific tests
# uv run pytest tests/ui/test_tkinter_ui.py
```

## Dependencies

- **zinfo**: Core project indexing functionality
- **Python 3.11+**: Minimum Python version
- **UI Frameworks**: None currently required (NullUI is framework-agnostic)

Future UI framework implementations may add dependencies:
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

1. **NullUI Behavior**: Current implementation is headless - dialogs return None/cancelled
2. **Database Errors**: Check file permissions and path validity for cache database
3. **Import Errors**: Ensure all dependencies are installed via `uv sync`
4. **Framework Selection**: Currently only NullUI is supported

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

- [ ] Implement concrete UI frameworks (Tkinter, Qt, Toga, etc.)
- [ ] Advanced filtering and sorting in result tables
- [ ] Export functionality (CSV, JSON, HTML)
- [ ] Drag-and-drop file operations
- [ ] Keyboard shortcuts and hotkeys
- [ ] Customizable themes and styling
- [ ] Settings persistence and management
- [ ] Plugin architecture for additional UI frameworks
- [ ] Accessibility features (screen reader support, keyboard navigation)
- [ ] Internationalization (i18n) support
