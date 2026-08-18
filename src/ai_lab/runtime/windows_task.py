from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class WindowsActionResult:
    changed: bool
    target: str
    verified: bool
    detail: str


def execute_open_youtube() -> WindowsActionResult:
    """Open YouTube using the Windows URL handler, then verify a browser exists."""
    subprocess.run(
        ["cmd", "/c", "start", "", "https://www.youtube.com/"],
        check=True,
        shell=False,
    )
    time.sleep(2.0)
    probe = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "@(Get-Process chrome,msedge,firefox -ErrorAction SilentlyContinue).Count",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        browser_count = int((probe.stdout or "0").strip().splitlines()[-1])
    except (ValueError, IndexError):
        browser_count = 0
    return WindowsActionResult(
        changed=True,
        target="https://www.youtube.com/",
        verified=browser_count > 0,
        detail=f"browser_process_count={browser_count}",
    )
