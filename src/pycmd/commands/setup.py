import shutil
from pathlib import Path

import typer
from rich.text import Text

from pycmd.config import Config, config_path
from pycmd.editors import PRESETS, is_installed
from pycmd.github import GitHub
from pycmd.languages import LANGUAGES, Language, find_language
from pycmd.ui import info, ok, out, warn

setup_app = typer.Typer(
    help="Configure pycmd. Run without a subcommand for the full wizard.",
    invoke_without_command=True,
)


def _ask_languages() -> list[Language]:
    out.print("Which languages do you work with?")
    for i, lang in enumerate(LANGUAGES, 1):
        out.print(Text(f"  {i}. {lang.label}"))
    while True:
        raw = typer.prompt("Numbers or names, comma-separated (e.g. 1,4 or py,rs)")
        picked: list[Language] = []
        bad: list[str] = []
        for tok in (t.strip() for t in raw.split(",") if t.strip()):
            if tok.isdigit() and 1 <= int(tok) <= len(LANGUAGES):
                lang = LANGUAGES[int(tok) - 1]
            else:
                lang = find_language(tok)
            if lang is None:
                bad.append(tok)
            elif lang not in picked:
                picked.append(lang)
        if bad:
            warn(f"Unknown: {', '.join(bad)}")
        elif picked:
            return picked


def configure_projects(cfg: Config) -> None:
    chosen = _ask_languages()
    root = Path(
        typer.prompt("Root folder for all projects", default=str(Path.home() / "Projects"))
    ).expanduser()
    custom = typer.confirm("Choose a separate folder per language?", default=False)
    for lang in chosen:
        default = root / lang.key
        path = (
            Path(typer.prompt(f"{lang.label} projects folder", default=str(default))).expanduser()
            if custom
            else default
        )
        path.mkdir(parents=True, exist_ok=True)
        cfg.projects[lang.key] = str(path.resolve())
        ok(f"{lang.label}: {path.resolve()}")
    cfg.save()


def configure_editor(cfg: Config) -> None:
    keys = list(PRESETS)
    out.print("Which editor should projects open in?")
    for i, key in enumerate(keys, 1):
        mark = " (found)" if is_installed(key) else ""
        out.print(Text(f"  {i}. {PRESETS[key].label}{mark}"))
    other = len(keys) + 1
    out.print(Text(f"  {other}. Other (custom command)"))
    default = next((i for i, k in enumerate(keys, 1) if is_installed(k)), 1)
    while True:
        n = typer.prompt("Choose", type=int, default=default)
        if 1 <= n <= other:
            break
        warn(f"Enter a number from 1 to {other}.")
    if n == other:
        cmd = typer.prompt("Command that opens a folder, e.g. hx or 'emacs -nw'").strip()
        if not shutil.which(cmd.split()[0]):
            warn(f"`{cmd.split()[0]}` is not in PATH right now.")
        cfg.editor = cmd
    else:
        cfg.editor = keys[n - 1]
    cfg.save()
    ok(f"Editor: {cfg.editor}")


def configure_git(cfg: Config) -> None:
    out.print("Create a classic token at https://github.com/settings/tokens/new")
    out.print("with the scopes: repo, delete_repo. Or export GITHUB_TOKEN instead.")
    token = typer.prompt("GitHub token (input hidden)", hide_input=True).strip()
    with GitHub(token) as gh:
        login = gh.user()["login"]
    cfg.github_token = token
    cfg.save()
    ok(f"Authenticated as {login}")


@setup_app.callback()
def wizard(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is not None:
        return
    cfg = Config.load()
    configure_projects(cfg)
    configure_editor(cfg)
    configure_git(cfg)
    ok("Setup complete.")


@setup_app.command("projects")
def projects_cmd() -> None:
    """Choose languages and project folders."""
    configure_projects(Config.load())


@setup_app.command("editor")
def editor_cmd() -> None:
    """Choose the editor."""
    configure_editor(Config.load())


@setup_app.command("git")
def git_cmd() -> None:
    """Store a GitHub token."""
    configure_git(Config.load())


@setup_app.command("show")
def show_cmd() -> None:
    """Print the current configuration (token hidden)."""
    cfg = Config.load()
    info(f"Config file: {config_path()}")
    out.print(Text(f"editor: {cfg.editor or '(not set)'}"))
    out.print(Text(f"github token: {'set' if cfg.token else '(not set)'}"))
    for key, path in cfg.projects.items():
        out.print(Text(f"{key}: {path}"))