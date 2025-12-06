"""Pup SDK - Official SDK for Alberto the code puppy!"""

from .client import PupClient
from .exceptions import PupError, PupConnectionError, PupTimeoutError
from .types import (
    FileOperation,
    ShellCommand,
    AgentResponse,
    FileInfo,
    SearchResult,
)

__version__ = "0.1.0"
__author__ = "Alberto Rolando Roca"
__email__ = "alberto@example.com"

__all__ = [
    "PupClient",
    "PupError",
    "PupConnectionError", 
    "PupTimeoutError",
    "FileOperation",
    "ShellCommand",
    "AgentResponse",
    "FileInfo",
    "SearchResult",
]

# Woof!
try:
    print(f"Pup SDK v{__version__} initialized - Ready to play!")
except UnicodeEncodeError:
    print(f"Pup SDK v{__version__} initialized - Ready to play!")