from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from pycmd.languages import LANGUAGES, Language, find_language
from pycmd.ui import PycmdError, warn

GIT_SUFFIXES = {"git", "github"}


@dataclass(frozen=True)
class Target:
    name: str
    language: Language | None  # None means "the GitHub repo only" (NAME.git)


def languages_hint() -> str:
    return "Supported extensions: " + " ".join(f".{lang.extension}" for lang in LANGUAGES)


def sanitize(stem: str) -> str:
    name = re.sub(r"\W", "_", stem)
    return f"_{name}" if name[0].isdigit() else name


def parse_target(raw: str) -> Target:
    stem, dot, ext = raw.rpartition(".")
    if not dot or not stem:
        raise PycmdError(f"'{raw}' needs a language extension, e.g. {raw}.py", hint=languages_hint())
    name = sanitize(stem)
    ext = ext.lower()
    if ext in GIT_SUFFIXES:
        return Target(name, None)
    lang = find_language(ext)
    if lang is None:
        raise PycmdError(f"Unknown project type '.{ext}'.", hint=languages_hint())
    return Target(name, lang)


def scaffold(path: Path, lang: Language, name: str) -> None:
    files = {**lang.files(name), "README.md": f"# {name}\n"}
    if lang.gitignore:
        files[".gitignore"] = lang.gitignore
    try:
        path.mkdir(parents=True)
        for rel, content in files.items():
            (path / rel).write_text(content, encoding="utf-8", newline="\n")
    except OSError as e:
        raise PycmdError(f"Could not create project: {e}") from e

    for step in lang.post:
        argv = [a.format(name=name) for a in step]
        exe = shutil.which(argv[0])
        if exe is None:
            warn(f"`{argv[0]}` not found in PATH, skipped `{' '.join(argv)}`")
            continue
        proc = subprocess.run(
            [exe, *argv[1:]], cwd=path, capture_output=True,
            text=True, encoding="utf-8", errors="replace",
        )
        if proc.returncode != 0:
            warn(f"`{' '.join(argv)}` failed: {proc.stderr.strip()}")