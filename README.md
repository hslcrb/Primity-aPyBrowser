# Primity (프리마이티) - Archive-Focused Minimalist Browser

> **Modern, Monochrome, Modular, Archive-Ready.**

---

# English Version (EN)

## Introduction
Primity is a high-performance, minimalist web browser built with PySide6 and QtWebEngine. It is designed for developers, researchers, and power users who value focus, purity, and **permanent archiving of web content**. Version 0.2.0 introduces a **Native Archiving Engine** (No Docker required) with high-fidelity replay capabilities.

> **⚠️ Warning**: The Web Archiving feature is currently **Under Development**. Experimental features may change or move.

## 🌟 Key Features

### 📦 Web Archiving (Native Engine - WIP)
- **One-Click Archive**: Hit the REC button to permanently save any webpage with a native "Breathing Aura" visual indicator.
- **High-Fidelity Replay**: Uses a custom `primity-archive://` virtual protocol to bypass security sandboxes, ensuring complex SPA sites (React, etc.) replay perfectly.
- **Real Data Vacuum**: Captures actual network payloads (JSON/Binary) into a local SQLite database for authentic offline reproduction.
- **URL Masking**: Even when viewing an archive, the address bar shows the original website URL for a seamless "Time Machine" experience.
- **No Docker Required**: Everything runs in pure Python/Qt for maximum portability.

### ⌨️ Built-in Korean IME (Omni-Engine v5.1)
- **Full State-Machine Hangul Automata**: Handles complex syllables and liaison ('국가와', '세계', '앉아') flawlessly.
- **OS-Independent**: Works without any system IME (fcitx/ibus) configuration.
- **Multiple Layouts**: Dubeolshik (2-set), Sebeolshik 390, Sebeolshik Final.

### 🎨 Professional Design
- **Monochrome Minimalism**: Pure black/white/gray aesthetic with zero distractions.
- **Native Overlay UI**: Professional recording indicators drawn directly on the browser frame.
- **Real-time Theme Toggle**: Seamless Dark/Light mode switching.

### 🚀 Modern Web Technologies
- **HTTP/3 (QUIC) Support**: Enabled for blazing-fast connections.
- **Bypass Mode**: Pre-configured security flags for advanced web forensic tasks.
- **Bookmark Collections**: Organize favorites into categorized folders.

## 🛠 Project Structure
```
Primity-aPyBrowser/
├── main.py                 # Application entry point & Global Scheme registration
├── src/
│   ├── core/               # Business logic
│   │   ├── browser.py      # Native UI orchestrator & Custom Scheme Handler
│   │   ├── archive_manager.py  # Async archiving orchestration
│   │   ├── archivebox_core/ # Internal native archiving engine (Python-based)
│   │   └── ime_manager.py  # Korean IME manager
│   ├── ui/                 # Styling and components
│   └── pages/              # Internal pages (settings, archive dashboard)
├── assets/                 # Icons, hooks.js, and replay.js
└── data/                   # Archiving database and asset storage
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

---

# 한국어 버전 (KO)

## 소개
프리마이티(Primity)는 PySide6와 QtWebEngine 기반의 고성능 미니멀리즘 웹 브라우저입니다. 본질에 집중하고자 하는 개발자, 연구자, 고급 사용자를 위해 설계되었으며, **웹 콘텐츠의 영구 보존**에 특화되어 있습니다. v0.2.0에서는 Docker 없이 작동하는 **네이티브 아카이빙 엔진**과 완벽한 재현(Replay) 시스템을 탑재했습니다.

> **⚠️ 알림**: 웹 아카이빙 기능은 현재 **개발 중(WIP)** 입니다. 실험적인 기능들이 포함되어 있습니다.

## 🌟 주요 기능

### 📦 웹 아카이빙 (네이티브 엔진 - 개발 중)
- **원클릭 아카이브**: REC 버튼 클릭 시 브라우저 프레임에 "숨쉬는 붉은 오라"가 생성되며 실시간 기록을 시작합니다.
- **완벽한 재현 (High-Fidelity)**: `primity-archive://` 가상 프로토콜을 도입하여 로컬 보안 제약을 우회, 리액트 등 복잡한 SPA 사이트도 완벽하게 리플레이합니다.
- **데이터 진공청소기**: 서버에서 받아오는 실제 데이터 페이로드(JSON/바이너리)를 SQLite에 실시간 박제하여 오프라인에서도 웹이 살아 움직이게 합니다.
- **주소창 URL 마스킹**: 아카이브 열람 중에도 주소창에 원본 사이트의 URL을 표시하여 진정한 '타임머신' 경험을 제공합니다.
- **Docker 필요 없음**: 복잡한 설정 없이 파이썬 환경에서 즉시 구동됩니다.

### ⌨️ 내장 한글 입력기 (Omni-Engine v5.1)
- **상태 머신 기반 한글 오토마타**: '국가와', '세계', '앉아' 등 복잡한 조합과 연음 법칙 완벽 처리.
- **OS 독립**: 리눅스 등에서 시스템 입력기(fcitx/ibus) 설정 없이 즉시 타이핑 가능.
- **다중 자판 지원**: 두벌식 표준, 세벌식 390, 세벌식 최종.

### 🎨 전문가용 디자인
- **흑백 미니멀리즘**: 집중력을 극대화하는 순수 흑/백/회색 기반의 정갈한 디자인.
- **네이티브 오버레이**: 웹사이트를 침범하지 않고 브라우저 레이어에서 직접 그리는 고급스러운 녹화 UI.
- **실시간 테마 전환**: 다크/라이트 모드 즉시 전환.

### 🚀 최신 웹 기술
- **HTTP/3 (QUIC) 지원**: 차세대 프로토콜로 초고속 연결 보장.
- **보안 정책 우회**: 웹 포렌식 및 아카이빙을 위한 강력한 보안 컨트롤 플래그 적용.
- **북마크 컬렉션**: 즐겨찾기를 폴더별로 체계적으로 관리.

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

---

## License
MIT License - See [LICENSE](LICENSE) for details.
