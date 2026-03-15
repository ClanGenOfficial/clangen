"""
JSON compatibility utilities for the application.
"""

try:
    import ujson as json  # Runs on macOS host
except ImportError:
    import json  # Falls back to pure Python on the iOS target
