# Primity (프리마이티)

> **Note: Korean translation follows the English version below.**
> **알림: 영문 설명 아래에 한국어 번역이 포함되어 있습니다.**

---

# English Version

## Primity Browser
A minimalist, monochrome web browser built with PySide6. Designed for those who seek maximum productivity with zero distractions.

### Key Features
- **Minimalist Design**: A clean, monochrome aesthetic with no unnecessary rounded corners or colorful distractions.
- **Custom Title Bar**: A fully custom window frame that respects your theme choice regardless of the OS.
- **Theme Support**: Real-time switching between High-Contrast Dark and Light modes.
- **Smart Password Suggestion**: Automatically detects password fields and suggests a strong 16-character password (copied to clipboard).
- **Tabbed Management**: Internal pages like Settings and Password Manager open as browser tabs (Chrome-style).
- **Internationalization**: Full support for English and Korean (프리마이티).
- **Cross-Platform**: Automated CI/CD builds for Windows, macOS, and Linux.

### Installation
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage
Run the browser using Python:
```bash
python main.py
```
Or use the convenience script (Linux/macOS):
```bash
./run.sh
```

---

# 한국어 버전

## 프리마이티 브라우저 (Primity Browser)
PySide6를 기반으로 개발된 미니멀리즘 흑백 웹 브라우저입니다. 시각적 방해 요소를 최소화하여 생산성을 극대화하도록 설계되었습니다.

### 주요 기능
- **미니멀리즘 디자인**: 불필요한 라운드나 유채색을 배제한 정갈한 흑백 에스테틱.
- **커스텀 타이틀바**: OS 환경에 구애받지 않고 브라우저 테마를 일관되게 적용한 커스텀 윈도우 프레임.
- **테마 지원**: 고대비 다크 모드와 라이트 모드 간 실시간 전환 기능.
- **스마트 비밀번호 추천**: 비밀번호 필드 감지 시 즉시 16자리 강력한 암호 생성 및 클립보드 복사.
- **탭 기반 관리**: 설정 및 비밀번호 관리자 등 내부 페이지를 크롬 스타일의 탭으로 관리.
- **다국어 지원**: 한국어(프리마이티) 및 영어 완벽 지원.
- **멀티 플랫폼**: Windows, macOS, Linux용 자동 빌드 배포 시스템 구축.

### 설치 방법
1. 저장소를 클론합니다.
2. 의존성 패키지를 설치합니다:
   ```bash
   pip install -r requirements.txt
   ```

### 실행 방법
파이썬으로 브라우저를 실행합니다:
```bash
python main.py
```
또는 실행 스크립트를 사용합니다 (리눅스/맥):
```bash
./run.sh
```
