#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正規化モジュール: OCRテキストを解析して構造化データに変換
"""

import re
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 部会のリスト
DEPARTMENTS = [
    "事務局", "会計", "書記", "名簿",
    "防犯防災", "回覧広報", "地域コミュ",
    "環境美化", "厚生福祉"
]


def normalize_fullwidth_to_halfwidth(text):
    """
    全角数字を半角数字に変換

    Args:
        text (str): 入力テキスト

    Returns:
        str: 変換後のテキスト
    """
    fullwidth_digits = "０１２３４５６７８９"
    halfwidth_digits = "0123456789"

    trans_table = str.maketrans(fullwidth_digits, halfwidth_digits)
    return text.translate(trans_table)


def parse_contact_info(contact_text):
    """
    住所・TEL・アドレスのテキストを解析して分割

    Args:
        contact_text (str): 住所・TEL・アドレスの情報

    Returns:
        dict: {'address': str, 'tel': str, 'email': str}

    例：
    入力: "虹ヶ丘１－２－１、044-988-4952、(090-3686-6434)、abc@xyz.com"
    出力: {
        'address': '虹ヶ丘１－２－１',
        'tel': '044-988-4952、(090-3686-6434)',
        'email': 'abc@xyz.com'
    }
    """
    result = {
        'address': '',
        'tel': '',
        'email': ''
    }

    if not contact_text:
        return result

    # 全角数字を半角に変換
    contact_text = normalize_fullwidth_to_halfwidth(contact_text)

    # メールアドレスを抽出（@を含むパターン）
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    email_match = re.search(email_pattern, contact_text)
    if email_match:
        result['email'] = email_match.group(0)
        # メールアドレスを元のテキストから削除
        contact_text = contact_text.replace(result['email'], '')

    # 電話番号を抽出（ハイフン区切りの数字、括弧付きも含む）
    # パターン: 044-988-4952 や (090-3686-6434) など
    tel_pattern = r'[\(（]?\d{2,4}[-ー]\d{2,4}[-ー]\d{4}[\)）]?'
    tel_matches = re.findall(tel_pattern, contact_text)
    if tel_matches:
        result['tel'] = '、'.join(tel_matches)
        # 電話番号を元のテキストから削除
        for tel in tel_matches:
            contact_text = contact_text.replace(tel, '')

    # 残りの部分を住所として扱う
    # カンマや句読点で区切られた最初の部分を住所とする
    address = contact_text.strip()
    # 先頭・末尾のカンマや空白を削除
    address = re.sub(r'^[、,\s]+|[、,\s]+$', '', address)
    # 連続するカンマや空白を1つにまとめる
    address = re.sub(r'[、,\s]+', '、', address)

    result['address'] = address if address else 'null'

    # 空の値はnullに置き換え
    if not result['tel']:
        result['tel'] = 'null'
    if not result['email']:
        result['email'] = 'null'

    return result


def parse_departments(dept_text):
    """
    希望部会のテキストを解析して部会ごとの優先順位を抽出

    Args:
        dept_text (str): 希望部会の情報

    Returns:
        dict: 各部会名をキーとし、優先順位（①、②、③）を値とする辞書

    例：
    入力: "①回覧広報、②厚生福祉、③環境美化"
    出力: {
        '回覧広報': '①',
        '厚生福祉': '②',
        '環境美化': '③',
        '事務局': '',
        ...（他の部会は空文字）
    }
    """
    # 全部会を空文字で初期化
    result = {dept: '' for dept in DEPARTMENTS}

    if not dept_text:
        return result

    # 全角数字を半角に変換
    dept_text = normalize_fullwidth_to_halfwidth(dept_text)

    # 優先順位マークを抽出（①、②、③、または1、2、3など）
    # パターン: ①部会名、②部会名、③部会名
    patterns = [
        r'([①②③])\s*([^、,\s]+)',  # ①回覧広報
        r'([1-3])\s*([^、,\s]+)',    # 1回覧広報
        r'([①②③1-3])[.．)\)）]\s*([^、,\s]+)'  # ①)回覧広報
    ]

    for pattern in patterns:
        matches = re.findall(pattern, dept_text)
        for priority, dept_name in matches:
            # 優先順位を丸数字に正規化
            priority_map = {
                '1': '①', '2': '②', '3': '③',
                '①': '①', '②': '②', '③': '③'
            }
            normalized_priority = priority_map.get(priority, priority)

            # 部会名をマッチング（部分一致）
            for dept in DEPARTMENTS:
                if dept in dept_name:
                    result[dept] = normalized_priority
                    break

    return result


def parse_班長_entry(text):
    """
    班長エントリーのテキストを解析して構造化データに変換

    実際のフォーマット：
    N班 氏名 住所... ①部会... 補足...
    ふりがな TEL ②部会...
    メールアドレス ③部会...

    Args:
        text (str): 班長エントリーのテキスト

    Returns:
        dict: 解析されたデータ
    """
    result = {
        '班': '',
        '氏名': '',
        '住所': '',
        'TEL': '',
        'メールアドレス': '',
        '補足事項': ''
    }

    # 部会カラムを初期化
    for dept in DEPARTMENTS:
        result[dept] = ''

    # テキストを1つの文字列として扱う（改行を保持）
    text = text.strip()

    # 全角数字を半角に変換
    text = normalize_fullwidth_to_halfwidth(text)

    # 班番号を抽出
    match = re.search(r'(\d+)\s*班', text)
    if match:
        result['班'] = match.group(1) + '班'

    # 氏名を抽出（班番号の後、最初の漢字・ひらがな・カタカナの連続）
    # パターン: "N班 氏名" の形式
    name_match = re.search(r'\d+\s*班\s+([^\s]+(?:\s+[^\s]+)?)', text)
    if name_match:
        name = name_match.group(1)
        # ふりがなを除外（ひらがなのみの行を除外）
        if not re.match(r'^[ぁ-ん\s]+$', name):
            result['氏名'] = name

    # メールアドレスを抽出
    email_pattern = r'[\w\.-]+@[\w\.-]+\.[\w]+'
    email_match = re.search(email_pattern, text)
    if email_match:
        result['メールアドレス'] = email_match.group(0)

    # 電話番号を抽出（複数の電話番号に対応）
    tel_pattern = r'[\(（]?\d{2,4}[-ー一=]\d{2,4}[-ー一=]\d{4}[\)）]?'
    tel_matches = re.findall(tel_pattern, text)
    if tel_matches:
        # 全角ハイフンを半角に変換
        tel_list = []
        for tel in tel_matches:
            tel = tel.replace('ー', '-').replace('一', '-').replace('=', '-')
            tel_list.append(tel)
        result['TEL'] = '、'.join(tel_list)

    # 住所を抽出（"虹ヶ丘" または "虹"で始まる住所パターン）
    address_pattern = r'虹[^0-9①②③\n]*[0-9０-９一ー=-]+[0-9０-９一ー=-]*[0-9０-９一ー=-]*'
    address_match = re.search(address_pattern, text)
    if address_match:
        address = address_match.group(0)
        # 全角数字を半角に、全角ハイフンを半角に変換
        address = normalize_fullwidth_to_halfwidth(address)
        address = address.replace('ー', '-').replace('一', '-').replace('=', '-')
        # 不要な文字を削除
        address = re.sub(r'[、,\s]+$', '', address)
        result['住所'] = address

    # 希望部会を抽出
    dept_text = text
    dept_info = parse_departments(dept_text)
    result.update(dept_info)

    # 補足事項を抽出（③の後ろにある文字列、または括弧内の文字列）
    # パターン1: ③部会名の後ろのテキスト
    # パターン2: 括弧で囲まれたテキスト
    supplement_patterns = [
        r'③[^①②③\n]+([^\n①②③]+)',  # ③の後ろ
        r'\(([^)]+)\)',  # 丸括弧
        r'（([^）]+)）'  # 全角丸括弧
    ]

    supplements = []
    for pattern in supplement_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            match = match.strip()
            # 部会名や番号を除外
            if match and not re.match(r'^[①②③]', match) and len(match) > 1:
                # 部会名でないことを確認
                is_dept = False
                for dept in DEPARTMENTS:
                    if dept in match and len(match) < 10:
                        is_dept = True
                        break
                if not is_dept:
                    supplements.append(match)

    if supplements:
        result['補足事項'] = '、'.join(supplements)

    # 空の値をnullに置き換え
    for key in result:
        if not result[key]:
            result[key] = 'null'

    return result


def parse_text_file(text_file_path):
    """
    テキストファイルを読み込んで班長エントリーのリストに変換

    Args:
        text_file_path (str): テキストファイルのパス

    Returns:
        list: 班長データの辞書のリスト
    """
    try:
        # UTF-8でテキストファイルを読み込み
        with open(text_file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        logger.info(f"テキストファイルを読み込みました: {text_file_path}")

        # ページ区切りで分割（OCRの出力形式に基づく）
        pages = re.split(r'===\s*ページ\s*\d+\s*===', text)

        # 全ページのテキストを結合
        combined_text = '\n'.join(pages)

        # 班ごとにエントリーを分割（"N班"パターンで分割）
        # 1班、2班...26班まで
        entries = []
        班_pattern = r'(\d+)\s*班'
        matches = list(re.finditer(班_pattern, combined_text))

        for i, match in enumerate(matches):
            start_pos = match.start()
            # 次の班の開始位置まで、またはテキストの終わりまで
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(combined_text)

            entry_text = combined_text[start_pos:end_pos]
            entry_data = parse_班長_entry(entry_text)

            if entry_data['班'] != 'null':  # 有効なエントリーのみ追加
                entries.append(entry_data)
                logger.info(f"{entry_data['班']} のデータを解析しました")

        logger.info(f"合計 {len(entries)} 件のエントリーを解析しました")
        return entries

    except Exception as e:
        logger.error(f"テキスト解析中にエラーが発生しました: {str(e)}")
        raise


if __name__ == "__main__":
    # テスト用コード
    import sys
    import json

    if len(sys.argv) < 2:
        print("使用方法: python normalize.py <テキストファイルパス>")
        sys.exit(1)

    text_file = sys.argv[1]

    try:
        entries = parse_text_file(text_file)
        print(json.dumps(entries, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"エラー: {str(e)}")
        sys.exit(1)
