"""Script to check that the version in pyproject.toml and constants.py match,
and that the version is not behind the latest GitHub release.
This is intended to be run as part of CI checks, but can also be run locally."""

import json
import os
import re
from pathlib import Path
from urllib.request import Request, urlopen

from notifyme_app.constants import APP_NAME

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT_PATH = ROOT / "pyproject.toml"
APP_MODULE_PATH = ROOT / "notifyme_app" / "constants.py"
APP_INIT_PATH = ROOT / "notifyme_app" / "__init__.py"
GITHUB_RELEASES_API_URL = (
    "https://api.github.com/repos/atulkumar2/notifyme/releases/latest"
)
TIMEOUT_SECONDS = 5


def parse_version(value: str) -> tuple[int, int, int]:
    """Parse version string into tuple of integers."""
    cleaned = value.strip().lower().lstrip("v")
    parts = cleaned.split(".")
    nums = []
    for part in parts[:3]:
        num = ""
        for ch in part:
            if ch.isdigit():
                num += ch
            else:
                break
        nums.append(int(num or 0))
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums[:3])


def read_pyproject_version() -> str:
    """Read version from pyproject.toml file."""
    content = PYPROJECT_PATH.read_text(encoding="utf-8")
    match = re.search(r'^\s*version\s*=\s*"(.*?)"\s*$', content, re.MULTILINE)
    if not match:
        raise RuntimeError("Could not find version in pyproject.toml")
    return match.group(1).strip()


def read_app_version() -> str:
    """Read version from constants.py file."""
    content = APP_MODULE_PATH.read_text(encoding="utf-8")
    match = re.search(r'^\s*APP_VERSION\s*=\s*"(.*?)"\s*$', content, re.MULTILINE)
    if not match:
        raise RuntimeError("Could not find APP_VERSION in constants.py")
    return match.group(1).strip()


def read_init_version() -> str:
    """Read version from __init__.py file."""
    content = APP_INIT_PATH.read_text(encoding="utf-8")
    match = re.search(r"^\s*__version__\s*=\s*.*?\s*$", content, re.MULTILINE)
    if not match:
        raise RuntimeError("Could not find __version__ in __init__.py")
    # After APP_VERSION import, __version__ should equal APP_VERSION
    # We extract the actual version from the APP_VERSION constant referenced
    init_content = content
    app_version_match = re.search(r"from \.constants import APP_VERSION", init_content)
    if app_version_match:
        # If __init__.py imports APP_VERSION, we just verify it's there
        version_match = re.search(r"__version__\s*=\s*APP_VERSION", init_content)
        if version_match:
            # The version is dynamically set from constants.py
            return read_app_version()
    raise RuntimeError("Could not determine __version__ in __init__.py")


def fetch_latest_release_version() -> str:
    """Fetch latest release version from GitHub API."""
    req = Request(GITHUB_RELEASES_API_URL, headers={"User-Agent": APP_NAME})
    with urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        payload = resp.read().decode("utf-8")
    data = json.loads(payload)
    tag = data.get("tag_name") or data.get("name")
    if not tag:
        raise RuntimeError("Could not find tag_name or name in release payload")
    return str(tag).strip().lstrip("v")


def main() -> int:
    """Check version consistency and GitHub release."""
    pyproject_version = read_pyproject_version()
    app_version = read_app_version()
    init_version = read_init_version()

    if pyproject_version != app_version:
        print(
            "Version mismatch: pyproject.toml has "
            f"{pyproject_version}, constants.py has {app_version}"
        )
        return 1

    if app_version != init_version:
        print(
            f"Version mismatch: constants.py has {app_version}, "
            f"__init__.py has {init_version}"
        )
        return 1

    if os.environ.get("SKIP_GITHUB_VERSION_CHECK") == "1":
        print("Skipping GitHub version check (SKIP_GITHUB_VERSION_CHECK=1).")
        return 0

    latest = fetch_latest_release_version()
    if parse_version(app_version) < parse_version(latest):
        print(
            "Version is behind latest GitHub release: "
            f"local {app_version} < latest {latest}"
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
