# Primity 0.3.0 검증 기록

검증일: 2026-11-05. 담당: ChatGPT root. 작업 브랜치: `chatgpt/20261105-primity-workspaces`.

## 결과

**전체 테스트 77개 통과, 소스 컴파일 검사 통과, Linux 실행 파일 빌드 및 실제 페이지 렌더링 확인.** 외부 서비스 계정 자격증명을 사용하지 않았다. GitHub Workflows는 사용하지 않았다.

검증한 제품 코드와 패키징 설정은 `391cc87f33f611bcb279bda908f534922e63d8b7`에 포함된다. 이후 문서·제외 목록 변경은 실행 코드에 영향을 주지 않는다. 최종 통합 커밋의 부모 관계와 정확한 SHA는 저장소의 `**main** merge:` 커밋 및 작업 완료 보고에서 확인한다.

## 환경과 실행 명령

| 항목 | 실측 환경 |
| --- | --- |
| OS / CPU | Linux x86_64, 관리형 컨테이너 |
| Python | 3.12.14 |
| PySide6 | 6.12.0 |
| Qt WebEngine 배포 패키지 | 6.12.0.140 |
| pytest | 9.2.0 |
| PyInstaller | 6.22.3 |
| 디스플레이 | Qt `offscreen`, 소프트웨어 렌더링 |
| 데이터 | 임시 폴더, 합성 A/B 계정 값, 로컬 HTTP 서버 |

일반 개발 환경의 검증 명령:

```bash
python -m pytest -q
python -m compileall -q main.py src tests scripts
bash -n run.sh
```

디스플레이가 없는 Linux에서는 테스트 명령에 `QT_QPA_PLATFORM=offscreen`을 지정한다. 이 세션은 root로 실행되는 제한된 컨테이너여서 **테스트 프로세스에만 외부 환경변수 `QTWEBENGINE_DISABLE_SANDBOX=1`을 제공했다.** 이 예외는 제품 코드, 실행기, Dockerfile, 빌드 스크립트에 포함하지 않았다. 실제 사용은 일반 OS 사용자와 Chromium의 기본 샌드박스 설정을 전제로 한다.

실제로 실행한 테스트 명령은 다음 형태였다. `TEST_QT_LIB_DIR`는 이 세션의 임시 라이브러리 폴더를 뜻하며 저장소 설정이 아니다.

```bash
env LD_LIBRARY_PATH="$TEST_QT_LIB_DIR" \
    QT_QPA_PLATFORM=offscreen QTWEBENGINE_DISABLE_SANDBOX=1 \
    timeout 60s .venv/bin/python -m pytest -q
```

최종 출력:

```text
77 passed in 3.57s
```

건너뛴 테스트는 없다. `compileall`과 `bash -n`도 종료 코드 0이었다. 부족한 Qt 라이브러리와 화면 확인용 한글 폰트는 공식 Ubuntu 패키지 인덱스의 크기·SHA256과 대조한 후 임시 폴더에 추출했다. 시스템 설치나 제품 의존성 경로 변경은 하지 않았다.

## 실제로 확인한 동작

