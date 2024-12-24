"""Test the map project listing functionality.

This script tests the MapProjectLister class by generating an HTML index of
test map projects. Before running this test, ensure you've run setup_test_env.py
to create the test environment.

Usage:
    1. First run setup_test_env.py to create test data:
       pixi run python test/setup_test_env.py
    
    2. Then run this test script:
       pixi run python test/test_envmapplist.py
    
    3. Check the generated HTML file at:
       test/test_output/maps/Map-Project-Index.html
"""
import sys
from pathlib import Path
import shutil

# Add the src directory to Python path
src_dir = Path(__file__).parent.parent / 'src'
sys.path.append(str(src_dir))

from zinfo.envmapplist import MapProjectLister

def setup_test_data(base_dir: Path):
    """Create test map project data."""
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Project 1 - Local file with Doc directory
    project1_dir = base_dir / 'project1'
    project1_dir.mkdir()
    
    with open(Path(__file__).parent / 'fixtures/sample_project.ini') as f:
        (project1_dir / 'project.ini').write_text(f.read())
    
    # Create Doc directory for project1
    doc_dir = project1_dir / 'Doc'
    doc_dir.mkdir()
    
    # Project 2 - Web-based project
    project2_dir = base_dir / 'project2'
    project2_dir.mkdir()
    
    project2_ini = """[Project]
title = Test Map Project 2
link = https://example.com/maps/project2
contact = external.mapper@example.com"""
    
    (project2_dir / 'project.ini').write_text(project2_ini)
    
    print(f'Test map projects created at: {base_dir}')

def main():
    """Test the MapProjectLister with local test data."""
    test_output = Path(__file__).parent / 'test_output'
    if test_output.exists():
        shutil.rmtree(test_output)
    test_output.mkdir(exist_ok=True)
    
    # Set up test environment
    maps_dir = test_output / 'maps'
    setup_test_data(maps_dir)
    
    # Generate the HTML index
    output_file = maps_dir / 'Map-Project-Index.html'
    print(f"\nUsing test data from: {maps_dir}")
    
    project_lister = MapProjectLister(maps_dir, output_file)
    project_lister.generate()
    
    print(f"\nHTML index generated at: {output_file}")
    print("Open this file in a web browser to view the results.")

if __name__ == '__main__':
    main()
