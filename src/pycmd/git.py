from __future__ import annotations

import base64
import os
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path

from pycmd.ui import PycmdError


def require_git() -> str:
    exe = shutil.which("git")
    if exe is None:
        raise PycmdError("git was not found in PATH.", hint="Install git, or pass --local.")
    return exe


def _auth_env(token: str) -> dict[str, str]:
    """One-shot auth header via env vars: never in argv, .git/config or a credential helper."""
    env = os.environ.copy()
    basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
    n = int(env.get("GIT_CONFIG_COUNT") or 0)  # append, keep the user's own GIT_CONFIG_*
    env["GIT_CONFIG_COUNT"] = str(n + 1)
    env[f"GIT_CONFIG_KEY_{n}"] = "http.https://github.com/.extraheader"
    env[f"GIT_CONFIG_VALUE_{n}"] = f"AUTHORIZATION: basic {basic}"
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env


def _run(exe: str, args: list[str], cwd: Path, env: dict[str, str] | None = None) -> None:
    proc = subprocess.run(
        [exe, *args], cwd=cwd, env=env, capture_output=True,
        text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        raise PycmdError(f"`git {' '.join(args)}` failed:\n{proc.stderr.strip()}")


def push_new_repo(
    path: Path, remote_url: str, token: str, on_step: Callable[[str], None] = lambda _s: None
) -> None:
    exe = require_git()
    steps: list[tuple[str, list[str], bool]] = [
        ("Initializing git", ["init", "-b", "main"], False),
        ("Connecting to remote", ["remote", "add", "origin", remote_url], False),
        ("Adding files", ["add", "-A"], False),
        ("Committing", ["commit", "-m", "Initial commit"], False),
        ("Pushing to GitHub", ["push", "-u", "origin", "main"], True),
    ]
    for label, args, needs_token in steps:
        on_step(label)
        _run(exe, args, path, _auth_env(token) if needs_token else None)