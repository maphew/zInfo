"""Main entry point for zinfo GUI application.

This module provides the main entry point for launching the zinfo GUI application.
"""

import logging
from pathlib import Path
from typing import Optional

from .toga_app import ZinfoTogaApp

logger = logging.getLogger(__name__)


def run_gui(cache_path: Optional[Path] = None) -> None:
    """Run the zinfo GUI application.

    Args:
        cache_path: Optional path to the cache database. If None, uses default.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info("Starting zinfo GUI application")

    # Create and start the GUI application
    gui_app = ZinfoTogaApp()
    gui_app.startup()

    # Initialize cache if path provided
    if cache_path:
        gui_app.zinfo_app.initialize_cache(cache_path)

    # Show the main window
    gui_app.show_main_window()


def main():
    """Main entry point for the GUI application."""
    import sys

    # Parse command line arguments
    cache_path = None
    if len(sys.argv) > 1:
        cache_path = Path(sys.argv[1])

    # Run the GUI
    run_gui(cache_path)


if __name__ == "__main__":
    main()
