# MarkitDown Converter

このプロジェクトは、Microsoftの[MarkItDown](https://github.com/microsoft/markitdown)ライブラリを使用して、様々な形式のファイルをMarkdownに変換するPythonアプリケーションです。GUIとコマンドラインの両方のインターフェースを提供しています。

## 機能

- 様々なファイル形式（PDF、Word、Excel、PowerPoint、画像など）をMarkdownに変換
- コマンドラインインターフェースとGUIの両方に対応
- 標準出力またはファイルへの出力に対応
- プラグインのサポート
- リアルタイムプレビュー（GUI版）

## インストール

このプロジェクトはPoetryを使用して依存関係を管理しています。以下のコマンドでインストールできます：

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/markitdown-converter.git
cd markitdown-converter

# Poetryを使用する場合
poetry install

# pipを使用する場合
pip install -r requirements.txt
```

## 使い方

### GUIの起動

```bash
# Poetryを使用する場合
poetry run python markitdown_app.py

# pipを使用する場合
python markitdown_app.py
```

### コマンドラインでの基本的な使い方

```bash
# ファイルをMarkdownに変換して標準出力に表示
poetry run python convert_to_markdown.py path/to/file.pdf

# ファイルをMarkdownに変換して指定したファイルに保存
poetry run python convert_to_markdown.py path/to/file.docx -o output.md

# プラグインを有効にしてファイルを変換
poetry run python convert_to_markdown.py path/to/file.xlsx -p -o output.md

# サポートされているファイル形式を表示
poetry run python convert_to_markdown.py -l
```

### コマンドラインオプション

- `file`: 変換するファイルのパス
- `-o, --output`: 出力ファイルのパス（指定しない場合は標準出力に表示）
- `-p, --plugins`: プラグインを有効にする
- `-l, --list-formats`: サポートされているファイル形式を表示

## サポートされているファイル形式

- PDF (.pdf)
- Microsoft Word (.docx, .doc)
- Microsoft PowerPoint (.pptx, .ppt)
- Microsoft Excel (.xlsx, .xls)
- HTML (.html, .htm)
- テキスト (.txt)
- CSV (.csv)
- JSON (.json)
- XML (.xml)
- 画像 (.jpg, .png, .gif)
- 音声 (.mp3, .wav)
- ZIP (.zip)
- EPub (.epub)
- YouTubeのURL

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細については[LICENSE](LICENSE)ファイルを参照してください。

## 謝辞

このプロジェクトは[Microsoft MarkItDown](https://github.com/microsoft/markitdown)ライブラリを使用しています。
