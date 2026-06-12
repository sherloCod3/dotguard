from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(slots=True)
class DotGuardConfig:
    """
    Minimal configuration for V0 CLI workflow:
    - discovery -> backup -> sha256 validation -> report
    """
    destination_root: Path = Path.home() / "dotfiles-backup"

    # Where report gets written (inside destination_root)
    reports_dirname: str = "reports"

    # Buckets (simple, V0 uses backup/ for sources; others reserved for later)
    backup_dirname: str = "backup"
    packages_dirname: str = "packages"
    archives_dirname: str = "archives"
    logs_dirname: str = "logs"

    # Source targets for discovery (expand ~ during discovery)
    targets: tuple[str, ...] = (
        # user-level dotfiles / configs
        "~/.config/xfce4",
        "~/.config/Code",
        "~/.bashrc",
        "~/.zshrc",
        "~/.gitconfig",
        "~/.ssh",
        "~/.themes",
        "~/.icons",
        # system-level themes/icons
        "/usr/share/themes",
        "/usr/share/icons",
    )

    def expand_targets(self) -> list[Path]:
        expanded: list[Path] = []
        for t in self.targets:
            expanded.append(Path(t).expanduser())
        return expanded

    @property
    def backup_root(self) -> Path:
        return self.destination_root / self.backup_dirname

    @property
    def reports_root(self) -> Path:
        return self.destination_root / self.reports_dirname
