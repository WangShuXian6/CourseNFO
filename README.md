# 课程NFO管理器 | Course NFO Manager

<div align="center">

[English](README_EN.md) | [简体中文](README.md) | [繁體中文](README_ZH_TW.md) | [日本語](README_JA.md) | [Español](README_ES.md) | [Deutsch](README_DE.md)

[![License](https://img.shields.io/github/license/your-username/course-nfo-manager)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![GitHub stars](https://img.shields.io/github/stars/your-username/course-nfo-manager)](https://github.com/your-username/course-nfo-manager/stargazers)
[![Build Status](https://github.com/your-username/course-nfo-manager/workflows/Build%20and%20Release/badge.svg)](https://github.com/your-username/course-nfo-manager/actions)

</div>

## 📖 项目介绍

课程NFO管理器是一个专门用于管理和生成在线课程NFO文件的强大工具。它能够帮助您组织和管理课程媒体库，解决普通媒体库自动生成的课程排序混乱问题。

### 主要特性

- 🚀 支持批量生成和编辑NFO文件
- 🖼️ 智能管理课程海报
- 📁 支持多层目录结构
- 🏷️ 智能标签管理系统
- 🔄 自动继承父目录标签
- ⚡ 高效的批量处理能力

### 兼容性

- ✅ 完全支持绿联NAS影视中心
- 🌟 理论上支持所有媒体库管理软件

## ��️ 技术要求

- Python 3.8+
- 操作系统：Windows/Linux/macOS

## 📥 安装指南

### 方式一：直接下载使用（推荐）

1. 从 [Releases](https://github.com/your-username/course-nfo-manager/releases) 页面下载适合您系统的最新版本：
   - Windows: `course-nfo-manager-windows.exe`
   - macOS: `course-nfo-manager-macos`
   - Linux: `course-nfo-manager-linux`
2. 运行下载的可执行文件

### 方式二：从源码安装

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/course-nfo-manager.git
cd course-nfo-manager

# 2. 安装 Poetry（如果尚未安装）
pip install poetry

# 3. 安装依赖
poetry install

# 4. 运行程序
poetry run course-nfo-manager
```

## 🚀 快速开始

```bash
# 运行程序
python main.py
```

## 📂 目录结构规范

课程目录需要遵循以下结构：

```
课程名称[语言标识]
├── 普通话Deepl/          # 中文课程目录
│   ├── 第1章/
│   │   ├── 1.1课程.mp4
│   │   └── 1.2课程.mp4
│   └── 第2章/
└── 原/                   # 原始语言课程目录
```

### 示例

```
完整的C#大师课程 Complete C# Masterclass[普通话]
├── 普通话Deepl
│   ├── 1 - 你的第一个 C 程序与 Visual Studio 概述
│   │   ├── 1 - 引言.mp4
│   │   └── 2 - 你想达成什么.mp4
│   └── 2 - 数据类型和变量
│       ├── 20 - 更多数据类型及其限制.mp4
│       └── 22 - 数据类型：整型、浮点型与双精度型.mp4
└── 原
```

## 💡 功能详解

### 1. NFO生成器
- 多层目录结构识别
- 智能章节结构分析
- 自动标签继承系统
- 灵活的覆盖选项

### 2. NFO编辑器
- 批量信息编辑
- 海报管理系统
- 自定义标签系统

## 📸 界面预览

<div align="center">
  <img src="docs/1.png" alt="主界面" width="600"/>
  <br/>
  <img src="docs/4.png" alt="NFO编辑" width="600"/>
  <br/>
  <img src="docs/5.png" alt="批量处理" width="600"/>
  <br/>
  <img src="docs/6.png" alt="设置界面" width="600"/>
</div>

## ⚠️ 注意事项

1. 课程目录命名规范：
   - 中文课程必须放在 `普通话Deepl` 目录下
   - 原始语言课程放在 `原` 目录下
   - NFO文件会自动添加相应的语言后缀（中文课程添加"[普通话]"，原始语言课程添加"[英语]"）
   - 课程目录名称应包含原始语言名称和中文翻译（如果有）

2. .nomedia文件处理：
   - 目前 .nomedia 检测功能处于关闭状态
   - NFO文件将始终在 `原` 目录下生成
   - 不会影响媒体库的正常扫描和识别

3. 文件命名建议：
   - 建议使用阿拉伯数字作为章节编号
   - 避免在文件名中使用特殊字符
   - 保持命名格式的一致性

4. 系统兼容性说明：
   - Windows 用户需要注意文件路径长度限制
   - Linux/macOS 用户注意文件系统大小写敏感性
   - 建议使用 UTF-8 编码保存所有文件

## 🤝 贡献指南

我们欢迎所有形式的贡献，无论是新功能、文档改进还是错误报告。请参考以下步骤：

1. Fork 本仓库
2. 创建新的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🌟 致谢

感谢所有为这个项目做出贡献的开发者们！

## 📮 联系方式

如有任何问题或建议，欢迎通过以下方式联系：

- 提交 [Issue](https://github.com/your-username/course-nfo-manager/issues)
- 发送邮件至：[airmusic@msn.com](mailto:airmusic@msn.com)

## 👨‍💻 开发指南

### 环境设置

```bash
# 安装 Poetry
pip install poetry

# 安装依赖
poetry install

# 激活虚拟环境
poetry shell
```

### 构建可执行文件

```bash
# 安装 PyInstaller
pip install pyinstaller

# Windows
pyinstaller --onefile --windowed --icon=docs/icon.ico --name=course-nfo-manager-windows.exe main.py

# macOS
pyinstaller --onefile --windowed --icon=docs/icon.icns --name=course-nfo-manager-macos main.py

# Linux
pyinstaller --onefile --name=course-nfo-manager-linux main.py
```

### 自动化发布

项目使用 GitHub Actions 进行自动化构建和发布。当推送新的版本标签时，将自动触发构建流程：

```bash
# 创建新的版本标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 推送标签到远程仓库
git push origin v1.0.0
```

这将自动触发构建流程，并在 GitHub Releases 页面创建新的发布版本。

---

<div align="center">

如果这个项目对您有帮助，请考虑给它一个 ⭐️

</div>