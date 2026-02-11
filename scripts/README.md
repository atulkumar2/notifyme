# Build and Development Scripts

This folder contains all build and development scripts for the NotifyMe project. Scripts are provided in both batch (`.bat`) and PowerShell (`.ps1`) formats for flexibility.

## Scripts Overview

### `build.ps1` / `build.bat`

**Purpose**: Build the NotifyMe executable using PyInstaller

**Usage**:

```bash
# PowerShell (recommended)
.\build.ps1

# Batch
.\build.bat

# From repo root
.\scripts\build.ps1
```

**What it does**:

- Validates or creates icon from PNG
- Compiles Python code to EXE using PyInstaller
- Builds to temporary location first (safe failure)
- Generates SHA256 checksum for verification
- Creates `dist/notifyme.exe` (~18.5 MB)

**Output**: `dist/notifyme.exe` and `dist/SHA256SUMS.txt`

---

### `run.ps1` / `run.bat`

**Purpose**: Run the NotifyMe application from source

**Usage**:

```bash
# PowerShell
.\run.ps1

# Batch
.\run.bat

# From repo root
.\scripts\run.ps1
```

**What it does**:

- Launches NotifyMe using `uv run notifyme.py`
- Provides fallback to local uv installation if needed

---

### `setup.ps1` / `setup.bat`

**Purpose**: Initialize development environment

**Usage**:

```bash
# PowerShell (recommended)
.\setup.ps1

# Batch
.\setup.bat

# From repo root
.\scripts\setup.ps1
```

**What it does**:

- Installs `uv` package manager (if not present)
- Runs `uv sync` to install project dependencies
- Sets up virtual environment

**Requirements**: Internet connection (first run only)

---

### `run_tests.ps1` / `run_tests.bat`

**Purpose**: Run the test suite

**Usage**:

```bash
# PowerShell (recommended)
.\run_tests.ps1

# Batch
.\run_tests.bat

# From repo root
.\scripts\run_tests.ps1
```

**What it does**:

- Runs pytest on `tests/test_notifyme.py`
- Displays verbose test results
- Returns exit code 0 (success) or 1 (failure)

---

### `check_version.py`

**Purpose**: Verify version consistency across all version files

**Usage**:

```bash
uv run python scripts/check_version.py
```

**What it checks**:

- `pyproject.toml` version
- `notifyme_app/constants.py` APP_VERSION
- `notifyme_app/__init__.py` **version**
- Local version vs latest GitHub release

**Used in**: CI/CD pipelines as a pre-release check

---

## Backward Compatibility

Wrapper scripts exist in the repository root (`build.bat`, `run.bat`, etc.) that delegate to the actual scripts in this folder. This ensures:

- ✅ Old commands still work: `build.bat` from root
- ✅ New commands work: `scripts\build.ps1`
- ✅ Either .bat or .ps1 can be used from any location

---

## Recommended Usage

For new development, prefer **PowerShell** files (`.ps1`):

| Task  | Command                   |
| ----- | ------------------------- |
| Setup | `.\scripts\setup.ps1`     |
| Run   | `.\scripts\run.ps1`       |
| Build | `.\scripts\build.ps1`     |
| Test  | `.\scripts\run_tests.ps1` |

**Benefits of PowerShell versions**:

- Better error handling and reporting
- More readable code (structured syntax)
- Native Windows integration
- Cleaner conditional logic

---

## PowerShell Execution Policy

If you get an execution policy error when running `.ps1` files:

```powershell
# One-time fix (current user only)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or allow scripts in a process
powershell -ExecutionPolicy Bypass -File .\script.ps1
```

The `.bat` wrappers automatically bypass this policy, so `build.bat` will always work.

---

## Troubleshooting

### "command not found" errors

- Ensure you're in the repository root directory
- Use full path: `.\scripts\build.ps1`

### Build fails at PyInstaller stage

- Check that `.venv\Scripts\python.exe` exists
- Verify `icon.png` exists (or PNG→ICO conversion fails)
- See `build.ps1` for detailed error messages

### Setup fails at uv installation

- Ensure you have internet connection
- Try manual: `uv sync` or `pip install -e .`
- Check that PowerShell has internet access (proxy issues?)

### Tests fail

- Run `.\scripts\setup.ps1` first to ensure dependencies installed
- Check that `tests/` folder exists with test files
- See test output for specific assertion failures

---

## Development Workflow

Typical development session:

```powershell
# Initial setup (once)
.\scripts\setup.ps1

# During development
.\scripts\run.ps1        # Test changes locally
.\scripts\run_tests.ps1  # Run automated tests

# Before release
.\scripts\build.ps1      # Create executable
# Verify dist/notifyme.exe works
```

---

## CI/CD Integration

These scripts are used in automated builds:

- **GitHub Actions**: Calls `scripts/check_version.py` for version verification
- **Build Pipeline**: Runs `scripts/build.ps1` to generate releases
- **Test Pipeline**: Runs `scripts/run_tests.ps1` for regression testing

See `.github/workflows/` for pipeline definitions.
