#!/usr/bin/env -S uv run --script
"""
Generate sample zInfo projects with metadata for testing purposes.

This script creates a specified number of sample project directories,
each containing a zinfo.txt metadata file and realistic subdirectories/files.
"""

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openai>=1.0.0",
# ]
# ///

import argparse
import hashlib
import json
import logging
import os
import random
import string
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import uuid

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Realistic project structure templates
PROJECT_TYPES = [
    "web-app", "library", "cli-tool", "data-analysis", "game", "api", "mobile-app"
]

SUBDIR_TEMPLATES = [
    ["src", "tests", "docs", "config"],
    ["lib", "examples", "build", "assets"],
    ["app", "components", "utils", "public"],
    ["notebooks", "data", "models", "scripts"],
    ["core", "ui", "resources", "levels"],
    ["routes", "models", "middleware", "controllers"],
    ["ios", "android", "shared", "fastlane"]
]

FILE_EXTENSIONS = [".py", ".js", ".ts", ".md", ".txt", ".json", ".yml", ".html", ".css"]

DETERMINISTIC_TEMPLATES = {
    "titles": [
        "Web Dashboard", "Data Processor", "Task Manager", "File Organizer",
        "Code Generator", "API Gateway", "User Interface", "Database Tool"
    ],
    "descriptions": [
        "A comprehensive solution for managing web interfaces",
        "Efficient data processing and analysis toolkit",
        "Streamlined task management application",
        "Organize and manage files with ease",
        "Generate code snippets and templates",
        "Gateway for API interactions and routing",
        "Modern user interface components",
        "Database management and querying tool"
    ],
    "authors": ["Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson"],
    "licenses": ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause"],
    "tags": ["python", "web", "data", "api", "cli", "ui", "automation", "tool"]
}

def generate_deterministic_metadata(sample_index: int) -> dict:
    """Generate metadata using deterministic templates."""
    random.seed(sample_index)  # Ensure reproducibility

    title = random.choice(DETERMINISTIC_TEMPLATES["titles"])
    description = random.choice(DETERMINISTIC_TEMPLATES["descriptions"])
    author = random.choice(DETERMINISTIC_TEMPLATES["authors"])
    license_name = random.choice(DETERMINISTIC_TEMPLATES["licenses"])
    tags = random.sample(DETERMINISTIC_TEMPLATES["tags"], k=random.randint(2, 4))

    return {
        "title": title,
        "description": description,
        "author": author,
        "license": license_name,
        "tags": tags
    }

def generate_llm_metadata(llm_model: str, creativity: float, sample_index: int) -> dict:
    """Generate metadata using OpenAI LLM."""
    if not OPENAI_AVAILABLE:
        raise ImportError("OpenAI library not available. Install with: uv add openai")

    prompt = f"""
Generate metadata for a sample software project. Return only valid JSON with these fields:
- title: A creative project title (string)
- description: A brief description of what the project does (string)
- author: A realistic author name (string)
- license: One of MIT, Apache-2.0, GPL-3.0, or BSD-3-Clause (string)
- tags: Array of 2-4 relevant tags like ["python", "web", "api"] (array of strings)

Make it unique and realistic. Project type: {random.choice(PROJECT_TYPES)}
"""

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=creativity,
            max_tokens=200
        )

        content = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        metadata = json.loads(content)
        return metadata

    except Exception as e:
        logger.warning(f"LLM generation failed: {e}. Falling back to deterministic.")
        return generate_deterministic_metadata(sample_index)

def create_project_structure(project_path: Path, depth: int) -> list[Path]:
    """Create realistic project directory structure and return list of created files."""
    created_files = []

    # Create root directory
    project_path.mkdir(parents=True, exist_ok=True)

    # Choose project type and subdirs
    project_type = random.choice(PROJECT_TYPES)
    subdirs = random.choice(SUBDIR_TEMPLATES)

    # Create subdirectories with random depth
    dirs_to_create = [project_path]
    current_depth = 0

    while current_depth < depth and dirs_to_create:
        next_dirs = []
        for parent_dir in dirs_to_create:
            # Create 1-3 subdirs per parent
            num_subdirs = random.randint(1, 3)
            for i in range(num_subdirs):
                if current_depth < depth:
                    subdir_name = random.choice(subdirs) + f"_{i+1}" if random.random() > 0.5 else random.choice(subdirs)
                    # Ensure no collision
                    counter = 1
                    original_name = subdir_name
                    while (parent_dir / subdir_name).exists():
                        subdir_name = f"{original_name}_{counter}"
                        counter += 1

                    subdir_path = parent_dir / subdir_name
                    subdir_path.mkdir(exist_ok=True)
                    next_dirs.append(subdir_path)

        dirs_to_create = next_dirs
        current_depth += 1

    # Create files in directories
    all_dirs = [project_path] + [d for d in project_path.rglob('*') if d.is_dir()]

    for dir_path in all_dirs:
        # Create 1-5 files per directory
        num_files = random.randint(1, 5)
        for i in range(num_files):
            file_ext = random.choice(FILE_EXTENSIONS)
            file_name = f"file_{i+1}{file_ext}"

            # Ensure no collision
            counter = 1
            original_name = file_name
            while (dir_path / file_name).exists():
                file_name = f"file_{i+1}_{counter}{file_ext}"
                counter += 1

            file_path = dir_path / file_name
            # Create dummy content
            content = f"# Dummy content for {file_path.name}\n" + "\n".join(
                f"Line {j}: {''.join(random.choices(string.ascii_letters + string.digits, k=50))}"
                for j in range(random.randint(5, 20))
            )
            file_path.write_text(content)
            created_files.append(file_path)

    return created_files

