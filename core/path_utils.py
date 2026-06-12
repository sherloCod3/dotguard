from __future__ import annotations

from pathlib import Path


def source_relpath(source: Path) -> Path:
    """
    Convert absolute paths into a stable relative path under backup root.

    Examples:
      /home/user/.bashrc -> home/user/.bashrc
      /usr/share/themes   -> usr/share/themes
    """
    parts = list(source.parts)
    if parts and parts[0] == "/":
        parts = parts[1:]
    return Path(*parts)
