"""
课程批量查找模块
"""
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
import os

@dataclass
class CourseInfo:
    """课程信息"""
    path: Path
    name: str
    has_mandarin: bool
    has_original: bool
    lesson_files: List[Path]
    mandarin_paths: List[Path] = field(default_factory=list)
    original_path: Optional[Path] = None

class CourseBatchFinder:
    """课程批量查找器"""
    
    def __init__(self):
        # 兼容不同的普通话目录命名（可由GUI在运行时扩展）
        self.mandarin_dir_names = {"普通话Deepl", "普通话DeepL", "普通话DeepL[男声]", "普通话DeepL[女声]", "普通话OpenAI-4o-mini", "普通话gemini"}
        # 兼容可能的原版目录命名（目前以“原”为主，后续可扩展）
        self.original_dir_names = {"原"}
        self.lesson_file_name = "lession"  # 课程标识文件名称
    
    def find_courses_with_lession(self, root_path: Path) -> List[CourseInfo]:
        """递归查找包含lession文件的课程目录
        
        Args:
            root_path: 根目录路径
            
        Returns:
            找到的课程信息列表
        """
        courses = []
        self._scan_directory_recursive(root_path, courses)
        return courses
    
    def _scan_directory_recursive(self, current_path: Path, courses: List[CourseInfo]):
        """递归扫描目录
        
        Args:
            current_path: 当前扫描的目录
            courses: 课程信息列表
        """
        try:
            # 检查当前目录是否包含lession文件
            if self._is_course_directory(current_path):
                # 如果包含lession文件，则这是一个课程目录
                course_info = self._create_course_info(current_path)
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
    
    def _is_course_directory(self, path: Path) -> bool:
        """检测目录是否包含lession文件
        
        Args:
            path: 目录路径
            
        Returns:
            是否包含lession文件
        """
        try:
            # 检查是否存在lession文件（不区分大小写）
            for item in path.iterdir():
                if item.is_file() and item.name.lower() == self.lesson_file_name.lower():
                    return True
            return False
        except Exception:
            return False
    
    def _create_course_info(self, path: Path) -> Optional[CourseInfo]:
        """创建课程信息
        
        Args:
            path: 课程目录路径
            
        Returns:
            课程信息对象，如果无效则返回None
        """
        try:
            # 获取课程名称
            course_name = path.name
            
            # 查找lession文件
            lesson_files = []
            for item in path.iterdir():
                if item.is_file() and item.name.lower() == self.lesson_file_name.lower():
                    lesson_files.append(item)
            
            if not lesson_files:
                return None
            
            # 检查语言目录并解析实际路径
            mandarin_paths, original_path = self._resolve_language_directories(path)
            has_mandarin = bool(mandarin_paths)
            has_original = original_path is not None
            
            return CourseInfo(
                path=path,
                name=course_name,
                has_mandarin=has_mandarin,
                has_original=has_original,
                lesson_files=lesson_files,
                mandarin_paths=mandarin_paths,
                original_path=original_path
            )
            
        except Exception as e:
            print(f"创建课程信息时出错 {path}: {e}")
            return None
    
    def _resolve_language_directories(self, path: Path) -> Tuple[List[Path], Optional[Path]]:
        """解析课程目录中的语言子目录，返回实际路径
        
        Args:
            path: 课程目录路径
            
        Returns:
            (普通话目录Path列表, 原版目录Path或None)
        """
        try:
            mandarin_paths = []
            original_path = None
            for item in path.iterdir():
                if not item.is_dir():
                    continue
                # 普通话目录匹配（两种命名）
                if item.name in self.mandarin_dir_names:
                    mandarin_paths.append(item)
                # 原版目录匹配（当前仅“原”）
                if item.name in self.original_dir_names:
                    original_path = item
            mandarin_paths.sort(key=lambda p: p.name)
            return mandarin_paths, original_path
        except Exception:
            return [], None
    
    def get_scan_statistics(self, courses: List[CourseInfo]) -> dict:
        """获取扫描统计信息
        
        Args:
            courses: 课程信息列表
            
        Returns:
            统计信息字典
        """
        total_courses = len(courses)
        mandarin_courses = sum(1 for course in courses if course.has_mandarin)
        original_courses = sum(1 for course in courses if course.has_original)
        both_languages = sum(1 for course in courses if course.has_mandarin and course.has_original)
        
        return {
            "total_courses": total_courses,
            "mandarin_courses": mandarin_courses,
            "original_courses": original_courses,
            "both_languages": both_languages,
            "mandarin_only": mandarin_courses - both_languages,
            "original_only": original_courses - both_languages
        }
