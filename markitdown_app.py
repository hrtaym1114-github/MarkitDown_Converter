#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PySide6を使用してファイルをMarkdownに変換するGUIアプリケーション
(ドラッグ&ドロップ対応、設定ページ、元ファイルパス追記)
"""

import sys
import os
import re
import datetime
import json
import urllib.request
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLineEdit, QTextEdit, QLabel, QComboBox,
    QCheckBox, QMessageBox, QStatusBar, QSizePolicy, QDialog,
    QFormLayout, QDialogButtonBox, QMenuBar, QGroupBox, QInputDialog
)
from PySide6.QtCore import Qt, QThread, Signal, QMimeData, QSettings
from PySide6.QtGui import QFont, QPalette, QColor, QAction
from youtube_transcript_api import YouTubeTranscriptApi
import re

def fetch_transcript(video_id, languages):
    if 'youtu' in video_id:
        m = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', video_id)
        if m:
            video_id = m.group(1)
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            return transcript_list.find_transcript(languages).fetch()
        except:
            return transcript_list.find_generated_transcript(languages).fetch()
    except Exception as e:
        return f"<!-- Transcript unavailable: {e} -->"


def get_youtube_info(video_id):
    """
    YouTubeのビデオIDからチャンネル名と動画タイトルを取得する
    """
    if 'youtu' in video_id:
        m = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', video_id)
        if m:
            video_id = m.group(1)
            
    try:
        # YouTube Data APIを使用せずにOEmbed APIを利用
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        with urllib.request.urlopen(oembed_url) as response:
            data = json.loads(response.read().decode())
            title = data.get('title', 'Unknown Title')
            author = data.get('author_name', 'Unknown Channel')
            return {
                'title': title,
                'channel': author,
                'video_id': video_id
            }
    except Exception as e:
        print(f"YouTubeの情報取得に失敗しました: {e}")
        return {
            'title': 'Unknown Title',
            'channel': 'Unknown Channel',
            'video_id': video_id
        }


def get_youtube_info(video_id):
    """
    YouTubeのビデオIDからチャンネル名と動画タイトルを取得する
    """
    if 'youtu' in video_id:
        m = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', video_id)
        if m:
            video_id = m.group(1)
            
    try:
        # YouTube Data APIを使用せずにOEmbed APIを利用
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        with urllib.request.urlopen(oembed_url) as response:
            data = json.loads(response.read().decode())
            title = data.get('title', 'Unknown Title')
            author = data.get('author_name', 'Unknown Channel')
            return {
                'title': title,
                'channel': author,
                'video_id': video_id
            }
    except Exception as e:
        print(f"YouTubeの情報取得に失敗しました: {e}")
        return {
            'title': 'Unknown Title',
            'channel': 'Unknown Channel',
            'video_id': video_id
        }

# Override the default get_transcript method with our robust version
YouTubeTranscriptApi.get_transcript = fetch_transcript

# markitdownのインポートを試みる (エラーハンドリングを追加)
try:
    from markitdown import MarkItDown
except ImportError:
    def show_import_error():
        app = QApplication([])
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("依存関係エラー")
        msg_box.setText("MarkItDownライブラリが見つかりません。")
        msg_box.setInformativeText(
            "プロジェクトのルートディレクトリで `poetry install` を実行して、"
            "必要な依存関係をインストールしてください。"
        )
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
        sys.exit(1)
    show_import_error()

# --- スタイルシート ---
# (QDialog, QMenuBar, QMenu スタイルを追加)
DARK_STYLE = """
QWidget {
    background-color: #2E2E2E;
    color: #E0E0E0;
    font-size: 11pt;
}
QMainWindow, QDialog {
    background-color: #2E2E2E;
}
QLineEdit, QTextEdit {
    background-color: #3C3C3C;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 5px;
    color: #E0E0E0;
}
QLineEdit:disabled {
    background-color: #333333;
    color: #888888;
}
QPushButton {
    background-color: #4A4A4A;
    color: #E0E0E0;
    border: 1px solid #555555;
    padding: 8px 15px;
    border-radius: 4px;
    min-width: 80px;
}
QPushButton:hover {
    background-color: #5A5A5A;
}
QPushButton:pressed {
    background-color: #6A6A6A;
}
QPushButton:disabled {
    background-color: #383838;
    color: #888888;
}
QCheckBox {
    spacing: 5px;
    color: #E0E0E0; /* チェックボックスのテキスト色 */
}
QCheckBox::indicator {
    width: 13px;
    height: 13px;
    background-color: #3C3C3C; /* インジケータの背景 */
    border: 1px solid #555555;
    border-radius: 3px;
}
QCheckBox::indicator:checked {
    background-color: #4A90E2; /* チェック時の色 */
    border: 1px solid #4A90E2;
}
QLabel {
    color: #E0E0E0;
}
QStatusBar {
    background-color: #3C3C3C;
    color: #B0B0B0;
}
QMessageBox {
    background-color: #2E2E2E;
}
QMessageBox QLabel {
    color: #E0E0E0;
}
QFileDialog {
    background-color: #2E2E2E; /* QFileDialogのスタイル設定は限定的 */
}
QMenuBar {
    background-color: #3C3C3C;
    color: #E0E0E0;
}
QMenuBar::item {
    background-color: #3C3C3C;
    color: #E0E0E0;
    padding: 4px 10px;
}
QMenuBar::item:selected {
    background-color: #5A5A5A;
}
QMenu {
    background-color: #3C3C3C;
    color: #E0E0E0;
    border: 1px solid #555555;
}
QMenu::item {
    padding: 4px 20px;
}
QMenu::item:selected {
    background-color: #5A5A5A;
}
QFormLayout QLabel { /* 設定ダイアログのラベル */
    color: #E0E0E0;
    padding-top: 5px; /* 少し上にスペース */
}
QGroupBox {
    border: 1px solid #555555;
    border-radius: 4px;
    margin-top: 1ex; /* leave space at the top for the title */
    padding-top: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center; /* position at the top center */
    padding: 0 3px;
    color: #E0E0E0;
}
"""

class ConversionWorker(QThread):
    """ファイル変換をバックグラウンドで実行するワーカースレッド"""
    # 元ファイルパスもシグナルで渡すように変更
    conversion_complete = Signal(str, str) # markdown_content, original_file_path
    conversion_error = Signal(str)

    def __init__(self, file_path, enable_plugins, proxy_settings=None, transcript_language=None):
        super().__init__()
        self.file_path = file_path
        self.enable_plugins = enable_plugins
        self.proxy_settings = proxy_settings
        self.transcript_language = transcript_language
        self._is_running = True

    def run(self):
        try:
            # プロキシ設定を環境変数に設定
            self._setup_proxy()
            
            # markitdownに渡すオプションを準備
            options = {
                'enable_plugins': self.enable_plugins
            }
            # YouTube文字起こしを有効にするためのオプション
            options['youtube'] = {
                'include_transcript': True,
                'transcript_languages': [self.transcript_language or 'ja']
            }
            
            # プロキシ設定があれば、requests_kwargsを設定
            if self.proxy_settings and self.proxy_settings.get('use_proxy', False):
                proxy_host = self.proxy_settings.get('proxy_host', '')
                proxy_port = self.proxy_settings.get('proxy_port', '')
                
                if proxy_host and proxy_port:
                    proxy_url = f"http://{proxy_host}:{proxy_port}"
                    
                    # 認証情報の追加
                    proxy_user = self.proxy_settings.get('proxy_user', '')
                    proxy_pass = self.proxy_settings.get('proxy_pass', '')
                    if proxy_user and proxy_pass:
                        proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
                    
                    # requestsライブラリの引数として渡すプロキシ設定
                    requests_kwargs = {
                        'proxies': {
                            'http': proxy_url,
                            'https': proxy_url
                        }
                    }
                    
                    # SSL検証スキップの設定
                    if self.proxy_settings.get('skip_ssl_verify', False):
                        requests_kwargs['verify'] = False
                        # SSL警告を無効化
                        import urllib3
                        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    
                    options['requests_kwargs'] = requests_kwargs
            
            # デバッグ情報を追加
            print(f"\n[DEBUG] 変換オプション: {options}")
            print(f"[DEBUG] 変換対象: {self.file_path}")
            
            # オプション付きでMarkItDownを初期化
            md = MarkItDown(**options)
            print("[DEBUG] MarkItDownインスタンス生成成功")
            
            # SSL検証をスキップする場合、内部セッションに直接設定
            if self.proxy_settings and self.proxy_settings.get('use_proxy', False) and self.proxy_settings.get('skip_ssl_verify', False):
                # 内部のrequestsセッションに直接アクセス
                if hasattr(md, '_requests_session'):
                    print("[DEBUG] requestsセッションに直接アクセスしてSSL検証を無効化")
                    md._requests_session.verify = False
                    
                    # プロキシ設定も直接適用
                    proxy_host = self.proxy_settings.get('proxy_host', '')
                    proxy_port = self.proxy_settings.get('proxy_port', '')
                    if proxy_host and proxy_port:
                        proxy_url = f"http://{proxy_host}:{proxy_port}"
                        
                        # 認証情報の追加
                        proxy_user = self.proxy_settings.get('proxy_user', '')
                        proxy_pass = self.proxy_settings.get('proxy_pass', '')
                        if proxy_user and proxy_pass:
                            proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
                        
                        md._requests_session.proxies = {
                            'http': proxy_url,
                            'https': proxy_url
                        }
                        print(f"[DEBUG] プロキシ設定を直接適用: {proxy_url}")
            
            result = md.convert(self.file_path)
            print("[DEBUG] 変換処理成功")
            
            if self._is_running:
                # 元ファイルパスを渡す
                self.conversion_complete.emit(result.text_content, self.file_path)
        except Exception as e:
            if self._is_running:
                # 詳細なエラー情報を取得
                import traceback
                error_traceback = traceback.format_exc()
                error_message = f"{str(e)}\n\n--- 詳細エラー情報 ---\n{error_traceback}"
                print(f"\n[ERROR] 変換エラー: {error_message}")
                self.conversion_error.emit(error_message)
        finally:
            # 環境変数を元に戻す
            self._cleanup_proxy()

    def _setup_proxy(self):
        """プロキシ設定を環境変数に設定"""
        if self.proxy_settings and self.proxy_settings.get('use_proxy', False):
            proxy_host = self.proxy_settings.get('proxy_host', '')
            proxy_port = self.proxy_settings.get('proxy_port', '')
            
            if proxy_host and proxy_port:
                proxy_url = f"http://{proxy_host}:{proxy_port}"
                # 環境変数に設定
                os.environ['HTTP_PROXY'] = proxy_url
                os.environ['HTTPS_PROXY'] = proxy_url
                
                # プロキシ認証情報がある場合
                proxy_user = self.proxy_settings.get('proxy_user', '')
                proxy_pass = self.proxy_settings.get('proxy_pass', '')
                if proxy_user and proxy_pass:
                    auth_proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
                    os.environ['HTTP_PROXY'] = auth_proxy_url
                    os.environ['HTTPS_PROXY'] = auth_proxy_url
                
                # SSL証明書の検証をスキップする場合
                if self.proxy_settings.get('skip_ssl_verify', False):
                    # SSL証明書の検証をスキップする環境変数を設定
                    os.environ['PYTHONHTTPSVERIFY'] = '0'
                    # requestsライブラリの警告を無効化
                    import urllib3
                    urllib3.disable_warnings()

    def _cleanup_proxy(self):
        """環境変数からプロキシ設定を削除"""
        if 'HTTP_PROXY' in os.environ:
            del os.environ['HTTP_PROXY']
        if 'HTTPS_PROXY' in os.environ:
            del os.environ['HTTPS_PROXY']
        if 'PYTHONHTTPSVERIFY' in os.environ:
            del os.environ['PYTHONHTTPSVERIFY']

    def stop(self):
        self._is_running = False

class SettingsDialog(QDialog):
    """設定ダイアログ"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("設定")
        self.setMinimumWidth(500) # 幅を少し広げる
        self.setStyleSheet(DARK_STYLE) # 親と同じスタイルを適用

        self.settings = QSettings("MyCompany", "MarkItDownApp") # 設定の読み書き用

        layout = QVBoxLayout(self)
        
        # 一般設定
        general_group = QGroupBox("一般設定")
        general_layout = QFormLayout(general_group)
        
        # デフォルト出力ディレクトリ
        self.default_output_dir_edit = QLineEdit()
        default_output_dir_layout = QHBoxLayout()
        default_output_dir_layout.addWidget(self.default_output_dir_edit)
        browse_output_dir_button = QPushButton("参照...")
        browse_output_dir_button.clicked.connect(self._browse_default_output_dir)
        default_output_dir_layout.addWidget(browse_output_dir_button)
        general_layout.addRow("デフォルト出力ディレクトリ:", default_output_dir_layout)

        # デフォルトプラグイン有効状態
        self.default_plugins_checkbox = QCheckBox("デフォルトでプラグインを有効にする")
        general_layout.addRow("", self.default_plugins_checkbox) # ラベルなしで行を追加
        
        layout.addWidget(general_group)
        
        # プロキシ設定
        proxy_group = QGroupBox("プロキシ設定")
        proxy_layout = QFormLayout(proxy_group)

        # YouTubeオプショングループ
        youtube_group = QGroupBox("YouTubeオプション")
        youtube_layout = QVBoxLayout()

        self.include_transcript = QCheckBox("文字起こしテキストを含める")
        youtube_layout.addWidget(self.include_transcript)

        youtube_group.setLayout(youtube_layout)
        layout.addWidget(youtube_group)
        
        # プロキシ使用チェックボックス
        self.use_proxy_checkbox = QCheckBox("プロキシを使用する")
        self.use_proxy_checkbox.stateChanged.connect(self._toggle_proxy_controls)
        proxy_layout.addRow("", self.use_proxy_checkbox)
        
        # プロキシホスト
        self.proxy_host_edit = QLineEdit()
        self.proxy_host_edit.setPlaceholderText("例: proxy.example.com")
        proxy_layout.addRow("プロキシホスト:", self.proxy_host_edit)
        
        # プロキシポート
        self.proxy_port_edit = QLineEdit()
        self.proxy_port_edit.setPlaceholderText("例: 8080")
        proxy_layout.addRow("プロキシポート:", self.proxy_port_edit)
        
        # プロキシ認証情報
        self.proxy_auth_checkbox = QCheckBox("認証が必要")
        self.proxy_auth_checkbox.stateChanged.connect(self._toggle_proxy_auth)
        proxy_layout.addRow("", self.proxy_auth_checkbox)
        
        # プロキシユーザー名
        self.proxy_user_edit = QLineEdit()
        proxy_layout.addRow("ユーザー名:", self.proxy_user_edit)
        
        # プロキシパスワード
        self.proxy_pass_edit = QLineEdit()
        self.proxy_pass_edit.setEchoMode(QLineEdit.Password)
        proxy_layout.addRow("パスワード:", self.proxy_pass_edit)
        
        # SSL証明書の検証をスキップ
        self.skip_ssl_verify_checkbox = QCheckBox("SSL証明書の検証をスキップ (安全でない接続を許可)")
        proxy_layout.addRow("", self.skip_ssl_verify_checkbox)
        
        layout.addWidget(proxy_group)
        
        # ボタンボックス (OK, Cancel)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept) # OKボタン
        button_box.rejected.connect(self.reject) # Cancelボタン
        layout.addWidget(button_box)

        self._load_settings()
        self._toggle_proxy_controls() # 初期状態の設定
        self._toggle_proxy_auth() # 初期状態の設定

    def _load_settings(self):
        """設定を読み込む"""
        # 一般設定
        self.default_output_dir_edit.setText(self.settings.value("defaultOutputDir", ""))
        self.default_plugins_checkbox.setChecked(self.settings.value("defaultPluginsEnabled", False, type=bool))
        
        # プロキシ設定
        self.use_proxy_checkbox.setChecked(self.settings.value("useProxy", False, type=bool))
        self.proxy_host_edit.setText(self.settings.value("proxyHost", ""))
        self.proxy_port_edit.setText(self.settings.value("proxyPort", ""))
        self.proxy_auth_checkbox.setChecked(self.settings.value("proxyAuthRequired", False, type=bool))
        self.proxy_user_edit.setText(self.settings.value("proxyUser", ""))
        self.proxy_pass_edit.setText(self.settings.value("proxyPass", ""))
        self.skip_ssl_verify_checkbox.setChecked(self.settings.value("skipSSLVerify", False, type=bool))
        self.include_transcript.setChecked(self.settings.value("includeTranscript", False, type=bool))

    def _toggle_proxy_controls(self):
        """プロキシ設定の有効/無効を切り替える"""
        enabled = self.use_proxy_checkbox.isChecked()
        self.proxy_host_edit.setEnabled(enabled)
        self.proxy_port_edit.setEnabled(enabled)
        self.proxy_auth_checkbox.setEnabled(enabled)
        
        # 認証関連のコントロールは、プロキシが有効かつ認証が必要な場合のみ有効
        auth_enabled = enabled and self.proxy_auth_checkbox.isChecked()
        self.proxy_user_edit.setEnabled(auth_enabled)
        self.proxy_pass_edit.setEnabled(auth_enabled)

    def _toggle_proxy_auth(self):
        """プロキシ認証の有効/無効を切り替える"""
        auth_enabled = self.proxy_auth_checkbox.isChecked() and self.use_proxy_checkbox.isChecked()
        self.proxy_user_edit.setEnabled(auth_enabled)
        self.proxy_pass_edit.setEnabled(auth_enabled)

    def _browse_default_output_dir(self):
        """デフォルト出力ディレクトリ選択ダイアログ"""
        dir_path = QFileDialog.getExistingDirectory(self, "デフォルト出力ディレクトリを選択")
        if dir_path:
            self.default_output_dir_edit.setText(dir_path)

    def accept(self):
        """設定を保存してダイアログを閉じる"""
        # 一般設定
        self.settings.setValue("defaultOutputDir", self.default_output_dir_edit.text())
        self.settings.setValue("defaultPluginsEnabled", self.default_plugins_checkbox.isChecked())
        
        # プロキシ設定
        self.settings.setValue("useProxy", self.use_proxy_checkbox.isChecked())
        self.settings.setValue("proxyHost", self.proxy_host_edit.text())
        self.settings.setValue("proxyPort", self.proxy_port_edit.text())
        self.settings.setValue("proxyAuthRequired", self.proxy_auth_checkbox.isChecked())
        self.settings.setValue("proxyUser", self.proxy_user_edit.text())
        self.settings.setValue("proxyPass", self.proxy_pass_edit.text())
        self.settings.setValue("skipSSLVerify", self.skip_ssl_verify_checkbox.isChecked())
        self.settings.setValue("includeTranscript", self.include_transcript.isChecked())
        
        super().accept()

