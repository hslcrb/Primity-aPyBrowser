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

## 진행

- 조사·설계 완료. 제품 코드 구현과 실제 검증 진행 예정.
- PySide6 6.12.0 / QtWebEngine 6.12.0.140 및 pytest 9.2.0 설치 확인. GUI용 시스템 라이브러리 보완을 별도로 준비한다.
- 테스트, 리뷰, 커밋/통합 결과는 실제 수행 후 추가한다.
