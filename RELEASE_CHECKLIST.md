# Release Checklist (NotifyMe)

> Repo specifics:
>
> - Version strings live in:
>   - `pyproject.toml`
>   - `notifyme_app/__init__.py`
>   - `constants.py`
> - Build output in `dist/`:
>   - `notifyme.exe`
>   - `SHA256SUMS.txt`
> - Build entrypoint: `build.bat` (repo root)

## 0) Decide the release version

- [ ] Pick next SemVer version: `vMAJOR.MINOR.PATCH`
- [ ] Confirm bump type:
  - [ ] MAJOR = breaking changes
  - [ ] MINOR = features
  - [ ] PATCH = fixes

## 1) Pre-flight sanity

- [ ] `git status` is clean
- [ ] On `main` (or intended release branch)
- [ ] `git pull origin main`
- [ ] Quick local smoke test (run from source)

## 2) Update version strings (ALL THREE)

- [ ] Update version in `pyproject.toml`
- [ ] Update version in `notifyme_app/__init__.py`
- [ ] Update version in `constants.py`
- [ ] Sanity check: all three match exactly (same number)

## 3) Release notes / changelog

- [ ] Update `CHANGELOG.md` **or** add `docs/releases/vX.Y.Z.md`
- [ ] Include:
  - [ ] Features
  - [ ] Fixes
  - [ ] Improvements
  - [ ] Security (if any)
  - [ ] Known issues (optional)

## 4) Commit version bump + notes

- [ ] `git add -A`
- [ ] `git commit -m "chore: bump version to vX.Y.Z"`

## 5) Build artifacts

- [ ] Run build from repo root:
  - [ ] `build.bat`
- [ ] Confirm build outputs exist:
  - [ ] `dist/notifyme.exe`
  - [ ] `dist/SHA256SUMS.txt`
- [ ] Basic binary smoke test:
  - [ ] Launch `dist/notifyme.exe`
  - [ ] Tray icon appears (if applicable)
  - [ ] Reminder fires at least once
  - [ ] Config/log path works (`%APPDATA%\\NotifyMe\\...`) if relevant

## 6) Create annotated git tag

- [ ] Create annotated tag:
  - [ ] `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- [ ] Verify tag exists:
  - [ ] `git tag --list | findstr vX.Y.Z`

## 7) Push commit + tag

- [ ] `git push origin main`
- [ ] `git push origin vX.Y.Z`

## 8) GitHub Release (recommended)

- [ ] Create GitHub Release for tag `vX.Y.Z`
- [ ] Paste release notes (or link to `docs/releases/vX.Y.Z.md`)
- [ ] Attach artifacts from `dist/`:
  - [ ] `notifyme.exe`
  - [ ] `SHA256SUMS.txt`

## 9) Post-release verification

- [ ] Download the uploaded `notifyme.exe`
- [ ] Verify checksum matches `SHA256SUMS.txt`
- [ ] Confirm tag points to correct commit:
  - [ ] `git show vX.Y.Z`

---

## Commands cheat-sheet (copy/paste)

```bash
git status
git pull origin main
git add -A
git commit -m "chore: bump version to vX.Y.Z"
.\build.bat
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin main
git push origin vX.Y.Z
```
