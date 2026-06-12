# DotGuard

DotGuard is a **dotfiles audit + backup** tool designed to reduce the risk of losing configuration and to prevent accidentally publishing secrets.

It performs an audit workflow:

1. **Discovery** – detect configured dotfiles/dirs
2. **Backup** – copy into `~/dotfiles-backup/`
3. **Validation** – verify backed content using SHA-256
4. **Reporting** – generate `reports/backup-report.txt`

Current focuses:
- Reliability (directory copying via `os.walk` + `shutil.copy2`)
- Safety against path drift (shared path mapping used by backup + validation)
- Extensibility for future restore / secret scanning / GitHub automation

---

## Folder Layout

Backups are stored here:

```text
~/dotfiles-backup/
├── backup/
├── packages/
├── archives/
├── logs/
└── reports/
```

Report file:

- `~/dotfiles-backup/reports/backup-report.txt`

---

## Requirements

- Python 3.12+
- Project dependencies from `requirements.txt`

---

## Install

```bash
pip install -r requirements.txt
```

---

## Usage (V0 CLI)

Discovery:

```bash
python main.py discover
```

Backup pipeline (discovery → copy → validation → report):

```bash
python main.py backup
```

Expected output:
- `~/dotfiles-backup/reports/backup-report.txt` is created/updated.

---

## What gets discovered (current targets)

Targets are configured in `core/config.py` and include:

- `~/.config/xfce4`
- `~/.config/*` (every immediate folder inside `~/.config`)
- `~/.bashrc`
- `~/.zshrc`
- `~/.gitconfig`
- `~/.gitconfig`
- `~/.ssh`
- `~/.themes`
- `~/.icons`
- `/usr/share/themes`
- `/usr/share/icons`

> Note: Discovery currently expands `~/.config` dynamically to include **every immediate subdirectory**.

---

## Validation

For backed items:
- Files: SHA-256 is computed and compared
- Directories: validated by recursively validating contained files

---

## Security Notes (future-proofing)

DotGuard is designed to evolve into:
- Secure Git workflow (safe `.gitignore` generation + no `git add .`)
- Secret scanning (gitleaks/trufflehog)
- GitHub guided setup
- Restore tooling

For now, the pipeline is copy + validate + report.

---

## Project Roadmap

See `TODO.md`.
