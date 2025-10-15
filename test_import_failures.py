"""Test for optional dependency import failures that might cause silent tool loss."""

import sys
import importlib


def test_module_imports():
    """Test if all modules can be imported without optional dependency errors."""

    modules_to_test = [
        'basic_open_agent_tools.archive',
        'basic_open_agent_tools.color',
        'basic_open_agent_tools.crypto',
        'basic_open_agent_tools.data',
        'basic_open_agent_tools.datetime',
        'basic_open_agent_tools.diagrams',
        'basic_open_agent_tools.excel',
        'basic_open_agent_tools.file_system',
        'basic_open_agent_tools.html',
        'basic_open_agent_tools.image',
        'basic_open_agent_tools.logging',
        'basic_open_agent_tools.markdown',
        'basic_open_agent_tools.network',
        'basic_open_agent_tools.pdf',
        'basic_open_agent_tools.powerpoint',
        'basic_open_agent_tools.system',
        'basic_open_agent_tools.text',
        'basic_open_agent_tools.todo',
        'basic_open_agent_tools.utilities',
        'basic_open_agent_tools.word',
        'basic_open_agent_tools.xml',
    ]

    print("=== Testing Module Imports ===\n")

    successful = []
    failed = []

    for module_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            # Check if module has __all__
            if hasattr(module, '__all__'):
                tool_count = len(module.__all__)
                successful.append((module_name, tool_count))
                print(f"✓ {module_name}: {tool_count} tools")
            else:
                successful.append((module_name, 0))
                print(f"⚠ {module_name}: No __all__ attribute")
        except Exception as e:
            failed.append((module_name, str(e)))
            print(f"✗ {module_name}: {e}")

    print(f"\n=== Summary ===")
    print(f"Successful imports: {len(successful)}")
    print(f"Failed imports: {len(failed)}")

    total_tools = sum(count for _, count in successful)
    print(f"Total tools from successful imports: {total_tools}")

    if failed:
        print(f"\n=== Failed Modules ===")
        for module, error in failed:
            print(f"{module}: {error}")

    return len(successful), len(failed), total_tools


def test_optional_dependencies():
    """Test which optional dependencies are available."""

    print("\n\n=== Testing Optional Dependencies ===\n")

    dependencies = [
        ('openpyxl', 'Excel tools'),
        ('python-docx', 'Word tools'),
        ('pypdf', 'PDF tools'),
        ('Pillow', 'Image tools'),
        ('diagrams', 'Diagram tools'),
        ('python-pptx', 'PowerPoint tools'),
    ]

    available = []
    missing = []

    for package, description in dependencies:
        try:
            importlib.import_module(package.replace('-', '_'))
            available.append((package, description))
            print(f"✓ {package:20s} - {description}")
        except ImportError:
            missing.append((package, description))
            print(f"✗ {package:20s} - {description} (MISSING)")

    print(f"\n=== Dependency Summary ===")
    print(f"Available: {len(available)}/{len(dependencies)}")
    print(f"Missing: {len(missing)}/{len(dependencies)}")

    if missing:
        print(f"\n⚠️  Missing optional dependencies may cause tool loss")
        print(f"   Missing packages: {', '.join(p for p, _ in missing)}")

    return len(available), len(missing)


if __name__ == "__main__":
    success, failed, total_tools = test_module_imports()
    available, missing = test_optional_dependencies()

    print(f"\n\n=== FINAL SUMMARY ===")
    print(f"Modules successfully loaded: {success}/21")
    print(f"Modules failed to load: {failed}/21")
    print(f"Tools available: {total_tools}")
    print(f"Optional dependencies available: {available}/6")
    print(f"Optional dependencies missing: {missing}/6")

    if missing > 0:
        estimated_lost_tools = missing * 15  # Rough estimate
        print(f"\nEstimated tools lost due to missing deps: ~{estimated_lost_tools}")
        print(f"Estimated visible tools: ~{total_tools - estimated_lost_tools}")
