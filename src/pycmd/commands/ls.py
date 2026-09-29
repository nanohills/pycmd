from typing import Annotated, Optional

import typer
from rich.text import Text

from pycmd.config import Config
from pycmd.github import GitHub
from pycmd.languages import LANGUAGES, Language, find_language
from pycmd.projects import languages_hint
from pycmd.ui import PycmdError, out, warn


def _list_local(cfg: Config, lang: Language) -> None:
    root = cfg.project_root(lang)
    if not root.is_dir():
        warn(f"{lang.label}: {root} does not exist.")
        return
    folders = sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith("."))
    out.print(Text(f"\n{lang.label} ({len(folders)})", style="bold cyan"))
    for p in folders:
        if not any(p.iterdir()):
            style = "bright_black"  # empty
        elif (p / ".git").exists():
            style = "green"  # git repo
        else:
            style = ""
        out.print(Text("  " + p.name, style=style))


def _list_repos(cfg: Config) -> None:
    with GitHub(cfg.token) as gh, out.status("Fetching repositories..."):
        repos = gh.list_repos()
    out.print(Text(f"\nGitHub ({len(repos)})", style="bold cyan"))
    for r in repos:
        private = r["private"]
        label = r["name"] + (" (private)" if private else "")
        out.print(Text("  " + label, style="bright_black" if private else ""))


def ls(
    language: Annotated[
        Optional[str],
        typer.Argument(help="py, js, rs, ... or 'git' for GitHub repos. Omit to list every language."),
    ] = None,
) -> None:
    """List projects."""
    cfg = Config.load()
    if language and language.lower() in {"git", "github", "repos"}:
        _list_repos(cfg)
        return
    if language:
        lang = find_language(language)
        if lang is None:
            raise PycmdError(f"Unknown language '{language}'.", hint=languages_hint())
        langs = [lang]
    else:
        langs = [lang for lang in LANGUAGES if lang.key in cfg.projects]
        if not langs:
            raise PycmdError("No project folders configured.", hint="Run `pycmd setup projects`.")
    for lang in langs:
        _list_local(cfg, lang)
    out.print()