# DotGuard TODO

## Status legend
- [x] done
- [~] in progress
- [ ] not started

---

## Current V0 (CLI + audit pipeline)

### Implemented
- [x] Models: `FileItem`, `Result` types
- [x] Discovery (Phase 2): auto-detect configured targets
- [x] Backup (Phase 3): create `~/dotfiles-backup/` structure + copy
- [x] Validation (Phase 4): SHA-256 + directory/file status
- [x] Reporting (Phase 5): write `reports/backup-report.txt`
- [x] Safety: unified source→relative path mapping used by backup + validation (`core/path_utils.py`)
- [x] Backup robustness: copy directories via incremental `os.walk` + `shutil.copy2`
- [x] Discovery coverage: every immediate folder inside `~/.config`
- [x] Theme/icon targets: `/usr/share/themes`, `/usr/share/icons`

### V0 verification criteria (done when)
- `python main.py discover` prints each target as `FOUND` or `MISSING`
- `python main.py backup` writes `~/dotfiles-backup/reports/backup-report.txt`
- Process exit code:
  - `0` when `run.validation_failed == 0 and run.failures == 0`
  - `1` otherwise

---

## Roadmap (future phases)

### Phase 1 — Diagnosis / pre-flight checks
- [ ] Goal: prevent unsafe runs by validating environment prerequisites.
- Tasks
  - [ ] Implement requirements checks (Python/runtime assumptions)
  - [ ] Check disk space availability for backup destination (based on discovery results)
  - [ ] Check permissions for read sources + write backup destination
- Verify
  - Running `python -u main.py backup` performs pre-flight before backup starts
  - Pre-flight failures:
    - produce clear, actionable error messages
    - exit non-zero (fail fast) without writing/partially writing backup artifacts
  - Pre-flight success:
    - pipeline continues to discovery/backup/validation/report steps
- Done when
  - `python main.py backup` fails fast (and clearly) when prerequisites are not met
  - No report/backup artifact is produced (or report explicitly marks “pre-flight failed” and no backup copy occurs)
- Dependencies
  - None (but should share config/targets with existing pipeline)

---

### Phase 2 — Discovery UI / selection
- [ ] Goal: allow users to choose which categories/targets to include.
- Tasks
  - [ ] Add selection mechanism (categories toggles)
  - [ ] Wire selection into `DiscoveryService.discover()` inputs
- Verify
  - Selected targets are the only ones backed/validated/reported
- Done when
  - `python main.py backup` respects user selection and still produces the same report artifact
- Dependencies
  - Phase 1 diagnosis (optional) for UX safety

---

### Phase 6 — Secure git workflow scaffolding
- [ ] Goal: reduce chance of accidentally publishing secrets.
- Tasks
  - [ ] Generate a minimal `.gitignore` aligned with DotGuard artifacts
  - [ ] Add guardrails to discourage `git add .` patterns (CLI guidance + validation)
  - [ ] Validate git state before commit (block if secrets-risk artifacts detected)
- Verify
  - Guardrails/validation trigger before “commit-ready” state when conditions indicate risk
  - Triggering behavior is documented as **Pragmatic-compatible** with V1 gate model (warnings still allow continuation where appropriate, except when an explicit commit/commit-like action is attempted)
- Done when
  - README/CLI instructions make it hard to accidentally stage sensitive files
- Dependencies
  - Phase 5 reporting (report artifacts define what should be ignored/checked)

---

### V1 Gate model 2 (Pragmatic) — Secure backup + secret posture
- [ ] Goal: improve security posture during `python main.py backup` while keeping reliability pragmatic.
- Gate definition (what runs / when it runs)
  - Phase 7 secret audit runs **after** backup + validation + report generation (so audit targets are deterministic artifacts)
- Pragmatic reliability semantics
  - On secret findings:
    - print a prominent warning summary
    - exit **non-zero** (so CI/audit pipelines can detect issues)
    - **do not hard-block artifact generation** already in progress
- Exit-code semantics (V1, aligned with V0)
  - Keep existing rule from V0 as the baseline:
    - exit `0` only when `run.validation_failed == 0 and run.failures == 0`
  - Add secret-audit outcome as an additional non-zero trigger:
    - exit is forced to non-zero when secret findings exist
- Reporting/artifact expectations (V1)
  - `~/dotfiles-backup/reports/backup-report.txt` must still be written on secret findings
  - Report must include (or reference) a secret-audit findings summary section for traceability
- Done when
  - Secret findings always produce non-zero exit
  - No hard-blocking prevents report artifact creation in the same run
- Dependencies
  - Phase 6 secure git workflow scaffolding (for ignore/guardrail consistency)

---

### Phase 7 — Secret audit (gitleaks/trufflehog)
- [ ] Goal: scan backups/reports for secrets and enforce the V1 “Pragmatic” gate.
- Tasks
  - [ ] Integrate gitleaks/trufflehog invocation
  - [ ] Ensure report generation still occurs (even when findings exist)
  - [ ] Summarize findings in the output/report deterministically
- Verify
  - Findings are summarized in output and cause **non-zero** exit code (Pragmatic gate model)
  - Backup/validation/report artifacts from the same run are still present and consistent with V0/Phase-1 semantics
- Done when
  - `python main.py backup` exits non-zero when secret findings exist, while still producing `backup-report.txt`
- Dependencies
  - Phase 6 secure git (for consistent ignore + workflow expectations)

---

### Phase 8 — GitHub guided setup
- [ ] Goal: help users initialize repository, remote, branch, and privacy safely.
- Tasks
  - [ ] Implement init + remote/branch configuration flow
  - [ ] Add “private repo” flag support
- Verify
  - Generated commands/config match explicit user choices
