"""AST parsing utilities for Python code analysis.

This module provides functions to extract structured information from Python
source files using the Abstract Syntax Tree (AST).
"""

import ast
from typing import Any

from basic_open_agent_tools.exceptions import CodeAnalysisError


def parse_python_ast(file_path: str) -> dict[str, Any]:
    """Parse a Python file and extract complete AST structure.

    Extracts functions, classes, imports, and module-level variables from
    a Python source file using AST parsing. Returns structured data that
    agents can use to understand code organization.

    Args:
        file_path: Absolute path to the Python file to parse

    Returns:
        Dictionary containing:
        - functions: List of function definitions with metadata
        - classes: List of class definitions with metadata
        - imports: Dictionary of import statements by type
        - module_docstring: Module-level docstring if present
        - line_count: Total number of lines in file

    Raises:
        TypeError: If file_path is not a string
        FileNotFoundError: If the file does not exist
        CodeAnalysisError: If file cannot be parsed as valid Python

    Example:
        >>> result = parse_python_ast("/path/to/module.py")
        >>> len(result["functions"])
        5
        >>> result["classes"][0]["name"]
        "MyClass"
    """
    if not isinstance(file_path, str):
        raise TypeError(f"file_path must be a string, got {type(file_path)}")

    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise CodeAnalysisError(f"Error reading file {file_path}: {str(e)}")

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as e:
        raise CodeAnalysisError(
            f"Syntax error in {file_path} at line {e.lineno}: {e.msg}"
        )
    except Exception as e:
        raise CodeAnalysisError(f"Error parsing {file_path}: {str(e)}")

    # Extract module docstring
    module_docstring = ast.get_docstring(tree) or ""

    # Count lines
    line_count = len(source.splitlines())

    # Extract functions
    functions = extract_functions(file_path)

    # Extract classes
    classes = extract_classes(file_path)

    # Extract imports
    imports = extract_imports(file_path)

    return {
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "module_docstring": module_docstring,
        "line_count": line_count,
    }


def extract_functions(file_path: str) -> list[dict[str, Any]]:
    """Extract all function definitions from a Python file.

    Parses a Python file and extracts metadata about all function definitions
    including parameters, return types, decorators, and docstrings.

    Args:
        file_path: Absolute path to the Python file to analyze

    Returns:
        List of dictionaries, each containing:
        - name: Function name
        - params: List of parameter names
        - return_type: Return type annotation as string (or None)
        - docstring: Function docstring (or empty string)
        - decorators: List of decorator names
        - line_start: Starting line number
        - line_end: Ending line number
        - is_async: Whether function is async

    Raises:
        TypeError: If file_path is not a string
        FileNotFoundError: If the file does not exist
        CodeAnalysisError: If file cannot be parsed

    Example:
        >>> functions = extract_functions("/path/to/module.py")
        >>> functions[0]["name"]
        "calculate_total"
        >>> functions[0]["params"]
        ["items", "tax_rate"]
    """
    if not isinstance(file_path, str):
        raise TypeError(f"file_path must be a string, got {type(file_path)}")

    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise CodeAnalysisError(f"Error reading file {file_path}: {str(e)}")

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as e:
        raise CodeAnalysisError(
            f"Syntax error in {file_path} at line {e.lineno}: {e.msg}"
        )
    except Exception as e:
        raise CodeAnalysisError(f"Error parsing {file_path}: {str(e)}")

    functions = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Extract parameters
            params = [arg.arg for arg in node.args.args]

            # Extract return type
            return_type = None
            if node.returns:
                return_type = ast.unparse(node.returns)

            # Extract decorators
            decorators = [ast.unparse(dec) for dec in node.decorator_list]

            # Extract docstring
            docstring = ast.get_docstring(node) or ""

            functions.append(
                {
                    "name": node.name,
                    "params": params,
                    "return_type": return_type,
                    "docstring": docstring,
                    "decorators": decorators,
                    "line_start": node.lineno,
                    "line_end": node.end_lineno or node.lineno,
                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                }
            )

    return functions


