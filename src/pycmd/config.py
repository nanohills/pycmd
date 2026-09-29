from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

from platformdirs import user_config_path

from pycmd.languages import Language
from pycmd.ui import PycmdError


def config_path() -> Path:
    override = os.environ.get("PYCMD_CONFIG")
    if override:
        return Path(override)
    return user_config_path("pycmd", appauthor=False) / "config.json"


@dataclass
class Config:
    editor: str = ""
    projects: dict[str, str] = field(default_factory=dict)
    github_token: str = ""

    @property
    def token(self) -> str:
        return os.environ.get("GITHUB_TOKEN") or self.github_token

    def project_root(self, lang: Language) -> Path:
        raw = self.projects.get(lang.key)
        if not raw:
            raise PycmdError(
                f"No projects folder set for {lang.label}.",
                hint="Run `pycmd setup projects`.",
            )
        return Path(raw).expanduser()

    @classmethod
    def load(cls) -> Config:
        path = config_path()
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            raise PycmdError(f"Could not read {path}: {e}") from e
        return cls(
            editor=data.get("editor", ""),
            projects=dict(data.get("projects", {})),
            github_token=data.get("github_token", ""),
        )

    def save(self) -> None:
        path = config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        # 0600 from creation, so the token is never briefly world-readable (ignored on Windows)
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)
        os.replace(tmp, path)