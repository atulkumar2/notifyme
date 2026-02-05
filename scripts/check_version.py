import json
import os
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
PYPROJECT_PATH = ROOT / "pyproject.toml"
APP_MODULE_PATH = ROOT / "notifyme_app" / "constants.py"
GITHUB_RELEASES_API_URL = (
    "https://api.github.com/repos/atulkumar2/notifyme/releases/latest"
)
TIMEOUT_SECONDS = 5


def parse_version(value: str) -> tuple[int, int, int]:
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
    content = PYPROJECT_PATH.read_text(encoding="utf-8")
    match = re.search(r'^\s*version\s*=\s*"(.*?)"\s*$', content, re.MULTILINE)
    if not match:
        raise RuntimeError("Could not find version in pyproject.toml")
    return match.group(1).strip()


def read_app_version() -> str:
    content = APP_MODULE_PATH.read_text(encoding="utf-8")
    match = re.search(r'^\s*APP_VERSION\s*=\s*"(.*?)"\s*$', content, re.MULTILINE)
    if not match:
        raise RuntimeError("Could not find APP_VERSION in constants.py")
    return match.group(1).strip()


def fetch_latest_release_version() -> str:
    req = Request(GITHUB_RELEASES_API_URL, headers={"User-Agent": "NotifyMe"})
    with urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        payload = resp.read().decode("utf-8")
    data = json.loads(payload)
    tag = data.get("tag_name") or data.get("name")
    if not tag:
        raise RuntimeError("Could not find tag_name or name in release payload")
    return str(tag).strip().lstrip("v")


def main() -> int:
    pyproject_version = read_pyproject_version()
    app_version = read_app_version()

    if pyproject_version != app_version:
        print(
            "Version mismatch: pyproject.toml has "
            f"{pyproject_version}, constants.py has {app_version}"
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
