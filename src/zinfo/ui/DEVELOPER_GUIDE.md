# zInfo UI Framework Integration Guide

**Note: This guide is for future native GUI framework implementations, which are not currently planned. The primary user interface for zInfo is now the FastHTML-based web UI. This document remains for reference if native GUI support is added in the future.**

This guide provides comprehensive instructions for developers who want to integrate new UI frameworks into the zInfo project. The zInfo GUI architecture is designed to be framework-agnostic, allowing easy swapping between different UI toolkits.

## Architecture Overview

zInfo uses a modular, layered architecture that separates UI concerns from business logic:

### Core Components

- **`AbstractUI`**: Abstract base class defining the interface for all UI implementations
- **`AbstractProgressDialog`**: Interface for progress dialog components
- **`AbstractTableWidget`**: Interface for table display components
- **`AbstractFormWidget`**: Interface for form input components
- **`ZinfoApp`**: Application controller that coordinates between UI and core functionality
- **Concrete Implementations**: Framework-specific implementations (e.g., `NullUI` for headless usage)

### Data Flow

```
User Input -> UI Implementation -> ZinfoApp -> Core (Scanner/Cache/Models) -> UI Implementation -> User Output
```

## Adding a New UI Framework

### Step 1: Choose Your Framework

Popular options include:
- **Tkinter**: Standard Python GUI (built-in)
- **Toga**: Cross-platform native widgets
- **PyQt/PySide**: Powerful Qt-based GUIs
- **Kivy**: OpenGL-accelerated touch interfaces
- **Dear PyGui**: Immediate mode GUI
- **Custom**: Web-based (Flask/Django + HTML), terminal (curses), etc.

### Step 2: Create Framework-Specific Implementation

Create a new module in `src/zinfo/ui/` (e.g., `tkinter_ui.py`, `qt_ui.py`).

#### Basic Structure

```python
from . import AbstractUI, AbstractProgressDialog, ScanConfig, QueryFilter
from zinfo.core.models import ResourceMetadata

class YourFrameworkProgressDialog(AbstractProgressDialog):
    """Progress dialog implementation for YourFramework."""

    def __init__(self, title: str, message: str):
        # Initialize your framework's progress dialog
        pass

    def update_progress(self, current: int, total: int, message: str = "") -> None:
        # Update progress display
        pass

    def close(self) -> None:
        # Close the dialog
        pass

    def is_cancelled(self) -> bool:
        # Return True if user cancelled
        return False

class YourFrameworkUI(AbstractUI):
    """YourFramework implementation of the UI interface."""

    def __init__(self):
        self.scan_progress_callback = None
        self.query_progress_callback = None
        self.zinfo_app = None

    def startup(self) -> None:
        """Initialize the UI and create the application controller."""
        from .app import ZinfoApp
        self.zinfo_app = ZinfoApp(self)

    def show_main_window(self) -> None:
        """Show the main application window."""
        # Create and display main window
        pass

    def show_scan_dialog(self, config: ScanConfig) -> Optional[ScanConfig]:
        """Show scan configuration dialog."""
        # Display dialog, return updated config or None if cancelled
        pass

    def show_query_dialog(self, filter_config: QueryFilter) -> Optional[QueryFilter]:
        """Show query filter dialog."""
        # Display dialog, return updated filter or None if cancelled
        pass

    def show_results_table(self, results: List[ResourceMetadata]) -> None:
        """Display results in a table."""
        # Show results table
        pass

    def show_progress_dialog(self, title: str, message: str) -> AbstractProgressDialog:
        """Return a progress dialog instance."""
        return YourFrameworkProgressDialog(title, message)

    def show_error_message(self, title: str, message: str) -> None:
        """Show error message dialog."""
        # Display error dialog
        pass

    def show_info_message(self, title: str, message: str) -> None:
        """Show info message dialog."""
        # Display info dialog
        pass

    def show_confirmation_dialog(self, title: str, message: str) -> bool:
        """Show confirmation dialog."""
        # Return True if confirmed
        return False

    def set_scan_progress_callback(self, callback) -> None:
        """Set scan progress callback."""
        self.scan_progress_callback = callback

    def set_query_progress_callback(self, callback) -> None:
        """Set query progress callback."""
        self.query_progress_callback = callback
```

### Step 3: Implement Required Components

Depending on your framework, you may need to implement additional abstract components:

#### Table Widget Implementation

```python
from . import AbstractTableWidget

class YourFrameworkTable(AbstractTableWidget):
    """Table widget for displaying resource metadata."""

    def set_data(self, data: List[ResourceMetadata]) -> None:
        # Populate table with data
        pass

    def get_selected_items(self) -> List[ResourceMetadata]:
        # Return selected items
        return []

    def refresh(self) -> None:
        # Refresh display
        pass

    def set_filter(self, filter_text: str) -> None:
        # Apply text filter
        pass
```

