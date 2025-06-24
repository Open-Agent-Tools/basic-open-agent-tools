"""Basic Open Agent Tools.

An open foundational toolkit providing essential components for building AI agents 
with minimal dependencies for local (non-HTTP/API) actions.
"""

__version__ = "0.1.0"

# Modular structure
from . import file_system

# Future modules (placeholder imports for when modules are implemented)
# from . import text
# from . import system
# from . import network
# from . import data
# from . import crypto
# from . import utilities

# Common infrastructure
from . import exceptions
from . import types

__all__ = [
    # Modular structure
    "file_system",
    
    # Future modules (uncomment when implemented)
    # "text", 
    # "system",
    # "network",
    # "data",
    # "crypto",
    # "utilities",
    
    # Common infrastructure
    "exceptions",
    "types",
]