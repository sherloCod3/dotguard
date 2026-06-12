from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from core.path_utils import source_relpath
from models.file_item import FileItem
from models.result import ItemResult, RunResult


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


@dataclass(slots=True)
class ValidationService:
    """
    V0 validation:
    - For files: sha256(source) == sha256(destination file)
    - For directories: validate each file inside (recursively) by sha256
      (If any file differs or missing -> directory fails)
    """
    backup_root: Path

    def validate(self, run: RunResult, items: list[FileItem]) -> RunResult:
        # Map for quick lookup by source string
        by_source: dict[str, ItemResult] = {d.source: d for d in run.details}

        for it in items:
            src = it.path
            rel = source_relpath(src)
            dest = self.backup_root / rel

            if not src.exists:
                # discovery says missing; leave as skipped
                continue
            if it.type == "dir":
                self._validate_dir(by_source[src.as_posix()], src, dest)
            elif it.type == "file":
                self._validate_file(by_source[src.as_posix()], src, dest)
            else:
                # unknown type -> skipped
                continue

        # recompute totals from updated detail statuses
        run.validation_ok = sum(1 for d in run.details if d.validation_status == "ok")
        run.validation_failed = sum(1 for d in run.details if d.validation_status == "failed")
        run.validation_skipped = sum(1 for d in run.details if d.validation_status == "skipped")
        return run

    def _validate_file(self, detail: ItemResult, src: Path, dest: Path) -> None:
        try:
            if not dest.exists():
                detail.validation_status = "failed"
                detail.exists_in_backup = False
                detail.validation_error = "dest_missing"
                return

            detail.exists_in_backup = True
            detail.source_sha256 = _sha256_file(src)
            detail.dest_sha256 = _sha256_file(dest)

            if detail.source_sha256 == detail.dest_sha256:
                detail.validation_status = "ok"
            else:
                detail.validation_status = "failed"
                detail.validation_error = "sha256_mismatch"
        except Exception as e:  # noqa: BLE001
            detail.validation_status = "failed"
            detail.validation_error = str(e)

    def _validate_dir(self, detail: ItemResult, src: Path, dest: Path) -> None:
        try:
            if not dest.exists():
                detail.validation_status = "failed"
                detail.exists_in_backup = False
                detail.validation_error = "dest_dir_missing"
                return

            # Validate all files under src
            src_files: list[Path] = []
            for p in src.rglob("*"):
                if p.is_file():
                    src_files.append(p)

            for src_file in src_files:
                rel_file = src_file.relative_to(src)
                dest_file = dest / rel_file
                if not dest_file.exists():
                    detail.validation_status = "failed"
                    detail.validation_error = f"missing_file:{rel_file.as_posix()}"
                    detail.exists_in_backup = False
                    return
                if _sha256_file(src_file) != _sha256_file(dest_file):
                    detail.validation_status = "failed"
                    detail.validation_error = f"sha_mismatch:{rel_file.as_posix()}"
                    detail.exists_in_backup = True
                    return

            detail.validation_status = "ok"
            detail.exists_in_backup = True
        except Exception as e:  # noqa: BLE001
            detail.validation_status = "failed"
            detail.validation_error = str(e)

    # NOTE: relative path mapping is shared via core.path_utils.source_relpath()
