# Source Code Structure (소스 코드 구조)

> This directory contains the core logic and UI components of the Primity Browser.
> 이 디렉토리에는 프리마이티 브라우저의 핵심 로직 및 UI 컴포넌트가 포함되어 있습니다.

---

## Directory Structure (디렉토리 구조)

```
src/
├── core/                   # 비즈니스 로직 레이어
│   ├── browser.py          # 메인 윈도우 오케스트레이터
│   ├── archive_manager.py  # ArchiveBox 하이브리드 통합 매니저
│   └── ime_manager.py      # 한글 IME 매니저
├── ui/                     # 디자인 레이어
│   ├── styles.py           # 테마 시스템 (Dark/Light)
│   ├── components.py       # 재사용 가능한 UI 컴포넌트
│   └── archive_config.py   # 아카이브 설정 다이얼로그
├── config/                 # 설정 레이어
│   └── constants.py        # 번역 데이터 및 기본값
├── pages/                  # 내부 페이지
│   ├── settings.py         # 설정 페이지
│   ├── passwords.py        # 비밀번호 관리자
│   └── archive_dashboard.py # 아카이브 대시보드
└── utils/                  # 유틸리티
    └── helpers.py          # 암호 생성기 등 헬퍼 함수
```

---

## Module Details (모듈 상세)

### `core/` - Business Logic

**`browser.py`**
- 메인 윈도우 오케스트레이터
- 탭 관리, 내비게이션, 북마크 시스템
- 모든 UI 요소와 웹 엔진의 상호작용 제어

**`archive_manager.py`** ⭐ NEW
- ArchiveBox 하이브리드 통합 매니저
- Docker CLI를 통한 아카이빙 작업 (add, remove)
- SQLite 직접 접근을 통한 데이터 조회 (스냅샷 목록, 검색, 상세 정보)
- Python 3.12 호환성 유지하면서 ArchiveBox 기능 활용

**`ime_manager.py`**
- 소프트웨어 한글 입력기 매니저
- 웹페이지에 JS 오토마타(`assets/hangul_ime.js`) 주입
- Python-JS 간 상태 동기화

### `ui/` - Design Layer

**`styles.py`**
- CSS 변수 기반 테마 시스템
- `DARK_VARS` / `LIGHT_VARS` 딕셔너리로 색상 관리
- `get_stylesheet()` 함수로 동적 스타일 생성

**`components.py`**
- `MinimalCard`: 내부 페이지용 카드 위젯
- `BookmarkDialog`: 크롬 스타일 북마크 편집 다이얼로그

**`archive_config.py`** ⭐ NEW
- `ArchiveConfigDialog`: 고급 아카이브 설정 (깊이, 추출기 선택)

### `config/` - Configuration

**`constants.py`**
- `TRANSLATIONS`: 한/영 번역 데이터 (i18n)
- `DEFAULT_SETTINGS`: 앱 기본값 (홈페이지, 테마, 자판 등)

### `pages/` - Internal Pages

**`settings.py`**
- 스크롤 가능한 설정 인터페이스
- 언어, 테마, 홈페이지, 자판 설정
- 데이터 내보내기/가져오기

**`passwords.py`**
- 로컬 저장 기반 자격 증명 관리

**`archive_dashboard.py`** ⭐ NEW
- 네이티브 ArchiveBox 대시보드
- 스냅샷 목록 조회, 검색, 삭제
- 현재 페이지 즉시 아카이브 버튼

### `utils/` - Utilities

**`helpers.py`**
- `generate_strong_password()`: 16자리 강력 암호 생성

---

## Design Principles (설계 원칙)

1. **Modularity (모듈화)**: 로직과 UI를 분리하여 유지보수성 향상
2. **Hybrid Integration (하이브리드 통합)**: 외부 도구(ArchiveBox)를 CLI + DB 직접 접근으로 유연하게 통합
3. **OS Independence (OS 독립)**: 시스템 IME 없이 작동하는 내장 한글 입력기
4. **Monochrome Aesthetic (흑백 미학)**: 일관된 미니멀리스트 디자인 유지
