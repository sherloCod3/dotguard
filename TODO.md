# DotGuard TODO

- [ ] Confirm/implement project scaffold (TUI + Typer entrypoint)
- [ ] Implement models: `FileItem`, `Result` types
- [ ] Implement Phase 1 diagnosis (requirements checks, disk space, permissions)
- [ ] Implement Phase 2 discovery (auto-detect paths + selectable categories)
- [ ] Implement Phase 3 backup (create `~/dotfiles-backup/` structure + copy)
- [ ] Implement Phase 4 validation (sha256 compare + directory/file status)
- [ ] Implement Phase 5 report generation (`reports/backup-report.txt`)
- [ ] Implement Phase 6 secure git (generate `.gitignore`, prevent accidental `git add .`)
- [ ] Implement Phase 7 secret audit (gitleaks/trufflehog scan + block on findings)
- [ ] Implement Phase 8 GitHub guided setup (init/remote/branch, private flag)
- [ ] Implement Phase 9 progress UI (Textual + Rich progress)
- [ ] Implement Phase 10 restore + main menu
- [ ] Add `requirements.txt` and minimal run instructions
- [ ] Smoke-test full workflow locally

