"""Test the environment application listing functionality.

This script tests the EnvAppLister class by generating an HTML index of
test applications. The test data will be created in a temporary test_output
directory that should not be committed to version control.
"""
import sys
from pathlib import Path
import shutil

# Add the src directory to Python path
src_dir = Path(__file__).parent.parent / 'src'
sys.path.append(str(src_dir))

from zinfo.envapplist import EnvAppLister
from fixtures.setup_test_env import setup_test_environment

def main():
    """Test the EnvAppLister with local test data."""
    # Create test output directory that will be ignored by version control
    test_output = Path(__file__).parent / 'test_output'
    if test_output.exists():
        shutil.rmtree(test_output)
    test_output.mkdir(exist_ok=True)
    
    # Set up test environment in the output directory
    infosys_dir = test_output / 'infosys'
    setup_test_environment(infosys_dir)
    
    # Generate the HTML index
    output_file = infosys_dir / 'envapps.html'
    print(f"\nUsing test data from: {infosys_dir}")
    
    app_lister = EnvAppLister(infosys_dir, output_file)
    app_lister.generate()
    
    print(f"\nHTML index generated at: {output_file}")
    print("Open this file in a web browser to view the results.")

if __name__ == '__main__':
    main()
