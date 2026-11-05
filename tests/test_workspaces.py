import json
from pathlib import Path

import pytest

from src.core.workspaces import WorkspaceError, WorkspaceStore


def test_workspace_ids_separate_storage_and_survive_rename(tmp_path):
    store = WorkspaceStore(tmp_path)
    a = store.create("디자인 A")
    b = store.create("디자인 B")
    before = store.path(a.id, "qt")
    assert before != store.path(b.id, "qt")
    assert store.path(a.id, "cache") != before
    assert store.path(a.id, "chrome") != before
    store.rename(a.id, "작업용")
    store.set_active(a.id)
    reopened = WorkspaceStore(tmp_path)
    assert reopened.get(a.id).name == "작업용"
    assert reopened.active_id == a.id
    assert reopened.path(a.id, "qt") == before


@pytest.mark.parametrize("name", ["", "  ", "a" * 41, "bad\nname", "bad\x00name"])
def test_invalid_names_do_not_mutate_catalog(tmp_path, name):
    store = WorkspaceStore(tmp_path)
    before = store.catalog_path.read_bytes()
    with pytest.raises(WorkspaceError):
        store.create(name)
    assert store.catalog_path.read_bytes() == before


def test_duplicate_names_are_rejected(tmp_path):
    store = WorkspaceStore(tmp_path)
    store.create("Design")
    with pytest.raises(WorkspaceError):
        store.create(" design ")


def test_corrupt_catalog_is_preserved(tmp_path):
    path = tmp_path / "workspaces.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(WorkspaceError):
        WorkspaceStore(tmp_path)
    assert path.read_text(encoding="utf-8") == "{not json"


@pytest.mark.parametrize("bad_id", ["../outside", "/tmp/outside", "../../x", "a/b", "a\\b"])
def test_untrusted_ids_cannot_escape_root(tmp_path, bad_id):
    store = WorkspaceStore(tmp_path)
    with pytest.raises(WorkspaceError):
        store.path(bad_id, "qt")


def test_catalog_with_duplicate_ids_is_not_silently_loaded(tmp_path):
    store = WorkspaceStore(tmp_path)
    payload = json.loads(store.catalog_path.read_text())
    payload["workspaces"].append(dict(payload["workspaces"][0]))
    store.catalog_path.write_text(json.dumps(payload))
    with pytest.raises(WorkspaceError):
        WorkspaceStore(tmp_path)


def test_symlinked_profile_cannot_point_to_other_workspace(tmp_path):
    store = WorkspaceStore(tmp_path)
    a, b = store.create("A"), store.create("B")
    actual = store.path(b.id, "qt")
    (tmp_path / "workspaces" / a.id).mkdir(parents=True, exist_ok=True)
    (tmp_path / "workspaces" / a.id / "qt").symlink_to(actual, target_is_directory=True)
    with pytest.raises(WorkspaceError):
        store.path(a.id, "qt")


def test_bookmarks_and_preferences_remain_in_workspace(tmp_path):
    store = WorkspaceStore(tmp_path)
    a, b = store.create("A"), store.create("B")
    store.save_bookmarks(a.id, [{"title": "작업", "url": "https://www.figma.com/"}])
    store.save_preferences(a.id, theme="light", language="en")
    reopened = WorkspaceStore(tmp_path)
    assert reopened.bookmarks(b.id) == []
    assert reopened.preferences(b.id) == {"theme": "dark", "language": "ko"}
    assert reopened.bookmarks(a.id)[0]["title"] == "작업"
    assert reopened.preferences(a.id) == {"theme": "light", "language": "en"}


def test_invalid_import_is_all_or_nothing(tmp_path):
    store = WorkspaceStore(tmp_path)
    ident = store.active_id
    original = [{"title": "Safe", "url": "https://example.com/"}]
    store.save_bookmarks(ident, original)
    with pytest.raises(WorkspaceError):
        store.import_bookmarks(ident, {"bookmarks": [
            {"title": "Good", "url": "https://good.example/"},
            {"title": "Bad", "url": "javascript:alert(1)"},
        ]})
    assert store.bookmarks(ident) == original


def test_explicit_legacy_bookmark_import_excludes_passwords_and_settings(tmp_path):
    store = WorkspaceStore(tmp_path)
    ident = store.active_id
    store.import_bookmarks(ident, {"bookmarks": {"Work": {"Figma": "https://figma.com/"}},
                                   "settings": {"password": "must-not-copy"}})
    exported = store.export_bookmarks(ident)
    assert exported == {"version": 1, "bookmarks": [{"title": "Figma", "url": "https://figma.com/"}]}
    assert "must-not-copy" not in json.dumps(exported)


def test_failed_atomic_replace_preserves_previous_catalog(tmp_path, monkeypatch):
    store = WorkspaceStore(tmp_path)
    before = store.catalog_path.read_bytes()
    def fail(*args):
        raise OSError("disk full")
    monkeypatch.setattr("src.core.workspaces.os.replace", fail)
    with pytest.raises(WorkspaceError):
        store.create("Cannot save")
    assert store.catalog_path.read_bytes() == before
    assert len(store.list()) == 1

