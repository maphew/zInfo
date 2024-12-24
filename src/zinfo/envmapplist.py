"""Generate HTML index of Geomatics Unit map projects.

This script scans a directory for map project folders containing metadata files
and generates a clickable HTML index with links to project files and documentation.

Originally by Matt Wilkie, 2017-12-05
Forked from envapplist.py by Jon Hourd
"""
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import logging
from email.utils import formataddr
import html
import configparser
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProjectInfo:
    """Store project information parsed from metadata file."""
    title: str
    link: str
    contact: str
    doc_dir: Optional[Path] = None

class MapProjectLister:
    """Generate HTML index of map projects."""
    
    def __init__(self, base_dir: Path, output_file: Path, meta_filename: str = 'project.ini'):
        """Initialize with base directory and output file path.
        
        Args:
            base_dir: Root directory containing map project folders
            output_file: Path where HTML output will be written
            meta_filename: Name of the metadata file to look for in project folders
        """
        self.base_dir = Path(base_dir)
        self.output_file = Path(output_file)
        self.meta_filename = meta_filename
        self.project_list = []
        self.config = configparser.ConfigParser()

    def read_project_info(self, project_dir: Path) -> Optional[ProjectInfo]:
        """Read project metadata from project.ini.
        
        Args:
            project_dir: Directory containing the project.ini file
            
        Returns:
            ProjectInfo object if successful, None if file not found or invalid
        """
        info_file = project_dir / self.meta_filename
        try:
            if info_file.is_file():
                self.config.read(info_file)
                if 'Project' in self.config:
                    project = self.config['Project']
                    return ProjectInfo(
                        title=project.get('title', ''),
                        link=project.get('link', ''),
                        contact=project.get('contact', ''),
                        doc_dir=project_dir / 'Doc' if (project_dir / 'Doc').is_dir() else None
                    )
                else:
                    logger.warning(f"No [Project] section in {info_file}")
            return None
        except Exception as e:
            logger.error(f"Error reading {info_file}: {e}")
            return None

    def format_link(self, project_info: ProjectInfo, project_dir: Path) -> str:
        """Format link based on whether it's a URL or file path."""
        if project_info.link.startswith(('http://', 'https://')):
            return f'<a href="{html.escape(project_info.link)}">{html.escape(project_info.link)}</a>'
        else:
            win_path = (project_dir / project_info.link).as_posix()
            return f'<a href="file:///{html.escape(win_path)}">{html.escape(str(win_path))}</a>'

    def format_contact(self, project_info: ProjectInfo) -> str:
        """Format contact information as mailto link."""
        email = project_info.contact
        if not '@gov.yk.ca' in email:
            email = 'service.desk@gov.yk.ca'
        
        subject = f"Map Project: {project_info.title}"
        mailto = f'mailto:{email}?Subject={html.escape(subject)}'
        return f'<a href="{mailto}" target="_top">{html.escape(project_info.contact)}</a>'

    def scan_directories(self):
        """Scan base directory for project folders and collect metadata."""
        self.project_list = [['Title', 'Link (IE only)', 'Contact', 'Document Dir']]
        
        try:
            for project_dir in self.base_dir.iterdir():
                if not project_dir.is_dir():
                    continue
                    
                project_info = self.read_project_info(project_dir)
                if not project_info:
                    continue

                logger.info(f"Processing {project_info.title}")
                
                doc_link = ''
                if project_info.doc_dir:
                    doc_path = str(project_info.doc_dir).replace('/', '\\')
                    doc_link = f'<a href="file:///{html.escape(str(project_info.doc_dir))}">{html.escape(doc_path)}</a>'

                self.project_list.append([
                    html.escape(project_info.title),
                    self.format_link(project_info, project_dir),
                    self.format_contact(project_info),
                    doc_link
                ])
        except Exception as e:
            logger.error(f"Error scanning directories: {e}")
            raise

    def generate_html(self) -> str:
        """Generate HTML output from collected project data."""
        html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Geomatics Unit Map Projects</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 2em; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ padding: 12px; text-align: left; border: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        h1 {{ color: #333; }}
        .note {{ background-color: #fff3cd; padding: 1em; margin: 1em 0; border-radius: 4px; }}
    </style>
</head>
<body>
    <h1>Geomatics Unit Map Projects</h1>
    <div class="note">
        <h2>"setup.bat" links will only work using Internet Explorer.</h2>
        For Firefox or Chrome:<br>
        1. Copy the link<br>
        2. Press "Windows Key" + "R"<br>
        3. Paste link and click "OK"<br>
    </div>
    <table>
        {rows}
    </table>
</body>
</html>'''

        rows = []
        for i, project in enumerate(self.project_list):
            cells = ''.join(f'<{"th" if i==0 else "td"}>{cell}</{"th" if i==0 else "td"}>' 
                          for cell in project)
            rows.append(f'<tr>{cells}</tr>')
        
        return html_template.format(rows='\n'.join(rows))

    def generate(self):
        """Main method to generate and save the HTML index."""
        try:
            self.scan_directories()
            html_content = self.generate_html()
            
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            self.output_file.write_text(html_content, encoding='utf-8')
            logger.info(f"Successfully generated index at {self.output_file}")
            
        except Exception as e:
            logger.error(f"Failed to generate index: {e}")
            raise

def main():
    """Entry point for the script."""
    base_dir = Path(r'\\ENVGEOSERVER\Maps')
    output_file = base_dir / 'Map-Project-Index.html'
    
    try:
        project_lister = MapProjectLister(base_dir, output_file)
        project_lister.generate()
    except Exception as e:
        logger.error(f"Script failed: {e}")
        raise

if __name__ == '__main__':
    main()
