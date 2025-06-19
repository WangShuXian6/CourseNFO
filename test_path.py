from pathlib import Path
import os

# 测试路径
base_path = Path(r"G:\测试nfo\后端\C#\完整的C#大师课程 Complete C# Masterclass[普通话]")
print(f"基础目录: {base_path}")
print("\n目录内容:")
try:
    for item in base_path.iterdir():
        print(f"- {item.name}")
except Exception as e:
    print(f"列出目录内容时出错: {e}")

# 检查 "原" 目录和 "普通话Deepl" 目录
original_dir = base_path / "原"
mandarin_dir = base_path / "普通话Deepl"

print(f"\n'原' 目录是否存在: {original_dir.exists()}")
print(f"'普通话Deepl' 目录是否存在: {mandarin_dir.exists()}")

if original_dir.exists():
    print("\n'原' 目录内容:")
    try:
        for item in original_dir.iterdir():
            print(f"- {item.name}")
    except Exception as e:
        print(f"列出目录内容时出错: {e}")

# 尝试创建 .nomedia 文件
if original_dir.exists():
    nomedia_file = original_dir / ".nomedia"
    print(f"\n准备在 '原' 目录中创建 .nomedia 文件: {nomedia_file}")
    try:
        open(str(nomedia_file), 'a').close()
        print(".nomedia 文件创建成功！")
    except Exception as e:
        print(f"创建文件时出错: {e}") 