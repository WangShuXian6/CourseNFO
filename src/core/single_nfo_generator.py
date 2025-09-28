"""
Single文件课程NFO生成模块
"""
from pathlib import Path
from typing import List
import xml.etree.ElementTree as ET
from xml.dom import minidom
from .single_course_finder import VideoFile, Chapter

class SingleNFOGenerator:
    """Single文件课程NFO生成器"""
    
    def __init__(self):
        self.overwrite = True  # 默认覆盖现有文件
        
    def generate_course_nfos(self, course_path: Path, chapters: List[Chapter]) -> None:
        """为Single文件课程生成所有NFO文件
        
        Args:
            course_path: 课程根目录路径
            chapters: 章节列表
        """
        try:
            # 生成tvshow.nfo
            self._generate_tvshow_nfo(course_path, chapters)
            
            # 生成所有视频的NFO文件
            self._generate_all_episode_nfos(course_path, chapters)
            
            print(f"成功为Single文件课程 {course_path.name} 生成所有NFO文件")
            
        except Exception as e:
            print(f"生成Single文件课程NFO文件时出错: {e}")
    
    def _generate_tvshow_nfo(self, course_path: Path, chapters: List[Chapter]) -> None:
        """生成Single文件课程主NFO文件"""
        try:
            nfo_path = course_path / "tvshow.nfo"
            
            if not nfo_path.exists() or self.overwrite:
                root = ET.Element("tvshow")
                
                # 添加标题
                title = ET.SubElement(root, "title")
                course_name = course_path.name
                if "[" in course_name:
                    course_name = course_name.split("[")[0].strip()
                
                title.text = f"{course_name} 课程"
                
                # 添加描述
                plot = ET.SubElement(root, "plot")
                total_videos = self._count_total_videos(chapters)
                plot.text = f"课程：{course_path.name}\n总集数：{total_videos}\n类型：Single文件课程"
                
                # 添加类型标签
                genre = ET.SubElement(root, "genre")
                genre.text = "课程"
                
                # 写入文件
                self._write_xml(root, nfo_path)
                print(f"生成tvshow.nfo: {nfo_path}")
                
        except Exception as e:
            print(f"生成tvshow.nfo时出错: {e}")
    
    def _generate_all_episode_nfos(self, course_path: Path, chapters: List[Chapter]) -> None:
        """生成所有视频的NFO文件"""
        try:
            for chapter in chapters:
                self._generate_chapter_episode_nfos(course_path, chapter)
                
        except Exception as e:
            print(f"生成视频NFO文件时出错: {e}")
    
    def _generate_chapter_episode_nfos(self, course_path: Path, chapter: Chapter, 
                                     parent_chapter_name: str = "") -> None:
        """生成章节中所有视频的NFO文件"""
        try:
            # 处理当前章节的视频
            if chapter.videos:
                chapter_name = f"{parent_chapter_name} - {chapter.name}" if parent_chapter_name else chapter.name
                for video in chapter.videos:
                    self._generate_episode_nfo(video, chapter_name)
            
            # 处理子章节的视频
            if chapter.sub_chapters is not None:
                for sub_chapter in chapter.sub_chapters:
                    parent_name = f"{parent_chapter_name} - {chapter.name}" if parent_chapter_name else chapter.name
                    self._generate_chapter_episode_nfos(course_path, sub_chapter, parent_name)
                
        except Exception as e:
            print(f"生成章节视频NFO文件时出错: {e}")
    
    def _generate_episode_nfo(self, video: VideoFile, chapter_name: str) -> None:
        """生成单个视频的NFO文件"""
        try:
            nfo_path = video.path.with_suffix('.nfo')
            
            if not nfo_path.exists() or self.overwrite:
                root = ET.Element("episodedetails")
                
                # 添加标题
                title = ET.SubElement(root, "title")
                title.text = video.name
                
                # 添加描述
                plot = ET.SubElement(root, "plot")
                base = f"章节：{chapter_name}" if chapter_name else ""
                plot.text = f"{base}\n类型：Single文件课程" if base else "类型：Single文件课程"
                
                # 添加季数
                season = ET.SubElement(root, "season")
                season.text = "1"
                
                # 添加集数
                episode = ET.SubElement(root, "episode")
                episode.text = str(video.global_episode_number)
                
                # 写入文件
                self._write_xml(root, nfo_path)
                print(f"生成视频NFO: {video.name} (集数: {video.global_episode_number})")
                
        except Exception as e:
            print(f"生成视频NFO文件时出错 {video.name}: {e}")
    
    def _count_total_videos(self, chapters: List[Chapter]) -> int:
        """计算总视频数量"""
        total = 0
        for chapter in chapters:
            total += len(chapter.videos)
            # 检查sub_chapters是否为None，避免NoneType错误
            if chapter.sub_chapters is not None:
                total += self._count_total_videos(chapter.sub_chapters)
        return total
    
    def _write_xml(self, root: ET.Element, path: Path) -> None:
        """格式化并写入XML文件"""
        try:
            # 转换为字符串并格式化
            xml_str = minidom.parseString(ET.tostring(root, 'utf-8')).toprettyxml(indent="  ")
            
            # 写入文件
            with open(path, 'w', encoding='utf-8') as f:
                f.write(xml_str)
                
        except Exception as e:
            print(f"写入XML文件时出错 {path}: {e}")
