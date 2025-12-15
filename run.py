#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
パイプライン実行スクリプト: OCR → 正規化 → Excel変換
"""

import os
import sys
import logging
from datetime import datetime

# 自作モジュールをインポート
import ocr
import normalize
import to_excel

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_pipeline(input_file, output_dir='output', lang='jpn', dpi=300):
    """
    完全なパイプラインを実行

    Args:
        input_file (str): 入力ファイル（PDFまたは画像）のパス
        output_dir (str): 出力ディレクトリ
        lang (str): OCR言語コード
        dpi (int): PDF変換時の解像度

    Returns:
        dict: 出力ファイルのパス
        {
            'text_file': str,
            'excel_file': str,
            'csv_file': str
        }
    """
    try:
        logger.info("=" * 60)
        logger.info("パイプライン処理を開始します")
        logger.info("=" * 60)

        # 出力ディレクトリを作成
        os.makedirs(output_dir, exist_ok=True)

        # ファイル名（拡張子なし）を取得
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # ステップ1: OCR処理
        logger.info("\n[ステップ1] OCR処理を開始します...")
        text_file = os.path.join(output_dir, f"{base_name}_extracted.txt")

        if input_file.lower().endswith('.pdf'):
            extracted_text, text_file = ocr.process_pdf(
                input_file,
                output_text_path=text_file,
                lang=lang,
                dpi=dpi
            )
        else:
            extracted_text, text_file = ocr.process_image_file(
                input_file,
                output_text_path=text_file,
                lang=lang
            )

        logger.info(f"✓ テキストファイルを作成しました: {text_file}")

        # ステップ2: テキスト正規化
        logger.info("\n[ステップ2] テキストの正規化を開始します...")
        data_list = normalize.parse_text_file(text_file)
        logger.info(f"✓ {len(data_list)} 件のエントリーを解析しました")

        # ステップ3: Excel出力
        logger.info("\n[ステップ3] Excelファイルを作成します...")
        excel_file = os.path.join(output_dir, f"{base_name}_output.xlsx")
        to_excel.create_excel(data_list, excel_file)
        logger.info(f"✓ Excelファイルを作成しました: {excel_file}")

        # ステップ4: CSV出力（オプション）
        logger.info("\n[ステップ4] CSVファイルを作成します...")
        csv_file = os.path.join(output_dir, f"{base_name}_output.csv")
        to_excel.create_csv(data_list, csv_file)
        logger.info(f"✓ CSVファイルを作成しました: {csv_file}")

        # 結果サマリー
        logger.info("\n" + "=" * 60)
        logger.info("パイプライン処理が完了しました！")
        logger.info("=" * 60)
        logger.info(f"入力ファイル: {input_file}")
        logger.info(f"処理件数: {len(data_list)} 件")
        logger.info("\n出力ファイル:")
        logger.info(f"  - テキスト: {text_file}")
        logger.info(f"  - Excel:    {excel_file}")
        logger.info(f"  - CSV:      {csv_file}")
        logger.info("=" * 60)

        return {
            'text_file': text_file,
            'excel_file': excel_file,
            'csv_file': csv_file
        }

    except Exception as e:
        logger.error(f"\nパイプライン処理中にエラーが発生しました: {str(e)}")
        raise


def main():
    """
    メイン関数
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='OCR → 正規化 → Excel変換パイプライン',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # PDFファイルを処理
  python run.py imgFile/班長からの役員希望内訳.pdf

  # 画像ファイルを処理
  python run.py image.png

  # 出力ディレクトリを指定
  python run.py input.pdf --output-dir results

  # 韓国語でOCR処理
  python run.py input.pdf --lang kor
        """
    )

    parser.add_argument(
        'input_file',
        help='入力ファイル（PDFまたは画像）のパス'
    )
    parser.add_argument(
        '--output-dir', '-o',
        default='output',
        help='出力ディレクトリ（デフォルト: output）'
    )
    parser.add_argument(
        '--lang', '-l',
        default='jpn',
        help='OCR言語コード（デフォルト: jpn）'
    )
    parser.add_argument(
        '--dpi', '-d',
        type=int,
        default=300,
        help='PDF変換時の解像度（デフォルト: 300）'
    )

    args = parser.parse_args()

    # 入力ファイルの存在確認
    if not os.path.exists(args.input_file):
        print(f"エラー: 入力ファイルが見つかりません: {args.input_file}")
        sys.exit(1)

    try:
        # パイプラインを実行
        result = run_pipeline(
            args.input_file,
            output_dir=args.output_dir,
            lang=args.lang,
            dpi=args.dpi
        )

        print("\n処理が正常に完了しました！")
        print(f"出力ファイルは {args.output_dir} ディレクトリに保存されています。")

    except Exception as e:
        print(f"\nエラー: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
