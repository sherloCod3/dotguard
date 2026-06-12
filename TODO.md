# DotGuard TODO

## Status legend
- [x] done
- [~] in progress
- [ ] not started

## Implemented / current V0

- [x] Implement models: `FileItem`, `Result` types
- [x] Implement Phase 2 discovery (auto-detect configured paths)
- [x] Implement Phase 3 backup (create `~/dotfiles-backup/` structure + copy)
- [x] Implement Phase 4 validation (SHA-256 + directory/file status)
- [x] Implement Phase 5 report generation (`reports/backup-report.txt`)
- [x] Improve safety: unified source→relative path mapping for backup + validation (`core/path_utils.py`)
- [x] Backup robustness: directory copying uses incremental `os.walk` + `shutil.copy2`
- [x] Added discovery coverage: **every immediate folder inside `~/.config`**
- [x] Added targets for themes/icons:
  - `/usr/share/themes`
  - `/usr/share/icons`

## Next phases (future)

- [ ] Implement Phase 1 diagnosis (requirements checks, disk space, permissions)
- [ ] Implement Phase 2 discovery UI/selection (categories toggles)
- [ ] Implement Phase 6 secure git (generate `.gitignore`, prevent accidental `git add .`, validate before commit)
- [ ] Implement Phase 7 secret audit (gitleaks/trufflehog scan + block on findings)
- [ ] Implement Phase 8 GitHub guided setup (init/remote/branch, private flag)
- [ ] Implement Phase 9 progress UI (Textual + Rich progress)
- [ ] Implement Phase 10 restore + main menu

## Maintenance

- [ ] Add minimal run instructions to README (more explicit commands/examples)
- [ ] Add smoke-test script (repeatable in CI)

