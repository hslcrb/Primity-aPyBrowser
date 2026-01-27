# Contributing to Primity (기여 가이드)

> **Note: Korean translation follows the English version below.**
> **알림: 영문 설명 아래에 한국어 번역이 포함되어 있습니다.**

---

# English Version

Thank you for your interest in contributing to the Primity Browser! We welcome all contributions that help make this archive-focused minimal browser better.

## Project Overview
Primity is a PySide6-based web browser with:
- **ArchiveBox Integration** for permanent web archiving
- **Built-in Korean IME** (Omni-Engine v5.1)
- **Monochrome Minimalist Design**

## How to Contribute

### 1. Create an Issue
Start by creating an issue for bug reports or feature requests. Please include:
- Clear description of the problem/suggestion
- Steps to reproduce (for bugs)
- Screenshots if applicable

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

# Start ArchiveBox container (optional, for archiving features)
docker-compose up -d
```

### 4. Branching Strategy
Use clear branch names:
- `feature/archive-dashboard` - New features
- `fix/ime-vowel-bug` - Bug fixes
- `docs/update-readme` - Documentation updates

### 5. Code Guidelines
- **Maintain the monochrome aesthetic**: No vibrant colors in UI
- **Follow existing patterns**: Check `src/core/browser.py` for conventions
- **Comment in bilingual**: Korean first, English second (for key sections)

### 6. Commit Messages
Write detailed commit messages in **Korean first, then English**:
```
기능 추가: 아카이브 대시보드 검색 기능 구현 (Feature: Implement archive dashboard search)
```

### 7. Pull Request
- Provide a thorough explanation of changes
- Reference related issues (`Fixes #123`)
- Include screenshots for UI changes

## Architecture Overview
```
src/
├── core/           # Business logic (browser.py, archive_manager.py, ime_manager.py)
├── ui/             # Styling (styles.py) and components (components.py)
├── config/         # Constants and translations
├── pages/          # Internal pages (settings, passwords, archive_dashboard)
└── utils/          # Helper functions
```

## Testing
```bash
./run.sh
```
Test key features:
- Korean input (한글 입력 버튼 or Right Alt)
- Archive functionality (REC button)
- Theme switching (Menu → Theme)

## License
By contributing, you agree that your code will be licensed under the MIT License.

---

# 한국어 버전

프리마이티 브라우저 기여에 관심을 가져주셔서 감사합니다! 이 아카이브 특화 미니멀 브라우저를 더 훌륭하게 만들기 위한 모든 기여를 환영합니다.

## 프로젝트 개요
프리마이티는 PySide6 기반 웹 브라우저로, 다음을 특징으로 합니다:
- **ArchiveBox 통합**을 통한 영구적 웹 아카이빙
- **내장 한글 입력기** (Omni-Engine v5.1)
- **흑백 미니멀리스트 디자인**

## 기여 방법

### 1. 이슈 생성
버그 리포트나 기능 제안을 위한 이슈를 먼저 생성해 주세요:
- 문제/제안에 대한 명확한 설명
- 재현 단계 (버그의 경우)
- 해당되는 경우 스크린샷 첨부

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

# ArchiveBox 컨테이너 시작 (아카이빙 기능 테스트 시)
docker-compose up -d
```

### 4. 브랜치 전략
명확한 브랜치명을 사용해 주세요:
- `feature/archive-dashboard` - 새 기능
- `fix/ime-vowel-bug` - 버그 수정
- `docs/update-readme` - 문서 업데이트

### 5. 코드 가이드라인
- **흑백 미학 유지**: UI에 화려한 색상 사용 금지
- **기존 패턴 준수**: `src/core/browser.py` 참조
- **한영 병기 주석**: 주요 섹션은 한국어 먼저, 영어 다음

### 6. 커밋 메시지
**한국어를 먼저 작성하고 영어를 병기**해 주세요:
```
기능 추가: 아카이브 대시보드 검색 기능 구현 (Feature: Implement archive dashboard search)
```

### 7. 풀 리퀘스트
- 변경 사항에 대한 상세한 설명 제공
- 관련 이슈 참조 (`Fixes #123`)
- UI 변경 시 스크린샷 포함

## 아키텍처 개요
```
src/
├── core/           # 비즈니스 로직 (browser.py, archive_manager.py, ime_manager.py)
├── ui/             # 스타일링 (styles.py) 및 컴포넌트 (components.py)
├── config/         # 상수 및 번역
├── pages/          # 내부 페이지 (settings, passwords, archive_dashboard)
└── utils/          # 헬퍼 함수
```

## 테스트
```bash
./run.sh
```
주요 기능 테스트:
- 한글 입력 (한글 입력 버튼 또는 오른쪽 Alt)
- 아카이브 기능 (REC 버튼)
- 테마 전환 (메뉴 → Theme)

## 라이선스
기여하신 모든 코드는 MIT 라이선스에 따라 라이선스가 부여되는 것에 동의하는 것으로 간주됩니다.
