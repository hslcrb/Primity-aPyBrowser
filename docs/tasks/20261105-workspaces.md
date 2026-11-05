# Primity 20261105 작업 대장

- 작업 ID: 20261105-primity-workspaces
- 담당/유일한 쓰기·통합 담당자: ChatGPT root
- 작업 브랜치: `chatgpt/20261105-primity-workspaces`
- 기준 main SHA: `95727349f03b5e31d57ef772733f31bed6ed6e0b`
- 기준 tree SHA: `92f96b33d98d5462994771d22b33acb04b8e9f97`
- 저장소 상태: public, archived=false, 기본 main, 기존 open PR 0, 브랜치 main만 존재. main protected=false 조회 결과이며 본 작업이 강제 보호를 설정했다고 주장하지 않는다.
- 읽기: CONTRIBUTING, README, 소스 전체, 기존 대화 기록의 관련 기술 지시, IDEA_BANK 요구와 코딩헌법, 공통 헌법 원본.
- 기존 Workflow: `.github/workflows/release.yml.txt`만 존재. 활성 yml/yaml 없음.
- 범위: `main.py`, `src/core/`의 브라우저/프로필/저장소, `src/ui/` 새 탭 UI, `tests/`, 실행·의존성·문서.
- 병렬 담당: browser_compatibility_research(공식 문서 조사), audit_current_browser(기존 코드 읽기), prepare_qt_runtime(격리된 테스트 런타임 준비). 저장소 쓰기는 root만 한다.
- 원격 변경 방법: GitHub API. 로컬은 고정 SHA의 검증용 스냅샷이며 git push/clone 및 별도 미러 동기화는 사용하지 않는다.

## 판단 기록

1. 사용자가 바로 고도화를 요청했으므로 기존 PySide6 기반을 유지하는 설계를 채택하고 실행한다.
2. CONTRIBUTING의 과거 PR/커밋 예시는 현재의 명시적 코딩헌법 지시로 대체한다. 흑백 UI·한영 주석·MIT는 유지한다.
3. 보안 우회와 전역 아카이브 연결은 계정 분리 목적에 반하므로 일반 실행 경로에서 제거한다. 기존 아카이브/IME 구현 파일과 기록은 보존한다.
4. Chrome Sync를 임베디드 엔진에 위장 구현하지 않는다. 선택적인 독립 Chrome user-data-dir으로 공식 브라우저 경로를 제공한다.

## 구현·검증 결과

- `0.3.0` 작업공간 브라우저 구현 완료. 작업공간마다 영속 Qt 프로필, 창마다 별도 시크릿 프로필을 사용한다.
- 친숙한 탐색·탭·단축키·찾기·북마크·다운로드와 한국어/영어·다크/라이트 UI를 연결했다. Chrome 연결은 별도 전용 프로필을 명시적으로 연다.
- 실제 Chromium에서 A/B 쿠키·Local Storage·IndexedDB·서비스 워커 분리, 로그인 팝업의 opener, 인코딩 URL과 iframe, 다운로드, 종료 후 재시작을 검사했다.
- 최종 전체 결과: **77 passed in 3.57s**, 건너뛴 테스트 0. `compileall main.py src tests scripts`와 `bash -n run.sh` 종료 코드 0.
- Linux PyInstaller onedir 빌드 성공(약 631 MiB). 실행 파일 버전·로컬 페이지 렌더링·JavaScript 응답·임시 프로필 생성 확인. 라이선스·공지 파일 포함 확인.
- 실제 다크·라이트·시크릿 화면을 `docs/images/`에 남겼다. 사용자 계정이 아닌 합성 작업공간 이름을 썼다.
- 자세한 환경·실패 후 수정·미실측 범위: [검증 기록](../verification-20261105.md).

## 리뷰 후 수정한 문제

저장 바이트 한도, 손상된 타입·Unicode·깊은 JSON, symlink/경로 재지정, 호스트·포트·IPv6, 북마크 재가져오기 중복을 보강했다. 실제 Qt 검토에서 발견한 URL 디코딩, data/blob 프레임 차단, 다운로드 종료 시그널 문제를 회귀 테스트로 고쳤다. 비공개 창의 새 창 동작과 작업공간 오류 표시도 보완했다.

독립 검토자는 팝업의 nonce·postMessage와 비공개 프로필 파괴 순서도 확인했다. 읽기 전용 검토 후 제품 파일과 API 수정은 root가 수행했다. 문서 초안은 저장소 밖에서 전달받아 root가 검토·적용했다.

## API 커밋 기록

