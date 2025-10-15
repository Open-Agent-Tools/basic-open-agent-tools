#!/usr/bin/env python3
"""Count how many tools have @strands_tool decorator."""

import ast
import sys
from pathlib import Path

def count_decorated_functions(file_path: Path) -> tuple[int, int]:
    """Count total functions and decorated functions in a file."""
    try:
        with open(file_path) as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        
        total = 0
        decorated = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private functions, helper functions, and fallback decorators
                if node.name.startswith('_'):
                    continue
                if node.name == 'strands_tool':  # Skip fallback decorator function
                    continue
                if node.name == 'check_user_confirmation':  # Skip confirmation helper
                    continue
                    
                total += 1
                
                # Check if function has @strands_tool decorator
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'strands_tool':
                        decorated += 1
                        break
                    elif isinstance(decorator, ast.Attribute) and decorator.attr == 'strands_tool':
                        decorated += 1
                        break
        
        return total, decorated
    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return 0, 0

def main():
    """Count decorated tools across the project."""
    src_dir = Path('src/basic_open_agent_tools')
    
    total_functions = 0
    total_decorated = 0
    files_checked = 0
    
    for py_file in sorted(src_dir.rglob('*.py')):
        if py_file.name in ('__init__.py', 'exceptions.py', 'types.py', 'helpers.py'):
            continue
        
        total, decorated = count_decorated_functions(py_file)
        if total > 0:
            files_checked += 1
            total_functions += total
            total_decorated += decorated
            
            if decorated < total:
                print(f"⚠️  {py_file.relative_to(src_dir)}: {decorated}/{total} decorated")
    
    print(f"\n{'='*60}")
    print(f"Files checked: {files_checked}")
    print(f"Total public agent tools: {total_functions}")
    print(f"Decorated with @strands_tool: {total_decorated}")
    print(f"Coverage: {100 * total_decorated / total_functions:.1f}%")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
