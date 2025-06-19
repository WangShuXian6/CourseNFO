"""
标签管理模块
"""
from pathlib import Path
from typing import Set, List
from ..utils.config import config
import os

class TagManager:
    """标签管理器"""
    
    def __init__(self):
        self.tag_extension = config.get('tag_file_extension')
        self.mandarin_dir_name = "普通话Deepl"  # 普通话目录名称
        self.original_dir_name = "原"  # 原始目录名称
        
    def collect_tags(self, course_path: Path) -> Set[str]:
        """收集课程的所有标签"""
        tags = set()
        
        # 收集父目录的标签
        current_path = course_path
        while current_path.parent != current_path:
            tags.update(self._read_tag_file(current_path))
            current_path = current_path.parent
            
        return tags
    
    def _read_tag_file(self, directory: Path) -> Set[str]:
        """读取目录中的标签文件"""
        tags = set()
        
        # 查找目录中的标签文件
        tag_files = list(directory.glob(f'*{self.tag_extension}'))
        
        for tag_file in tag_files:
            try:
                with open(tag_file, 'r', encoding='utf-8') as f:
                    # 读取文件中的每一行作为一个标签
                    for line in f:
                        tag = line.strip()
                        if tag and not tag.startswith('#'):  # 忽略空行和注释
                            tags.add(tag)
            except Exception as e:
                print(f"读取标签文件 {tag_file} 时出错: {e}")
                
        return tags
    
    def save_tags(self, course_path: Path, tags: Set[str]) -> None:
        """保存课程标签"""
        tag_file = course_path / f"course{self.tag_extension}"
        try:
            # 保存标签文件
            with open(tag_file, 'w', encoding='utf-8') as f:
                for tag in sorted(tags):
                    f.write(f"{tag}\n")
            
            # 处理 .nomedia 文件
            # 检查是否存在 "原" 目录（与 "普通话Deepl" 目录同级）
            original_dir = course_path / self.original_dir_name
            if original_dir.exists() and original_dir.is_dir():
                nomedia_file = original_dir / ".nomedia"
                try:
                    # 使用简单的方式创建 .nomedia 文件
                    open(str(nomedia_file), 'a').close()
                except Exception as e:
                    print(f"创建 .nomedia 文件时出错: {e}")
                
        except Exception as e:
            print(f"保存标签文件 {tag_file} 时出错: {e}")
    
    def merge_tags(self, existing_tags: Set[str], new_tags: Set[str]) -> Set[str]:
        """合并标签集合"""
        return existing_tags.union(new_tags)
    
    def remove_tags(self, tags: Set[str], tags_to_remove: Set[str]) -> Set[str]:
        """移除指定标签"""
        return tags.difference(tags_to_remove)
        
    def create_nomedia_files(self, root_path: Path) -> int:
        """在所有"原"目录中创建.nomedia文件
        
        Args:
            root_path: 起始目录路径
            
        Returns:
            创建的文件数量
        """
        created_count = 0
        original_dirs = self._find_original_dirs(root_path)
        
        for directory in original_dirs:
            if self._create_nomedia_file(directory):
                created_count += 1
                
        return created_count
        
    def _find_original_dirs(self, current_path: Path) -> List[Path]:
        """递归查找所有"原"目录
        
        Args:
            current_path: 当前目录路径
            
        Returns:
            找到的"原"目录列表
        """
        original_dirs = []
        
        try:
            # 如果当前目录有.nomedia文件，跳过该目录
            if (current_path / ".nomedia").exists():
                return []
                
            # 如果当前目录是"原"目录，添加到列表
            if current_path.name == self.original_dir_name:
                original_dirs.append(current_path)
            
            # 递归处理子目录
            for path in current_path.iterdir():
                if path.is_dir():
                    original_dirs.extend(self._find_original_dirs(path))
                    
        except Exception as e:
            print(f"扫描目录 {current_path} 时出错: {e}")
            
        return original_dirs
        
    def _create_nomedia_file(self, directory: Path) -> bool:
        """在指定目录中创建.nomedia文件
        
        Args:
            directory: 目标目录
            
        Returns:
            是否创建成功
        """
        try:
            nomedia_file = directory / ".nomedia"
            if not nomedia_file.exists():
                open(str(nomedia_file), 'a').close()
                return True
        except Exception as e:
            print(f"在目录 {directory} 中创建 .nomedia 文件时出错: {e}")
        return False 