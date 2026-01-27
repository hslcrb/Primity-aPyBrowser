# User Manual Content (Bilingual)

MANUAL_KO = """
# 프리마이티 브라우저 사용 설명서

## 1. 소개
프리마이티(Primity)는 전문가를 위한 초경량 아카이브 특화 브라우저입니다. 
웹의 영구 보존(Archiving)과 한국어 입력 환경에 최적화되어 있습니다.

## 2. 주요 기능 가이드

### ⌨️ 한글 입력 (Omni-Engine)
- **한영 전환**: 키보드의 **[오른쪽 Alt]** 키 또는 툴바의 **[한글 입력]** 버튼을 클릭하세요.
- **특징**: 리눅스 시스템 입력기(fcitx 등) 설정과 무관하게 독자적으로 작동합니다.
- **주소창**: 주소창에서도 동일하게 한글 입력이 가능합니다.

### 📦 웹 아카이빙 (ArchiveBox 통합)
이 브라우저는 ArchiveBox 엔진을 내장하고 있습니다.
- **수동 저장**: 상단 🔴 **[REC]** 버튼을 누르면 현재 페이지가 영구 저장됩니다.
- **고급 저장**: REC 버튼 옆의 화살표(▼)를 눌러 **Advanced Capture**를 선택하면 깊이(Depth) 및 저장 방식(PDF, 스크린샷 등)을 설정할 수 있습니다.
- **자동 저장**: 툴바의 **[Auto]** 버튼을 켜면 방문하는 모든 페이지가 자동으로 저장됩니다.
- **저장된 데이터 확인**: 메뉴(☰) → **Archive Dashboard**에서 확인 및 관리할 수 있습니다.

### ⚙️ 설정 및 데이터 관리
- **저장 위치 변경**: 설정(Settings) → Archive Settings에서 데이터 저장 경로를 변경할 수 있습니다. (Docker 재시작 필요)
- **테마 변경**: 메뉴에서 다크/라이트 모드를 즉시 전환할 수 있습니다.

## 3. 문제 해결
- **한글이 안 써져요**: 오른쪽 Alt 키를 한 번 눌러 상태를 동기화해 주세요.
- **아카이브가 안 돼요**: Docker 컨테이너가 실행 중인지 확인하세요 (`docker ps`). 설정 메뉴에서 저장 경로가 올바른지 확인하세요.

---
© 2026 Rheeworks Inc.
"""

MANUAL_EN = """
# Primity Browser User Manual

## 1. Introduction
Primity is a lightweight, archive-focused browser designed for professionals. 
It is optimized for permanent web preservation and seamless text input.

## 2. Feature Guide

### ⌨️ Korean Input (Omni-Engine)
- **Toggle Language**: Press **[Right Alt]** key or click the **[Korean Input]** button on the toolbar.
- **Feature**: Operates independently of system IMEs (fcitx, etc.).
- **URL Bar**: Korean input is fully supported in the address bar.

### 📦 Web Archiving (ArchiveBox Integration)
This browser integrates the full ArchiveBox engine.
- **Manual Save**: Click the 🔴 **[REC]** button to permanently archive the current page.
- **Advanced Save**: Click the arrow (▼) next to REC and select **Advanced Capture** to configure depth and extractors (PDF, Screenshot, etc.).
- **Auto Save**: Toggle the **[Auto]** button to automatically archive every page you visit.
- **View Archives**: Go to Menu(☰) → **Archive Dashboard** to browse and manage snapshots.

### ⚙️ Settings & Data
- **Storage Location**: Change the data storage path in Settings → Archive Settings. (Requires Docker restart)
- **Themes**: Toggle Dark/Light mode instantly from the menu.

## 3. Troubleshooting
- **Input Issues**: Press Right Alt once to sync the input state.
- **Archive Failed**: Ensure Docker container is running (`docker ps`). Verify storage path in settings.

---
© 2026 Rheeworks Inc.
"""
