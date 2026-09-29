from pathlib import Path
from typing import Annotated

import typer

from pycmd.config import Config
from pycmd.editors import launch_editor, open_folder
from pycmd.ui import PycmdError, ok


def src(
    explorer: Annotated[
        bool, typer.Option("--explorer", "-e", help="Open in the system file manager.")
    ] = False,
) -> None:
    """Open pycmd's own source code."""
    path = Path(__file__).resolve().parent.parent
    if explorer:
        open_folder(path)
    else:
        cfg = Config.load()
        if not cfg.editor:
            raise PycmdError("No editor configured.", hint="Run `pycmd setup editor`.")
        launch_editor(cfg.editor, path)
    ok(f"Opened {path}")