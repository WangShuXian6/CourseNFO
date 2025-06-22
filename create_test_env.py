# -*- coding: utf-8 -*-
import os
from pathlib import Path

def create_test_env():
    # 基础路径和课程名称
    base_dir = Path("测试目录")
    course_name = "完整的C#大师课程 Complete C# Masterclass[普通话]"
    
    # 创建基础目录结构
    course_path = base_dir / "后端" / "C#" / course_name
    mandarin_path = course_path / "普通话Deepl" / course_name
    original_path = course_path / "原"
    
    # 创建所有必要的目录
    mandarin_path.mkdir(parents=True, exist_ok=True)
    original_path.mkdir(parents=True, exist_ok=True)
    
    # 创建子目录
    chapter_dirs = [
        mandarin_path / "01 - 简介" / "01 - module",
        mandarin_path / "01 - 简介" / "02 - module",
        mandarin_path / "02 - 设定产品愿景、战略和战略路线图" / "01 - modulea"
    ]
    
    for dir_path in chapter_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # 创建视频文件
    videos = [
        (mandarin_path / "01 - 简介" / "01 - module" / "6 - 引言.mp4", b""),
        (mandarin_path / "01 - 简介" / "01 - module" / "7 - 你想达成什么.mp4", b""),
        (mandarin_path / "01 - 简介" / "02 - module" / "0 - 引言a.mp4", b""),
        (mandarin_path / "01 - 简介" / "02 - module" / "1 - 你想达成什么a.mp4", b""),
        (mandarin_path / "02 - 设定产品愿景、战略和战略路线图" / "01 - modulea" / "2 - 更多数据类型及其限制.mp4", b""),
        (mandarin_path / "02 - 设定产品愿景、战略和战略路线图" / "01 - modulea" / "3 - 数据类型：整型、浮点型与双精度型.mp4", b"")
    ]
    
    for video_path, content in videos:
        with open(video_path, "wb") as f:
            f.write(content)
    
    print("测试环境创建完成！")

if __name__ == "__main__":
    create_test_env()
