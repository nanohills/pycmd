import os
import shutil
import stat
import sys
from pathlib import Path
from typing import Annotated

import typer

from pycmd.config import Config
from pycmd.github import GitHub, GitHubError
from pycmd.projects import parse_target
from pycmd.ui import PycmdError, info, ok


def _force_remove(func, path, _exc) -> None:
    # git object files are read-only on Windows; clear the flag and retry
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _delete_local(path: Path) -> None:
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=_force_remove)
    else:
        shutil.rmtree(path, onerror=_force_remove)


def rm(
    target: Annotated[
        str, typer.Argument(metavar="NAME.EXT", help="scraper.py = local project, scraper.git = GitHub repo only")
    ],
    remote: Annotated[
        bool, typer.Option("--remote", "-r", help="Also delete the GitHub repository.")
    ] = False,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Do not ask for confirmation.")] = False,
) -> None:
    """Delete a project locally. The GitHub repo is only touched with --remote or NAME.git."""
    cfg = Config.load()
    t = parse_target(target)

    local_path: Path | None = None
    if t.language is not None:
        candidate = cfg.project_root(t.language).resolve() / t.name
        if candidate.is_symlink() or not candidate.is_dir():
            raise PycmdError(f"Project not found: {candidate}")
        local_path = candidate

    remote_slug: str | None = None
    if remote or t.language is None:
        with GitHub(cfg.token) as gh:
            remote_slug = f"{gh.user()['login']}/{t.name}"  # also validates the token up front

    if local_path and not (yes or typer.confirm(f"Delete {local_path} and everything in it?", default=False)):
        info("Cancelled.")
        raise typer.Exit()
    if remote_slug and not (
        yes or typer.confirm(f"Delete GitHub repository {remote_slug}? This cannot be undone.", default=False)
    ):
        info("Keeping the GitHub repository.")
        remote_slug = None

    if local_path:
        try:
            _delete_local(local_path)
        except OSError as e:
            raise PycmdError(f"Could not delete {local_path}: {e}") from e
        ok(f"Deleted {local_path}")

    if remote_slug:
        owner, name = remote_slug.split("/", 1)
        with GitHub(cfg.token) as gh:
            try:
                gh.delete_repo(owner, name)
            except GitHubError as e:
                if e.status == 404:
                    raise PycmdError(f"Repository {remote_slug} not found.") from e
                raise
        ok(f"Deleted {remote_slug} from GitHub")