# Primity 기여 가이드

Primity 0.3.0의 목표는 **계정 간섭 없는 Chromium 작업공간과 익숙한 브라우저 사용성**입니다. 현재의 PySide6·QtWebEngine 구조, 흑백 UI, 한국어·영어 지원, MIT 라이선스를 유지합니다.

변경 전 [AGENTS.md](AGENTS.md)와 [CODING_CONSTITUTION.md](CODING_CONSTITUTION.md)를 먼저 읽습니다. 이 안내는 코딩헌법의 Primity 특별 부칙을 구체화합니다. 현재 저장소의 작업 방식은 **GitHub API, 고유 작업 브랜치, 초소형 커밋, PR 없는 2부모 통합, GitHub Workflows 금지**입니다.

## 시작 전에 확인할 것

1. [설계](docs/superpowers/specs/2026-11-05-workspaces-design.md), [구현 계획](docs/superpowers/plans/2026-11-05-workspaces.md), [작업 대장](docs/tasks/20261105-workspaces.md)과 관련 소스를 읽습니다.
2. API로 실제 기본 브랜치, 최신 SHA, 작업 브랜치, 다른 작업자의 변경을 조회합니다. 기존 PR은 필요할 때 읽기만 하며 새 PR을 만들지 않습니다.
3. 작업 ID·담당자·기준 SHA·고유 브랜치·수정 경로·검증 계획을 작업 대장에 등록합니다. 예: `chatgpt/20261105-workspace-downloads`.
4. 코드 쓰기 담당과 통합 담당을 분명히 합니다. 현재 작업의 제품 파일 쓰기와 원격 통합은 root 한 명이 맡습니다. 다른 에이전트는 읽기·리뷰를 수행하고, 명시적으로 요청받은 초안도 제품 저장소 밖에서 작성해 전달합니다.

같은 파일에 여러 담당자가 동시에 쓰지 않습니다. 새로운 작업에서 분리된 작성자를 두기로 합의했다면 각자 격리된 작업 사본과 브랜치를 사용하며, 서로의 커밋이나 파일을 덮어쓰지 않습니다.

## 개발 환경

Python 3.10 이상, 3.16 미만과 해당 플랫폼의 PySide6 지원이 필요합니다. 현재 고정 런타임은 PySide6 6.12.0이며, 검증에 사용한 Python은 3.12.14입니다.

Linux/macOS에서 저장소 루트 기준:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
bash run.sh --data-dir "$HOME/Primity-development-data"
```

Windows 명령 프롬프트:

```bat
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
run.bat --data-dir "%LOCALAPPDATA%\Primity-development-data"
```

`requirements-dev.txt`에 런타임·테스트·빌드 의존성을 함께 고정합니다. 프로필을 사용하는 테스트에는 임시 데이터 루트를 쓰고, 실제 사용자 쿠키나 계정 자격증명을 사용하지 않습니다. 같은 데이터 루트로 앱을 중복 실행할 수 없으므로 기존 창을 이용하거나 별도 테스트 루트를 지정합니다.

## 구현 원칙

- **작업공간 경계:** UUID 기반 경로와 작업공간별 `QWebEngineProfile`을 유지합니다. 같은 작업공간의 새 탭·팝업만 해당 프로필을 공유하고, 살아 있는 페이지의 프로필을 다른 작업공간으로 바꾸지 않습니다.
- **시크릿 수명:** 창별 off-the-record 프로필을 사용합니다. 페이지를 먼저 해제한 뒤 프로필을 정리하며 시크릿 사이트 데이터를 영속 저장소에 쓰지 않습니다.
- **로그인과 보안:** Chromium 보안 기능을 끄거나 UA를 위장해 로그인을 우회하지 않습니다. 일반 웹페이지에 네이티브 WebChannel을 노출하지 않으며 인증서 오류는 거절합니다. 권한은 출처를 보여주고 사용자가 선택합니다.
- **사용자 데이터:** 쿠키·토큰·비밀번호·개인 프로필을 커밋하거나 자동 이식하지 않습니다. 사용자 요청에 따른 북마크 JSON 이동만 지원합니다. Chrome 연결은 전용 데이터 경로와 인자 배열 실행을 유지합니다.
- **표시와 입력:** 흑백·회색 UI를 유지합니다. 빨강은 기존 REC 상태에만 예약된 색이며 일반 작업공간 UI에 새로 쓰지 않습니다. 주요 로직 주석은 한국어·영어를 병기하고 OS 입력기와 Qt의 기본 입력 동작을 존중합니다.
- **보존된 모듈:** 아카이브·비밀번호·사용자 정의 IME 파일은 현재 실행 경로와 분리되어 있습니다. 해당 코드를 일반 사이트나 로그인 세션에 다시 연결하는 변경은 별도 범위·설계 검토가 필요합니다.

[src/README.md](src/README.md)에 현재 실행 경로와 보존 모듈을 구분했습니다. 단순 수정에 불필요한 계층을 추가하지 않고, 저장소 경계나 수명 관리에 영향을 주는 변경에는 실제 회귀 위험을 검증하는 테스트를 추가합니다.

## 커밋 형식과 즉시 API 반영

커밋 제목의 별표 두 개도 실제 문자열에 포함합니다.

```text
**<실제 브랜치>** <type>: 구체적인 한국어 설명
```

예시:

```text
**chatgpt/20261105-workspace-downloads** fix: 다운로드를 요청한 작업공간에 저장 대화상자 연결

