# Implementation Plan - Linux Build Support

This plan outlines the changes required to make NotifyMe compatible with Linux, while maintaining full Windows support.

## User Review Required

> [!IMPORTANT]
> **Linux Idle Time Detection**: Detecting idle time on Linux is complex and typically requires external tools like `xprintidle` or specific X11/Wayland libraries. For the first version, idle time suppression might be disabled on Linux unless a reliable cross-distro method is found.

> [!NOTE]
> **Windows-specific Features**: Some features like "Mark Completed" buttons in toast notifications are highly specific to Windows (via `winotify`). On Linux, notifications will be displayed without these action buttons using `plyer`. Users can still mark tasks as completed via the system tray menu.

## Proposed Changes

### Core Logic & Utilities

#### [MODIFY] [utils.py](file:///e:/ws-notifyme/notifyme/notifyme_app/utils.py)

- Make `get_app_data_dir()` platform-aware: use `APPDATA` on Windows and `~/.config/NotifyMe` on Linux.
- Make `get_idle_seconds()` platform-aware: return `None` on Linux for now, or implement a basic check.
- Ensure `ctypes.wintypes` is only imported on Windows.

#### [MODIFY] [notifications.py](file:///e:/ws-notifyme/notifyme/notifyme_app/notifications.py)

- Refactor `NotificationManager` to use `winotify` only on Windows.
- Use `plyer` for notifications on Linux and other platforms.

#### [MODIFY] [system.py](file:///e:/ws-notifyme/notifyme/notifyme_app/system.py)

- Replace `explorer` calls with platform-agnostic folder opening (using `os.startfile` on Windows and `xdg-open` on Linux).

### Entry Point & Application

#### [MODIFY] [notifyme.py](file:///e:/ws-notifyme/notifyme/notifyme.py)

- Make `winotify` imports conditional.
- Update `cleanup_instances()` to use `pkill` or similar on Linux.
- Update `show_notification` to be platform-aware.

#### [MODIFY] [app.py](file:///e:/ws-notifyme/notifyme/notifyme_app/app.py)

- Make `winotify` imports and usage conditional (e.g., in medicine notifications).

### Build Configuration

#### [MODIFY] [pyproject.toml](file:///e:/ws-notifyme/notifyme/pyproject.toml)

- Add platform markers to `winotify` dependency to prevent installation failures on Linux.

#### [NEW] [NotifyMe_linux.spec](file:///e:/ws-notifyme/notifyme/NotifyMe_linux.spec)

- Create a Linux-specific PyInstaller spec file using `icon.png` and no `.ico` files.

#### [NEW] [build.sh](file:///e:/ws-notifyme/notifyme/scripts/build.sh)

- Create a shell script for building the application on Linux using `pyinstaller` and the Linux spec file.

## Testing Strategy

To ensure cross-platform reliability without needing separate test suites:

- **Mock Platform Modules**: Use `unittest.mock` to simulate both Windows (`winotify`) and Linux (`plyer`) environments in tests.
- **Platform Choice Tests**: Add tests that specifically verify the application selects the correct notification/system handler based on `sys.platform`.
- **Shared Logic Verification**: Ensure that core logic (timers, state, configuration) continues to be tested in a platform-agnostic way.
- **CI Integration (Future)**: Recommend running tests on both Windows and Linux runners once CI is established.

---

## Verification Plan

### Automated Tests

- **Regression Testing**: Run existing `pytest` suite on Windows to ensure no breaks.
- **Mocked Platform Tests**: Add new tests in `tests/test_notifications.py` and `tests/test_system.py` that mock `sys.platform` to verify Linux-specific code paths even when running on Windows.
- **Conditionals**: Use `@pytest.mark.skipif` for any tests that absolutely require a specific OS (e.g., calling a native binary).

### Manual Verification

- **Windows**: Verify that `notifyme.py` starts, notifications appear with buttons, and menu functions normally.
- **Linux (User-assisted)**:

  - Verify app starts in system tray.
  - Verify notifications appear (using `plyer`).
  - Verify folder opening works via `xdg-open`.
  - Verify build via `scripts/build.sh`.
