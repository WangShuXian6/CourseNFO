# 课程NFO管理器 CourseNFO

一个用于管理和生成课程NFO文件的工具，支持批量生成和编辑NFO文件，管理课程海报等功能。

支持 绿联 NAS 影视中心。
理论上支持所有媒体库管理软件。

注意，课程必须放在 `普通话Deepl` 目录下，nfo名称自带 `普通话` 后缀。
放在 `原` 目录下，nfo名称自带 `英语` 后缀。

例如

```
----完整的C#大师课程 Complete C# Masterclass[普通话]
------普通话Deepl
--------1 - 你的第一个 C 程序与 Visual Studio 概述
----------1 - 引言.mp4
----------2 - 你想达成什么.mp4
--------2 - 数据类型和变量
----------20 - 更多数据类型及其限制.mp4
----------22 - 数据类型：整型、浮点型与双精度型.mp4
------原
```


![1](docs/1.png)
![4](docs/4.png)

## 项目结构

```
nfo/
├── requirements.txt    # 项目依赖
├── README.md          # 项目说明
├── src/               # 源代码目录
│   ├── core/          # 核心功能
│   │   ├── scanner.py     # 目录扫描器
│   │   ├── nfo.py         # NFO生成器
│   │   └── tags.py        # 标签管理器
│   ├── gui/           # 界面相关
│   │   ├── main_window.py # 主窗口
│   │   ├── nfo_gen.py     # NFO生成标签页
│   │   └── nfo_edit.py    # NFO编辑标签页
│   └── utils/         # 工具类
│       ├── config.py      # 配置管理
│       └── poster.py      # 海报处理
└── main.py            # 程序入口
```

## 功能特性

1. NFO生成器
   - 支持多层目录结构的课程识别
   - 智能识别课程章节结构
   - 自动继承父目录标签
   - 可选是否覆盖已有NFO

2. NFO编辑器
   - 批量编辑NFO信息
   - 管理课程海报
   - 自定义标签管理

## 使用说明

使用虚拟环境
若想使用虚拟环境，要先将其“激活”
```bash
python -m venv venv
pip install -r requirements.txt
source venv/Scripts/activate
```

Linux 或 macOS
```bash
source venv/bin/activate
```
Windows
```bash
#开启脚本权限
#管理员权限运行 powershell，更改策略后也许需要重启系统
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

venv\Scripts\activate
```
1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行程序：
```bash
python main.py
``` 


注意：
是否开启对 .nomedia 的检测 功能无效，永远不会检测，始终在 原 目录下生成 nfo.