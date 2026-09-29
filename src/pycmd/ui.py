from __future__ import annotations

from rich.console import Console
from rich.text import Text

out = Console()
err = Console(stderr=True)


def _line(console: Console, tag: str, style: str, msg: str) -> None:
    # Text() is not parsed for markup, so paths containing [brackets] print verbatim.
    console.print(Text(f"{tag} ", style=style) + Text(msg), soft_wrap=True)


def info(msg: str) -> None:
    _line(out, "INFO", "bold blue", msg)


def ok(msg: str) -> None:
    _line(out, "OK", "bold green", msg)


def warn(msg: str) -> None:
    _line(err, "WARN", "bold yellow", msg)


class PycmdError(Exception):
    """Expected failure. main() prints it and exits with code 1."""

    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint

    def show(self) -> None:
        _line(err, "ERR", "bold red", self.message)
        if self.hint:
            _line(err, "INFO", "bold blue", self.hint)