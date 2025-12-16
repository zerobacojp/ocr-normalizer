# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an OCR (Optical Character Recognition) utility that extracts text from images using Tesseract OCR. The primary focus is on supporting Japanese and Korean languages, with extensibility for other languages.

## Dependencies

- `Pillow` (PIL): Image processing library
- `pytesseract`: Python wrapper for Tesseract OCR engine
- Tesseract OCR must be installed on the system separately

## Core Functionality

The main module `textUsingOcr.py` contains:
- `ocr_image(image_path, lang="jpn")`: Extracts text from an image file
  - Supports multiple languages via the `lang` parameter
  - Common language codes: `jpn` (Japanese horizontal), `jpn_vert` (Japanese vertical), `kor` (Korean), `eng` (English)
  - Returns extracted text as a string

## Running the Code

To use the OCR functionality:

```python
from textUsingOcr import ocr_image

# Extract Japanese text
text = ocr_image("path/to/image.png", lang="jpn")

# Extract Korean text
text = ocr_image("path/to/image.png", lang="kor")
```

## System Requirements

Tesseract OCR must be installed with appropriate language packs:
- On Ubuntu/Debian: `sudo apt-get install tesseract-ocr tesseract-ocr-jpn tesseract-ocr-kor`
- On macOS: `brew install tesseract tesseract-lang`
- On Windows: Download from GitHub releases and add to PATH

-------
#(추가)
# Project: OCR → 정규화 → CSV/Excel 파이프라인

## 목적
- 스캔된 일본어/한국어 문서에서 텍스트를 추출(OCR)하고,
- 이를 규칙 기반으로 정규화하여,
- 구조화된 CSV/Excel 파일로 변환하는 자동화 파이프라인을 구축한다.

## 데이터 규칙

- **인코딩:**
  - 모든 텍스트 파일과 CSV는 UTF-8로 저장할 것.
- **날짜 형식:**
  - 입력: `2024/1/3`, `2024-1-3`, `2024年1月3日` 등 다양한 형식 가능.
  - 출력: 반드시 `YYYY-MM-DD` 형식으로 통일 (예: `2024-01-03`).
- **빈 값 처리:**
  - 의미 없는 빈 값은 `null` 문자열로 채운다.
- **숫자:**
  - 전각 숫자는 반각 숫자로 변환한다.
- **언어:**
  - 일본어(`jpn`, `jpn_vert`)와 한국어(`kor`) OCR을 주로 사용한다.

## 코드 스타일

- Python 3 기준.
- 함수는 한 가지 역할만 수행하도록 나눌 것.
- 파일 이름 예:
  - `ocr.py` : 이미지 → 텍스트
  - `normalize.py` : 텍스트 정규화
  - `to_csv.py` : 구조화 → CSV
  - `run.py` : 전체 파이프라인 실행
- 예외 발생 시 가능한 한 `try/except`로 잡고, 로그를 남긴다.

## OCR 규칙

- Tesseract + pytesseract 사용.
- 기본 언어는 `jpn`으로, 필요 시 `jpn_vert` 또는 `kor` 사용.
- OCR 전처리(회전, 노이즈 제거)가 필요해 보이면, 먼저 제안한 뒤 코드에 반영해라.

## CSV/Excel 규칙

- CSV는 쉼표(,) 구분, UTF-8 인코딩.
- Excel은 `.xlsx` 형식, 헤더 포함.
- 컬럼 순서는 다음을 기본으로 한다(필요 시 수정 가능):
  - `date`, `name`, `role`, `value1`, `value2`, `raw_text`

## Claude Code에 대한 요청

- 이 프로젝트 폴더 내에서 작업할 때는 항상 이 규칙을 우선적으로 따른다.
- 파일을 생성/수정할 때는:
  - 변경 이유를 간단히 설명하고,
  - 중요한 로직에는 주석을 추가한다.
- 정규화 규칙을 변경할 때는:
  - 기존 규칙과의 차이를 설명하고,
  - 예시 입력/출력 샘플을 함께 제시한다.
