import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path
from src.core.tags import TagManager

# 创建 TagManager 实例
tag_manager = TagManager()

# 测试路径
course_path = Path(r"G:\测试nfo\后端\C#\完整的C#大师课程 Complete C# Masterclass[普通话]")

# 测试保存标签
print("测试保存标签...")
tags = {"测试标签", "隐藏"}
tag_manager.save_tags(course_path, tags)
print("测试完成！")

# 测试创建 .nomedia 文件
original_dir = course_path / "原"
if original_dir.exists():
    print(f"找到原始目录: {original_dir}")
    nomedia_file = original_dir / ".nomedia"
    print(f"准备创建 .nomedia 文件: {nomedia_file}")
    try:
        # 使用 os.open 和 os.close
        fd = os.open(str(nomedia_file), os.O_CREAT | os.O_WRONLY)
        os.close(fd)
        print(f".nomedia 文件创建成功: {nomedia_file}")
    except Exception as e:
        print(f"创建 .nomedia 文件时出错: {e}")
else:
    print(f"原始目录不存在: {original_dir}") 