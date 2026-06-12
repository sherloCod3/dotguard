from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


ItemType = Literal["file", "dir", "unknown"]


@dataclass(frozen=True, slots=True)
class FileItem:
    """
    Represents a discovered source path (file or directory) that may be backed up.
    """
    path: Path
    exists: bool
    size: int = 0
    type: ItemType = "unknown"
