#!/usr/bin/env python3
"""Find undecorated public functions."""

import ast
from pathlib import Path

def find_undecorated(file_path: Path) -> list[str]:
    """Find public functions without @strands_tool decorator."""
    try:
        with open(file_path) as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        
        undecorated = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private functions
                if node.name.startswith('_'):
                    continue
                
                # Check if function has @strands_tool decorator
                has_decorator = False
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'strands_tool':
                        has_decorator = True
                        break
                    elif isinstance(decorator, ast.Attribute) and decorator.attr == 'strands_tool':
                        has_decorator = True
                        break
                
                if not has_decorator:
                    undecorated.append(node.name)
        
        return undecorated
    except Exception as e:
        return []

def main():
    """Find all undecorated functions."""
    src_dir = Path('src/basic_open_agent_tools')
    
    for py_file in sorted(src_dir.rglob('*.py')):
        if py_file.name in ('__init__.py', 'exceptions.py', 'types.py', 'helpers.py'):
            continue
        
        undecorated = find_undecorated(py_file)
        if undecorated:
            print(f"\n{py_file.relative_to(src_dir)}:")
            for func in undecorated:
                print(f"  - {func}")

if __name__ == '__main__':
    main()
