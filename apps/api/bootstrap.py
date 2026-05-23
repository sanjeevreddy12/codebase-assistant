"""
Configure sys.path for monorepo imports.

Run scripts from ``apps/api`` (or import ``setup_paths`` first). After setup:

- ``from app.<module>`` — API package under ``apps/api/app``
- ``from packages.<module>`` — shared packages at repo root
"""

import sys
from pathlib import Path

_API_ROOT = Path(__file__).resolve().parent
_REPO_ROOT = _API_ROOT.parent.parent


def setup_paths() -> None:
    """Add ``apps/api`` and repo root to ``sys.path`` if not already present."""
    for path in (_API_ROOT, _REPO_ROOT):
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)
