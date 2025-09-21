#!/usr/bin/env uv run
# /// script
# dependencies = []
# ///
"""Debug script to reproduce GUI issues and test fixes."""

import logging
import threading
import tkinter as tk
from tkinter import ttk

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s [Thread: %(thread)d]"
)

logger = logging.getLogger(__name__)

def test_threading_issue():
    """Reproduce the threading issue that causes XCB errors."""
    logger.info("Starting threading issue test")
    
    root = tk.Tk()
    root.title("Threading Debug Test")
    
    def create_dialog_from_thread():
        """This should cause XCB threading issues - GUI operations from worker thread."""
        logger.info("Creating dialog from worker thread - this should cause issues")
        try:
            dialog = tk.Toplevel(root)
            dialog.title("Worker Thread Dialog")
            label = ttk.Label(dialog, text="This dialog was created from a worker thread!")
            label.pack(padx=20, pady=20)
            logger.info("Dialog created successfully from worker thread")
        except Exception as e:
            logger.error(f"Error creating dialog from worker thread: {e}")
    
    def safe_create_dialog():
        """Safe version using root.after() to schedule on main thread."""
        logger.info("Scheduling dialog creation on main thread")
        
        def _create_dialog():
            logger.info("Creating dialog on main thread")
            dialog = tk.Toplevel(root)
            dialog.title("Main Thread Dialog")
            label = ttk.Label(dialog, text="This dialog was created safely on the main thread!")
            label.pack(padx=20, pady=20)
        
        root.after(0, _create_dialog)
    
    # Buttons to test both approaches
    unsafe_btn = ttk.Button(root, text="Create Dialog (Unsafe - Worker Thread)", 
                           command=lambda: threading.Thread(target=create_dialog_from_thread, daemon=True).start())
    unsafe_btn.pack(pady=10, padx=20)
    
    safe_btn = ttk.Button(root, text="Create Dialog (Safe - Main Thread)", 
                         command=lambda: threading.Thread(target=safe_create_dialog, daemon=True).start())
    safe_btn.pack(pady=10, padx=20)
    
    # Font size test
    font_label = ttk.Label(root, text="Default font size test", font=("TkDefaultFont", 10))
    font_label.pack(pady=10)
    
    large_font_label = ttk.Label(root, text="Larger font size test", font=("TkDefaultFont", 14))
    large_font_label.pack(pady=10)
    
    logger.info("GUI initialized, starting main loop")
    root.mainloop()

if __name__ == "__main__":
    test_threading_issue()
