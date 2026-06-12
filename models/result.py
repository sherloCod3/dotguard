from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


ValidationStatus = Literal["ok", "failed", "skipped"]


@dataclass(slots=True)
class ItemResult:
    """
    Per-item result for copy/validation/reporting.
    """
    source: str
    copied: bool = False
    copy_error: str | None = None

    exists_in_backup: bool = False

    validation_status: ValidationStatus = "skipped"
    validation_error: str | None = None

    # hash comparison is file-based
    source_sha256: str | None = None
    dest_sha256: str | None = None


@dataclass(slots=True)
class RunResult:
    """
    Aggregate result for a full workflow run.
    """
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: datetime | None = None

    items_found: int = 0
    items_copied: int = 0
    failures: int = 0

    validation_ok: int = 0
    validation_failed: int = 0
    validation_skipped: int = 0

    # paths used in the run
    backup_root: str | None = None

    # per-item details
    details: list[ItemResult] = field(default_factory=list)

    def finish(self) -> None:
        self.finished_at = datetime.utcnow()

    @property
    def elapsed_seconds(self) -> float:
        end = self.finished_at or datetime.utcnow()
        delta = end - self.started_at
        return delta.total_seconds()