| 영역 | 확인한 내용 | 방법 |
| --- | --- | --- |
| 작업공간 저장소 | 안정된 ID, 이름 변경 후 경로 유지, 다른 작업공간 경로 분리, 별도 북마크·표시 설정 | 순수 Python 테스트 |
| 손상 데이터 | 잘못된 ID·타입·JSON·Unicode·과도한 중첩·2 MiB 초과 데이터 거절, 기존 파일 보존 | 회귀 테스트 |
| 경로 | symlink를 통한 다른 저장소 접근 거절 | 로컬 파일시스템 테스트 |
| 북마크 | 형식 검증, 명시적 가져오기, URL 중복 병합, 실제 저장 바이트 한도 | 순수 Python 테스트 |
| 주소창 | 검색 인코딩, HTTP/HTTPS, localhost, 호스트·포트, IPv6, 위험 스킴 거절 | 단위 테스트 |
| 별도 Chrome | 별도 `--user-data-dir`, URL 단일 인자, `shell=False`, 실행 파일 탐색 경로 | 명령 구성 테스트·정적 검토 |
| 일반 프로필 | 명시적 저장소·캐시 경로, 영속 쿠키 정책, 메모리 권한 정책 | 실제 Qt 프로필 검사 |
| A/B 계정 분리 | 같은 로컬 출처의 쿠키·Local Storage·IndexedDB·서비스 워커가 다른 작업공간에 보이지 않음 | 실제 Chromium 통합 테스트 |
| 재시작 지속성 | 쓰기 프로세스 종료 후 새 프로세스에서 영속 쿠키·Local Storage 복원 | 두 실제 subprocess와 로컬 HTTP 서버 |
| 비공개 창 | 일반 창과 사이트 데이터 분리, off-the-record 설정, 새 비공개 창마다 별도 프로필, 비공개 창의 새 창도 비공개 유지 | 실제 Qt/Chromium 테스트 |
| 로그인 팝업 | 같은 작업공간 프로필·쿠키, `window.opener` 유지, 인코딩된 scope URL, `window.close()` 처리 | 실제 Chromium 통합 테스트 |
| 웹 문서 프레임 | `srcdoc`, `data:`, `blob:` iframe의 메시지 수신 | 실제 Chromium 통합 테스트 |
| 일반 탐색 | URL 이동, 뒤로 가기 상태·동작, 탭 닫기·복원, 작업공간 배지 | GUI 통합 테스트 |
| 다운로드 | 요청 작업공간 쿠키로 받은 파일을 지정 위치에 저장, 완료 상태 정리 | 실제 HTTP 다운로드 테스트 |
| 시작과 잠금 | CLI 검증, 같은 데이터 폴더의 중복 실행 잠금 | 자동 테스트 |
| 화면 | 다크·라이트·시크릿 화면, 한글, 흑백 닫기 아이콘, 명시적 시크릿 배지 | 실제 QWidget 캡처와 시각 점검 |

HTTP 캐시 경로의 분리는 Qt 프로필 설정에서 확인했다. 모든 웹 저장소 종류의 디스크 내부 구조까지 조사했다고 주장하지 않는다. 세션 쿠키 만료, 서버의 로그인 정책과 MFA는 각 사이트의 규칙을 따른다.

## 독립 코드 리뷰와 수정

읽기 전용 검토자가 저장소 계층과 브라우저 실행 경로를 각각 검토했다. 다음 재현 사례를 수정하고 회귀 테스트에 반영했다.

- 저장 JSON이 읽기 제한보다 커지는 문제: 교체 전에 실제 직렬화 바이트 수를 검사한다.
- 손상된 scalar 타입, surrogate 문자, 깊게 중첩된 JSON: 일관된 오류로 처리하고 기존 데이터를 보존한다.
- 일반 도메인의 포트 및 IPv6 입력: 위험 스킴 검사에 앞서 올바른 호스트·포트를 구분한다.
- 북마크 재가져오기: 중복 URL을 제거한 최종 개수로 저장 한도를 확인한다.
- Qt URL의 `%20`이 공백으로 풀리면서 탐색·OAuth 팝업이 거절되는 문제: 기계에 전달하는 URL은 `QUrl.FullyEncoded`를 사용한다.
- 웹 앱의 `data:`·`blob:` 프레임 차단: 브라우저 소유 문서는 Chromium 출처 정책에 맡긴다. 외부 `file:` 경로는 계속 거절한다.
- 다운로드 완료 후 진행 상태가 남는 문제: `isFinishedChanged`로 정리한다.
- 비공개 창의 `Ctrl+N`이 일반 창을 열던 문제와 작업공간 손상 설정 오류가 UI에 보이지 않던 문제: 명시적인 동작과 회귀 테스트를 추가했다.

