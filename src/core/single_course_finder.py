"""
Single文件课程查找模块
"""
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
import glob
import re

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
    sub_chapters: List['Chapter'] = None

@dataclass
class SingleCourseInfo:
    """Single文件课程信息"""
    path: Path
    name: str
    single_file: Path
    video_count: int
    chapters: List[Chapter]

class SingleCourseFinder:
    """Single文件课程查找器"""
    
    def __init__(self):
        self.single_file_patterns = ["single", "single.*"]  # 支持无后缀和任意后缀
        self.video_extensions = ['.mp4', '.mkv', '.avi']
    
    def is_video_file(self, path: Path) -> bool:
        """判断是否为视频文件"""
        return path.suffix.lower() in self.video_extensions
    
    def _extract_number(self, filename: str) -> int:
        """从文件名中提取数字"""
        match = re.match(r'^(\d+)(?:\s*-\s*|\s+|\-)?', filename)
        if match:
            return int(match.group(1))
        return 999999
    
    def _get_video_files_sorted(self, path: Path) -> List[VideoFile]:
        """获取目录下所有视频文件并排序"""
        video_files = []
        for file in path.rglob("*"):
            if self.is_video_file(file):
                video_files.append(VideoFile(
                    path=file,
                    name=file.stem,
                    episode_number=1
                ))
        
        # 按最顶层目录名称中的数字和文件名中的数字排序
        def sort_key(video: VideoFile) -> tuple:
            parents = list(video.path.parents)
            top_level_dir = None
            for parent in reversed(parents):
                if parent.parent == path:
                    top_level_dir = parent
                    break
            
            # 根目录视频优先级最高（序号为0）
            if top_level_dir is None:
                file_num = self._extract_number(video.name)
                return (0, file_num, video.name)
            
            # 二级目录视频：目录数字 * 1000 + 文件名数字
            top_dir_num = self._extract_number(top_level_dir.name)
            file_num = self._extract_number(video.name)
            
            return (top_dir_num, file_num, video.name)
        
        video_files.sort(key=sort_key)
        
        # 更新全局集数
        for i, video in enumerate(video_files, 1):
            video.global_episode_number = i
            
        return video_files
    
    def _detect_structure_type(self, path: Path) -> int:
        """检测目录结构类型
        返回值：
        1: 一级结构（仅根目录有视频）
        2: 二级结构（仅二级目录有视频）
        3: 三级结构（三级目录有视频）
        4: 混合结构（根目录有视频 + 二级目录有视频）
        0: 无有效结构
        """
        # 检查根目录是否有直接视频
        root_has_videos = any(self.is_video_file(f) for f in path.iterdir())
        
        # 检查是否有二级目录包含视频
        subdir_has_videos = False
        has_three_level = False
        
        for item in path.iterdir():
            if item.is_dir():
                # 检查二级目录下是否有视频
                subdir_videos = any(self.is_video_file(f) for f in item.iterdir())
                if subdir_videos:
                    subdir_has_videos = True
                
                # 检查是否有三级目录
                for subitem in item.iterdir():
                    if subitem.is_dir():
                        has_three_level = True
                        break
        
        # 判断结构类型
        if root_has_videos and subdir_has_videos:
            return 4  # 混合结构
        elif root_has_videos:
            return 1  # 一级结构
        elif has_three_level:
            return 3  # 三级结构
        elif subdir_has_videos:
            return 2  # 二级结构
        
        return 0
    
    def _scan_chapters(self, path: Path, structure_type: int, all_videos: List[VideoFile]) -> List[Chapter]:
        """扫描章节"""
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
                    
                videos = [v for v in all_videos if v.path.parent == chapter_dir]
                if videos:
                    chapters.append(Chapter(
                        name=chapter_dir.name,
                        videos=videos
                    ))
            return chapters
            
        elif structure_type == 4:
            # 混合结构：根目录视频 + 二级目录视频
            chapters = []
            
            # 首先添加根目录视频作为第一个章节
            root_videos = [v for v in all_videos if v.path.parent == path]
            if root_videos:
                chapters.append(Chapter(
                    name="根目录",
                    videos=root_videos
                ))
            
            # 然后添加二级目录视频
            for chapter_dir in sorted(path.iterdir()):
                if not chapter_dir.is_dir():
                    continue
                    
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
    
    def find_single_courses(self, root_path: Path) -> List[SingleCourseInfo]:
        """递归查找包含single文件的课程目录
        
        Args:
            root_path: 根目录路径
            
        Returns:
            找到的Single文件课程信息列表
        """
        courses = []
        self._scan_directory_recursive(root_path, courses)
        return courses
    
    def _scan_directory_recursive(self, current_path: Path, courses: List[SingleCourseInfo]):
        """递归扫描目录
        
        Args:
            current_path: 当前扫描的目录
            courses: 课程信息列表
        """
        try:
            # 检查当前目录是否包含single文件
            single_file = self._find_single_file(current_path)
            if single_file:
                # 如果包含single文件，则这是一个课程目录
                course_info = self._create_single_course_info(current_path, single_file)
                if course_info:
                    courses.append(course_info)
                # 找到课程目录后，不再递归扫描其子目录
                return
            
            # 如果不是课程目录，继续递归扫描子目录
            for item in current_path.iterdir():
                if item.is_dir():
                    self._scan_directory_recursive(item, courses)
                    
        except PermissionError:
            print(f"权限不足，无法访问目录: {current_path}")
        except Exception as e:
            print(f"扫描目录时出错 {current_path}: {e}")
    
    def _find_single_file(self, path: Path) -> Optional[Path]:
        """检测目录是否包含single文件
        
        Args:
            path: 目录路径
            
        Returns:
            single文件路径，如果不存在则返回None
        """
        try:
            # 检查是否存在single文件（无后缀）
            single_file = path / "single"
            if single_file.exists() and single_file.is_file():
                return single_file
            
            # 检查是否存在single.*文件（任意后缀）
            for pattern in self.single_file_patterns:
                matches = list(path.glob(pattern))
                if matches:
                    return matches[0]  # 返回第一个匹配的文件
            
            return None
        except Exception:
            return None
    
    def _create_single_course_info(self, path: Path, single_file: Path) -> Optional[SingleCourseInfo]:
        """创建Single文件课程信息
        
        Args:
            path: 课程目录路径
            single_file: single文件路径
            
        Returns:
            课程信息对象，如果无效则返回None
        """
        try:
            # 获取课程名称
            course_name = path.name
            
            # 检测目录结构类型
            structure_type = self._detect_structure_type(path)
            if structure_type == 0:
                return None
            
            # 获取所有视频文件并排序
            all_videos = self._get_video_files_sorted(path)
            if not all_videos:
                return None
            
            # 根据结构类型组织章节
            chapters = self._scan_chapters(path, structure_type, all_videos)
            
            return SingleCourseInfo(
                path=path,
                name=course_name,
                single_file=single_file,
                video_count=len(all_videos),
                chapters=chapters
            )
            
        except Exception as e:
            print(f"创建Single文件课程信息时出错 {path}: {e}")
            return None
    
    def get_scan_statistics(self, courses: List[SingleCourseInfo]) -> dict:
        """获取扫描统计信息
        
        Args:
            courses: 课程信息列表
            
        Returns:
            统计信息字典
        """
        total_courses = len(courses)
        total_videos = sum(course.video_count for course in courses)
        
        return {
            "total_courses": total_courses,
            "total_videos": total_videos,
            "average_videos_per_course": total_videos / total_courses if total_courses > 0 else 0
        }