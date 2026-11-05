"""프로필 메타데이터와 명시적 북마크 저장. / Workspace metadata and bookmarks."""

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import tempfile
import unicodedata
from uuid import uuid4

from src.core.navigation import is_web_url

MAX_WORKSPACES = 32
MAX_BOOKMARKS = 5000
MAX_JSON_BYTES = 2 * 1024 * 1024
ID_PATTERN = re.compile(r"(?:default|[0-9a-f]{32})\Z")


class WorkspaceError(ValueError):
    """저장소 오류를 사용자에게 알린다. / Report storage errors without data loss."""


@dataclass(frozen=True)
class Workspace:
    id: str
    name: str


def _name(value):
    if not isinstance(value, str) or any(unicodedata.category(c).startswith("C") for c in value):
        raise WorkspaceError("작업공간 이름에 제어 문자를 사용할 수 없습니다.")
    value = value.strip()
    if not 1 <= len(value) <= 40:
        raise WorkspaceError("작업공간 이름은 1~40자로 입력하세요.")
    return value


def _read_json(path, default):
    if not path.exists():
        return default
    try:
        if path.stat().st_size > MAX_JSON_BYTES:
            raise ValueError("file is too large")
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as error:
        raise WorkspaceError(f"설정 파일을 읽을 수 없습니다. 원본을 보존했습니다: {path.name}") from error


def _atomic_json(path, value):
    """완성된 파일만 교체한다. / Replace only a fully written file."""
    temporary = None
    try:
        descriptor, temporary = tempfile.mkstemp(prefix=".primity-", dir=path.parent)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except OSError as error:
        raise WorkspaceError("저장하지 못했습니다. 기존 데이터는 유지됩니다.") from error
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def validate_bookmarks(items):
    if not isinstance(items, list) or len(items) > MAX_BOOKMARKS:
        raise WorkspaceError("북마크 형식 또는 개수가 올바르지 않습니다.")
    result, seen = [], set()
    for item in items:
        if not isinstance(item, dict):
            raise WorkspaceError("북마크 항목이 올바르지 않습니다.")
        title, url = item.get("title"), item.get("url")
        if (not isinstance(title, str) or not 1 <= len(title.strip()) <= 256
                or any(ord(c) < 32 for c in title) or not is_web_url(url)):
            raise WorkspaceError("북마크 제목과 HTTP/HTTPS 주소를 확인하세요.")
        if url not in seen:
            seen.add(url)
            result.append({"title": title.strip(), "url": url})
    return result


