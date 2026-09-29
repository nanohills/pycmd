import pytest
import sys
from typer.testing import CliRunner

from pycmd.cli import app
from pycmd.config import Config

runner = CliRunner()


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("PYCMD_CONFIG", str(tmp_path / "cfg.json"))
    Config(projects={"python": str(tmp_path / "py")}).save()
    return tmp_path


def test_create_local(home):
    r = runner.invoke(app, ["create", "demo.py", "-l", "-y", "--no-open"])
    assert r.exit_code == 0, r.output
    assert (home / "py" / "demo" / "main.py").exists()
    assert (home / "py" / "demo" / "README.md").read_text() == "# demo\n"


def test_create_twice_fails(home):
    runner.invoke(app, ["create", "demo.py", "-l", "-y", "--no-open"])
    r = runner.invoke(app, ["create", "demo.py", "-l", "-y", "--no-open"])
    assert r.exit_code == 1


def test_rm_local(home):
    runner.invoke(app, ["create", "demo.py", "-l", "-y", "--no-open"])
    r = runner.invoke(app, ["rm", "demo.py", "-y"])
    assert r.exit_code == 0, r.output
    assert not (home / "py" / "demo").exists()


def test_did_you_mean(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["pycmd", "lss"])
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1
    assert "ls" in capsys.readouterr().err