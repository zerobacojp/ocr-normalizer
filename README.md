# OCR正規化パイプライン

スキャンされた日本語文書からテキストを抽出し、構造化されたExcel/CSVファイルに変換する自動化ツールです。

## 📋 概要

このプロジェクトは、PDFや画像ファイルから以下の処理を自動で行います：

1. **OCR処理**: PDFまたは画像からテキストを抽出
2. **データ正規化**: 抽出したテキストを解析し、構造化データに変換
3. **Excel/CSV出力**: 整形されたデータをExcelとCSVファイルとして出力

## ✨ 主な機能

- ✅ PDF/画像ファイルから日本語テキストを高精度で抽出
- ✅ 複雑なレイアウトのデータを自動解析
- ✅ 住所、電話番号、メールアドレスを自動分離
- ✅ 全角数字を半角数字に自動変換
- ✅ Excel（.xlsx）とCSV（UTF-8）の両方を出力
- ✅ ログファイルで処理状況を記録

## 📦 システム要件

### 必須要件

- **Python**: 3.8以上
- **Tesseract OCR**: システムにインストール必要
  - 日本語言語パック（`tesseract-ocr-jpn`）
  - 韓国語言語パック（`tesseract-ocr-kor`、オプション）

### Pythonパッケージ

`requirements.txt`に記載されているパッケージ：
- Pillow (画像処理)
- pytesseract (OCRエンジンラッパー)
- PyMuPDF (PDF処理)
- openpyxl (Excel出力)

## 🚀 インストール

### 1. Tesseract OCRのインストール

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-jpn tesseract-ocr-kor
```

#### macOS
```bash
brew install tesseract tesseract-lang
```

#### Windows
[Tesseract GitHub Releases](https://github.com/UB-Mannheim/tesseract/wiki)からインストーラーをダウンロードし、PATHに追加してください。

### 2. Pythonパッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. 動作確認

```bash
# Tesseractが正しくインストールされているか確認
tesseract --version

# 日本語言語パックが利用可能か確認
tesseract --list-langs | grep jpn
```

## 📖 使用方法

### 基本的な使い方

```bash
python run.py <入力ファイルパス>
```

### 例

```bash
# PDFファイルを処理
python run.py imgFile/班長からの役員希望内訳.pdf

# 出力ディレクトリを指定
python run.py input.pdf --output-dir results

# 韓国語でOCR処理
python run.py document.pdf --lang kor

# 高解像度でPDF変換（DPI指定）
python run.py input.pdf --dpi 600
```

### オプション

| オプション | 短縮形 | 説明 | デフォルト |
|-----------|--------|------|-----------|
| `--output-dir` | `-o` | 出力ディレクトリ | `output` |
| `--lang` | `-l` | OCR言語コード | `jpn` |
| `--dpi` | `-d` | PDF変換時の解像度 | `300` |

### ヘルプ表示

```bash
python run.py --help
```

## 📂 出力ファイル

パイプライン実行後、以下のファイルが出力されます：

```
output/
├── <ファイル名>_extracted.txt   # OCR抽出テキスト
├── <ファイル名>_output.xlsx     # Excelファイル
└── <ファイル名>_output.csv      # CSVファイル（UTF-8）
```

### Excelファイルのカラム構成（15カラム）

| カラム名 | 説明 |
|---------|------|
| 班 | 班番号 |
| 氏名 | 名前 |
| 住所 | 住所 |
| TEL | 電話番号（複数可） |
| メールアドレス | メールアドレス |
| 事務局 | 希望部会の優先順位（①②③） |
| 会計 | 希望部会の優先順位（①②③） |
| 書記 | 希望部会の優先順位（①②③） |
| 名簿 | 希望部会の優先順位（①②③） |
| 防犯防災 | 希望部会の優先順位（①②③） |
| 回覧広報 | 希望部会の優先順位（①②③） |
| 地域コミュ | 希望部会の優先順位（①②③） |
| 環境美化 | 希望部会の優先順位（①②③） |
| 厚生福祉 | 希望部会の優先順位（①②③） |
| 補足事項 | 補足情報 |

## 🗂️ プロジェクト構成

```
ocr-normalizer/
│
├── run.py                  # メイン実行スクリプト（パイプライン全体）
├── ocr.py                  # OCRモジュール（PDF/画像 → テキスト）
├── normalize.py            # 正規化モジュール（テキスト解析）
├── to_excel.py             # Excel/CSV出力モジュール
├── textUsingOcr.py         # レガシーOCRスクリプト
│
├── requirements.txt        # Pythonパッケージ依存関係
├── CLAUDE.md              # Claude Code用の開発ガイド
├── README.md              # このファイル
│
├── imgFile/               # 入力ファイル格納ディレクトリ
│   └── 班長からの役員希望内訳.pdf
│
└── output/                # 出力ファイル格納ディレクトリ（自動生成）
    ├── *_extracted.txt
    ├── *_output.xlsx
    └── *_output.csv