class MarkItDownApp(QMainWindow):
    """PySide6を使用したmarkitdownのGUIアプリケーション"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MarkItDown Converter")
        self.setGeometry(100, 100, 900, 700)
        
        # ファイル変換ワーカー
        self.worker = None

        self.settings = QSettings("MyCompany", "MarkItDownApp") # アプリケーション設定

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.worker = None

        self._init_menu() # メニューバー初期化
        self._init_ui()
        self._load_settings() # アプリ起動時に設定を読み込む
        self.statusBar().showMessage("準備完了")

    def _init_menu(self):
        """メニューバーの初期化"""
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("ファイル") # "&File" のように & をつけると Alt+F で開ける

        # 設定アクション
        settings_action = QAction("設定...", self)
        settings_action.triggered.connect(self._open_settings_dialog)
        file_menu.addAction(settings_action)

        # 終了アクション
        exit_action = QAction("終了", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _init_ui(self):
        # --- ファイル選択セクション ---
        file_layout = QHBoxLayout()
        self.layout.addLayout(file_layout)
        # ラベルを変更: ファイルまたはURLを受け付けることを明示
        file_label = QLabel("変換するファイル または URL:")
        file_layout.addWidget(file_label)
        self.file_path_edit = QLineEdit()
        # プレースホルダーテキストを変更
        self.file_path_edit.setPlaceholderText("ファイルパス または YouTube URL を入力、またはファイルをドラッグ＆ドロップ")
        file_layout.addWidget(self.file_path_edit)
        # 言語選択メニュー
        lang_layout = QHBoxLayout()
        lang_label = QLabel("YouTube文字起こしの言語:")
        self.language_dropdown = QComboBox()
        self.language_dropdown.addItem("日本語", "ja")
        self.language_dropdown.addItem("英語", "en")
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.language_dropdown)
        self.layout.addLayout(lang_layout)
        browse_button = QPushButton("参照...")
        browse_button.clicked.connect(self._browse_file)
        file_layout.addWidget(browse_button)

        # --- 出力ファイル選択セクション ---
        output_group_layout = QVBoxLayout()
        self.layout.addLayout(output_group_layout)
        self.save_output_checkbox = QCheckBox("出力ファイルを保存する")
        self.save_output_checkbox.stateChanged.connect(self._toggle_output_controls)
        output_group_layout.addWidget(self.save_output_checkbox)

        # ファイル名自動生成のチェックボックス（デフォルトON）
        self.auto_filename_checkbox = QCheckBox("ファイル名を自動生成する")
        self.auto_filename_checkbox.setChecked(True)
        output_group_layout.addWidget(self.auto_filename_checkbox)

        output_path_layout = QHBoxLayout()
        output_group_layout.addLayout(output_path_layout)
        output_label = QLabel("保存先フォルダ:")
        output_path_layout.addWidget(output_label)
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setReadOnly(True)
        self.output_path_edit.setPlaceholderText("保存先フォルダを選択してください（ファイル名は自動生成されます）")
        output_path_layout.addWidget(self.output_path_edit)
        self.save_button = QPushButton("保存先...")
        self.save_button.clicked.connect(self._browse_output_directory)
        output_path_layout.addWidget(self.save_button)

        # --- オプションと変換ボタンセクション ---
        options_layout = QHBoxLayout()
        self.layout.addLayout(options_layout)
        self.plugins_checkbox = QCheckBox("プラグインを有効にする") # 初期値は_load_settingsで設定
        options_layout.addWidget(self.plugins_checkbox)
        options_layout.addStretch()
        self.convert_button = QPushButton("変換開始")
        self.convert_button.clicked.connect(self._start_conversion)
        options_layout.addWidget(self.convert_button)

        # --- プレビューセクション ---
        preview_label = QLabel("Markdown プレビュー:")
        self.layout.addWidget(preview_label)
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Courier New", 10))
        self.preview_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.preview_text)

        # --- ステータスバー ---
        self.setStatusBar(QStatusBar(self))

        # 初期状態で出力関連コントロールを無効化 (チェックボックスの状態に依存)
        self._toggle_output_controls()

    def _load_settings(self):
        """アプリケーション起動時に設定を読み込み、UIに反映"""
        # デフォルトのプラグイン状態を設定
        default_plugins_enabled = self.settings.value("defaultPluginsEnabled", False, type=bool)
        self.plugins_checkbox.setChecked(default_plugins_enabled)
        
        # デフォルト出力ディレクトリが設定されていれば出力パスに反映
        default_output_dir = self.settings.value("defaultOutputDir", "")
        if default_output_dir and os.path.isdir(default_output_dir):
            # デフォルト出力ディレクトリにダミーファイル名を追加
            dummy_path = os.path.join(default_output_dir, "output.md")
            self.output_path_edit.setText(dummy_path)

        # 保存チェックボックスの初期状態 (ここでは設定しない、ユーザーが都度決める方が自然か)
        self.save_output_checkbox.setChecked(False) # 常に最初はオフ
        self._toggle_output_controls() # チェックボックスの状態に合わせて更新

    def _get_proxy_settings(self):
        """現在のプロキシ設定を辞書として取得"""
        use_proxy = self.settings.value("useProxy", False, type=bool)

        if not use_proxy:
            return {'use_proxy': False}

        proxy_settings = {
            'use_proxy': True,
            'proxy_host': self.settings.value("proxyHost", ""),
            'proxy_port': self.settings.value("proxyPort", ""),
            'skip_ssl_verify': self.settings.value("skipSSLVerify", False, type=bool),
        }

        # 認証情報が必要な場合
        if self.settings.value("proxyAuthRequired", False, type=bool):
            proxy_settings['proxy_user'] = self.settings.value("proxyUser", "")
            proxy_settings['proxy_pass'] = self.settings.value("proxyPass", "")

        return proxy_settings

    def _open_settings_dialog(self):
        """設定ダイアログを開く"""
        dialog = SettingsDialog(self)
        if dialog.exec(): # OKが押された場合
            self._load_settings() # 設定を再読み込みしてUIに反映 (特にプラグインのデフォルト)
            self.statusBar().showMessage("設定を保存しました")

    def _toggle_output_controls(self):
        enabled = self.save_output_checkbox.isChecked()
        self.output_path_edit.setEnabled(enabled)
        self.save_button.setEnabled(enabled)

    def _browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "変換するファイルを選択")
        if file_path:
            self._set_input_file(file_path)

    def _set_input_file(self, file_path):
        self.file_path_edit.setText(file_path)
        # デフォルトの出力パスを設定 (設定値 or 元ファイルと同じディレクトリ)
        default_output_dir = self.settings.value("default_output_dir", "")
        output_dir = default_output_dir if default_output_dir and os.path.isdir(default_output_dir) else os.path.dirname(file_path)

        # 入力がURLかどうかを判断
        is_url = file_path.startswith(('http://', 'https://'))

        if is_url:
            # URLの場合はYouTube動画IDを抽出してファイル名に使用
            youtube_id = self._extract_youtube_id(file_path)
            if youtube_id:
                file_base = f"youtube_{youtube_id}"
            else:
                file_base = "youtube_output"  # IDが抽出できない場合のデフォルト名
        else:
            # 通常のファイルの場合
            file_name = os.path.basename(file_path)
            file_base, _ = os.path.splitext(file_name)

        default_output = os.path.join(output_dir, f"{file_base}.md")
        self.output_path_edit.setText(default_output)

    def _extract_youtube_id(self, url):
        """YouTube URLから動画IDを抽出する"""
        # YouTube URL形式: [https://www.youtube.com/watch?v=VIDEO_ID](https://www.youtube.com/watch?v=VIDEO_ID) や
        # [https://youtu.be/VIDEO_ID](https://youtu.be/VIDEO_ID) などから動画IDを抽出
        youtube_regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        match = re.search(youtube_regex, url)
        return match.group(1) if match else None

    def _browse_output_directory(self):
        if not self.save_output_checkbox.isChecked():
            return
        # 保存ダイアログの初期ディレクトリを設定から取得
        initial_dir = self.settings.value("defaultOutputDir", "")
        if not initial_dir or not os.path.isdir(initial_dir):
             # 設定がない、または無効なら現在表示中のパスのディレクトリ
             current_path = self.output_path_edit.text()
             initial_dir = os.path.dirname(current_path) if current_path else ""

        dir_path = QFileDialog.getExistingDirectory(self, "保存先フォルダを選択", initial_dir)
        if dir_path:
            self.output_path_edit.setText(dir_path)
            self.settings.setValue("defaultOutputDir", dir_path)

    def _start_conversion(self):
        input_path = self.file_path_edit.text()
        if not input_path:
            QMessageBox.warning(self, "エラー", "変換するファイルまたはURLを入力してください。")
            return

        # ファイルの存在チェックは削除 (URLの場合に失敗するため)
        # markitdownライブラリ側でエラーハンドリングされることを期待

        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "情報", "現在、別の変換処理が実行中です。")
            return

        self.convert_button.setEnabled(False)
        self.convert_button.setText("変換中...")

        # URLかファイルかを判断してステータスメッセージを変更
        is_url = input_path.startswith(('http://', 'https://'))
        if is_url:
            self.statusBar().showMessage(f"変換開始: {input_path}")
        else:
            self.statusBar().showMessage(f"変換開始: {os.path.basename(input_path)}")

        self.preview_text.clear()

        enable_plugins = self.plugins_checkbox.isChecked()
        include_transcript = self.settings.value("includeTranscript", False, type=bool)

        # プロキシ設定を取得
        proxy_settings = self._get_proxy_settings()

        # include_transcript を渡す必要があるため、enable_pluginsがTrueの時に有効化
        transcript_language = self.language_dropdown.currentData()
        self.worker = ConversionWorker(input_path, enable_plugins, proxy_settings, transcript_language)
        self.worker.include_transcript = include_transcript

        # シグナルの接続
        self.worker.conversion_complete.connect(self._on_conversion_complete)
        self.worker.conversion_error.connect(self._on_conversion_error)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()

    def _generate_filename(self, original_source):
        """
        元のファイルパスを基に自動的にファイル名を生成する
        YouTubeの場合：日付_チャンネル名_動画タイトル.md
        その他のファイル：日付_元ファイル名.md
        """
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        # URLがYouTubeかどうかを判断
        if 'youtu' in original_source:
            # YouTube動画の場合
            video_id_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', original_source)
            if video_id_match:
                video_id = video_id_match.group(1)
                video_info = get_youtube_info(video_id)

                # ファイル名に使えない文字を置換
                channel = re.sub(r'[\\/:*?"<>|]', '_', video_info['channel'])
                title = re.sub(r'[\\/:*?"<>|]', '_', video_info['title'])

                return f"{today}_{channel}_{title}.md"

        # それ以外のファイルの場合
        base_name = os.path.basename(original_source)
        name_without_ext = os.path.splitext(base_name)[0]
        # ファイル名に使えない文字を置換
        name_without_ext = re.sub(r'[\\/:*?"<>|]', '_', name_without_ext)

        return f"{today}_{name_without_ext}.md"

    def _ask_filename_confirmation(self, suggested_filename, output_dir):
        """
        自動生成されたファイル名の確認と修正をユーザーに求める
        """
        dialog = QInputDialog(self)
        dialog.setWindowTitle("ファイル名の確認")
        dialog.setLabelText("生成されたファイル名を確認または修正してください:")
        dialog.setTextValue(suggested_filename)
        dialog.setMinimumWidth(500)  # ダイアログの幅を広げる
        dialog.setStyleSheet(DARK_STYLE)

        if dialog.exec():
            modified_filename = dialog.textValue()
            # 拡張子が .md でない場合は追加
            if not modified_filename.lower().endswith(".md"):
                modified_filename += ".md"
            # 出力ディレクトリとファイル名を結合
            return os.path.join(output_dir, modified_filename)
        return None

    def _on_conversion_complete(self, markdown_content, original_source):
        # 元ファイルパスを追加 (Markdownコメント形式)
        file_path_comment = f"<!-- Original Source: {original_source} -->\n\n"
        full_markdown = file_path_comment + markdown_content

        self.preview_text.setPlainText(full_markdown) # プレビューも更新
        self.statusBar().showMessage("変換完了")

        if self.save_output_checkbox.isChecked():
            try:
                # 出力パスが指定されているかチェック
                output_path = self.output_path_edit.text().strip()

                # 出力ディレクトリを決定
                try:
                    output_dir = os.path.dirname(output_path)
                    if not output_dir:  # ファイル名のみ指定された場合はカレントディレクトリ
                        output_dir = os.getcwd()
                except:
                    # 設定から取得するか、デスクトップを使用
                    default_dir = self.settings.value("defaultOutputDir", "")
                    if default_dir and os.path.isdir(default_dir):
                        output_dir = default_dir
                    else:
                        # デフォルトディレクトリが設定されていない場合はデスクトップを使用
                        output_dir = os.path.join(os.path.expanduser("~"), "Desktop")

                # ディレクトリが存在しない場合は作成
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                # ファイル名を自動生成
                suggested_filename = self._generate_filename(original_source)

                # ユーザーに確認を求める
                confirmed_path = self._ask_filename_confirmation(suggested_filename, output_dir)

                if confirmed_path:
                    # 保存する内容もフルパスコメント付きにする
                    with open(confirmed_path, 'w', encoding='utf-8') as f:
                        f.write(full_markdown)
                    self.statusBar().showMessage(f"変換完了: 結果を {os.path.basename(confirmed_path)} に保存しました")
                    # 保存先を更新
                    self.output_path_edit.setText(confirmed_path)
                    QMessageBox.information(self, "保存完了", f"変換結果を {confirmed_path} に保存しました。")
                else:
                    self.statusBar().showMessage("保存がキャンセルされました")
            except Exception as e:
                QMessageBox.critical(self, "保存エラー", f"出力ファイルの保存中にエラーが発生しました: {e}")
                self.statusBar().showMessage("ファイル保存エラー")
        else:
            self.statusBar().showMessage("変換完了 (プレビューのみ)")

    def _on_conversion_error(self, error_message):
        # 詳細なエラー情報を表示するダイアログ
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle("変換エラー")
        error_dialog.setMinimumSize(700, 500)
        error_dialog.setStyleSheet(DARK_STYLE)
        
        layout = QVBoxLayout(error_dialog)
        
        # エラーメッセージ
        error_label = QLabel("変換中にエラーが発生しました:")
        layout.addWidget(error_label)
        
        # 詳細なエラー情報を表示するテキストエリア
        error_text = QTextEdit()
        error_text.setReadOnly(True)
        error_text.setFont(QFont("Courier New", 10))
        error_text.setText(error_message)
        layout.addWidget(error_text)
        
        # クリップボードにコピーするボタン
        copy_button = QPushButton("エラー情報をコピー")
        copy_button.clicked.connect(lambda: QApplication.clipboard().setText(error_message))
        
        # 閉じるボタン
        close_button = QPushButton("閉じる")
        close_button.clicked.connect(error_dialog.accept)
        
        # ボタンレイアウト
        button_layout = QHBoxLayout()
        button_layout.addWidget(copy_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        # ダイアログを表示
        error_dialog.exec()
        
        self.statusBar().showMessage("変換エラー")

    def _on_worker_finished(self):
        self.convert_button.setEnabled(True)
        self.convert_button.setText("変換開始")
        self.worker = None

    def dragEnterEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasUrls() and len(mime_data.urls()) == 1:
            url = mime_data.urls()[0]
            if url.isLocalFile():
                event.acceptProposedAction()

    def dropEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            url = mime_data.urls()[0]
            if url.isLocalFile():
                file_path = url.toLocalFile()
                self._set_input_file(file_path)
                event.acceptProposedAction()

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(self, '確認',
                                           "変換処理が実行中です。中断しますか？",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                           QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.worker.stop()
                self.worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == '__main__':
    # アプリケーション名と組織名を設定 (QSettingsで必要)
    QApplication.setOrganizationName("MyCompany")
    QApplication.setApplicationName("MarkItDownApp")

    app = QApplication(sys.argv)
    main_window = MarkItDownApp()
    main_window.show()
    sys.exit(app.exec())