from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from pycmd.ui import PycmdError


@dataclass(frozen=True)
class Editor:
    label: str
    commands: tuple[str, ...]  # candidate executables, first one found wins
    gui: bool
    args: tuple[str, ...] = (".",)


PRESETS: dict[str, Editor] = {
    "vscode": Editor("Visual Studio Code", ("code", "code-insiders", "codium", "code-oss"), True),
    "sublime": Editor("Sublime Text", ("subl", "sublime_text"), True),
    "zed": Editor("Zed", ("zed", "zeditor"), True),
    "pycharm": Editor("PyCharm", ("pycharm", "pycharm64.exe", "pycharm.sh", "charm"), True),
    "neovim": Editor("Neovim", ("nvim",), False),
    "vim": Editor("Vim", ("vim",), False),
    "nano": Editor("GNU Nano", ("nano",), False, args=()),  # nano cannot open a directory
    "emacs": Editor("GNU Emacs", ("emacs",), False),
}


def _find(editor: Editor) -> str | None:
    return next((p for c in editor.commands if (p := shutil.which(c))), None)


def is_installed(key: str) -> bool:
    return _find(PRESETS[key]) is not None


def _spawn_detached(argv: list[str], cwd: Path | None) -> None:
    kwargs: dict = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(
            subprocess, "CREATE_NO_WINDOW", 0
        )
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(
        argv, cwd=cwd, stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs,
    )


def launch_editor(editor: str, path: Path) -> None:
    """`editor` is a preset key or a custom command line."""
    preset = PRESETS.get(editor)
    if preset:
        exe = _find(preset)
        if exe is None:
            raise PycmdError(
                f"{preset.label} was not found in PATH.",
                hint="Run `pycmd setup editor` to pick another one.",
            )
        argv, gui = [exe, *preset.args], preset.gui
    else:
        parts = shlex.split(editor, posix=os.name != "nt")
        exe = shutil.which(parts[0]) if parts else None
        if exe is None:
            raise PycmdError(
                f"Editor command '{editor}' was not found in PATH.",
                hint="Run `pycmd setup editor` to pick another one.",
            )
        argv, gui = [exe, *parts[1:], "."], False

    if gui:
        _spawn_detached(argv, path)
    else:
        subprocess.run(argv, cwd=path)


def open_folder(path: Path) -> None:
    if sys.platform == "win32":
        os.startfile(path)  # type: ignore[attr-defined]
        return
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    exe = shutil.which(opener)
    if exe is None:
        raise PycmdError(f"`{opener}` was not found in PATH.")
    _spawn_detached([exe, str(path)], None)