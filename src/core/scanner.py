"""
目录扫描模块
"""
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass, field
import re
from ..utils.config import config

@dataclass
class VideoFile:
    """视频文件信息"""
    path: Path
    name: str
    episode_number: int = 1
    global_episode_number: int = 1  # 全局集数

@dataclass
class Chapter:
    """章节信息"""
    name: str
    videos: List[VideoFile]
    sub_chapters: List['Chapter'] = field(default_factory=list)

@dataclass
class Course:
    """课程信息"""
    path: Path
    name: str
    structure_type: int  # 1: 一级结构, 2: 二级结构, 3: 三级结构
    chapters: List[Chapter]
    video_count: int

class DirectoryScanner:
    """目录扫描器"""
    
    def __init__(self):
        self.min_length = config.get('min_course_name_length')
        self.video_extensions = config.get('video_extensions')
        self.mandarin_dir_name = "普通话Deepl"  # 普通话目录名称
        self.original_dir_name = "原"  # 原始目录名称
        self.check_nomedia = config.get('check_nomedia')  # 是否检查 .nomedia 文件
    
    def is_video_file(self, path: Path) -> bool:
        """判断是否为视频文件"""
        return path.suffix.lower() in self.video_extensions
    
    def _should_skip_directory(self, path: Path) -> bool:
        """检查是否应该跳过目录扫描
        
        如果启用了 .nomedia 检查，且目录中存在 .nomedia 文件，则跳过该目录
        """
        return self.check_nomedia and (path / ".nomedia").exists()
    
    def _extract_number(self, filename: str) -> int:
        """从文件名中提取数字
        
        处理通用的"数字+汉字字母"格式，例如：
        - 1引言.mp4
        - 1-引言.mp4
        - 1 引言.mp4
        - 1 - 引言.mp4
        - 001引言.mp4
        - 001 引言.mp4
        - 001-引言.mp4
        - 001 - 引言.mp4
        """
        # 匹配文件名开头的数字部分
        match = re.match(r'^(\d+)(?:\s*-\s*|\s+|\-)?', filename)
        if match:
            return int(match.group(1))
            
        # 如果没有找到数字，返回一个大数，确保未命名的文件排在最后
        return 999999  # 使用固定的大整数替代 float('inf')
    
    def _get_video_files_sorted(self, path: Path) -> List[VideoFile]:
        """获取目录下所有视频文件并排序
        
        排序规则：
        1. 父目录名称中的数字优先级最高
        2. 在同一父目录内，按视频文件名中的数字排序
        """
        video_files = []
        for file in path.rglob("*"):
            if self.is_video_file(file):
                video_files.append(VideoFile(
                    path=file,
                    name=file.stem,
                    episode_number=1  # 临时值，稍后更新
                ))
        
        # 按父目录名称中的数字和文件名中的数字排序
        def sort_key(video: VideoFile) -> tuple:
            # 获取父目录名称中的数字
            parent_dir_num = self._extract_number(video.path.parent.name)
            # 获取文件名中的数字
            file_num = self._extract_number(video.name)
            # 返回排序元组：(父目录数字, 文件名数字, 完整文件名)
            return (parent_dir_num, file_num, video.name)
        
        # 按复合键排序
        video_files.sort(key=sort_key)
        
        # 更新全局集数
        for i, video in enumerate(video_files, 1):
            video.global_episode_number = i
            
        return video_files
    
    def scan_directory(self, root_path: Path) -> List[Course]:
        """扫描目录"""
        courses = []
        self._scan_directory_recursive(root_path, courses)
        return courses
    
    def _scan_directory_recursive(self, current_path: Path, courses: List[Course]):
        """递归扫描目录"""
        # 检查是否应该跳过该目录
        if self._should_skip_directory(current_path):
            return
            
        # 扫描当前目录
        for path in current_path.iterdir():
            if not path.is_dir():
                continue
                
            # 检查是否为课程目录（包含"普通话Deepl"或"原"子目录）
            mandarin_path = path / self.mandarin_dir_name
            original_path = path / self.original_dir_name
            
            if (mandarin_path.exists() and mandarin_path.is_dir()) or (original_path.exists() and original_path.is_dir()):
                # 如果目录名长度符合要求，添加为课程
                if len(path.name) >= self.min_length:
                    # 检查并处理"普通话Deepl"目录
                    if mandarin_path.exists() and mandarin_path.is_dir():
                        structure_type = self._detect_structure_type(mandarin_path)
                        if structure_type > 0:
                            # 先获取所有视频文件并排序
                            all_videos = self._get_video_files_sorted(mandarin_path)
                            if all_videos:
                                # 根据结构类型组织章节
                                chapters = self._scan_chapters(mandarin_path, structure_type, all_videos)
                                courses.append(Course(
                                    path=path,
                                    name=path.name,
                                    structure_type=structure_type,
                                    chapters=chapters,
                                    video_count=len(all_videos)
                                ))
                    
                    # 检查并处理"原"目录
                    if original_path.exists() and original_path.is_dir():
                        structure_type = self._detect_structure_type(original_path)
                        if structure_type > 0:
                            # 先获取所有视频文件并排序
                            all_videos = self._get_video_files_sorted(original_path)
                            if all_videos:
                                # 根据结构类型组织章节
                                chapters = self._scan_chapters(original_path, structure_type, all_videos)
                                courses.append(Course(
                                    path=path,
                                    name=path.name,
                                    structure_type=structure_type,
                                    chapters=chapters,
                                    video_count=len(all_videos)
                                ))
            else:
                # 如果不是课程目录，递归扫描子目录
                self._scan_directory_recursive(path, courses)
    
    def _detect_structure_type(self, path: Path) -> int:
        """检测目录结构类型"""
        # 检查是否为一级结构（直接包含视频）
        has_videos = any(self.is_video_file(f) for f in path.iterdir())
        if has_videos:
            return 1
            
        # 检查二级结构
        for item in path.iterdir():
            if item.is_dir():
                # 如果章节目录下有子目录，则为三级结构
                has_subdirs = any(f.is_dir() for f in item.iterdir())
                if has_subdirs:
                    return 3
                # 如果章节目录下直接有视频，则为二级结构
                has_videos = any(self.is_video_file(f) for f in item.iterdir())
                if has_videos:
                    return 2
        
        return 0
    
    def _scan_chapters(self, path: Path, structure_type: int, all_videos: List[VideoFile]) -> List[Chapter]:
        """扫描章节
        
        Args:
            path: 目录路径
            structure_type: 目录结构类型
            all_videos: 所有视频文件（已排序且已设置全局集数）
        """
        if structure_type == 1:
            # 一级结构：直接返回视频列表
            videos = [v for v in all_videos if v.path.parent == path]
            return [Chapter(name="", videos=videos)]
            
        elif structure_type == 2:
            # 二级结构：每个目录是一个章节
            chapters = []
            for chapter_dir in sorted(path.iterdir()):
                if not chapter_dir.is_dir():
                    continue
                    
                # 获取当前章节的视频
                videos = [v for v in all_videos if v.path.parent == chapter_dir]
                if videos:
                    chapters.append(Chapter(
                        name=chapter_dir.name,
                        videos=videos
                    ))
            return chapters
            
        else:  # structure_type == 3
            # 三级结构：大章节下包含小章节
            chapters = []
            for major_chapter in sorted(path.iterdir()):
                if not major_chapter.is_dir():
                    continue
                    
                sub_chapters = []
                for minor_chapter in sorted(major_chapter.iterdir()):
                    if not minor_chapter.is_dir():
                        continue
                        
                    # 获取当前小章节的视频
                    videos = [v for v in all_videos if v.path.parent == minor_chapter]
                    if videos:
                        sub_chapters.append(Chapter(
                            name=minor_chapter.name,
                            videos=videos
                        ))
                        
                if sub_chapters:
                    chapters.append(Chapter(
                        name=major_chapter.name,
                        videos=[],
                        sub_chapters=sub_chapters
                    ))
            return chapters 