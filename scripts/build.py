"""수동 onedir 패키징. / Manual onedir packaging without GitHub Actions."""

from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
               "--onedir", "--windowed", "--name", "Primity",
               "--add-data", str(root / "assets") + ":assets",
               "--add-data", str(root / "LICENSE") + ":.",
               "--add-data", str(root / "NOTICE") + ":.", str(root / "main.py")]
    subprocess.run(command, cwd=root, check=True)
    print("Built for this operating system: " + str(root / "dist/Primity"))


if __name__ == "__main__":
    main()
