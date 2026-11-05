# Primity 0.3.0 소스 안내

현재 실행 경로는 **작업공간별 Chromium 프로필을 사용하는 브라우저**입니다. 저장소에 남아 있는 이전 아카이브·비밀번호·사용자 정의 IME 코드와 구분해서 읽어 주세요.

사용법은 [루트 README](../README.md), 변경 규칙은 [AGENTS.md](../AGENTS.md)와 [기여 가이드](../CONTRIBUTING.md), 데이터 경계는 [설계 문서](../docs/superpowers/specs/2026-11-05-workspaces-design.md)에 있습니다.

## 현재 실행 경로

| 파일 | 책임 |
| --- | --- |
| [main.py](../main.py) | 명령행 인자, 앱 이름·버전, 기본 데이터 루트, `QLockFile` 단일 실행 잠금, 시작·종료 순서 |
| [core/browser.py](core/browser.py) | `BrowserController`와 `PrimityBrowser`; 작업공간 창, 탭·주소창·단축키, 북마크 메뉴, 다운로드, 표시 설정, Chrome 연결 |
| [core/workspaces.py](core/workspaces.py) | `WorkspaceStore`; 안정된 ID, 경로 경계, 카탈로그·북마크·설정 검증, 원자적 JSON 저장, 명시적 북마크 가져오기·내보내기 |
| [core/profiles.py](core/profiles.py) | `ProfileRegistry`; 작업공간별 영속 `QWebEngineProfile`, 창별 메모리 시크릿 프로필, 저장·캐시 경로와 권한 보존 정책 |
| [core/webpage.py](core/webpage.py) | `BrowserPage`와 `BrowserView`; 같은 작업공간의 팝업, 문서 탐색 규칙, 출처별 권한 확인, 인증서 오류 거절 |
| [core/navigation.py](core/navigation.py) | 주소·검색어 해석, HTTP(S) URL 검증, 외부 브라우저에 전달할 URL 경계 |
| [core/chrome_launcher.py](core/chrome_launcher.py) | 설치된 Google Chrome 탐색, 전용 `--user-data-dir` 명령 구성, 셸을 사용하지 않는 실행 |
| [ui/workspace_widgets.py](ui/workspace_widgets.py) | 네이티브 새 탭 페이지, 빠른 링크, 작업공간·시크릿 표시, 흑백 다크·라이트 스타일 |
| [ui/dialogs.py](ui/dialogs.py) | 일반 텍스트 안내·확인 대화상자와 기본 거절 선택 |
| [assets/](../assets/) | 현재 UI에서 사용하는 아이콘과 보존된 이전 자산 |

`main.py`는 앱 데이터 루트에 대한 잠금을 얻은 뒤 `WorkspaceStore`와 `BrowserController`를 만듭니다. 컨트롤러가 작업공간 ID에 맞는 프로필을 가져와 창을 열고, 그 창이 생성하는 모든 일반 웹 페이지에 같은 프로필을 전달합니다. 일반 사이트에는 네이티브 WebChannel을 연결하지 않습니다.

## 작업공간과 수명 관리

- **일반 작업공간:** ID 하나에 영속 프로필 하나를 대응시킵니다. 프로필의 저장·캐시 경로는 페이지를 만들기 전에 지정합니다. 같은 작업공간의 일반 창과 탭은 세션을 공유합니다.
- **다른 작업공간:** 다른 ID·경로·프로필을 사용합니다. 기존 페이지의 프로필을 바꾸는 대신 해당 작업공간 창을 열거나 활성화합니다. 이름 변경으로 ID를 바꾸지 않습니다.
- **팝업:** `newWindowRequested`의 `openIn()`으로 요청한 창의 새 페이지에 연결합니다. 같은 프로필과 opener 관계를 유지하고, 사용자 동작 없이 요청한 팝업에는 확인을 표시합니다.
- **시크릿:** 새 창마다 이름 없는 off-the-record 프로필을 만듭니다. 같은 시크릿 창의 탭은 그 프로필을 공유하지만 다른 시크릿 창과는 공유하지 않습니다. 북마크 변경과 Chrome 연결은 차단하고 다운로드 파일은 남습니다.
- **종료:** 페이지를 먼저 정리한 뒤 프로필을 해제합니다. 진행 중인 다운로드가 있으면 창을 닫기 전에 취소 여부를 확인합니다.
- **권한:** `permissionRequested`에서 출처·기능을 보여줍니다. 알려지지 않은 권한은 거절하며, 선택은 `StoreInMemory` 정책으로 앱 실행 동안만 기억합니다.

영속 쿠키는 `AllowPersistentCookies`, 일반 캐시는 `DiskHttpCache`를 사용합니다. 사이트의 쿠키 만료·로그아웃 정책을 덮어쓰지 않습니다. 시크릿 프로필은 `NoPersistentCookies`와 `MemoryHttpCache`를 사용합니다.

## 데이터와 외부 실행 경계

기본 저장 루트는 `QStandardPaths.AppLocalDataLocation`이며 `--data-dir`로 바꿀 수 있습니다. `workspaces.json`은 ID·이름·마지막 작업공간을 보관하고, 작업공간마다 다음 경로를 사용합니다.

