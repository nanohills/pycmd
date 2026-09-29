# PYCMD

Create, open, list and delete projects, and their GitHub repos, from one command.
Works on Windows, Linux and macOS.

## Install

```bash
uv tool install pycmd-cli
uv tool upgrade pycmd-cli
uvx --from pycmd-cli pycmd --help   # run without installing
```

Requires Python 3.10+ and git 2.31+. `npm`, `cargo` and `go` are used when present for
Node.js, Rust and Go projects.

## Quick start

```bash
pycmd setup
pycmd create scraper.py
```

`setup` asks for your languages and folders, your editor, and a GitHub classic token
(scopes `repo` and `delete_repo`). Run one step alone with `pycmd setup projects|editor|git`.
`GITHUB_TOKEN` in the environment overrides the stored token. `pycmd setup show` prints the
config path and values.

## Commands

| Command | What it does |
|---|---|
| `pycmd create NAME.EXT [-p] [-l] [-y] [--no-open]` | Scaffold, create the GitHub repo, push, open the editor |
| `pycmd ls [LANG\|git]` | List local projects, or GitHub repos |
| `pycmd open NAME.EXT [-e]` | Open in the editor, or with `-e` in the file manager |
| `pycmd rm NAME.EXT [-r] [-y]` | Delete locally, add `-r` to delete the GitHub repo too |
| `pycmd rm NAME.git` | Delete only the GitHub repo |
| `pycmd setup [projects\|editor\|git\|show]` | Configure |
| `pycmd src [-e]` | Open pycmd's own source |

Use `pycmd COMMAND --help` for details.

## Project types

| Extension | Language | Files |
|---|---|---|
| `.py` | Python | `main.py` |
| `.js` `.nodejs` | JavaScript | `index.js`, `npm init -y` |
| `.ts` | TypeScript | `main.ts` |
| `.java` | Java | `Main.java` |
| `.html` `.css` `.web` | Web | `index.html`, `index.js`, `style.css` |
| `.rs` | Rust | `cargo init` |
| `.cpp` `.c++` | C++ | `main.cpp` |
| `.go` | Go | `main.go`, `go mod init` |
| `.cs` | C# | `Program.cs` |

Every project also gets a `README.md` and a `.gitignore` where it makes sense. Names are
sanitized: non-word characters become `_`, a leading digit gets a `_` prefix.

## Config location

| OS | Path |
|---|---|
| Linux | `~/.config/pycmd/config.json` |
| macOS | `~/Library/Application Support/pycmd/config.json` |
| Windows | `%LOCALAPPDATA%\pycmd\config.json` |

Override with the `PYCMD_CONFIG` environment variable.

## Development

```bash
uv sync
uv run pycmd --help
uv run pytest
uv build
```

Release: bump `version` in `pyproject.toml`, then `git tag v2.0.0 && git push --tags`.