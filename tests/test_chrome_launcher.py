from pathlib import Path

import pytest

from src.core.chrome_launcher import build_chrome_command, find_chrome


def test_chrome_arguments_use_only_a_dedicated_directory(tmp_path):
    executable = tmp_path / "Google Chrome" / "chrome"
    executable.parent.mkdir()
    executable.touch()
    directory = tmp_path / "한글 작업공간" / "chrome"
    command = build_chrome_command(executable, directory, "https://figma.com/?q=--no-sandbox")
    assert command == [str(executable), "--user-data-dir=" + str(directory),
                       "--new-window", "--no-first-run", "https://figma.com/?q=--no-sandbox"]
    assert "--no-sandbox" not in command
    assert not any(value.startswith("--remote-debugging") for value in command)


@pytest.mark.parametrize("url", ["--user-data-dir=/other", "file:///tmp/x", "javascript:alert(1)", "chrome://flags"])
def test_unsafe_urls_never_enter_chrome_command(tmp_path, url):
    executable = tmp_path / "chrome"
    executable.touch()
    with pytest.raises(ValueError):
        build_chrome_command(executable, tmp_path / "profile", url)


def test_missing_browser_gives_actionable_failure(tmp_path):
    with pytest.raises(FileNotFoundError):
        build_chrome_command(tmp_path / "missing", tmp_path / "profile", "https://figma.com/")


def test_profile_path_must_be_absolute(tmp_path):
    executable = tmp_path / "chrome"
    executable.touch()
    with pytest.raises(ValueError):
        build_chrome_command(executable, Path("Default"), "https://figma.com/")


def test_linux_detection_does_not_fallback_to_default_browser(monkeypatch):
    monkeypatch.setattr("src.core.chrome_launcher.sys.platform", "linux")
    monkeypatch.setattr("src.core.chrome_launcher.shutil.which", lambda _: None)
    assert find_chrome() is None

