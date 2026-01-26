# Source Code Structure (소스 코드 구조)

This directory contains the core logic and UI components of the Primity Browser.

## Directory Structure (디렉토리 구조)

- **`core/`**: Non-UI business logic.
  - `browser.py`: Main window logic (orchestrator).
  - `ime_manager.py`: Handles the built-in Software IME state and script injection.
- **`ui/`**: UI-specific components and styling.
  - `styles.py`: Monochrome CSS theme generator and constants.
  - `components.py`: Custom reusable widgets (e.g., `MinimalCard`).
- **`config/`**: Global configuration and translations.
  - `constants.py`: Application defaults and multi-language strings.
- **`pages/`**: Internal browser pages (custom URLs like `primity://settings`).
  - `settings.py`: Advanced settings interface with multi-layout support.
  - `passwords.py`: Secure credential management interface.
- **`utils/`**: General purpose helper functions.
  - `helpers.py`: Password generation and other utilities.

## Refactoring Goals (리팩토링 목표)

1. **Modularity (모듈화)**: Logic is separated from UI to improve maintainability.
2. **Systematic Division (체계적 분리)**: Files are grouped by responsibility (Logic, UI, Config).
3. **Encapsulation (캡슐화)**: Features like the Software IME are self-contained in dedicated managers.
