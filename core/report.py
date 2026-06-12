from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from models.result import RunResult


class ReportService:
    """
    Writes a V0 textual report to:
      {backup_root}/reports/backup-report.txt
    """
    def __init__(self, reports_dir: Path) -> None:
        self.reports_dir = reports_dir

    def write_report(self, run: RunResult) -> Path:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.reports_dir / "backup-report.txt"

        lines: list[str] = []
        lines.append("DotGuard Backup Report")
        lines.append(f"Time: {datetime.utcnow().isoformat(timespec='seconds')}Z")
        lines.append("")
        lines.append(f"Items found: {run.items_found}")
        lines.append(f"Copied: {run.items_copied}")
        lines.append(f"Failures: {run.failures}")
        lines.append("")
        lines.append(
            f"Validation: {run.validation_ok} OK, {run.validation_failed} FAILED, {run.validation_skipped} SKIPPED"
        )
        lines.append("")
        lines.append("Details:")
        lines.append("------------------------------------------------------------")
        for d in run.details:
            status = f"{d.validation_status.upper()}"
            extra = ""
            if d.validation_error:
                extra = f" ({d.validation_error})"
            lines.append(f"- {d.source} -> {status}{extra}")

        lines.append("------------------------------------------------------------")
        if run.finished_at:
            lines.append(f"Elapsed: {run.elapsed_seconds:.2f}s")
        else:
            lines.append("Elapsed: n/a")

        # Optional: keep a tiny JSON blob for future parsing.
        lines.append("")
        lines.append("Run summary (json):")
        lines.append(self._safe_summary_json(run))

        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return report_path

    @staticmethod
    def _safe_summary_json(run: RunResult) -> str:
        try:
            # Convert datetime objects to strings
            data = asdict(run)
            if data.get("started_at") is not None:
                data["started_at"] = run.started_at.isoformat()
            if data.get("finished_at") is not None:
                data["finished_at"] = run.finished_at.isoformat()
            return str(data)
        except Exception:
            return "{}"
