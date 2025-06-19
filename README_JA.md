# コースNFOマネージャー | Course NFO Manager

<div align="center">

[English](README_EN.md) | [简体中文](README.md) | [繁體中文](README_ZH_TW.md) | [日本語](README_JA.md) | [Español](README_ES.md) | [Deutsch](README_DE.md)

[![License](https://img.shields.io/github/license/your-username/course-nfo-manager)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/)
[![GitHub stars](https://img.shields.io/github/stars/your-username/course-nfo-manager)](https://github.com/your-username/course-nfo-manager/stargazers)

</div>

## 📖 プロジェクト紹介

コースNFOマネージャーは、オンラインコースのNFOファイルを管理・生成するための強力なツールです。通常のメディアライブラリで自動生成されるコースの順序の混乱を解決し、コースメディアライブラリの整理と管理をサポートします。

### 主な機能

- 🚀 NFOファイルの一括生成と編集をサポート
- 🖼️ コースポスターのスマート管理
- 📁 多層ディレクトリ構造をサポート
- 🏷️ スマートタグ管理システム
- 🔄 親ディレクトリタグの自動継承
- ⚡ 効率的な一括処理機能

### 互換性

- ✅ UGREEN NASメディアセンターを完全サポート
- 🌟 理論的にすべてのメディアライブラリ管理ソフトウェアをサポート

## 🛠️ 技術要件

- Python 3.6+
- 対応OS：Windows/Linux/macOS

## 📥 インストールガイド

### 方法1：pipを使用したインストール（推奨）

```bash
# 1. リポジトリをクローン
git clone https://github.com/your-username/course-nfo-manager.git
cd course-nfo-manager

# 2. 仮想環境の作成と有効化
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

# 3. 依存関係のインストール
pip install -r requirements.txt
```

### 方法2：直接ダウンロード

1. [Releases](https://github.com/your-username/course-nfo-manager/releases)ページから最新バージョンをダウンロード
2. ファイルを解凍
3. 実行ファイルを実行

## 🚀 クイックスタート

```bash
# プログラムの実行
python main.py
```

## 📂 ディレクトリ構造規格

コースディレクトリは以下の構造に従う必要があります：

```
コース名[言語識別子]
├── MandarinDeepl/          # 中国語コースディレクトリ
│   ├── 第1章/
│   │   ├── 1.1レッスン.mp4
│   │   └── 1.2レッスン.mp4
│   └── 第2章/
└── Original/               # オリジナル言語コースディレクトリ
```

### 例

```
Complete C# Masterclass[Mandarin]
├── MandarinDeepl
│   ├── 1 - 最初のC#プログラムとVisual Studio概要
│   │   ├── 1 - はじめに.mp4
│   │   └── 2 - 目標設定.mp4
│   └── 2 - データ型と変数
│       ├── 20 - その他のデータ型と制限.mp4
│       └── 22 - データ型：整数、浮動小数点、倍精度.mp4
└── Original
```

## 💡 機能の詳細

### 1. NFOジェネレーター
- 多層ディレクトリ構造の認識
- スマートな章構造分析
- 自動タグ継承システム
- 柔軟な上書きオプション

### 2. NFOエディター
- 一括情報編集
- ポスター管理システム
- カスタムタグシステム

## 📸 インターフェースプレビュー

<div align="center">
  <img src="docs/1.png" alt="メインインターフェース" width="600"/>
  <br/>
  <img src="docs/4.png" alt="NFO編集" width="600"/>
  <br/>
  <img src="docs/5.png" alt="一括処理" width="600"/>
  <br/>
  <img src="docs/6.png" alt="設定画面" width="600"/>
</div>

## ⚠️ 注意事項

1. コースディレクトリの命名規則：
   - 中国語コースは `MandarinDeepl` ディレクトリに配置
   - オリジナル言語コースは `Original` ディレクトリに配置
   - NFOファイルには自動的に対応する言語サフィックスが追加されます

2. .nomediaファイルの処理：
   - 現在、.nomedia検出機能は無効
   - NFOファイルは常に `Original` ディレクトリに生成されます

## 🤝 貢献ガイド

新機能、ドキュメントの改善、バグレポートなど、あらゆる形式の貢献を歓迎します。以下の手順に従ってください：

1. リポジトリをフォーク
2. 新しい機能ブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. Pull Requestを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています - 詳細は[LICENSE](LICENSE)ファイルをご覧ください

## 🌟 謝辞

このプロジェクトに貢献してくださったすべての開発者に感謝いたします！

## 📮 お問い合わせ

ご質問やご提案がございましたら、以下の方法でお気軽にお問い合わせください：

- [Issue](https://github.com/your-username/course-nfo-manager/issues)の作成
- メール：[airmusic@msn.com](mailto:airmusic@msn.com)

---

<div align="center">

このプロジェクトがお役に立ちましたら、⭐️ をお願いします

</div> 