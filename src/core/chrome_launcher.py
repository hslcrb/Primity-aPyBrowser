"""공식 Chrome을 독립 프로필로 연결. / Launch installed Chrome in its own profile."""

import os
from pathlib import Path
import shutil
import subprocess
import sys

from src.core.navigation import safe_external_url


def find_chrome():
    """기본 브라우저나 사용자의 기존 프로필은 읽지 않는다. / No profile discovery."""
    candidates = []
    if sys.platform == "win32":
        for key in ("LOCALAPPDATA", "PROGRAMFILES", "PROGRAMFILES(X86)"):
            if os.environ.get(key):
                candidates.append(Path(os.environ[key]) / "Google/Chrome/Application/chrome.exe")
    elif sys.platform == "darwin":
        candidates = [Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
                      Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    else:
        for name in ("google-chrome-stable", "google-chrome"):
            found = shutil.which(name)
            if found:
                candidates.append(Path(found))
    return next((candidate for candidate in candidates if candidate.is_file()), None)


def build_chrome_command(executable: Path, profile_dir: Path, url: str):
    executable, profile_dir = Path(executable), Path(profile_dir)
    if not executable.is_absolute() or not executable.is_file():
        raise FileNotFoundError("설치된 Google Chrome을 찾을 수 없습니다. / Google Chrome was not found.")
    if not profile_dir.is_absolute() or profile_dir.is_symlink():
        raise ValueError("별도의 절대 프로필 경로가 필요합니다. / A dedicated absolute profile path is required.")
    return [str(executable), "--user-data-dir=" + str(profile_dir), "--new-window",
            "--no-first-run", safe_external_url(url)]


def launch_chrome(profile_dir: Path, url: str):
    executable = find_chrome()
    if executable is None:
        raise FileNotFoundError("Google Chrome 설치 후 다시 시도하세요. / Install Google Chrome and try again.")
    command = build_chrome_command(executable, profile_dir, url)
    # 셸을 사용하지 않아 URL이 실행 인자가 될 수 없다. / No shell interpolation.
    return subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, shell=False)

