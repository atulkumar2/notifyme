# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Fixed

### Removed

## [2.2.0] - 2026-02-11

### Added

- TTS (Text-to-Speech) functionality for reminder notifications
- PowerShell (.ps1) versions of all build and run scripts

### Changed

- Reorganized scripts to proper project structure (moved to `/scripts` directory)
- Improved script portability with automatic directory resolution
- Enhanced cross-platform script compatibility

### Fixed

- Fixed script path resolution issues when running from different directories
- Improved error handling in build and deployment scripts

## [2.1.0] - 2026-02-04

### Added

- Pranayama reminders (new breathing reminders with 120-minute default interval)
- Default test notification for new reminders
- Update checks on startup and manual check via menu
- Version sync check via pre-commit
- Menu status showing update availability
- Per-reminder pause/resume controls
- Documentation and help updates with learning resources

### Changed

- Improved reminder timing with staggered intervals to avoid collisions
- Idle/lock detection now resets timers to prevent immediate pings after returning

### Fixed

- Fixed app exiting immediately after launch
- Fixed reminders not starting on launch
- General stability improvements

## [2.0.1] - 2026-01-31

### Added

- Integrated help system bundled within the executable
- Online documentation via GitHub Pages
- Help → User Guide menu option
- SHA256 checksum verification for releases

### Changed

- Deterministic PyInstaller build using spec file
- Cleaner asset bundling (icons, help files)
- Better Windows behavior with tray-only execution
- Improved startup reliability

### Fixed

- Removed console window from tray execution
- Safer packaging defaults

## [1.0.0] - 2026-01-17

### Added

- Triple reminder system: Eye blink (20 min), walking (60 min), water (30 min)
- System tray integration
- Windows Toast notifications support
- Customizable reminder intervals
- Per-reminder pause/resume controls
- Portable single exe file (no installation required)
- Configuration storage in %APPDATA%\NotifyMe\
- Auto-start with Windows capability
- Modular application architecture
- TTS (Text-to-Speech) functionality
- Application updater
