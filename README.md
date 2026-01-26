# Primity (프리마이티)

> **Note: Korean translation follows the English version below.**
> **알림: 영문 설명 아래에 한국어 번역이 포함되어 있습니다.**

---

# English Version

## Primity Browser
A minimalist, monochrome web browser built with PySide6. Designed for users who demand purity and focus. Primity features an independent, built-in Software IME to solve the long-standing "Korean input bug" on Linux.

### 🚀 Key Features
- **Independent Software IME**: A custom Hangul automata integrated directly into the browser. Type Korean ('국가와' etc.) flawlessly regardless of Linux version or OS IME settings.
- **Multi-Layout Support**: Switch between **Dubeolshik**, **Sebeolshik 390**, and **Sebeolshik Final** instantly in settings.
- **Minimalist Design**: Zero distractions. A pure monochrome aesthetic with a custom title bar and refined tab management.
- **High Contrast Themes**: Real-time switching between professional Dark and Light modes.
- **Custom Title Bar**: A consistent window experience across all operating systems.
- **Smart Address Bar**: Automatically distinguishes between URLs and search queries (directs to Google).
- **Favicon Support**: Visual site identification with a minimal globe icon fallback.
- **Password Manager**: Secure internal page for managing credentials with 16-character strong password generation.

### 🛠 Installation
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 💻 Usage
Run the browser:
```bash
./run.sh
```
*Toggle Korean Input:* Click the **[Korean Input]** button in the toolbar or press the **Right Alt** key.

---

# 한국어 버전

## 프리마이티 브라우저 (Primity Browser)
PySide6 기반의 미니멀리즘 흑백 웹 브라우저입니다. 오직 본질에만 집중하고자 하는 사용자를 위해 설계되었습니다. 리눅스 환경에서 고질적으로 발생하는 '한글 입력 오류'를 완벽히 해결하기 위해 독자적인 **내장형 소프트웨어 입력기(Software IME)**를 탑재했습니다.

### 🚀 주요 기능
- **독립형 한글 입력기 (Software IME)**: 브라우저에 직접 통합된 한글 오토마타 엔진. 리눅스 버전이나 OS 입력(Fcitx/IBus) 설정에 구애받지 않고 '국가와' 같은 복잡한 글자도 완벽하게 입력 가능합니다.
- **다중 자판 레이아웃**: **두벌식 표준**, **세벌식 390**, **세벌식 최종** 자판을 설정에서 즉시 변경할 수 있습니다.
- **미니멀리즘 디자인**: 시각적 방해 요소를 제거한 정갈한 흑백 디자인과 커스텀 상단바.
- **고대비 테마**: 전문가를 위한 다크 모드 및 라이트 모드 실시간 전환 지원.
- **스마트 주소창**: URL과 검색어를 지능적으로 구분하여 자동으로 구글 검색으로 연결.
- **파비콘 지원**: 개별 사이트 아이콘 표시 및 미니멀 지구본 기본 아이콘 제공.
- **비밀번호 관리자**: 내장 페이지를 통한 보안 관리 및 16자리 강력 암호 생성 기능.

### 🛠 설치 방법
1. 저장소를 클론합니다.
2. 의존성 패키지를 설치합니다:
   ```bash
   pip install -r requirements.txt
   ```

### 💻 사용 방법
브라우저 실행:
```bash
./run.sh
```
*한글 전환:* 툴바의 **[한글 입력]** 버튼을 누르거나 키보드의 **오른쪽 Alt 키**를 누르세요.
