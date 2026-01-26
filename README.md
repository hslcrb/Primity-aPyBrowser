# Primity (프리마이티) - Professional Minimalist Browser

> **Modern, Monochrome, Modular.**

---

# English Version (EN)

## Introduction
Primity is a high-performance, minimalist web browser built with PySide6. It is designed for developers and power users who value focus and purity. Version 0.0.32 introduces a completely refactored modular architecture and professional-grade internal IME.

## 🌟 Key Features
- **Independent Software IME**: Full state-machine Hangul automata. Handles complex syllables and liaison ('국가와', '앉아') flawlessly without OS dependencies.
- **Modular Architecture**: Reorganized source code for high maintainability. Logical separation of Core, UI, Config, and Pages.
- **Advanced Data Management**: Export and Import your entire browser profile (bookmarks, settings) as a JSON file.
- **HTTP/3 (QUIC) Support**: Fully enabled latest transmission protocols for blazing-fast browsing.
- **Refined Navigation UX**:
  - **Animated Reload**: Real-time status feedback (Yellow: Loading, Green: Success).
  - **Bookmark Collections**: Organize your favorite sites into categorized folders.
  - **Embedded Security Indicators**: Visual HTTPS/HTTP status without sacrificing UI space.
- **High Contrast Professionals Themes**: Seamless real-time switching between professional Dark and Light modes.

## 🛠 Project Structure
- `src/core`: Main logic and managers.
- `src/ui`: Styling and layouts.
- `src/config`: Translations and defaults.
- `src/pages`: Internal secure pages.

---

# 한국어 버전 (KO)

## 소개 (Introduction)
프리마이티(Primity)는 PySide6를 기반으로 제작된 고성능 미니멀리즘 웹 브라우저입니다. 본질에 집중하고자 하는 전문가와 고급 사용자를 위해 설계되었습니다. 이번 v0.0.32 업데이트에서는 체계적인 **소스코드 모듈화**와 **프로급 내장 한글 입력기**를 탑재했습니다.

## 🌟 주요 기능
- **독립형 소프트웨어 IME**: 상태 머신 기반의 고성능 한글 오토마타. '국가와', '앉아', '읽기' 등 복잡한 조합과 연음 법칙을 OS 입력기 없이 완벽하게 처리합니다.
- **체계적 모듈화 (Modular)**: 소스코드를 기능별(Core, UI, Config, Pages)로 철저히 분리하여 높은 유지보수성과 확장성을 확보했습니다.
- **고급 데이터 관리**: 북마크 컬렉션 및 모든 브라우저 설정을 JSON 형식으로 내보내거나 가져올 수 있습니다.
- **최신 기술 지원 (HTTP/3)**: Chromium 엔진의 QUIC 지원을 활성화하여 차세대 웹 환경에서의 압도적인 속도를 제공합니다.
- **고도화된 내비게이션 UX**:
  - **애니메이션 새로고침**: 진행 단계별 색상 변화(노란색: 로딩, 초록색: 완료)로 직관적인 피드백 제공.
  - **북마크 컬렉션**: 즐겨찾기를 카테고리별 폴더로 세분화하여 체계적으로 관리.
  - **전용 보안 표시기**: 주소창 내 별도의 자물쇠 아이콘으로 보안 연결 상태 구분.
- **전문가용 고대비 테마**: 눈이 편안한 흑백 기반의 다크 모드와 세련된 라이트 모드 실시간 전환.

## 🛠 설치 및 실행
```bash
./run.sh
```
*한글 전환:* 툴바의 **[한글 입력]** 버튼 또는 키보드의 **오른쪽 Alt 키**를 활용하세요.
