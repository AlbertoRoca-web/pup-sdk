"""Web interface for Pup SDK.

This module provides a mobile-friendly web interface for Alberto
that's ready to deploy on HuggingFace Spaces.
"""

from .app import create_app, launch_web

__all__ = ["create_app", "launch_web"]

try:
    print("Web interface loaded - Ready to serve Alberto to the world!")
except UnicodeEncodeError:
    print("Web interface loaded - Ready to serve Alberto to the world!")