| 상대 경로 | 용도 |
| --- | --- |
| `workspaces/<id>/qt/` | Qt 사이트 데이터 |
| `workspaces/<id>/cache/` | Qt HTTP 캐시 |
| `workspaces/<id>/state/` | 북마크와 표시 설정 JSON |
| `workspaces/<id>/chrome/` | 사용자가 선택한 Chrome 연결의 독립 프로필 |

`WorkspaceStore`는 ID·자료형·이름·경로·JSON 크기를 검증하고, 완성한 임시 파일을 교체해 저장합니다. 손상된 메타데이터를 기본값으로 덮어쓰지 않습니다. 현재 작업공간 삭제 UI는 없습니다.

Chrome 연결은 사용자의 기존 Chrome 프로필을 읽거나 복제하지 않습니다. HTTP(S) 주소만 인자 배열로 전달하며 Qt 세션과 Chrome 세션은 공유되지 않습니다. Google OAuth 또는 Chrome Sync의 정책 제약을 우회하는 모듈은 없습니다. 외부 인증 한계와 공식 출처는 [루트 README](../README.md)에 정리했습니다.

## 보존되어 있지만 현재 앱에 연결하지 않는 코드

| 파일·디렉터리 | 상태 |
| --- | --- |
| [core/archive_manager.py](core/archive_manager.py), [core/archivebox_core/](core/archivebox_core/), [core/archivebox_config.py](core/archivebox_config.py) | 이전 아카이브 엔진·설정 보존. 일반 웹 페이지나 로그인 프로필에 연결하지 않습니다. |
| [pages/archive_dashboard.py](pages/archive_dashboard.py), [ui/archive_config.py](ui/archive_config.py) | 이전 아카이브 UI 보존. 현재 메뉴에서 열지 않습니다. |
| [pages/passwords.py](pages/passwords.py) | 이전 비밀번호 페이지 보존. 평문 비밀번호 자동 가져오기와 현재 UI 연결은 없습니다. |
| [core/ime_manager.py](core/ime_manager.py), [hangul.py](hangul.py), [ui/hangul_lineedit.py](ui/hangul_lineedit.py) | 사용자 정의 한글 입력기 보존. 현재 브라우저는 OS 입력기를 쓰며 사이트에 입력기 스크립트를 주입하지 않습니다. |
| [pages/settings.py](pages/settings.py), [ui/components.py](ui/components.py), [ui/styles.py](ui/styles.py), [config/](config/), [utils/](utils/) | 이전 설정·UI·지원 코드 보존. 현재 창의 설정과 스타일은 위의 작업공간 모듈이 담당합니다. |

보존 모듈의 존재는 0.3.0에서 그 기능을 제공한다는 뜻이 아닙니다. 재연결할 때에는 별도 설계와 보안·수명 검토를 거칩니다. 기존 파일과 사용자 데이터를 자동으로 삭제하거나 마이그레이션하지 않습니다.

## 테스트와 빌드 위치

| 파일 | 검증 범위 |
| --- | --- |
| [tests/test_workspaces.py](../tests/test_workspaces.py) | ID·경로·중복 이름, 손상·과대 JSON, 원자적 저장, 북마크·설정 분리와 가져오기 |
| [tests/test_navigation.py](../tests/test_navigation.py) | 웹 주소·검색·포트·스킴·입력 검증 |
| [tests/test_chrome_launcher.py](../tests/test_chrome_launcher.py) | 전용 프로필 인자, URL 검증, Chrome 미설치 처리 |
| [tests/test_profiles.py](../tests/test_profiles.py) | 실제 Qt 프로필 경로·쿠키·권한·시크릿 설정 |
| [tests/test_browser_gui.py](../tests/test_browser_gui.py) | 로컬 HTTP 사이트의 저장소 분리, 탐색·복원, 시크릿 창, 팝업·opener, 문서 프레임, 다운로드, 재시작 |
| [tests/fixtures/profile_session.py](../tests/fixtures/profile_session.py) | 별도 프로세스로 영속 쿠키·Local Storage 재시작 검사 |
| [tests/test_startup.py](../tests/test_startup.py) | CLI와 데이터 루트별 단일 실행 잠금 |
| [scripts/build.py](../scripts/build.py) | 현재 운영체제에서 수행하는 수동 PyInstaller `onedir` 빌드 |

실행 명령과 검증 한계는 [기여 가이드](../CONTRIBUTING.md)를 따릅니다. 테스트는 임시 프로필과 로컬 사이트를 사용하며 실제 Google/Figma 인증 성공이나 Windows/macOS 패키지 호환성을 증명하지 않습니다.

## English summary

The active runtime is `main.py` → `BrowserController` → workspace windows and explicitly selected QtWebEngine profiles. `workspaces.py` owns metadata and storage paths; `profiles.py` owns persistent/private profiles; `webpage.py` owns popup, permission, and navigation handling; `browser.py` owns familiar browser actions. New-tab widgets and dialogs live in `ui/workspace_widgets.py` and `ui/dialogs.py`.

One normal workspace shares a profile across its tabs and windows. Different workspaces and newly created private windows use separate profiles. Popups retain the originating workspace. Pages must be destroyed before their profiles. Chrome compatibility launches installed Chrome with a dedicated user-data directory, without copying cookies or credentials.

Legacy archive, password, custom IME, and supporting UI modules are preserved but disconnected. Tests cover local data isolation and browser behavior; they do not certify external identity-provider login or untested platforms.