검토자는 별도 실행에서 팝업의 `sessionStorage` nonce 상속·`postMessage`, 그리고 **페이지 → 창 → 비공개 프로필**의 파괴 순서도 확인했다. Windows junction 방어는 경로의 원래 위치와 resolve 결과를 비교하는 방식으로 보강했지만, Windows에서 junction을 실제 생성하는 검사는 실행하지 않았다.

새 실행 경로에는 웹 페이지에 노출되는 WebChannel, 전역 아카이브 후크, 사용자 에이전트 위장, 인증서 무시, 웹 보안 비활성화가 없다. 권한 요청은 출처를 plain text로 표시하며 기본 선택은 거절이다.

## 수동 패키징

```bash
python -m pip install -r requirements-dev.txt
python scripts/build.py
./dist/Primity/Primity --version
```

Linux에서 약 631 MiB의 `onedir` 출력이 생성됐다. 실행 파일은 `Primity 0.3.0`을 반환했고, 포함된 `LICENSE`와 `NOTICE`도 확인했다. 자동 업로드나 릴리스 발행은 하지 않았다.

완성된 실행 파일을 **추가 `LD_LIBRARY_PATH` 없이**, 임시 `--data-dir`과 로컬 HTTP 서버로 실행했다. 페이지의 JavaScript가 서버로 `/renderer-ready` 요청을 보냈고 전용 Qt 프로필 폴더가 생성됐다. 이 검사는 패키징된 Python·QtWebEngine·렌더러의 기동을 확인하며, 데스크톱 전체 사용성 검사나 장시간 안정성 검사는 아니다. 확인 후 테스트 프로세스를 종료했다.

최종 빌드는 성공했다. PySide6 배포본에 없는 선택적 `Qt/labs/assetdownloader` QML plugin 경고 한 건이 남았다. 앱은 해당 QML 기능을 사용하지 않으며 위 페이지 렌더링은 성공했다. 처음 재빌드할 때 기존 산출물 디렉터리 삭제에서 `ENOTEMPTY`가 발생했으나, 해당 임시 산출물을 옮기고 새 출력 디렉터리에서 빌드해 해결했다. 사용자 프로필이나 소스 파일은 삭제하지 않았다.

## 미실측과 제품 경계

- 실제 Google/Figma 계정 로그인, MFA 및 Google Sync는 자격증명 없이 검증하지 않았다.
- 설치된 Chrome의 실제 실행과 동기화는 미실측이다. 실행 인자·프로필 경로·오류 처리를 검사했다.
- Windows/macOS 실행·패키징 및 Docker build/run은 미실측이다. Dockerfile은 일반 사용자 실행으로 정비했지만 실행 성공을 주장하지 않는다.
- 실제 카메라·마이크·화면 공유 장치, 하드웨어 가속, DRM 콘텐츠, 브라우저 확장 기능은 이번 검증 범위가 아니다.
- 일부 저장소 검증 오류는 영어 UI에서도 한국어로 표시된다.
- Qt 프로필과 Chrome 연결 프로필은 별개의 로그인 저장소다. Chrome Sync는 Chrome에서 직접 설정하며 Qt로 동기화되지 않는다.
- 작업공간은 브라우저 데이터 분리 기능이다. 같은 OS 사용자 권한의 다른 프로그램이나 사이트 서버가 계정을 연관 짓는 동작까지 격리하는 경계는 아니다.

관련 공식 문서: [Qt 프로필](https://doc.qt.io/qtforpython-6/PySide6/QtWebEngineCore/QWebEngineProfile.html), [Google OAuth 사용자 에이전트 정책](https://developers.google.com/identity/protocols/oauth2/policies), [Chrome 전용 API 제한](https://blog.chromium.org/2021/01/limiting-private-api-availability-in.html), [Chromium 사용자 데이터 경로](https://chromium.googlesource.com/chromium/src/+/main/docs/user_data_dir.md).