def extract_classes(file_path: str) -> list[dict[str, Any]]:
    """Extract all class definitions from a Python file.

    Parses a Python file and extracts metadata about all class definitions
    including methods, attributes, inheritance, and docstrings.

    Args:
        file_path: Absolute path to the Python file to analyze

    Returns:
        List of dictionaries, each containing:
        - name: Class name
        - methods: List of method names
        - bases: List of base class names (inheritance)
        - docstring: Class docstring (or empty string)
        - decorators: List of decorator names
        - line_start: Starting line number
        - line_end: Ending line number

    Raises:
        TypeError: If file_path is not a string
        FileNotFoundError: If the file does not exist
        CodeAnalysisError: If file cannot be parsed

    Example:
        >>> classes = extract_classes("/path/to/module.py")
        >>> classes[0]["name"]
        "DataProcessor"
        >>> classes[0]["methods"]
        ["__init__", "process", "validate"]
    """
    if not isinstance(file_path, str):
        raise TypeError(f"file_path must be a string, got {type(file_path)}")

    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise CodeAnalysisError(f"Error reading file {file_path}: {str(e)}")

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as e:
        raise CodeAnalysisError(
            f"Syntax error in {file_path} at line {e.lineno}: {e.msg}"
        )
    except Exception as e:
        raise CodeAnalysisError(f"Error parsing {file_path}: {str(e)}")

    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Extract methods
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append(item.name)

            # Extract base classes
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(ast.unparse(base))

            # Extract decorators
            decorators = [ast.unparse(dec) for dec in node.decorator_list]

            # Extract docstring
            docstring = ast.get_docstring(node) or ""

            classes.append(
                {
                    "name": node.name,
                    "methods": methods,
                    "bases": bases,
                    "docstring": docstring,
                    "decorators": decorators,
                    "line_start": node.lineno,
                    "line_end": node.end_lineno or node.lineno,
                }
            )

    return classes


