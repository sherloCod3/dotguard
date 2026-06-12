from __future__ import annotations

from pathlib import Path

import typer

from core.backup import BackupService
from core.config import DotGuardConfig
from core.discovery import DiscoveryService
from core.report import ReportService
from core.validation import ValidationService

app = typer.Typer(help="DotGuard - audit workflow for dotfiles backups (V0)")


@app.command()
def discover() -> None:
    """
    Discover configured dotfiles/targets and print which ones exist.
    """
    cfg = DotGuardConfig()
    service = DiscoveryService(targets=cfg.targets)
    items = service.discover()

    for it in items:
        state = "FOUND" if it.exists else "MISSING"
        typer.echo(f"{state:7} {it.type:6} {it.path} (size={it.size})")


@app.command()
def backup() -> None:
    """
    V0 workflow:
      discovery -> backup -> sha256 validation -> report
    """
    cfg = DotGuardConfig()

    discovery = DiscoveryService(targets=cfg.targets)
    items = discovery.discover()

    # Put backups under ~/dotfiles-backup/backup/<absolute-path-sans-leading-slash>
    backup_service = BackupService(destination_backup_root=cfg.backup_root / "backup")

    # Validation compares into the same backup location
    validation_service = ValidationService(backup_root=cfg.backup_root / "backup")

    # Report under ~/dotfiles-backup/reports/backup-report.txt
    report_service = ReportService(reports_dir=cfg.reports_root)

    run = backup_service.backup(items)
    run = validation_service.validate(run, items)
    run.finish()

    report_path: Path = report_service.write_report(run)

    ok = run.validation_failed == 0 and run.failures == 0
    typer.echo(f"Report: {report_path}")
    raise typer.Exit(code=0 if ok else 1)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