#### Form Widget Implementation

```python
from . import AbstractFormWidget

class YourFrameworkForm(AbstractFormWidget):
    """Form widget for configuration dialogs."""

    def get_field_value(self, field_name: str):
        # Get field value
        pass

    def set_field_value(self, field_name: str, value):
        # Set field value
        pass

    def validate(self) -> bool:
        # Validate form
        return True

    def get_all_values(self) -> dict:
        # Return all values
        return {}
```

### Step 4: Update Main Entry Point

Modify `src/zinfo/ui/main.py` to support your new framework:

```python
def _instantiate_gui(framework: str = "null"):
    """Instantiate the appropriate UI implementation."""
    if framework == "tkinter":
        from .tkinter_ui import TkinterUI
        return TkinterUI()
    elif framework == "qt":
        from .qt_ui import QtUI
        return QtUI()
    else:  # default to null
        from .null_ui import NullUI
        return NullUI()
```

### Step 5: Add Framework Selection Logic

Update the CLI or configuration to allow framework selection:

```python
# In main.py or CLI
def run_gui(framework: str = "null", cache_path: Optional[Path] = None):
    gui_app = _instantiate_gui(framework)
    # ... rest of initialization
```

### Step 6: Handle Dependencies

Add framework-specific dependencies to `pyproject.toml`:

```toml
[project.optional-dependencies]
tkinter = []  # Usually built-in
toga = ["toga"]
qt = ["PyQt6"]
kivy = ["kivy"]
```

### Step 7: Create Tests

Create comprehensive tests following the pattern in `tests/ui/test_null_ui.py`:

```python
# tests/ui/test_yourframework_ui.py
import pytest
from zinfo.ui.yourframework_ui import YourFrameworkUI

def test_yourframework_ui_initialization():
    ui = YourFrameworkUI()
    assert ui.zinfo_app is None

def test_show_main_window():
    ui = YourFrameworkUI()
    ui.show_main_window()  # Should not raise

# Add tests for all abstract methods
```

### Step 8: Update Documentation

- Add your framework to this guide
- Update the main UI README
- Document any framework-specific setup requirements

## Framework-Specific Examples

### Tkinter Implementation

```python
import tkinter as tk
from tkinter import ttk, messagebox

class TkinterProgressDialog(AbstractProgressDialog):
    def __init__(self, title: str, message: str):
        self.root = tk.Toplevel()
        self.root.title(title)
        self.progress = ttk.Progressbar(self.root, mode='determinate')
        self.progress.pack(pady=10)
        self.label = tk.Label(self.root, text=message)
        self.label.pack()

    def update_progress(self, current: int, total: int, message: str = ""):
        self.progress['value'] = (current / total) * 100
        self.label.config(text=message)
        self.root.update()

    def close(self):
        self.root.destroy()

    def is_cancelled(self):
        return False  # Could add cancel button
```

### Web Framework (Flask) Implementation

```python
from flask import Flask, render_template, request, jsonify

class FlaskUI(AbstractUI):
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def main_window():
            return render_template('main.html')

        @self.app.route('/scan', methods=['POST'])
        def scan():
            # Handle scan request
            pass

    def show_main_window(self):
        self.app.run(debug=True)

    # Implement other methods to return JSON responses or redirect
```

## Best Practices

### Error Handling
- Always wrap framework-specific operations in try-catch
- Provide meaningful error messages to users
- Log errors for debugging

### Threading
- GUI operations should be thread-safe
- Long-running operations (scans, queries) should run in background threads
- Use appropriate synchronization mechanisms

### User Experience
- Follow platform conventions
- Provide clear feedback for all operations
- Support keyboard shortcuts where appropriate
- Ensure accessibility features

### Testing
- Test all abstract method implementations
- Mock framework components where possible
- Test error conditions and edge cases
- Run tests in CI/CD pipeline

### Performance
- Lazy load heavy components
- Implement virtual scrolling for large result sets
- Cache expensive operations
- Provide progress feedback for long operations

## Common Pitfalls

1. **Blocking Operations**: Don't perform long operations on the main UI thread
2. **Framework Assumptions**: Don't assume specific framework behaviors
3. **State Management**: Keep UI state synchronized with application state
4. **Resource Cleanup**: Properly dispose of framework resources
5. **Cross-Platform Issues**: Test on all target platforms

## Contributing

When contributing a new UI framework:

1. Follow the established patterns in existing implementations
2. Include comprehensive tests
3. Update documentation
4. Consider performance implications
5. Test integration with existing functionality

## Future Enhancements

- Plugin architecture for third-party UI frameworks
- Theme support across frameworks
- Advanced component abstractions
- UI framework benchmarking tools