Route download handling to the window that owns the requesting page.
Validation: python -m pytest -q
Version: 0.3.0
```

제목에는 실제 브랜치와 한국어 변경 내용을 쓰고, 영어 설명·검증 결과·버전은 본문에 씁니다. `feat`, `fix`, `refactor`, `docs`, `test`, `build`, `deps`, `security` 등 코딩헌법의 허용 type을 사용합니다. 전체 목록과 선택적 scope 규칙은 [코딩헌법 제2장](CODING_CONSTITUTION.md)을 따릅니다.

논리적으로 완결된 작은 변경마다 해당 파일만 검토해 API로 커밋하고 **즉시 작업 브랜치 ref를 갱신**합니다. 변경을 큰 로컬 묶음으로 쌓아 두지 않습니다. 로컬에서 읽기 스냅샷을 실행·검증하더라도 원격 쓰기는 지정된 API 경로로 수행합니다. 기존 공유 이력을 다시 쓰거나 다른 담당자의 커밋을 덮어쓰지 않습니다.

## 수동 검증과 빌드

가상환경의 Python으로 실행합니다.

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q main.py src tests scripts
.venv/bin/python scripts/build.py
```

Windows에서는 `.venv\Scripts\python.exe`로 동일한 명령을 실행합니다. GUI 검사를 제외한 순수 로직을 먼저 확인하려면 `python -m pytest -q -m "not gui"`를 사용할 수 있지만, 이를 전체 브라우저 검증으로 기록하지 않습니다.

전체 GUI 테스트에는 동작하는 QtWebEngine과 디스플레이가 필요합니다. 화면 없는 Linux에서는 환경이 지원하는 Xvfb 또는 offscreen 플랫폼을 준비합니다. 일반 사용자와 정상 보안 설정에서 검증하는 것이 기준입니다. 격리된 테스트 환경의 제약으로 보안 설정에 예외를 적용했다면 환경·이유·검증 한계를 명시하고, 그 예외를 제품 코드·실행·빌드 스크립트로 옮기지 않습니다. 이번 루트 테스트 환경의 sandbox 예외는 [README의 검증 범위](README.md)에 기록했습니다.

