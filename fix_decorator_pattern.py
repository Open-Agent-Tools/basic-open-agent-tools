#!/usr/bin/env python3
"""Fix decorator pattern in all files with incorrect @strands_tool usage."""

import os
import re
from pathlib import Path

def fix_file(file_path: Path) -> bool:
    """Fix decorator pattern in a single file.
    
    Returns True if file was modified, False otherwise.
    """
    content = file_path.read_text()
    original_content = content
    
    # Check if file needs fixing - look for the problematic pattern
    if '@strands_tool\n    def strands_tool(func: Callable' in content:
        # Remove the @strands_tool decorator before the fallback function
        content = content.replace(
            '@strands_tool\n    def strands_tool(func: Callable',
            'def strands_tool(func: Callable'
        )
        print(f"Fixed decorator pattern in: {file_path}")
        
    # Check if typing imports are missing
    has_callable_import = 'from typing import' in content and 'Callable' in content.split('from typing import')[1].split('\n')[0] if 'from typing import' in content else False
    has_any_import = 'from typing import' in content and 'Any' in content.split('from typing import')[1].split('\n')[0] if 'from typing import' in content else False
    
    needs_typing = 'Callable' in content or 'Any' in content
    
    if needs_typing and not (has_callable_import and has_any_import):
        # Find the position to insert typing imports (after module docstring)
        lines = content.split('\n')
        insert_pos = 0
        
        # Skip module docstring
        in_docstring = False
        for i, line in enumerate(lines):
            if i == 0 and line.startswith('"""'):
                in_docstring = True
                continue
            if in_docstring:
                if '"""' in line:
                    insert_pos = i + 1
                    break
                continue
            if not line.strip() or line.strip().startswith('#'):
                continue
            if line.startswith('import ') or line.startswith('from '):
                insert_pos = i
                break
        
        # Add typing imports if not present
        if insert_pos > 0:
            # Check what's already imported
            existing_imports = []
            for line in lines:
                if line.startswith('from typing import'):
                    existing_imports = [x.strip() for x in line.replace('from typing import', '').split(',')]
                    break
            
            if 'Callable' not in existing_imports or 'Any' not in existing_imports:
                # Find existing typing import line and update it
                for i, line in enumerate(lines):
                    if line.startswith('from typing import'):
                        imports = [x.strip() for x in line.replace('from typing import', '').split(',')]
                        if 'Callable' not in imports:
                            imports.append('Callable')
                        if 'Any' not in imports:
                            imports.append('Any')
                        lines[i] = f"from typing import {', '.join(sorted(imports))}"
                        print(f"Updated typing imports in: {file_path}")
                        content = '\n'.join(lines)
                        break
                else:
                    # No existing typing import, add new one
                    lines.insert(insert_pos, 'from typing import Any, Callable')
                    lines.insert(insert_pos + 1, '')
                    print(f"Added typing imports to: {file_path}")
                    content = '\n'.join(lines)
    
    # Only write if content changed
    if content != original_content:
        file_path.write_text(content)
        return True
    
    return False

def main():
    """Fix decorator pattern in all Python files."""
    src_dir = Path('src/basic_open_agent_tools')
    
    fixed_files = []
    for py_file in src_dir.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue
        
        if fix_file(py_file):
            fixed_files.append(py_file)
    
    print(f"\n{'='*60}")
    print(f"Fixed {len(fixed_files)} files")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
