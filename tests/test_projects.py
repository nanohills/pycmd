import pytest
import sys

from pycmd.projects import parse_target
from pycmd.ui import PycmdError


@pytest.mark.parametrize(
    "raw,name,lang",
    [
        ("scraper.py", "scraper", "python"),
        ("my-app.rs", "my_app", "rust"),
        ("2048.js", "_2048", "javascript"),
        ("site.css", "site", "web"),
        ("game.cs", "game", "csharp"),
        ("a.b.go", "a_b", "go"),
    ],
)
def test_parse(raw, name, lang):
    t = parse_target(raw)
    assert t.name == name
    assert t.language.key == lang


def test_git_suffix_means_remote_only():
    assert parse_target("x.git").language is None


@pytest.mark.parametrize("raw", ["noext", "x.unknown", ".py"])
def test_bad_targets(raw):
    with pytest.raises(PycmdError):
        parse_target(raw)