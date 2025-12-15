#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR モジュール: PDF/画像からテキストを抽出
PDFファイルを画像に変換してからOCR処理を行う
"""

from PIL import Image
import pytesseract
import fitz  # PyMuPDF
import io
import logging
import os

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_text_from_image(image, lang="jpn"):
    """
    画像オブジェクトからテキストを抽出

    Args:
        image: PIL Image オブジェクト
        lang (str): OCR言語 (デフォルト: jpn)

    Returns:
        str: 抽出されたテキスト
    """
    try:
        text = pytesseract.image_to_string(image, lang=lang)
        return text
    except Exception as e:
        logger.error(f"OCR処理中にエラーが発生しました: {str(e)}")
        raise


def pdf_to_images(pdf_path, dpi=300):
    """
    PDFファイルを画像のリストに変換（PyMuPDFを使用）

    Args:
        pdf_path (str): PDFファイルのパス
        dpi (int): 画像の解像度 (デフォルト: 300)

    Returns:
        list: PIL Imageオブジェクトのリスト
    """
    try:
        logger.info(f"PDFを画像に変換中: {pdf_path}")
        images = []

        # PDFを開く
        pdf_document = fitz.open(pdf_path)

        # 各ページを画像に変換
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]

            # DPIに基づいてズーム倍率を計算（72 DPI がデフォルト）
            zoom = dpi / 72
            mat = fitz.Matrix(zoom, zoom)

            # ページを画像に変換
            pix = page.get_pixmap(matrix=mat)

            # PyMuPDFのPixmapをPIL Imageに変換
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            images.append(img)

        pdf_document.close()
        logger.info(f"{len(images)}ページを変換しました")
        return images
    except Exception as e:
        logger.error(f"PDF変換中にエラーが発生しました: {str(e)}")
        raise


def process_pdf(pdf_path, output_text_path=None, lang="jpn", dpi=300):
    """
    PDFファイルからテキストを抽出してファイルに保存

    Args:
        pdf_path (str): 入力PDFファイルのパス
        output_text_path (str, optional): 出力テキストファイルのパス
        lang (str): OCR言語 (デフォルト: jpn)
        dpi (int): 画像の解像度

    Returns:
        tuple: (抽出されたテキスト, 出力ファイルパス)
    """
    try:
        # ファイルの存在確認
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")

        # PDFを画像に変換
        images = pdf_to_images(pdf_path, dpi=dpi)

        # 各ページからテキストを抽出
        all_text = []
        for i, image in enumerate(images, 1):
            logger.info(f"ページ {i}/{len(images)} をOCR処理中...")
            text = extract_text_from_image(image, lang=lang)
            all_text.append(f"=== ページ {i} ===\n{text}\n")

        # 全テキストを結合
        combined_text = "\n".join(all_text)

        # 出力パスが指定されていない場合、自動生成
        if output_text_path is None:
            base_name = os.path.splitext(pdf_path)[0]
            output_text_path = f"{base_name}.txt"

        # UTF-8エンコーディングで保存
        with open(output_text_path, 'w', encoding='utf-8') as f:
            f.write(combined_text)

        logger.info(f"テキストファイルを保存しました: {output_text_path}")
        logger.info(f"抽出されたテキスト: {len(combined_text)} 文字")

        return combined_text, output_text_path

    except Exception as e:
        logger.error(f"処理中にエラーが発生しました: {str(e)}")
        raise


def process_image_file(image_path, output_text_path=None, lang="jpn"):
    """
    画像ファイルからテキストを抽出してファイルに保存

    Args:
        image_path (str): 入力画像ファイルのパス
        output_text_path (str, optional): 出力テキストファイルのパス
        lang (str): OCR言語

    Returns:
        tuple: (抽出されたテキスト, 出力ファイルパス)
    """
    try:
        # ファイルの存在確認
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"画像ファイルが見つかりません: {image_path}")

        logger.info(f"画像を読み込んでいます: {image_path}")
        image = Image.open(image_path)

        # OCR処理
        logger.info(f"OCR処理中 (言語: {lang})...")
        text = extract_text_from_image(image, lang=lang)

        # 出力パスが指定されていない場合、自動生成
        if output_text_path is None:
            base_name = os.path.splitext(image_path)[0]
            output_text_path = f"{base_name}.txt"

        # UTF-8エンコーディングで保存
        with open(output_text_path, 'w', encoding='utf-8') as f:
            f.write(text)

        logger.info(f"テキストファイルを保存しました: {output_text_path}")
        logger.info(f"抽出されたテキスト: {len(text)} 文字")

        return text, output_text_path

    except Exception as e:
        logger.error(f"処理中にエラーが発生しました: {str(e)}")
        raise


if __name__ == "__main__":
    # テスト用コード
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python ocr.py <ファイルパス> [言語コード]")
        print("例: python ocr.py file.pdf jpn")
        print("   python ocr.py image.png jpn")
        sys.exit(1)

    file_path = sys.argv[1]
    lang_code = sys.argv[2] if len(sys.argv) > 2 else "jpn"

    try:
        # ファイル拡張子で処理を分岐
        if file_path.lower().endswith('.pdf'):
            text, output_file = process_pdf(file_path, lang=lang_code)
        else:
            text, output_file = process_image_file(file_path, lang=lang_code)

        print(f"\nテキストファイル: {output_file}")
        print(f"抽出された文字数: {len(text)}")
    except Exception as e:
        print(f"エラー: {str(e)}")
        sys.exit(1)
