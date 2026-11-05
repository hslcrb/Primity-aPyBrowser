# Primity 작업 계약

[CODING_CONSTITUTION.md](CODING_CONSTITUTION.md)를 모든 향후 변경에 적용한다.

- 소유자의 현재 작업: 계정 간섭 없는 간단한 Chromium 작업공간 브라우저.
- GitHub API로 작업 브랜치·초소형 커밋·즉시 ref 갱신. 신규 PR과 GitHub Workflows 금지.
- 통합 담당자 한 명만 최신 양쪽 SHA를 재검증하고 2부모 merge commit + `expected_sha`, `force=false`로 통합한다.
- `CONTRIBUTING.md`의 PySide6 기반, 흑백 UI(빨강은 REC만), 핵심 한국어/영어 주석, MIT 조건은 계속 유효하다.
- 새 커밋 제목: `**<실제 브랜치>** <type>: 구체적 한국어 설명`. 영어 설명과 버전은 본문에 쓴다.
- 원격 읽기 스냅샷을 로컬에서 검증해도 원격 쓰기는 API로 수행한다. 리뷰 에이전트는 읽기 전용이며 제품 파일 쓰기는 한 담당자가 맡는다.
- 사용자 프로필·쿠키·로그인·비밀번호를 저장소에 커밋하지 않는다. 보안 기능을 끄거나 브라우저 신원을 위장하여 로그인을 우회하지 않는다.
- 검증: `python -m pytest -q`, `python -m compileall -q main.py src tests`; GUI/격리 테스트는 QtWebEngine과 디스플레이가 필요하며 실행 여부를 정확히 기록한다.
- 실제 Google/Figma 로그인, Windows/macOS 실행은 실측하지 않았으면 성공으로 쓰지 않는다.
