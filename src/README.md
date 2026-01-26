# Source Code Structure (소스 코드 구조)

This directory contains the core logic and UI components of the Primity Browser.

## Directory Structure (상세 디렉토리 구조)

- **`core/`**: 어플리케이션의 중추 역할을 하는 비즈니스 로직 모듈입니다.
  - `browser.py`: 메인 윈도우 오케스트레이터. 모든 UI 요소와 웹 엔진의 상호작용을 제어하며, 탭 관리 및 브라우저의 전반적인 라이프사이클을 담당합니다.
  - `ime_manager.py`: 프리마이티만의 독자적인 소프트웨어 한글 입력기 매니저. 웹페이지 내부로 JS 오토마타를 주입하고 Python-JS 간의 상태 동기화를 관리합니다.
- **`ui/`**: 순수 디자인 및 스타일링 레이어입니다.
  - `styles.py`: monochrome 테마 시스템의 핵심. CSS 변수(QSS)를 활용하여 다크/라이트 모드를 동적으로 생성하고 테마 일관성을 유지합니다.
  - `components.py`: 커스텀 카드 위젯, 버튼 등 재사용 가능한 UI 컴포넌트들이 정의되어 있어 디자인 중복을 방지합니다.
- **`config/`**: 전역 설정 및 정적 데이터 관리 레이어입니다.
  - `constants.py`: 한영 번역 데이터(i18n), 앱 기본값(홈페이지, 테마, 자판 규격) 등을 상수로 관리하여 코드 변경 없이 설정을 튜닝할 수 있게 합니다.
- **`pages/`**: 브라우저 내부 기능용 특수 웹 레이아웃입니다.
  - `settings.py`: 스크롤 가능한 고도화된 설정 인터페이스. 자판 변경, 홈페이지 설정, 데이터 관리 등을 담당하는 QWidget 기반 페이지입니다.
  - `passwords.py`: 로컬 암호화 저장소를 기반으로 안전하게 자격 증명을 관리하는 전용 관리창입니다.
- **`utils/`**: 독립적으로 동작하는 유틸리티 도구 모음입니다.
  - `helpers.py`: 16자리 강력 암호 생성기 등 브라우저 어디서나 호출 가능한 순수 함수들의 집합입니다.

## Refactoring Goals (리팩토링 목표)

1. **Modularity (모듈화)**: Logic is separated from UI to improve maintainability.
2. **Systematic Division (체계적 분리)**: Files are grouped by responsibility (Logic, UI, Config).
3. **Encapsulation (캡슐화)**: Features like the Software IME are self-contained in dedicated managers.