def extract_imports(file_path: str) -> dict[str, list[str]]:
    """Extract all import statements from a Python file.

    Parses a Python file and categorizes all import statements into
    standard library, third-party, and local imports.

    Args:
        file_path: Absolute path to the Python file to analyze

    Returns:
        Dictionary containing:
        - stdlib: List of standard library imports
        - third_party: List of third-party imports
        - local: List of local/relative imports
        - all: List of all imports (combined)

    Raises:
        TypeError: If file_path is not a string
        FileNotFoundError: If the file does not exist
        CodeAnalysisError: If file cannot be parsed

    Example:
        >>> imports = extract_imports("/path/to/module.py")
        >>> imports["stdlib"]
        ["os", "sys", "json"]
        >>> imports["local"]
        ["my_module", "utils"]
    """
    if not isinstance(file_path, str):
        raise TypeError(f"file_path must be a string, got {type(file_path)}")

    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise CodeAnalysisError(f"Error reading file {file_path}: {str(e)}")

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as e:
        raise CodeAnalysisError(
            f"Syntax error in {file_path} at line {e.lineno}: {e.msg}"
        )
    except Exception as e:
        raise CodeAnalysisError(f"Error parsing {file_path}: {str(e)}")

    # Standard library modules (Python 3.9+)
    stdlib_modules = {
        "abc",
        "aifc",
        "argparse",
        "array",
        "ast",
        "asynchat",
        "asyncio",
        "asyncore",
        "atexit",
        "audioop",
        "base64",
        "bdb",
        "binascii",
        "binhex",
        "bisect",
        "builtins",
        "bz2",
        "calendar",
        "cgi",
        "cgitb",
        "chunk",
        "cmath",
        "cmd",
        "code",
        "codecs",
        "codeop",
        "collections",
        "colorsys",
        "compileall",
        "concurrent",
        "configparser",
        "contextlib",
        "contextvars",
        "copy",
        "copyreg",
        "crypt",
        "csv",
        "ctypes",
        "curses",
        "dataclasses",
        "datetime",
        "dbm",
        "decimal",
        "difflib",
        "dis",
        "distutils",
        "doctest",
        "email",
        "encodings",
        "enum",
        "errno",
        "faulthandler",
        "fcntl",
        "filecmp",
        "fileinput",
        "fnmatch",
        "formatter",
        "fractions",
        "ftplib",
        "functools",
        "gc",
        "getopt",
        "getpass",
        "gettext",
        "glob",
        "graphlib",
        "grp",
        "gzip",
        "hashlib",
        "heapq",
        "hmac",
        "html",
        "http",
        "imaplib",
        "imghdr",
        "imp",
        "importlib",
        "inspect",
        "io",
        "ipaddress",
        "itertools",
        "json",
        "keyword",
        "lib2to3",
        "linecache",
        "locale",
        "logging",
        "lzma",
        "mailbox",
        "mailcap",
        "marshal",
        "math",
        "mimetypes",
        "mmap",
        "modulefinder",
        "multiprocessing",
        "netrc",
        "nis",
        "nntplib",
        "numbers",
        "operator",
        "optparse",
        "os",
        "ossaudiodev",
        "parser",
        "pathlib",
        "pdb",
        "pickle",
        "pickletools",
        "pipes",
        "pkgutil",
        "platform",
        "plistlib",
        "poplib",
        "posix",
        "posixpath",
        "pprint",
        "profile",
        "pstats",
        "pty",
        "pwd",
        "py_compile",
        "pyclbr",
        "pydoc",
        "queue",
        "quopri",
        "random",
        "re",
        "readline",
        "reprlib",
        "resource",
        "rlcompleter",
        "runpy",
        "sched",
        "secrets",
        "select",
        "selectors",
        "shelve",
        "shlex",
        "shutil",
        "signal",
        "site",
        "smtpd",
        "smtplib",
        "sndhdr",
        "socket",
        "socketserver",
        "spwd",
        "sqlite3",
        "ssl",
        "stat",
        "statistics",
        "string",
        "stringprep",
        "struct",
        "subprocess",
        "sunau",
        "symbol",
        "symtable",
        "sys",
        "sysconfig",
        "syslog",
        "tabnanny",
        "tarfile",
        "telnetlib",
        "tempfile",
        "termios",
        "test",
        "textwrap",
        "threading",
        "time",
        "timeit",
        "tkinter",
        "token",
        "tokenize",
        "trace",
        "traceback",
        "tracemalloc",
        "tty",
        "turtle",
        "turtledemo",
        "types",
        "typing",
        "unicodedata",
        "unittest",
        "urllib",
        "uu",
        "uuid",
        "venv",
        "warnings",
        "wave",
        "weakref",
        "webbrowser",
        "winreg",
        "winsound",
        "wsgiref",
        "xdrlib",
        "xml",
        "xmlrpc",
        "zipapp",
        "zipfile",
        "zipimport",
        "zlib",
        "zoneinfo",
    }

    all_imports = []
    stdlib_imports = []
    third_party_imports = []
    local_imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.split(".")[0]
                all_imports.append(alias.name)

                if module_name in stdlib_modules:
                    stdlib_imports.append(alias.name)
                else:
                    third_party_imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:  # Relative import
                module_name = node.module or ""
                all_imports.append(f".{module_name}" if module_name else ".")
                local_imports.append(f".{module_name}" if module_name else ".")
            elif node.module:
                module_name = node.module.split(".")[0]
                all_imports.append(node.module)

                if module_name in stdlib_modules:
                    stdlib_imports.append(node.module)
                else:
                    third_party_imports.append(node.module)

    return {
        "stdlib": sorted(set(stdlib_imports)),
        "third_party": sorted(set(third_party_imports)),
        "local": sorted(set(local_imports)),
        "all": sorted(set(all_imports)),
    }
