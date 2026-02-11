# NotifyMe - Installation Guide

[← Back to Home](index.md) | [📖 Usage](usage.md) | [⚙️ Configuration](configuration.md) | [🆘 Troubleshooting](troubleshooting.md)

---

## Option 1: Download Pre-built Executable (Recommended)

1. Download the latest `NotifyMe.exe` from [GitHub Releases](https://github.com/atulkumar2/notifyme/releases)
2. Run `NotifyMe.exe` - no installation required!
3. Optional: [Auto-start with Windows](#auto-start-with-windows)

## Option 2: Run from Source

### Prerequisites

- Windows 10 or Windows 11
- Python 3.8 or higher

### Installation Steps

1. Clone or download the repository:

   ```bash
   git clone https://github.com/atulkumar2/notifyme.git
   cd notifyme
   ```

2. Run setup to install dependencies:

   **Batch** (for CMD):

   ```bash
   scripts\setup.bat
   ```

   **PowerShell** (recommended):

   ```powershell
   .\scripts\setup.ps1
   ```

   Or manually:

   ```bash
   uv sync
   ```

3. Run the application:

   **Batch** (for CMD):

   ```bash
   scripts\run.bat
   ```

   **PowerShell**:

   ```powershell
   .\scripts\run.ps1
   ```

   Or manually:

   ```bash
   uv run notifyme.py
   ```

## Auto-start with Windows

### Method 1: Using Startup Folder (Easiest)

1. Press `Win + R`
2. Type `shell:startup` and press Enter
3. Copy `NotifyMe.exe` or create a shortcut there
4. Restart Windows to test

### Method 2: Using Task Scheduler

1. Press `Win + X` and select "Task Scheduler"
2. Click "Create Basic Task"
3. Name it "NotifyMe"
4. Set trigger to "At startup"
5. Set action to "Start a program" and browse to `NotifyMe.exe`
6. Click Finish

## Building a Standalone Executable

If you want to build your own `.exe`:

1. Ensure you have the source code
2. Run the build script:

   **Batch** (for CMD):

   ```bash
   scripts\build.bat
   ```

   **PowerShell** (recommended):

   ```powershell
   .\scripts\build.ps1
   ```

   Or manually with Python:

   ```bash
   .venv\Scripts\python.exe -m PyInstaller NotifyMe.spec
   ```

3. Find your executable at `dist/NotifyMe.exe`

The build process automatically:

- Bundles all dependencies (including pyttsx3 for offline TTS)
- Includes required data files (icon, help HTML)
- Detects and includes hidden modules

**Note**: The `.spec` file is pre-configured with all necessary settings. Only modify it if you have advanced PyInstaller knowledge.

## Troubleshooting Installation

- **"Python not found"**: Install Python 3.8+ from [python.org](https://www.python.org/)
- **"uv command not found"**: Run `setup.bat` to install uv
- **Notifications not working**: Check [Troubleshooting Guide](troubleshooting.md)

---

[← Back to Home](index.md) | [Next: Usage Guide →](usage.md)
