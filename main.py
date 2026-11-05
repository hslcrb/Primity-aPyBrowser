"""Primity 0.3.0 — 독립된 계정 작업공간. / Isolated account workspaces."""

import argparse
from pathlib import Path
import sys

VERSION = "0.3.0"


def parse_arguments(argv=None):
    parser = argparse.ArgumentParser(description="Primity · isolated Chromium workspaces")
    parser.add_argument("--version", action="version", version="Primity " + VERSION)
    parser.add_argument("--data-dir", type=Path, help="Use a dedicated application data directory")
    parser.add_argument("--workspace", help="Open a stored workspace ID")
    parser.add_argument("urls", nargs="*", help="HTTP(S) addresses or search terms")
    return parser.parse_args(argv)


def acquire_instance_lock(root):
    from PySide6.QtCore import QLockFile
    root = Path(root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = QLockFile(str(root / "instance.lock"))
    lock.setStaleLockTime(0)
    if not lock.tryLock(0):
        raise RuntimeError("같은 데이터 폴더를 사용하는 Primity가 이미 실행 중이거나 잠금을 만들 수 없습니다.\n"
                           "Primity is already running with this data directory, or its lock cannot be created.")
    return lock


def main(argv=None):
    args = parse_arguments(argv)
    from PySide6.QtCore import QStandardPaths
    from PySide6.QtWidgets import QApplication
    from src.core.browser import BrowserController
    from src.core.navigation import address_to_url
    from src.core.workspaces import WorkspaceStore, WorkspaceError
    from src.ui.dialogs import inform

    # Chromium 보안 플래그와 사용자 에이전트를 재정의하지 않는다.
    # Keep Chromium's security configuration and honest default user agent.
    app = QApplication([sys.argv[0]])
    app.setOrganizationName("Primity")
    app.setApplicationName("Primity")
    app.setApplicationVersion(VERSION)
    root = args.data_dir or Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation))
    controller, lock = None, None
    try:
        urls = [address_to_url(value) for value in args.urls]
        lock = acquire_instance_lock(root)
        controller = BrowserController(WorkspaceStore(root), app)
        window = controller.open_workspace(args.workspace)
        for url in urls:
            window.add_new_tab(url)
        app.aboutToQuit.connect(controller.shutdown)
        return app.exec()
    except (WorkspaceError, OSError, RuntimeError, ValueError) as error:
        inform(None, "Primity", str(error), error=True)
        return 1
    finally:
        if controller is not None:
            controller.shutdown()
        if lock is not None:
            lock.unlock()


if __name__ == "__main__":
    raise SystemExit(main())

