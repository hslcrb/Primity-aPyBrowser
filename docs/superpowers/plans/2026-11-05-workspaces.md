# Primity 작업공간 구현 계획

> 실행 방식: 소유자의 직접 구현 요청에 따라 이 세션에서 실행한다. 코드 쓰기는 root 한 명, 조사·리뷰는 병렬 읽기 전용.

**Goal:** Chromium 계정 작업공간을 분리하고 일상 탐색 UX를 복구한다.
**Architecture:** 순수 저장소 계층 + Qt 프로필 레지스트리 + 작업공간 창 + 선택적 Chrome 연결.
**Tech Stack:** Python 3.10+, PySide6 6.12 계열, pytest; GitHub API.
**Spec:** [설계](../specs/2026-11-05-workspaces-design.md).

## 공통 제약

- 헌법 형식 커밋, 워크플로/PR 없음, 최신 SHA 재확인 뒤 2부모 통합.
- 작업공간마다 별도 영속 프로필. Chrome 정상 프로필을 읽지 않는다.
- 주요 주석 한영 병기, 흑백 UI, MIT 유지. 인증 우회 및 평문 암호 저장 없음.

## 검토 집중 항목

- 손상 JSON·중복/악의적 ID·symlink 경로가 다른 저장소를 덮어쓰지 않는가.
- 팝업/OAuth opener와 닫힌 탭 복원이 원래 작업공간에 남는가.
- 여러 창 종료 순서에서 페이지보다 프로필이 먼저 파괴되지 않는가.
- 검색어·로컬호스트·위험 스킴·Chrome URL 인자가 정확히 처리되는가.
- 다운로드/권한/오류가 다른 창에 귀속되거나 조용히 허용되지 않는가.

## 작업

- [x] 1. 저장소·주소 해석 테스트를 먼저 실패시킨 후 `workspaces.py`, `navigation.py` 구현. 원자적 저장 및 경로 분리 검증 후 커밋.
- [x] 2. Chrome 명령 구성 테스트 실패 후 `chrome_launcher.py` 구현. 전용 프로필과 인자 검증 후 커밋.
- [x] 3. 실제 Qt 프로필 격리 테스트 실패 후 `profiles.py`, `webpage.py` 구현. 쿠키·스토리지·팝업 경계 검증 후 커밋.
- [x] 4. `browser.py`, 새 탭 UI, 앱 진입점 통합. 탐색·단축키·작업공간·다운로드 동작 검사 후 작은 단위로 커밋.
- [x] 5. README·사용법·로컬 검증/패키징 안내와 작업 증거 정리. 전체 테스트·컴파일·GUI 스모크·독립 코드 리뷰.

## 마지막 통합 게이트

문서를 포함한 최종 원격 diff·활성 workflow 부재·양쪽 SHA를 재확인한다. API로 첫 부모가 최신 main, 둘째 부모가 검증된 작업 head인 merge commit을 생성하고 `expected_sha`, `force=false`로 main을 갱신한다. 그 뒤 원격 ref·부모·tree와 작업 브랜치 포함 여부를 읽어 검증한다. 이 문서는 통합 전 스냅샷이며, 실제 완료 증거는 `**main** merge:` 커밋과 작업 완료 보고의 SHA·원격 읽기 결과다.

검증된 제품 상태: 77 tests passed, compileall 통과, Linux onedir 빌드·로컬 웹페이지/JavaScript 기동 확인. 상세는 [검증 기록](../../verification-20261105.md)을 참조한다.

통합 직전 재조회에서 PR #1을 통한 동시 병합을 감지해 기존 main 기준 작업을 중단했다. 관측된 tree가 검증한 tree와 같음을 확인했으며, 해당 기존 이력을 보존한다. 예외 기록 후 최신 main `10013828d8e93c74e8781271c36f8df188efa73b`를 첫 부모로 삼아 최종 API 2부모 통합을 수행한다. PR 경유 사실과 처리 근거는 [작업 대장](../../tasks/20261105-workspaces.md)에 남긴다.

실행 기록은 [작업 대장](../../tasks/20261105-workspaces.md)에 계속 남긴다.

