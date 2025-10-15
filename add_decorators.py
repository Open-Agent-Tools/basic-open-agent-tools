"""Script to add @strands_tool decorator to all public functions."""

import ast
import os
from pathlib import Path


def add_strands_decorator(file_path: Path) -> bool:
    """Add @strands_tool decorator to functions that don't have it."""

    with open(file_path, 'r') as f:
        lines = f.readlines()

    modified = False
    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this is a function definition
        if line.strip().startswith('def ') and not line.strip().startswith('def _'):
            # Check if previous line has decorator
            prev_line_idx = i - 1
            while prev_line_idx >= 0 and lines[prev_line_idx].strip() == '':
                prev_line_idx -= 1

            if prev_line_idx >= 0:
                prev_line = lines[prev_line_idx].strip()

                # Skip if already has @strands_tool or other decorators
                if not prev_line.startswith('@'):
                    # Get indentation
                    indent = len(line) - len(line.lstrip())
                    decorator = ' ' * indent + '@strands_tool\n'
                    lines.insert(i, decorator)
                    modified = True
                    i += 1  # Skip the line we just added

        i += 1

    if modified:
        with open(file_path, 'w') as f:
            f.writelines(lines)
        return True
    return False


def process_all_files():
    """Process all Python files in the project."""
    src_dir = Path('src/basic_open_agent_tools')

    # Files that need decorators based on our analysis
    target_files = [
        'markdown/generation.py',
        'markdown/parsing.py',
        'diagrams/plantuml.py',
        'diagrams/mermaid.py',
        'excel/writing.py',
        'excel/reading.py',
        'excel/formatting.py',
        'pdf/manipulation.py',
        'pdf/parsing.py',
        'pdf/creation.py',
        'html/generation.py',
        'html/parsing.py',
        'image/manipulation.py',
        'image/reading.py',
        'xml/transformation.py',
        'xml/parsing.py',
        'xml/authoring.py',
        'xml/validation.py',
        'word/reading.py',
        'word/authoring.py',
        'word/business.py',
        'powerpoint/reading.py',
        'powerpoint/authoring.py',
        'color/manipulation.py',
        'color/conversion.py',
        'data/config_processing.py',
        'data/csv_tools.py',
        'data/json_tools.py',
        'data/validation.py',
        'datetime/generation.py',
        'datetime/formatting.py',
        'datetime/parsing.py',
        'datetime/ranges.py',
        'datetime/timing.py',
        'datetime/timezone.py',
        'file_system/operations.py',
        'file_system/tree.py',
        'file_system/info.py',
        'todo/operations.py',
        'text/processing.py',
        'text/structured.py',
        'archive/formats.py',
        'crypto/encoding.py',
        'network/http_client.py',
        'system/runtime.py',
        'system/info.py',
        'system/processes.py',
        'system/environment.py',
        'logging/structured.py',
        'utilities/debugging.py',
    ]

    modified_count = 0
    for rel_path in target_files:
        file_path = src_dir / rel_path
        if file_path.exists():
            if add_strands_decorator(file_path):
                print(f'✓ Added decorators to {rel_path}')
                modified_count += 1
        else:
            print(f'✗ File not found: {rel_path}')

    print(f'\nModified {modified_count} files')


if __name__ == '__main__':
    process_all_files()
