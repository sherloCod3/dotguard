from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from models.file_item import FileItem


@dataclass(slots=True)
class DiscoveryService:
    """
    V0 discovery:
    - expands configured target paths
    - creates FileItem for each target with existence + size + type
    """
    targets: tuple[str, ...] = (
        "~/.config/xfce4",
        "~/.config/Code",
        "~/.bashrc",
        "~/.zshrc",
        "~/.gitconfig",
        "~/.ssh",
        "~/.themes",
        "~/.icons",
        "/usr/share/themes",
        "/usr/share/icons",
    )

    def discover(self) -> list[FileItem]:
        items: list[FileItem] = []

        for raw in self.targets:
            root = Path(raw).expanduser()

            # Special expansion:
            # If ~/.config is included as a target, also include every directory inside it.
            if root.name == ".config" and root.is_dir():
                items.extend(self._discover_config_dirs(root))
                continue

            items.append(self._discover_one(root))

        return items

    def _discover_config_dirs(self, config_dir: Path) -> list[FileItem]:
        discovered: list[FileItem] = []

        # Include the config root itself as well (useful for validation/reporting)
        discovered.append(self._discover_one(config_dir))

        try:
            # Only immediate subdirectories per request: "every folder inside ~/.config"
            for child in sorted(config_dir.iterdir()):
                if child.is_dir():
                    discovered.append(self._discover_one(child))
        except Exception:
            # If iteration fails (permissions), keep tool alive; errors will be reflected as missing/unknown.
            pass

        return discovered

    def _discover_one(self, p: Path) -> FileItem:
        exists = p.exists()

        if not exists:
            detected_type = "unknown"
            size = 0
        elif p.is_dir():
            detected_type = "dir"
            size = self._safe_size(p)
        elif p.is_file():
            detected_type = "file"
            size = p.stat().st_size
        else:
            detected_type = "unknown"
            size = self._safe_size(p)

        return FileItem(
            path=p,
            exists=exists,
            size=size,
            type=detected_type,  # type: ignore[arg-type]
        )

    @staticmethod
    def _safe_size(p: Path) -> int:
        try:
            if p.is_file():
                return p.stat().st_size
            # For dirs: approximate size as 0 for V0 (we don't need exact here)
            return 0
        except OSError:
            return 0