def calculate_checksum(file_path: Path) -> str:
    """Calculate SHA-256 checksum of a file."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def generate_zinfo_metadata(project_path: Path, created_files: list[Path],
                          metadata: dict, sample_index: int) -> str:
    """Generate zinfo.txt content in JSON format."""
    # Choose a representative file for checksum (prefer source files)
    representative_file = None
    for file_path in created_files:
        if file_path.suffix in ['.py', '.js', '.ts', '.java', '.cpp']:
            representative_file = file_path
            break
    if not representative_file:
        representative_file = random.choice(created_files)

    checksum = calculate_checksum(representative_file)
    size_bytes = sum(f.stat().st_size for f in created_files)

    # Get relative paths
    files = [str(f.relative_to(project_path)) for f in created_files]

    zinfo_data = {
        "id": str(uuid.uuid4()),
        "zinfo_version": "1.0",
        "title": metadata["title"],
        "description": metadata["description"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "checksum": checksum,
        "size_bytes": size_bytes,
        "files": files,
        "tags": metadata["tags"],
        "author": metadata["author"],
        "license": metadata["license"],
        "metadata_generated_by": "generate_zinfo_samples.py"
    }

    return json.dumps(zinfo_data, indent=2)

def main():
    parser = argparse.ArgumentParser(
        description="Generate sample zInfo projects with metadata for testing."
    )
    parser.add_argument(
        "--number-samples", "-n",
        type=int,
        required=True,
        help="Number of sample projects to generate"
    )
    parser.add_argument(
        "--destination-path", "-d",
        type=str,
        required=True,
        help="Destination directory for generated samples"
    )
    parser.add_argument(
        "--min-dir-depth",
        type=int,
        default=1,
        help="Minimum directory depth (default: 1)"
    )
    parser.add_argument(
        "--max-dir-depth",
        type=int,
        default=3,
        help="Maximum directory depth (default: 3)"
    )
    parser.add_argument(
        "--llm-model",
        type=str,
        default=None,
        help="OpenAI model to use for metadata generation (e.g., gpt-4)"
    )
    parser.add_argument(
        "--creativity",
        type=float,
        default=0.7,
        help="Creativity level for LLM (temperature, 0.0-1.0, default: 0.7)"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.number_samples <= 0:
        logger.error("Number of samples must be positive")
        return 1

    dest_path = Path(args.destination_path)
    if dest_path.exists() and not dest_path.is_dir():
        logger.error("Destination path exists and is not a directory")
        return 1

    if args.min_dir_depth < 0 or args.max_dir_depth < args.min_dir_depth:
        logger.error("Invalid directory depth range")
        return 1

    if args.creativity < 0.0 or args.creativity > 1.0:
        logger.error("Creativity must be between 0.0 and 1.0")
        return 1

    # Create destination directory
    dest_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Generating {args.number_samples} samples in {dest_path}")

    for i in range(args.number_samples):
        sample_name = f"sample_project_{i+1:03d}"
        project_path = dest_path / sample_name

        # Skip if already exists
        if project_path.exists():
            logger.warning(f"Project {sample_name} already exists, skipping")
            continue

        logger.info(f"Creating sample {i+1}/{args.number_samples}: {sample_name}")

        # Generate random depth
        depth = random.randint(args.min_dir_depth, args.max_dir_depth)

        # Create project structure
        created_files = create_project_structure(project_path, depth)

        # Generate metadata
        if args.llm_model:
            metadata = generate_llm_metadata(args.llm_model, args.creativity, i)
        else:
            metadata = generate_deterministic_metadata(i)

        # Create zinfo.txt
        zinfo_content = generate_zinfo_metadata(project_path, created_files, metadata, i)
        zinfo_path = project_path / "zinfo.txt"
        zinfo_path.write_text(zinfo_content)

        logger.info(f"Created {len(created_files)} files, zinfo.txt written")

    logger.info("Sample generation completed successfully")
    return 0

if __name__ == "__main__":
    exit(main())

# Example usage:
# python generate_zinfo_samples.py --number-samples 5 --destination-path ./samples
# uv run generate_zinfo_samples.py --number-samples 5 --destination-path ./samples --llm-model gpt-4 --creativity 0.8
