# 기여 가이드 (Contributing Guide)

Primity Browser 프로젝트에 기여해 주셔서 감사합니다! 이 문서는 프로젝트에 기여하는 방법과 규칙을 설명합니다.

## 기여 방법

1.  **Issue 생성**: 버그를 발견하거나 새로운 기능을 제안하고 싶다면 먼저 GitHub Issue를 생성해 주세요.
2.  **Fork 및 Clone**: 프로젝트를 자신의 계정으로 Fork한 후 로컬에 Clone합니다.
3.  **Branch 생성**: 작업할 내용을 명확히 나타내는 브랜치를 생성하세요 (예: `feature/bookmark`, `fix/crash-bug`).
4.  **코드 작성**: 일관된 코딩 스타일을 유지하며 작업해 주세요.
5.  **Commit 메시지**: 커밋 메시지는 한국어를 우선으로 하고 영어를 병기하며, 상세하게 작성해 주세요. (예: `기능 추가: 즐겨찾기 기능 구현 (Feature: Implement bookmark functionality)`)
6.  **Pull Request**: 작업이 완료되면 원본 저장소로 Pull Request를 보내주세요.

## 개발 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 의존성 설치
pip install -r requirements.txt
```

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 기여하신 코드는 프로젝트의 라이선스에 동의하는 것으로 간주됩니다.

---

# Contributing Guide

Thank you for contributing to the Primity Browser project! This document outlines how to contribute.

## How to Contribute

1.  **Create an Issue**: If you find a bug or want to propose a feature, start by creating a GitHub Issue.
2.  **Fork and Clone**: Fork the repository and clone it locally.
3.  **Create a Branch**: Make a branch for your changes (e.g., `feature/bookmark`, `fix/crash-bug`).
4.  **Code**: Write code consistent with existing styles.
5.  **Commit Messages**: Write detailed commit messages in Korean first, followed by English.
6.  **Pull Request**: Submit a Pull Request to the main repository.

## Setup Development Environment

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
