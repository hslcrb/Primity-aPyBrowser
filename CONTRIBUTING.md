# Contributing to Primity (기여 가이드)

> **Note: Korean translation follows the English version below.**
> **알림: 영문 설명 아래에 한국어 번역이 포함되어 있습니다.**

---

# English Version

Thank you for your interest in contributing to the Primity Browser! We welcome all contributions that help make this archive-focused minimal browser better.

## Project Overview
Primity is a PySide6-based web browser with:
- **Native Archiving Engine** (Currently Under Development) for high-fidelity web forensics
- **Built-in Korean IME** (Omni-Engine v5.1)
- **Monochrome Minimalist Design**

## How to Contribute

### 1. Create an Issue
Start by creating an issue for bug reports or feature requests. Please include:
- Clear description of the problem/suggestion
- Steps to reproduce (for bugs)
- Samples of target websites (for archiving bugs)

### 2. Fork and Clone
```bash
git clone https://github.com/YOUR_USERNAME/Primity-aPyBrowser.git
cd Primity-aPyBrowser
```

### 3. Development Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
*Note: Docker is no longer required as of v0.2.0.*

### 4. Branching Strategy
Use clear branch names:
- `feature/aura-ui` - New features
- `fix/masking-bug` - Bug fixes
- `docs/update-spec` - Documentation updates

### 5. Code Guidelines
- **Maintain the monochrome aesthetic**: Red is reserved only for REC state (The Aura).
- **Native Protocol Caution**: Be careful when modifying the `ArchiveSchemeHandler` as it bypasses critical security layers.
- **Comment in bilingual**: Korean first, English second (for key sections).

### 6. Commit Messages
Write detailed commit messages with version tags in **Korean first, then English**:
```
버그 수정: 아카이브 열람 시 스크립트 실행 차단 오류 해결 (Fix: Resolved script execution block in archive viewer v0.x.x)
```

### 7. Pull Request
- Provide a thorough explanation of changes.
- Reference related issues (`Fixes #123`).
- Include a demo video or screenshots for UI/Archiving changes.

## Architecture Overview
```
src/
├── core/           
│   ├── browser.py         # Main orchestrator & Native UI Container
│   ├── archive_manager.py # Async Worker orchestration
│   ├── archivebox_core/   # Native archiving engine logic
│   └── ime_manager.py     # Korean IME manager
├── pages/                 # Internal dashboards
└── ui/                    # Global styling & components
```

---

# 한국어 버전

프리마이티 브라우저 기여에 관심을 가져주셔서 감사합니다! 이 아카이브 특화 미니멀 브라우저를 더 훌륭하게 만들기 위한 모든 기여를 환영합니다.

## 프로젝트 개요
프리마이티는 PySide6 기반 웹 브라우저로, 다음을 특징으로 합니다:
- **네이티브 아카이빙 엔진** (현재 개발 중) - 고정밀 웹 보존 기술
- **내장 한글 입력기** (Omni-Engine v5.1)
- **흑백 미니멀리스트 디자인**

## 기여 방법

### 1. 이슈 생성
버그 리포트나 기능 제안을 위한 이슈를 먼저 생성해 주세요:
- 문제/제안에 대한 명확한 설명
- 재현 단계 (버그의 경우)
- 아카이빙 관련 버그의 경우 대상 웹사이트 URL 포함

### 2. 포크 및 클론
```bash
git clone https://github.com/YOUR_USERNAME/Primity-aPyBrowser.git
cd Primity-aPyBrowser
```

### 3. 개발 환경 설정
```bash
# 가상환경 생성
python -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```
*참고: v0.2.0 버전부터 더 이상 Docker가 필요하지 않습니다.*

### 4. 브랜치 전략
명확한 브랜치명을 사용해 주세요:
- `feature/aura-ui` - 새 기능
- `fix/masking-bug` - 버그 수정
- `docs/update-spec` - 문서 업데이트

### 5. 코드 가이드라인
- **흑백 미학 유지**: 붉은색은 오직 REC 상태(오라 효과)를 위해서만 예약되어 있습니다.
- **네이티브 프로토콜 주의**: `ArchiveSchemeHandler`는 중요한 보안 레이어를 우회하므로 수정 시 각별한 주의가 필요합니다.
- **한영 병기 주석**: 주요 섹션은 한국어 먼저, 영어 다음.

### 6. 커밋 메시지
버전 태그를 포함하여 **한국어를 먼저 작성하고 영어를 병기**해 주세요:
```
버그 수정: 아카이브 열람 시 스크립트 실행 차단 오류 해결 (Fix: Resolved script execution block in archive viewer v0.x.x)
```

### 7. 풀 리퀘스트
- 변경 사항에 대한 상세한 설명 제공.
- 관련 이슈 참조 (`Fixes #123`).
- UI 또는 아카이브 기능 변경 시 데모 영상이나 스크린샷 포함.

## 아키텍처 개요
```
src/
├── core/           
│   ├── browser.py         # 메인 오케스트레이터 및 네이티브 UI 컨테이너
│   ├── archive_manager.py # 비동기 워커 관리
│   ├── archivebox_core/   # 네이티브 아카이빙 엔진 로직
│   └── ime_manager.py     # 한글 입력기 매니저
├── pages/                 # 내부 대시보드 페이지
└── ui/                    # 전역 스타일링 및 컴포넌트
```

---

## License
MIT License.