현재 테스트는 작업공간 ID·경로·손상 JSON·원자적 저장, 주소 해석·Chrome 인자, 실제 로컬 사이트의 쿠키·Local Storage·IndexedDB·서비스 워커 분리, 팝업 opener, 시크릿 창, 다운로드, 프로세스 재시작, 단일 실행 잠금을 다룹니다. 검증 결과에는 명령·환경·통과/실패/미실행 범위를 기록하고, 실제 Google/Figma 로그인이나 Windows/macOS 실행을 해 보지 않았다면 성공으로 표시하지 않습니다.

`scripts/build.py`는 현재 운영체제용 PyInstaller `onedir` 패키지를 `dist/`에 만들고 `LICENSE`·`NOTICE`를 포함합니다. 각 플랫폼에서 직접 빌드하고 시작·탐색·종료를 확인합니다. 생성된 사용자 프로필, `.venv`, 빌드 캐시, 배포 산출물을 소스 커밋에 섞지 않습니다.

**GitHub Workflows는 만들거나 활성화하지 않습니다.** 기존 `.github/workflows/*.yml.txt` 보존 파일은 그대로 두고 `.yml`/`.yaml`로 바꾸지 않습니다. 수동 검증과 배포 기록을 작업 대장에 남깁니다.

## PR 없는 2부모 통합

통합은 지정된 한 담당자만 수행합니다.

1. API로 기본 브랜치와 작업 브랜치의 **현재 head SHA 두 개를 다시 조회**합니다. 이 저장소의 현재 기본 브랜치는 `main`이지만 매번 실제 설정을 확인합니다.
2. 해당 두 SHA를 기준으로 diff·부모 관계·검증 결과와 최종 tree를 확인합니다. 어느 head라도 달라지면 기존 통합 판단을 중단하고 새 기준에서 다시 검토합니다.
3. **첫 부모 = 통합 직전 main SHA, 둘째 부모 = 검증한 작업 브랜치 head SHA**인 명시적 2부모 merge commit을 API로 생성합니다. 제목 예시는 `**main** merge: 작업공간 다운로드 개선 정식 통합`입니다.
4. `expected_sha`에 검증한 기존 main SHA를 넣고 `force=false`로 기본 ref를 갱신합니다. 낙관적 잠금이 거부되면 새 head를 읽고 검토부터 다시 수행합니다.
5. 원격에서 merge SHA·부모·tree·기본 ref를 다시 읽어 확인하고 작업 대장에 기록합니다. 작업 브랜치 삭제는 모든 커밋의 기본 브랜치 포함 여부를 확인한 뒤에만 수행합니다.

신규 PR, PR 병합, squash, rebase, fast-forward 통합과 강제 ref 갱신은 사용하지 않습니다. 이 문서나 작업 대장은 브랜치 보호·분산 잠금을 자동 설정하지 않으며, 실제 API 결과로 충돌과 반영 여부를 확인해야 합니다.

## English summary

Read `AGENTS.md` and `CODING_CONSTITUTION.md` before changing Primity. Preserve PySide6/QtWebEngine, workspace data boundaries, monochrome UI, bilingual key comments, and the MIT license. Keep legacy archive, password, and custom IME modules disconnected from normal browsing.

Use a unique task branch, small atomic commits, and immediate GitHub API ref updates. The literal title format is `**<actual-branch>** <type>: <specific Korean subject>`; put the English explanation, validation, and version in the body. Do not create PRs or GitHub Workflows. Preserve inactive `.yml.txt` files.

The designated integrator rereads both exact heads, validates the resulting tree, creates a merge commit with the current main head as first parent and the verified task head as second parent, and updates main with `expected_sha` and `force=false`. A changed head requires renewed review. Product writes and remote integration for the current task belong to root; other agents provide reviews or drafts outside the repository.

Run pytest, compile checks, and native manual builds with the virtual environment. GUI tests need a working display/QtWebEngine environment. Record what was actually tested; local isolation tests do not establish successful Google/Figma authentication or cross-platform package compatibility.

## 라이선스

기여 코드는 프로젝트의 [MIT License](LICENSE)를 따릅니다. 기존 저작권 표기와 라이선스 파일을 보존합니다.
