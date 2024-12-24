"""Generate an HTML index of environment applications with their metadata.

This script scans a directory for application folders containing metadata files
and generates a clickable HTML index with links to setup files and documentation.
"""
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import logging
from email.utils import formataddr
import html

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AppInfo:
    """Store application information parsed from metadata file."""
    title: str
    link: str
    contact: str
    doc_dir: Optional[Path] = None

class EnvAppLister:
    """Generate HTML index of environment applications."""
    
    def __init__(self, base_dir: Path, output_file: Path):
        """Initialize with base directory and output file path.
        
        Args:
            base_dir: Root directory containing application folders
            output_file: Path where HTML output will be written
        """
        self.base_dir = Path(base_dir)
        self.output_file = Path(output_file)
        self.app_list = []

    def read_app_info(self, app_dir: Path) -> Optional[AppInfo]:
        """Read application metadata from appinfo.txt.
        
        Args:
            app_dir: Directory containing the appinfo.txt file
            
        Returns:
            AppInfo object if successful, None if file not found or invalid
        """
        info_file = app_dir / 'appinfo.txt'
        try:
            with info_file.open('r', encoding='utf-8') as f:
                lines = f.read().splitlines()
                if len(lines) < 3:
                    logger.warning(f"Invalid appinfo.txt in {app_dir}: insufficient lines")
                    return None
                title, link, contact = lines[:3]
                
                # Check for documentation directory
                doc_dir = app_dir / 'Doc'
                return AppInfo(
                    title=title,
                    link=link,
                    contact=contact,
                    doc_dir=doc_dir if doc_dir.is_dir() else None
                )
        except Exception as e:
            logger.error(f"Error reading {info_file}: {e}")
            return None

    def format_link(self, app_info: AppInfo, app_dir: Path) -> str:
        """Format link based on whether it's a URL or file path."""
        if app_info.link.startswith(('http://', 'https://')):
            return f'<a href="{html.escape(app_info.link)}">{html.escape(app_info.link)}</a>'
        else:
            win_path = (app_dir / app_info.link).as_posix()
            return f'<a href="file:///{html.escape(win_path)}">{html.escape(str(win_path))}</a>'

    def format_contact(self, app_info: AppInfo) -> str:
        """Format contact information as mailto link."""
        email = app_info.contact
        if not '@gov.yk.ca' in email:
            email = 'service.desk@gov.yk.ca'
        
        subject = f"Environment Application: {app_info.title}"
        mailto = f'mailto:{email}?Subject={html.escape(subject)}'
        return f'<a href="{mailto}" target="_top">{html.escape(app_info.contact)}</a>'

    def scan_directories(self):
        """Scan base directory for application folders and collect metadata."""
        self.app_list = [['Title', 'Link (IE only)', 'Contact', 'Document Dir']]
        
        try:
            for app_dir in self.base_dir.iterdir():
                if not app_dir.is_dir():
                    continue
                    
                app_info = self.read_app_info(app_dir)
                if not app_info:
                    continue

                logger.info(f"Processing {app_info.title}")
                
                doc_link = ''
                if app_info.doc_dir:
                    doc_path = str(app_info.doc_dir).replace('/', '\\')
                    doc_link = f'<a href="file:///{html.escape(str(app_info.doc_dir))}">{html.escape(doc_path)}</a>'

                self.app_list.append([
                    html.escape(app_info.title),
                    self.format_link(app_info, app_dir),
                    self.format_contact(app_info),
                    doc_link
                ])
        except Exception as e:
            logger.error(f"Error scanning directories: {e}")
            raise

    def generate_html(self) -> str:
        """Generate HTML output from collected application data."""
        html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Environment System List</title>
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
    <h1>Environment System List</h1>
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
        for i, app in enumerate(self.app_list):
            cells = ''.join(f'<{"th" if i==0 else "td"}>{cell}</{"th" if i==0 else "td"}>' 
                          for cell in app)
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
    base_dir = Path('//carver/infosys')
    output_file = base_dir / 'envapps.html'
    
    try:
        app_lister = EnvAppLister(base_dir, output_file)
        app_lister.generate()
    except Exception as e:
        logger.error(f"Script failed: {e}")
        raise

if __name__ == '__main__':
    main()
