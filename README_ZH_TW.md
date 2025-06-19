# 課程NFO管理器 | Course NFO Manager

<div align="center">

[English](README_EN.md) | [简体中文](README.md) | [繁體中文](README_ZH_TW.md) | [日本語](README_JA.md) | [Español](README_ES.md) | [Deutsch](README_DE.md)

[![License](https://img.shields.io/github/license/your-username/course-nfo-manager)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/)
[![GitHub stars](https://img.shields.io/github/stars/your-username/course-nfo-manager)](https://github.com/your-username/course-nfo-manager/stargazers)

</div>

## 📖 專案介紹

課程NFO管理器是一個專門用於管理和生成線上課程NFO文件的強大工具。它能夠幫助您組織和管理課程媒體庫，解決普通媒體庫自動生成的課程排序混亂問題。

### 主要特性

- 🚀 支援批量生成和編輯NFO文件
- 🖼️ 智能管理課程海報
- 📁 支援多層目錄結構
- 🏷️ 智能標籤管理系統
- 🔄 自動繼承父目錄標籤
- ⚡ 高效的批量處理能力

### 相容性

- ✅ 完全支援綠聯NAS影視中心
- 🌟 理論上支援所有媒體庫管理軟體

## 🛠️ 技術要求

- Python 3.6+
- 作業系統：Windows/Linux/macOS

## 📥 安裝指南

### 方式一：使用 pip 安裝（推薦）

```bash
# 1. 克隆倉庫
git clone https://github.com/your-username/course-nfo-manager.git
cd course-nfo-manager

# 2. 建立並啟用虛擬環境
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

# 3. 安裝依賴
pip install -r requirements.txt
```

### 方式二：直接下載使用

1. 從 [Releases](https://github.com/your-username/course-nfo-manager/releases) 頁面下載最新版本
2. 解壓文件
3. 執行可執行文件

## 🚀 快速開始

```bash
# 執行程式
python main.py
```

## 📂 目錄結構規範

課程目錄需要遵循以下結構：

```
課程名稱[語言標識]
├── 普通話Deepl/          # 中文課程目錄
│   ├── 第1章/
│   │   ├── 1.1課程.mp4
│   │   └── 1.2課程.mp4
│   └── 第2章/
└── 原/                   # 原始語言課程目錄
```

### 示例

```
完整的C#大師課程 Complete C# Masterclass[普通話]
├── 普通話Deepl
│   ├── 1 - 你的第一個 C 程序與 Visual Studio 概述
│   │   ├── 1 - 引言.mp4
│   │   └── 2 - 你想達成什麼.mp4
│   └── 2 - 數據類型和變量
│       ├── 20 - 更多數據類型及其限制.mp4
│       └── 22 - 數據類型：整型、浮點型與雙精度型.mp4
└── 原
```

## 💡 功能詳解

### 1. NFO生成器
- 多層目錄結構識別
- 智能章節結構分析
- 自動標籤繼承系統
- 靈活的覆蓋選項

### 2. NFO編輯器
- 批量信息編輯
- 海報管理系統
- 自定義標籤系統

## 📸 界面預覽

<div align="center">
  <img src="docs/1.png" alt="主界面" width="600"/>
  <br/>
  <img src="docs/4.png" alt="NFO編輯" width="600"/>
  <br/>
  <img src="docs/5.png" alt="批量處理" width="600"/>
  <br/>
  <img src="docs/6.png" alt="設置界面" width="600"/>
</div>

## ⚠️ 注意事項

1. 課程目錄命名規範：
   - 中文課程必須放在 `普通話Deepl` 目錄下
   - 原始語言課程放在 `原` 目錄下
   - NFO文件會自動添加相應的語言後綴

2. .nomedia文件處理：
   - 目前 .nomedia 檢測功能處於關閉狀態
   - NFO文件將始終在 `原` 目錄下生成

## 🤝 貢獻指南

我們歡迎所有形式的貢獻，無論是新功能、文檔改進還是錯誤報告。請參考以下步驟：

1. Fork 本倉庫
2. 創建新的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟一個 Pull Request

## 📄 許可證

本專案採用 MIT 許可證 - 查看 [LICENSE](LICENSE) 文件了解詳情

## 🌟 致謝

感謝所有為這個專案做出貢獻的開發者們！

## 📮 聯絡方式

如有任何問題或建議，歡迎通過以下方式聯絡：

- 提交 [Issue](https://github.com/your-username/course-nfo-manager/issues)
- 發送郵件至：[airmusic@msn.com](mailto:airmusic@msn.com)

---

<div align="center">

如果這個專案對您有幫助，請考慮給它一個 ⭐️

</div> 