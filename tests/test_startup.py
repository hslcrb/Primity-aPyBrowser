from pathlib import Path

import pytest

from main import acquire_instance_lock, parse_arguments


def test_startup_rejects_security_disabling_flags():
    with pytest.raises(SystemExit):
        parse_arguments(["--no-sandbox"])
    with pytest.raises(SystemExit):
        parse_arguments(["--disable-web-security"])


def test_startup_accepts_explicit_data_directory_and_urls(tmp_path):
    args = parse_arguments(["--data-dir", str(tmp_path), "https://figma.com/", "https://github.com/"])
    assert args.data_dir == Path(tmp_path)
    assert args.urls == ["https://figma.com/", "https://github.com/"]


def test_one_process_owns_the_profile_directory(tmp_path):
    first = acquire_instance_lock(tmp_path)
    try:
        with pytest.raises(RuntimeError):
            acquire_instance_lock(tmp_path)
    finally:
        first.unlock()
    second = acquire_instance_lock(tmp_path)
    second.unlock()

