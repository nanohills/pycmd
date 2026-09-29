from __future__ import annotations

import difflib
import sys
from typing import Annotated

import typer

from pycmd import __version__
from pycmd.commands.create import create
from pycmd.commands.ls import ls
from pycmd.commands.open import open_project
from pycmd.commands.rm import rm
from pycmd.commands.setup import setup_app
from pycmd.commands.src import src
from pycmd.ui import PycmdError

COMMANDS = ["create", "ls", "open", "rm", "src", "setup"]


def _version(value: bool) -> None:
    if value:
        typer.echo(f"pycmd {__version__}")
        raise typer.Exit()


app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_enable=False,
    help="Create and manage projects and their GitHub repositories.",
)


@app.callback()
def _root(
    version: Annotated[
        bool, typer.Option("--version", callback=_version, is_eager=True, help="Show version.")
    ] = False,
) -> None:
    pass


app.command("create")(create)
app.command("ls")(ls)
app.command("open")(open_project)
app.command("rm")(rm)
app.command("src")(src)
app.add_typer(setup_app, name="setup")


def _suggest() -> None:
    """`pycmd lss` -> "Did you mean 'ls'?" Runs before Typer parses anything."""
    args = sys.argv[1:]
    if not args or args[0].startswith("-") or args[0] in COMMANDS:
        return
    hits = difflib.get_close_matches(args[0], COMMANDS, n=1, cutoff=0.4)
    if hits:
        raise PycmdError(f"Unknown command '{args[0]}'.", hint=f"Did you mean '{hits[0]}'?")


def main() -> None:
    try:
        _suggest()
        app()
    except PycmdError as e:
        e.show()
        sys.exit(1)