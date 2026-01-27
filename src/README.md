# Source Code Structure (소스 코드 구조)

> This directory contains the core logic and UI components of the Primity Browser.
> 이 디렉토리에는 프리마이티 브라우저의 핵심 로직 및 UI 컴포넌트가 포함되어 있습니다.

---

## Directory Structure (디렉토리 구조)

```
src/
├── core/                   # 비즈니스 로직 레이어 및 코어 엔진
│   ├── browser.py          # 메인 윈도우 오케스트레이터 & 네이티브 오라 UI
│   ├── archive_manager.py  # 비동기 아카이빙 워커 매니저
│   ├── archivebox_core/    # [NEW] 네이티브 아카이빙 엔진 (WIP/개발 중)
│   └── ime_manager.py      # 한글 IME 매니저
├── ui/                     # 디자인 레이어
├── config/                 # 설정 레이어
├── pages/                  # 내부 대시보드 페이지
└── utils/                  # 유틸리티 및 헬퍼
```

---

## Module Details (모듈 상세)

### `core/` - Business Logic & Engine

**`browser.py`**
- 메인 윈도우 오케스트레이터.
- **RecordingContainer**: 웹사이트를 침범하지 않고 브라우저 프레임에 붉은 오라를 그리는 네이티브 컨테이너 포함.
- **ArchiveSchemeHandler**: `primity-archive://` 가상 프로토콜을 처리하여 보안 샌드박스를 우회.

**`archive_manager.py`**
- 비동기 아카이빙 프로세스 관리자.
- **ArchiveWorker**: UI 프리징 없이 백그라운드에서 `wget`, `WARC`, `Media` 수집을 수행하는 독립 쓰레드.

**`archivebox_core/`** ⭐ NEW (Under Development)
- Docker 없이 파이썬 환경에서 즉시 실행되는 네이티브 아카이빙 엔진.
- SQLite 기반 스냅샷 관리 및 네트워크 로그 저장.

**`ime_manager.py`**
- 소프트웨어 한글 입력기 매니저.
- 웹페이지에 JS 오토마타 주입 및 Python-JS 상태 동기화.

### `ui/` - Design Layer

**`styles.py`**
- CSS 변수 및 Qt 네이티브 스타일 통합 관리.
- REC 상태 전용 색상 및 애니메이션 변수 포함.

### `pages/` - Internal Pages

**`archive_dashboard.py`**
- 네이티브 아카이브 관리 센터.
- **Smart Launcher**: Wget, MHTML, DOM 스냅샷 중 가장 적합한 파일 자동 선택.
- 가상 프로토콜 연동을 통한 무결성 리플레이 지원.

---

## Design Principles (설계 원칙)

1. **Native Overlay (네이티브 오버레이)**: 페이지 내부 수정 없이 브라우저 프레임 수준에서 UI 효과 구현.
2. **Zero-Freeze Archiving (무중단 아카이빙)**: 모든 수집 작업을 백그라운드 워커로 분리하여 성능 보장.
3. **Protocol Virtualization (프로토콜 가상화)**: 커스텀 스킴을 통한 로컬 보안 장벽(Sandbox) 혁파.
4. **Data Integrity (데이터 무결성)**: API 페이로드까지 완벽 박제하여 영구 보존성 극대화.

> **Note**: The archiving features are currently in an active developmental state (WIP).
> **알림**: 아카이빙 및 리플레이 기능은 현재 활발히 개발 중인 단계(WIP)입니다.