- Done when
  - Setup completes without exposing secrets in logs/output
- Dependencies
  - Phase 6 (secure git posture) and Phase 7 (secret audit posture)

---

### Phase 9 — Progress UI (Textual + Rich)
- [ ] Goal: show real-time progress for discovery/backup/validation/reporting.
- Tasks
  - [ ] Add progress rendering for each phase + per-target status
- Verify
  - UI does not change pipeline correctness; artifacts still match CLI-mode expectations
- Done when
  - Users can follow progress and receive the same exit-code semantics
- Dependencies
  - None (but should re-use existing services’ state)

---

### Phase 10 — Restore + main menu
- [ ] Goal: provide restore capability and a friendly navigation entrypoint.
- Tasks
  - [ ] Implement restore logic (restore from `~/dotfiles-backup/backup/...`)
  - [ ] Add main menu that links to discover/backup/restore
- Verify
  - Restore produces the expected files/dirs and does not break relative-path mapping
- Done when
  - End-to-end: backup → restore results in consistent structure with valid artifacts
- Dependencies
  - Phase 5 report + path mapping correctness (`core/path_utils.py`)

---

## Maintenance

### Working method (custom instructions we follow)
- **Planning discipline**
  - Use *brainstorming* mindset first: clarify context, list assumptions, and confirm an “understanding lock” before design decisions.
  - Use *plan-writing* style for implementation plans: short goal + 2–10 focused tasks.
  - Each task must include:
    - **Verify**: how to check it’s correct
    - **Done when** (or “Done criteria”) for phase-level completion

- **Editing discipline**
  - Apply changes incrementally and keep diffs minimal.
  - Use exact-match replacements when editing (no partial/placeholder edits).
  - After any edit, re-open the file for a quick sanity check (indentation/structure/no duplicates).

- **Always-Complete Update Briefing (mandatory)**
  After **every** change made in code or docs/instructions, record an update briefing in this repo so the work is always auditable.

  **Briefing structure**
  - **Change summary**
    - What was changed (bullets)
  - **What was not changed**
    - Expected unchanged behaviors (bullets)
  - **Verification performed**
    - Commands run + where outputs/artifacts were observed (bullets)
  - **Results**
    - Pass/fail notes (bullets)
  - **Known gaps / remaining risks**
    - What is still unverified or potentially impacted (bullets)
  - **Exit-code / artifact expectations**
    - For CLI tasks: state expected exit code rules and artifact paths
  - **Next step**
    - What will be done next (single short bullet)

- **Diff re-evaluation discipline (mandatory after any change)**
  - Immediately review the diff for:
    - What was changed
    - What was not changed (but might be expected)
    - Whether anything was partially done or accidentally removed
    - Whether formatting/indentation is correct
    - Whether there are redundant/duplicate lines or inconsistent structure
  - If any issue is found, update the file again until the diff is clean and intentional.

- **Validation discipline**
  - Map verification back to the actual CLI/service behavior (e.g., exit codes, generated artifacts).
  - Prefer objective checks (artifact existence, output shape, return codes) over subjective inspection.

- **Testing discipline**
  - Prefer running thorough integration/end-to-end checks (and edge cases) before further development.
  - If earlier tests were skipped, explicitly enumerate what remains untested before finishing.


### Ongoing maintenance items
- [ ] README: add minimal run instructions (explicit commands/examples)
  - Verify: README includes `python main.py discover` and `python main.py backup` examples + expected report path
- [ ] Smoke test script (repeatable in CI)
  - Verify: smoke test asserts report file exists and exit code is correct for a small fixture scenario
- [ ] Add/confirm CI guidance (optional)
  - Verify: documented how to run smoke tests locally and in CI

---

## How to run automated verification (future smoke/integration)

### Goals
- Validate DotGuard V0 behavior after any change (refactor/feature).
- Ensure artifacts + exit codes remain stable.
- Keep tests non-destructive for user’s real dotfiles (use fixtures/temp dirs).

### Smoke tests (fast, run on every change)
1) Discover output smoke
- Command:
  - `python -u main.py discover`
- Verify:
  - Output contains only lines in the shape:
    - `FOUND   <type> <path> (size=<n>)`
    - `MISSING <type> <path> (size=<n>)`

2) Backup pipeline smoke
- Command:
  - `python -u main.py backup`
- Verify:
  - `~/dotfiles-backup/reports/backup-report.txt` exists
  - Exit code matches report counters:
    - exit code `0` iff `run.validation_failed == 0 and run.failures == 0`
    - exit code `1` otherwise

### Integration tests (edge cases, automated with fixtures)
A fixture harness should isolate:
- discovery sources (configured targets pointing to temp dirs/files)
- backup destination root (point `backup_root` to a temp dir)

3) Missing target / validation failures
- Fixture:
  - At least one configured target path does not exist.
- Verify:
  - Report reflects failures for missing/unreadable items
  - Exit code becomes `1`

4) Write-permission failure on backup destination
- Fixture:
  - Set `backup_root` to a temp directory that is not writable.
- Verify:
  - Backup fails with non-zero exit code
  - Failure is clearly represented in logs/report (no silent success)

5) SHA-256 integrity correctness
- Fixture:
  - Create deterministic fixture files with known contents.
- Verify:
  - Validation outcomes match expected hashes (files + directories)

### Recommended structure for test automation
- Add an in-repo runner such as:
  - `scripts/smoke_test.sh` and/or `tests/test_v0_pipeline.py`
- Always:
  - capture stdout/stderr
  - assert on both:
    - produced artifacts (report file)
    - process exit codes

### CI checklist
- Smoke tests on every PR
- Integration tests on merge or nightly (if they require more fixture setup)