각 커밋 직후 작업 브랜치 ref를 `expected_sha`와 `force=false`로 갱신했다. 아래는 구현과 패키징의 증거이며, 뒤따르는 문서 커밋은 동일 브랜치 이력에서 확인할 수 있다.

| SHA | 내용 |
| --- | --- |
| `f066bc3` | 설계·헌법·계획·작업 등록 |
| `137b467` | 주소창 URL/검색 검증 |
| `0d8cbb8` | 작업공간 저장소·북마크 |
| `6dd0ca8` | 별도 Chrome 실행 인자 |
| `b87583d` | 저장소 경계·손상 데이터·포트 주소 회귀 수정 |
| `008715d` | Qt 영속/시크릿 프로필 |
| `fa3d39a` | 팝업·권한·인증서 처리 |
| `31fd618` | 흑백 새 탭 UI |
| `46bdda7` | 브라우저 창과 진입점 통합 |
| `27803ba` | 실제 팝업·프레임·다운로드·시크릿 회귀 수정 |
| `d712b79` | 흑백 아이콘·명확한 시크릿 배지·실제 화면 |
| `391cc87` | 의존성·실행기·수동 빌드·컨테이너 정비 |
| `69b391a` | 기존 Docker 제외 규칙 보존 |

## 통합 전 상태와 최종 증거 위치

제품·빌드 검증 후 main을 다시 조회했으며 기준 SHA `95727349f03b5e31d57ef772733f31bed6ed6e0b`와 일치했다. 초기 tree와 후보 tree를 비교해 삭제 파일 0개, 기존 `data/**`·`primity_archive.db`·`.github/workflows/release.yml.txt` blob 보존, 활성 workflow 0개를 확인했다. 최종 문서 커밋 후 같은 검사를 다시 수행하며, 원격 blob SHA를 실제 검증한 로컬 파일과 대조한다.

이 대장은 마지막 API 통합 전 기록이다. 통합 담당자는 **최신 main → 첫 부모, 검증한 작업 head → 둘째 부모**인 `**main** merge:` 커밋을 만들고, 비강제 ref 갱신 후 원격에서 부모·tree·SHA를 다시 읽는다. 정확한 merge SHA와 최종 main SHA는 해당 병합 커밋과 사용자에게 전달하는 작업 완료 보고에 남긴다. 조회한 커넥터에는 브랜치 삭제 기능이 없어 작업 브랜치는 보존하며, 삭제했다고 보고하지 않는다.

이 세션은 신규 PR·GitHub Workflow·자동 릴리스를 생성하지 않았다. 아래와 같이 별도 경로로 관측된 PR 병합은 예외로 기록한다. Linux 패키지는 로컬 검증 산출물이며 배포 릴리스로 발행하지 않았다. 실제 Google/Figma 인증, 설치된 Chrome 실행, Windows/macOS 및 Docker 실행은 미실측이다. 기존 브랜치 보호 설정을 변경하거나 자동 강제 검증을 설정한 것처럼 주장하지 않는다.

## 최종 조회에서 감지한 동시 변경

2026-11-05 07:40:20 UTC에 [PR #1](https://github.com/hslcrb/Primity-aPyBrowser/pull/1)이 병합됐음을 API로 확인했다. 통합 직전 main이 `10013828d8e93c74e8781271c36f8df188efa73b`로 변경돼 기존 기준의 API 통합을 중단했다. 해당 커밋의 부모는 `[95727349f03b5e31d57ef772733f31bed6ed6e0b, 79dd717f650de951f7992bbeee4edef34729b0a5]`이고, tree는 검증한 `a896dc2d3cc298a90b58ba42a25b23e726260898`과 같다. 작업 head 대비 파일 차이는 0개다.

이 세션에서는 PR을 생성하거나 PR 병합을 요청하지 않았다. 다만 저장소 전체 이력에는 이 PR 병합이 존재하므로 “PR 경유가 전혀 없었다”고 보고하지 않는다. 기존 커밋 제목과 이력은 보존하고, 예외 기록 문서를 작업 브랜치에 커밋한 뒤 최신 main `10013828d8e93c74e8781271c36f8df188efa73b`를 첫 부모로 하는 헌법 형식의 최종 2부모 통합을 진행한다. 강제 갱신·이력 재작성은 하지 않는다.

마지막 바이트 대조는 검증용 파일 87개, 변경 파일 39개에서 일치했다. 정규화 후 전체 테스트도 **77 passed in 3.50s**로 다시 통과했다. 이후 변경은 이 예외를 설명하는 문서뿐이다.

