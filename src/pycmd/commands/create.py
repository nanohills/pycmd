from typing import Annotated

import typer

from pycmd.config import Config
from pycmd.editors import launch_editor
from pycmd.git import push_new_repo, require_git
from pycmd.github import GitHub
from pycmd.projects import languages_hint, parse_target, scaffold
from pycmd.ui import PycmdError, info, ok, out, warn


def create(
    target: Annotated[
        str, typer.Argument(metavar="NAME.EXT", help="Project name plus language, e.g. scraper.py")
    ],
    private: Annotated[bool, typer.Option("--private", "-p", help="Make the GitHub repo private.")] = False,
    local: Annotated[bool, typer.Option("--local", "-l", help="Skip git and GitHub.")] = False,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Do not ask for confirmation.")] = False,
    no_open: Annotated[bool, typer.Option("--no-open", help="Do not open the editor.")] = False,
) -> None:
    """Create a project from a template and push it to a new GitHub repository."""
    cfg = Config.load()
    t = parse_target(target)
    lang = t.language
    if lang is None:
        raise PycmdError("create needs a language extension, not .git.", hint=languages_hint())

    path = cfg.project_root(lang) / t.name
    if path.exists():
        raise PycmdError(f"{path} already exists.")

    if not local:
        require_git()
        with GitHub(cfg.token) as gh:
            gh.user()  # fail before touching the disk if the token is bad

    if not yes:
        where = "" if local else f" with a {'private' if private else 'public'} GitHub repo"
        if not typer.confirm(f"Create {lang.label} project '{t.name}' at {path}{where}?", default=True):
            info("Cancelled.")
            raise typer.Exit()

    scaffold(path, lang, t.name)
    ok(f"Created {path}")

    if not local:
        with GitHub(cfg.token) as gh, out.status("Creating repository...") as status:
            repo = gh.create_repo(t.name, private)
            try:
                push_new_repo(path, repo["clone_url"], cfg.token, status.update)
            except PycmdError:
                warn(f"The repository exists on GitHub: {repo['html_url']}")
                raise
        ok(f"Pushed to {repo['html_url']}")

    if no_open:
        return
    if not cfg.editor:
        warn("No editor configured. Run `pycmd setup editor`.")
        return
    try:
        launch_editor(cfg.editor, path)
    except PycmdError as e:
        warn(e.message)