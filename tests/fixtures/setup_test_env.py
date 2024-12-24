"""Test environment setup utilities.

This module provides functions to create test data for the zinfo application.
The actual test data should be created in a directory that is ignored by
version control (e.g., tests/test_output).
"""
from pathlib import Path

def setup_test_environment(infosys_dir: Path) -> None:
    """Create test directory structure and sample files.
    
    Args:
        infosys_dir: Directory where test data should be created
    """
    # Create base directory
    infosys_dir.mkdir(parents=True, exist_ok=True)
    
    # Test Application 1 - Local setup file with Doc directory
    app1_dir = infosys_dir / 'app1'
    app1_dir.mkdir()
    
    app1_info = app1_dir / 'appinfo.txt'
    app1_info.write_text(
        'Test Application 1\n'
        'setup.bat\n'
        'john.doe@test.com'
    )
    
    # Create Doc directory for app1
    doc_dir = app1_dir / 'Doc'
    doc_dir.mkdir()
    
    # Test Application 2 - Web application
    app2_dir = infosys_dir / 'app2'
    app2_dir.mkdir()
    
    app2_info = app2_dir / 'appinfo.txt'
    app2_info.write_text(
        'Test Application 2\n'
        'https://example.com/app2\n'
        'support@gov.yk.ca'
    )
    
    print(f'Test environment created at: {infosys_dir}')
    print('Directory structure:')
    print('infosys/')
    print('|-- app1/')
    print('|   |-- appinfo.txt')
    print('|   +-- Doc/')
    print('+-- app2/')
    print('    +-- appinfo.txt')