class WorkspaceStore:
    """ID는 불변, 표시명은 변경 가능. / Stable IDs keep renamed profiles intact."""

    def __init__(self, root: Path):
        self.root = Path(root).expanduser().resolve()
        try:
            self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        except OSError as error:
            raise WorkspaceError("앱 데이터 폴더를 만들 수 없습니다.") from error
        self.catalog_path = self._safe_path("workspaces.json")
        initial = {"version": 1, "active_id": "default", "workspaces": [
            {"id": "default", "name": "기본 작업공간"}]}
        catalog = _read_json(self.catalog_path, initial)
        self._validate_catalog(catalog)
        if not self.catalog_path.exists():
            _atomic_json(self.catalog_path, catalog)
        self._catalog = catalog

    def _safe_path(self, *parts):
        path = self.root
        for part in parts:
            path = path / part
            if path.is_symlink():
                raise WorkspaceError("다른 폴더로 연결된 프로필 경로는 사용할 수 없습니다.")
        try:
            path.resolve().relative_to(self.root)
        except ValueError as error:
            raise WorkspaceError("프로필 경로가 앱 데이터 폴더를 벗어났습니다.") from error
        return path

    def _validate_catalog(self, data):
        if not isinstance(data, dict) or type(data.get("version")) is not int or data["version"] != 1:
            raise WorkspaceError("지원하지 않는 작업공간 설정입니다. 파일을 보존했습니다.")
        items = data.get("workspaces")
        if not isinstance(items, list) or not 1 <= len(items) <= MAX_WORKSPACES:
            raise WorkspaceError("작업공간 목록이 올바르지 않습니다.")
        ids, names = set(), set()
        for item in items:
            if (not isinstance(item, dict) or not isinstance(item.get("id"), str)
                    or not ID_PATTERN.fullmatch(item["id"])):
                raise WorkspaceError("작업공간 ID가 올바르지 않습니다.")
            name = _name(item.get("name"))
            if item["id"] in ids or name.casefold() in names:
                raise WorkspaceError("중복 작업공간이 있습니다. 설정 파일을 보존했습니다.")
            ids.add(item["id"])
            names.add(name.casefold())
        if data.get("active_id") not in ids:
            raise WorkspaceError("마지막 작업공간을 찾을 수 없습니다. 설정 파일을 보존했습니다.")

    def _save_catalog(self, catalog):
        self._validate_catalog(catalog)
        _atomic_json(self._safe_path("workspaces.json"), catalog)
        self._catalog = catalog

    @property
    def active_id(self):
        return self._catalog["active_id"]

    def list(self):
        return [Workspace(item["id"], item["name"]) for item in self._catalog["workspaces"]]

    def get(self, workspace_id):
        for workspace in self.list():
            if workspace.id == workspace_id:
                return workspace
        raise WorkspaceError("작업공간을 찾을 수 없습니다.")

    def create(self, name):
        workspace = Workspace(uuid4().hex, _name(name))
        self._save_catalog({**self._catalog, "workspaces": [
            *self._catalog["workspaces"], asdict(workspace)]})
        return workspace

    def rename(self, workspace_id, name):
        self.get(workspace_id)
        name = _name(name)
        items = [{**item, "name": name} if item["id"] == workspace_id else dict(item)
                 for item in self._catalog["workspaces"]]
        self._save_catalog({**self._catalog, "workspaces": items})
        return self.get(workspace_id)

    def set_active(self, workspace_id):
        self.get(workspace_id)
        self._save_catalog({**self._catalog, "active_id": workspace_id})

    def path(self, workspace_id, kind):
        self.get(workspace_id)
        if kind not in {"qt", "cache", "chrome", "state"}:
            raise WorkspaceError("지원하지 않는 저장소 종류입니다.")
        path = self._safe_path("workspaces", workspace_id, kind)
        try:
            # 각 디렉터리를 개인 권한으로 만든다. / Private directories on POSIX.
            current = self.root
            for part in ("workspaces", workspace_id, kind):
                current = current / part
                current.mkdir(exist_ok=True, mode=0o700)
        except OSError as error:
            raise WorkspaceError("작업공간 폴더를 만들 수 없습니다.") from error
        return path

    def _state_path(self, workspace_id, filename):
        self.path(workspace_id, "state")
        return self._safe_path("workspaces", workspace_id, "state", filename)

    def bookmarks(self, workspace_id):
        return validate_bookmarks(_read_json(self._state_path(workspace_id, "bookmarks.json"), []))

    def save_bookmarks(self, workspace_id, items):
        valid = validate_bookmarks(items)
        _atomic_json(self._state_path(workspace_id, "bookmarks.json"), valid)

    def preferences(self, workspace_id):
        result = _read_json(self._state_path(workspace_id, "preferences.json"),
                            {"theme": "dark", "language": "ko"})
        if (not isinstance(result, dict) or result.get("theme") not in {"dark", "light"}
                or result.get("language") not in {"ko", "en"}):
            raise WorkspaceError("표시 설정이 올바르지 않습니다. 파일을 보존했습니다.")
        return {"theme": result["theme"], "language": result["language"]}

    def save_preferences(self, workspace_id, *, theme, language):
        if theme not in {"dark", "light"} or language not in {"ko", "en"}:
            raise WorkspaceError("지원하지 않는 테마 또는 언어입니다.")
        _atomic_json(self._state_path(workspace_id, "preferences.json"),
                     {"theme": theme, "language": language})

    def export_bookmarks(self, workspace_id):
        return {"version": 1, "bookmarks": self.bookmarks(workspace_id)}

    def import_bookmarks(self, workspace_id, payload):
        if not isinstance(payload, dict):
            raise WorkspaceError("북마크 JSON 객체가 필요합니다.")
        items = payload.get("bookmarks", payload)
        if isinstance(items, dict):
            # 이전 컬렉션 형식도 명시적 가져오기만 허용한다. / Opt-in legacy import.
            flattened = []
            for title, value in items.items():
                if isinstance(value, dict):
                    flattened.extend({"title": key, "url": url} for key, url in value.items())
                else:
                    flattened.append({"title": title, "url": value})
            items = flattened
        valid = validate_bookmarks(items)
        merged = validate_bookmarks([*self.bookmarks(workspace_id), *valid])
        self.save_bookmarks(workspace_id, merged)
        return len(merged)

