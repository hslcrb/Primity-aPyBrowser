# Primity (프리마이티) - Archive-Focused Minimalist Browser

> **Modern, Monochrome, Modular, Archive-Ready.**

---

# English Version (EN)

## Introduction
Primity is a high-performance, minimalist web browser built with PySide6 and QtWebEngine. It is designed for developers, researchers, and power users who value focus, purity, and **permanent archiving of web content**. Version 0.0.57 introduces complete **ArchiveBox integration** for professional-grade web archiving.

## 🌟 Key Features

### 📦 Web Archiving (ArchiveBox Integration)
- **One-Click Archive**: Hit the REC button to permanently save any webpage
- **Advanced Capture Options**: Configure depth, extractors (wget, singlefile, screenshot, PDF, etc.)
- **Native Dashboard**: Browse, search, and manage archived pages directly within the browser
- **Hybrid Integration**: Docker CLI for archiving + Direct SQLite access for fast data queries

### ⌨️ Built-in Korean IME (Omni-Engine v5.1)
- **Full State-Machine Hangul Automata**: Handles complex syllables and liaison ('국가와', '세계', '앉아') flawlessly
- **OS-Independent**: Works without any system IME (fcitx/ibus) configuration
- **Multiple Layouts**: Dubeolshik (2-set), Sebeolshik 390, Sebeolshik Final

### 🎨 Professional Design
- **Monochrome Minimalism**: Pure black/white/gray aesthetic with zero distractions
- **Custom Frameless Window**: Fully integrated title bar with native controls
- **Real-time Theme Toggle**: Seamless Dark/Light mode switching

### 🚀 Modern Web Technologies
- **HTTP/3 (QUIC) Support**: Enabled for blazing-fast connections
- **Security Indicators**: Visual HTTPS/HTTP lock icons
- **Bookmark Collections**: Organize favorites into categorized folders
- **Data Import/Export**: Full browser profile backup as JSON

## 🛠 Project Structure
```
Primity-aPyBrowser/
├── main.py                 # Application entry point
├── src/
│   ├── core/               # Business logic
│   │   ├── browser.py      # Main window orchestrator
│   │   ├── archive_manager.py  # ArchiveBox integration
│   │   └── ime_manager.py  # Korean IME manager
│   ├── ui/                 # Styling and components
│   ├── config/             # Translations and defaults
│   └── pages/              # Internal pages (settings, passwords, archive dashboard)
├── assets/                 # Icons and scripts
├── vendor/ArchiveBox/      # ArchiveBox source (vendored)
└── data/                   # ArchiveBox data directory
```

## 🚀 Quick Start
```bash
# Clone and setup
git clone https://github.com/hslcrb/Primity-aPyBrowser.git
cd Primity-aPyBrowser
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run
./run.sh
```

## 📦 ArchiveBox Setup
The browser automatically starts the ArchiveBox Docker container on first run.
```bash
# Manual start (if needed)
docker-compose up -d
```

Access the Archive Dashboard: Menu (☰) → **Archive Dashboard (Pro)**

---

# 한국어 버전 (KO)

## 소개
프리마이티(Primity)는 PySide6와 QtWebEngine 기반의 고성능 미니멀리즘 웹 브라우저입니다. 본질에 집중하고자 하는 개발자, 연구자, 고급 사용자를 위해 설계되었으며, **웹 콘텐츠의 영구 보존**에 특화되어 있습니다. v0.0.57에서는 **ArchiveBox 완전 통합**을 통해 전문가급 웹 아카이빙 기능을 제공합니다.

## 🌟 주요 기능

### 📦 웹 아카이빙 (ArchiveBox 통합)
- **원클릭 아카이브**: REC 버튼 하나로 어떤 웹페이지든 영구 저장
- **고급 캡처 옵션**: 깊이(depth), 추출기(wget, singlefile, screenshot, PDF 등) 세밀 설정
- **네이티브 대시보드**: 브라우저 내에서 아카이브된 페이지 검색, 열람, 관리
- **하이브리드 통합**: Docker CLI로 아카이빙 + SQLite 직접 접근으로 빠른 데이터 조회

### ⌨️ 내장 한글 입력기 (Omni-Engine v5.1)
- **상태 머신 기반 한글 오토마타**: '국가와', '세계', '앉아' 등 복잡한 조합과 연음 법칙 완벽 처리
- **OS 독립**: 시스템 입력기(fcitx/ibus) 설정 없이 작동
- **다중 자판 지원**: 두벌식 표준, 세벌식 390, 세벌식 최종

### 🎨 전문가용 디자인
- **흑백 미니멀리즘**: 순수한 흑/백/회색 기반의 집중력 높은 디자인
- **커스텀 프레임리스 윈도우**: 네이티브 컨트롤이 통합된 전용 타이틀바
- **실시간 테마 전환**: 다크/라이트 모드 즉시 전환

### 🚀 최신 웹 기술
- **HTTP/3 (QUIC) 지원**: 차세대 프로토콜로 초고속 연결
- **보안 표시기**: 주소창 자물쇠 아이콘으로 HTTPS/HTTP 구분
- **북마크 컬렉션**: 즐겨찾기를 폴더별로 체계적 관리
- **데이터 가져오기/내보내기**: JSON 형식의 전체 프로필 백업

## 🛠 설치 및 실행
```bash
# 클론 및 설정
git clone https://github.com/hslcrb/Primity-aPyBrowser.git
cd Primity-aPyBrowser
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 실행
./run.sh
```

## 📦 ArchiveBox 설정
브라우저 첫 실행 시 ArchiveBox Docker 컨테이너가 자동으로 시작됩니다.

대시보드 접근: 메뉴(☰) → **Archive Dashboard (Pro)**

---

## License
MIT License - See [LICENSE](LICENSE) for details.
