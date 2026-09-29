from typing import Annotated

import typer

from pycmd.config import Config
from pycmd.editors import launch_editor, open_folder
from pycmd.projects import languages_hint, parse_target
from pycmd.ui import PycmdError, ok


def open_project(
    target: Annotated[str, typer.Argument(metavar="NAME.EXT", help="e.g. scraper.py")],
    explorer: Annotated[
        bool, typer.Option("--explorer", "-e", help="Open in the system file manager.")
    ] = False,
) -> None:
    """Open a project in your editor."""
    cfg = Config.load()
    t = parse_target(target)
    if t.language is None:
        raise PycmdError("open needs a language extension, not .git.", hint=languages_hint())
    path = cfg.project_root(t.language) / t.name
    if not path.is_dir():
        raise PycmdError(f"Project not found: {path}")

    if explorer:
        open_folder(path)
        ok(f"Opened {t.name} in the file manager")
        return
    if not cfg.editor:
        raise PycmdError("No editor configured.", hint="Run `pycmd setup editor`.")
    launch_editor(cfg.editor, path)
    ok(f"Opened {t.name}")