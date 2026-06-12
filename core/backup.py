from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from core.path_utils import source_relpath
from models.file_item import FileItem
from models.result import ItemResult, RunResult


@dataclass(slots=True)
class BackupService:
    """
    V0 backup:
    - copies discovered sources into destination_backup_root/<relative-path>
    - directory copy uses walk+copy2 (more incremental than copytree internals)
    """
    destination_backup_root: Path

    def backup(self, items: list[FileItem]) -> RunResult:
        run = RunResult(backup_root=str(self.destination_backup_root.parent))
        run.items_found = len(items)

        self.destination_backup_root.mkdir(parents=True, exist_ok=True)

        for it in items:
            item_result = ItemResult(source=str(it.path))

            if not it.exists:
                item_result.copied = False
                item_result.copy_error = "source_missing"
                run.failures += 1
                run.details.append(item_result)
                continue

            try:
                rel = source_relpath(it.path)
                dest = self.destination_backup_root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)

                if it.type == "dir":
                    self._copy_dir_walk(it.path, dest)
                    item_result.copied = True
                else:
                    shutil.copy2(it.path, dest)
                    item_result.copied = True

                run.items_copied += 1
                run.details.append(item_result)
            except Exception as e:  # noqa: BLE001
                item_result.copied = False
                item_result.copy_error = str(e)
                run.failures += 1
                run.details.append(item_result)

        return run

    @staticmethod
    def _copy_dir_walk(src_dir: Path, dest_dir: Path) -> None:
        """
        Incremental directory copy:
        - creates dest_dir
        - walks all files under src_dir and copies preserving relative layout
        """
        dest_dir.mkdir(parents=True, exist_ok=True)

        # copy symlinks as links? For V0 safety, preserve symlinks as symlinks
        # rather than following them (avoids leaking elsewhere).
        for root, dirs, files in os.walk(src_dir, followlinks=False):
            root_path = Path(root)
            rel_root = root_path.relative_to(src_dir)
            target_root = dest_dir / rel_root
            target_root.mkdir(parents=True, exist_ok=True)

            # ensure subdirs exist
            for d in dirs:
                (target_root / d).mkdir(parents=True, exist_ok=True)

            for f in files:
                src_path = root_path / f
                dst_path = target_root / f

                if src_path.is_symlink():
                    # Recreate symlink target
                    if dst_path.exists() or dst_path.is_symlink():
                        dst_path.unlink(missing_ok=True)  # type: ignore[attr-defined]
                    link_target = os.readlink(src_path)
                    os.symlink(link_target, dst_path)
                else:
                    shutil.copy2(src_path, dst_path)

    # NOTE: relative path mapping is shared via core.path_utils.source_relpath()
