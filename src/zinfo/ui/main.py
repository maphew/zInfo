"""Main entry point for zinfo GUI application.

This module provides the main entry point for launching the zinfo GUI application.
Supports selecting the UI framework via:
- Environment variable: ZINFO_GUI=tk|toga (default: tk)
- Optional CLI flag: --gui tk|toga
- Optional positional arg for cache path remains supported for backwards compatibility.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _select_gui_from_args_and_env(argv: list[str]) -> tuple[Optional[str], list[str], Optional[Path]]:
    """Parse argv and environment to select GUI framework and cache path.

    Returns:
        (gui_mode, remaining_argv, cache_path)
    """
    gui_mode: Optional[str] = None
    cache_path: Optional[Path] = None
    remaining = list(argv)

    # Parse --gui[=value] or "--gui value"
    if "--gui" in remaining:
        idx = remaining.index("--gui")
        # Expect a following value
        try:
            gui_mode = remaining[idx + 1]
            del remaining[idx:idx + 2]
        except IndexError:
            logger.warning("--gui provided without a value; ignoring")
            del remaining[idx]
    else:
        # Look for --gui=value form
        for i, arg in enumerate(list(remaining)):
            if arg.startswith("--gui="):
                gui_mode = arg.split("=", 1)[1].strip() or None
                remaining.pop(i)
                break

    # Fallback to environment variable
    if not gui_mode:
        gui_mode = os.environ.get("ZINFO_GUI")

    # Determine cache_path if any positional arg remains (first non-flag)
    positional = [a for a in remaining[1:] if not a.startswith("-")]  # skip argv[0]
    if positional:
        try:
            cache_path = Path(positional[0])
        except Exception:
            cache_path = None

    return gui_mode, remaining, cache_path


def _instantiate_gui(gui_mode: Optional[str]):
    """Dynamically instantiate the selected GUI app class.

    Prefers Tk (tkinter) by default. Falls back to Tk if Toga import fails.
    """
    mode = (gui_mode or "tk").lower()
    if mode == "toga":
        try:
            from .toga_app import ZinfoTogaApp
            return ZinfoTogaApp()
        except Exception as e:
            logger.warning(f"Requested Toga GUI but failed to import/start ({e!r}); falling back to Tkinter")

    # Default/Fallback: Tkinter
    from .tk_app import ZinfoTkApp
    return ZinfoTkApp()


def run_gui(cache_path: Optional[Path] = None, gui: Optional[str] = None) -> None:
    """Run the zinfo GUI application.

    Args:
        cache_path: Optional path to the cache database. If None, uses default.
        gui: Optional GUI selection ('tk' or 'toga'); overrides env if provided.
    """
    # Configure logging once
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Starting zinfo GUI application")

    # Create and start the GUI application
    gui_app = _instantiate_gui(gui)
    gui_app.startup()

    # Initialize cache if path provided
    if cache_path:
        # Some UI implementations expose zinfo_app after startup
        if getattr(gui_app, "zinfo_app", None) is not None:
            gui_app.zinfo_app.initialize_cache(cache_path)

    # Show the main window (enters main loop)
    gui_app.show_main_window()


def main():
    """Main entry point for the GUI application."""
    gui_mode, argv, cache_path = _select_gui_from_args_and_env(sys.argv)

    # Run the GUI
    run_gui(cache_path, gui=gui_mode)


if __name__ == "__main__":
    main()
