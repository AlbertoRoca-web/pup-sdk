"""Web interface for Pup SDK.

This module provides a mobile-friendly web interface for Alberto
that's ready to deploy on HuggingFace Spaces.
"""

from .app import create_app, launch_web
from .static import serve_static

__all__ = ["create_app", "launch_web", "serve_static"]

print("\ud83d\dd35 Web interface loaded - Ready to serve Alberto to the world!")