#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
markitdownを使用してファイルをMarkdownに変換する簡単なプログラム
"""

import os
import sys
import argparse
from pathlib import Path
from markitdown import MarkItDown


def convert_file(file_path, output_path=None, enable_plugins=False):
    """
    指定されたファイルをMarkdownに変換する
    
    Args:
        file_path (str): 変換するファイルのパス
        output_path (str, optional): 出力ファイルのパス。指定しない場合は標準出力に表示
        enable_plugins (bool, optional): プラグインを有効にするかどうか
    
    Returns:
        bool: 変換が成功したかどうか
    """
    try:
        # MarkItDownインスタンスを作成
        md = MarkItDown(enable_plugins=enable_plugins)
        
        # ファイルを変換
        result = md.convert(file_path)
        
        # 結果を出力
        if output_path:
            # 出力ディレクトリが存在しない場合は作成
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # ファイルに書き込み
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.text_content)
            print(f"変換結果を {output_path} に保存しました。")
        else:
            # 標準出力に表示
            print(result.text_content)
            
        return True
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        return False


def list_supported_formats():
    """
    サポートされているファイル形式を表示する
    """
    formats = [
        "PDF (.pdf)",
        "Microsoft Word (.docx, .doc)",
        "Microsoft PowerPoint (.pptx, .ppt)",
        "Microsoft Excel (.xlsx, .xls)",
        "HTML (.html, .htm)",
        "テキスト (.txt)",
        "CSV (.csv)",
        "JSON (.json)",
        "XML (.xml)",
        "画像 (.jpg, .png, .gif)",
        "音声 (.mp3, .wav)",
        "ZIP (.zip)",
        "EPub (.epub)",
        "YouTubeのURL"
    ]
    
    print("サポートされているファイル形式:")
    for fmt in formats:
        print(f"- {fmt}")


def main():
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='ファイルをMarkdownに変換するツール')
    parser.add_argument('file', nargs='?', help='変換するファイルのパス')
    parser.add_argument('-o', '--output', help='出力ファイルのパス')
    parser.add_argument('-p', '--plugins', action='store_true', help='プラグインを有効にする')
    parser.add_argument('-l', '--list-formats', action='store_true', help='サポートされているファイル形式を表示')
    
    args = parser.parse_args()
    
    # サポートされている形式を表示
    if args.list_formats:
        list_supported_formats()
        return 0
    
    # ファイルが指定されていない場合はヘルプを表示
    if not args.file:
        parser.print_help()
        return 1
    
    # ファイルが存在するか確認
    if not os.path.exists(args.file):
        print(f"エラー: ファイル '{args.file}' が見つかりません。", file=sys.stderr)
        return 1
    
    # ファイルを変換
    success = convert_file(args.file, args.output, args.plugins)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