```

## 🔧 各モジュールの説明

### 1. `ocr.py` - OCRモジュール

**機能:**
- PDFファイルを画像に変換（PyMuPDF使用）
- 画像からテキストを抽出（Tesseract OCR使用）
- UTF-8エンコーディングでテキストファイルを保存

**単体実行:**
```bash
python ocr.py <ファイルパス> [言語コード]
```

### 2. `normalize.py` - 正規化モジュール

**機能:**
- OCR抽出テキストを解析
- 班番号、氏名、住所、TEL、メールアドレスを抽出
- 全角数字を半角数字に変換
- 希望部会を各部会カラムに展開

**データ正規化ルール:**
- **全角 → 半角**: 数字は全て半角に統一
- **住所・TEL・アドレス分離**: 正規表現で自動分割
- **希望部会展開**: ①②③を対応する部会カラムに配置
- **空値処理**: 空の値は`null`文字列で統一

**単体実行:**
```bash
python normalize.py <テキストファイルパス>
```

### 3. `to_excel.py` - Excel/CSV出力モジュール

**機能:**
- 構造化データからExcelファイルを作成
- CSVファイルを作成（UTF-8エンコーディング）
- カラム幅を自動調整

**単体実行:**
```bash
python to_excel.py <JSONファイル> <出力ファイル>
```

### 4. `run.py` - パイプライン実行スクリプト

**機能:**
- 上記の全モジュールを統合
- ログ出力（コンソール + `pipeline.log`）
- エラーハンドリング

## 📊 処理フロー

```
┌─────────────────┐
│  PDFまたは画像   │
│   ファイル       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   OCR処理       │  ocr.py
│ (Tesseract)     │  - PDFを画像に変換
│                 │  - テキスト抽出
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  テキストファイル │
│   (.txt)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  テキスト解析    │  normalize.py
│  正規化処理      │  - データ抽出
│                 │  - 全角→半角変換
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  構造化データ    │
│   (dict list)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Excel/CSV生成  │  to_excel.py
│                 │  - .xlsx出力
│                 │  - .csv出力
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  出力ファイル    │
│  (.xlsx/.csv)   │
└─────────────────┘
```

## 🐛 トラブルシューティング

### エラー: `tesseract: command not found`

**原因**: Tesseract OCRがインストールされていない、またはPATHに追加されていない

**解決方法**:
```bash
# インストール確認
which tesseract

# インストールされていない場合
sudo apt-get install tesseract-ocr tesseract-ocr-jpn
```

### エラー: `Unable to get page count. Is poppler installed and in PATH?`

**原因**: pdf2imageの依存関係（poppler）が不足している

**解決方法**: PyMuPDFを使用するように修正済み（最新版では発生しません）

### エラー: OCR精度が低い

**原因**: 画像の解像度が低い、または画像品質が悪い

**解決方法**:
```bash
# DPIを上げて処理
python run.py input.pdf --dpi 600
```

### データが正しく抽出されない

**原因**: OCRの誤認識、またはフォーマットが想定と異なる

**解決方法**:
1. `output/*_extracted.txt`を確認してOCR結果を確認
2. `normalize.py`の正規表現パターンを調整
3. より高解像度でOCR処理を実行

## 📝 開発ガイド

### コードスタイル

- Python 3標準
- 関数は単一責任の原則に従う
- UTF-8エンコーディングを使用
- ログ記録を適切に行う

### 新機能の追加

1. `CLAUDE.md`を参照して、プロジェクトの規則を確認
2. 各モジュールは独立して動作可能にする
3. エラーハンドリングを必ず実装
4. テスト用のサンプルデータで動作確認

### デバッグ方法

```bash
# 各モジュールを個別にテスト
python ocr.py test.pdf jpn
python normalize.py test.txt
python to_excel.py data.json output.xlsx

# ログファイルを確認
cat pipeline.log
```

## 📄 ライセンス

このプロジェクトは内部使用を目的としています。

## 🤝 貢献

バグ報告や機能リクエストがある場合は、開発チームにお知らせください。

## 📞 サポート

問題が発生した場合：
1. `pipeline.log`を確認
2. 出力された`*_extracted.txt`を確認してOCR結果を検証
3. 開発者に連絡する際は、エラーメッセージとログファイルを共有

---

**最終更新日**: 2025-12-15
