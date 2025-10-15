"""Script to add @strands_tool decorator and imports to all tool functions."""

import re
from pathlib import Path


STRANDS_IMPORT_BLOCK = '''try:
    from strands import tool as strands_tool
except ImportError:
    # Create a no-op decorator if strands is not installed
    def strands_tool(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[no-redef]
        return func


'''


def add_imports_and_decorators(file_path: Path) -> bool:
    """Add strands import and decorators to a file."""

    with open(file_path, 'r') as f:
        content = f.read()

    # Check if file already has strands import
    has_strands_import = 'from strands import' in content or 'strands_tool' in content

    modified = False

    # Add strands import if missing
    if not has_strands_import:
        # Find where to insert (after docstring and imports)
        lines = content.split('\n')
        insert_idx = 0

        # Skip module docstring
        in_docstring = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if i == 0 and (stripped.startswith('"""') or stripped.startswith("'''")):
                in_docstring = True
                if stripped.count('"""') == 2 or stripped.count("'''") == 2:
                    insert_idx = i + 1
                    break
            elif in_docstring and ('"""' in stripped or "'''" in stripped):
                insert_idx = i + 1
                break

        # Find last import statement after docstring
        for i in range(insert_idx, len(lines)):
            if lines[i].strip().startswith(('import ', 'from ')):
                insert_idx = i + 1
            elif lines[i].strip() and not lines[i].strip().startswith('#'):
                break

        # Insert strands import block
        lines.insert(insert_idx, STRANDS_IMPORT_BLOCK)
        content = '\n'.join(lines)
        modified = True

    # Add @strands_tool decorator to functions
    lines = content.split('\n')
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if next line is a function definition
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            if next_line.strip().startswith('def ') and not next_line.strip().startswith('def _'):
                # Check if current line already has a decorator
                if not line.strip().startswith('@'):
                    # Add decorator
                    indent = len(next_line) - len(next_line.lstrip())
                    result_lines.append(line)
                    result_lines.append(' ' * indent + '@strands_tool')
                    modified = True
                    i += 1
                    continue

        result_lines.append(line)
        i += 1

    if modified:
        with open(file_path, 'w') as f:
            f.write('\n'.join(result_lines))
        return True

    return False


def main():
    """Process all Python files that need decorators."""
    src_dir = Path('src/basic_open_agent_tools')

    # Get all Python files (excluding __init__.py and private files)
    files_to_process = []
    for py_file in src_dir.rglob('*.py'):
        if py_file.name == '__init__.py' or py_file.name.startswith('_'):
            continue
        if py_file.parent.name in ['__pycache__']:
            continue

        # Skip certain utility files
        if py_file.name in ['types.py', 'exceptions.py', 'confirmation.py', 'helpers.py']:
            continue

        files_to_process.append(py_file)

    print(f'Processing {len(files_to_process)} files...\n')

    modified_count = 0
    for file_path in sorted(files_to_process):
        rel_path = file_path.relative_to('src/basic_open_agent_tools')
        if add_imports_and_decorators(file_path):
            print(f'✓ {rel_path}')
            modified_count += 1

    print(f'\n✅ Modified {modified_count} files')


if __name__ == '__main__':
    main()
