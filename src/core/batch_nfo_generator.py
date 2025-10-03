"""
批量NFO生成模块
"""
from pathlib import Path
from typing import List, Set, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom
from .scanner import VideoFile, Chapter

class BatchNFOGenerator:
    """批量NFO生成器"""
    
    def __init__(self):
        self.overwrite = True  # 默认覆盖现有文件
        # 语言目录命名映射支持
        self.mandarin_dir_names = {"普通话Deepl", "普通话DeepL", "普通话DeepL[男声]", "普通话DeepL[女声]", "普通话OpenAI-4o-mini", "普通话gemini"}
        self.original_dir_names = {"原"}
        
    def generate_course_nfos(self, course_path: Path, language_path: Path, 
                           chapters: List[Chapter], is_mandarin: bool = True) -> None:
        """为课程生成所有NFO文件
        
        Args:
            course_path: 课程根目录路径
            language_path: 语言目录路径（普通话DeepL或原）
            chapters: 章节列表
            is_mandarin: 是否为普通话版本
        """
        try:
            # 生成tvshow.nfo
            self._generate_tvshow_nfo(course_path, language_path, chapters, is_mandarin)
            
            # 生成所有视频的NFO文件
            language_label = self._get_language_label(language_path.name, is_mandarin)
            self._generate_all_episode_nfos(language_path, chapters, language_label)
            
            print(f"成功为 {course_path.name} 的 {language_path.name} 版本生成所有NFO文件")
            
        except Exception as e:
            print(f"生成课程NFO文件时出错: {e}")
    
    def _generate_tvshow_nfo(self, course_path: Path, language_path: Path, 
                            chapters: List[Chapter], is_mandarin: bool) -> None:
        """生成课程主NFO文件"""
        try:
            nfo_path = language_path / "tvshow.nfo"
            
            if not nfo_path.exists() or self.overwrite:
                root = ET.Element("tvshow")
                
                # 添加标题
                title = ET.SubElement(root, "title")
                course_name = course_path.name
                if "[" in course_name:
                    course_name = course_name.split("[")[0].strip()
                
                language_label = self._get_language_label(language_path.name, is_mandarin)
                title.text = f"{course_name} {language_label}"
                
                # 添加描述
                plot = ET.SubElement(root, "plot")
                total_videos = self._count_total_videos(chapters)
                language_label = self._get_language_label(language_path.name, is_mandarin)
                plot.text = f"课程：{course_path.name}\n总集数：{total_videos}\n语言：{language_label}"
                
                # 添加语言标签
                genre = ET.SubElement(root, "genre")
                # genre 只标记主语种
                genre.text = "普通话" if is_mandarin else "英语"
                
                # 写入文件
                self._write_xml(root, nfo_path)
                print(f"生成tvshow.nfo: {nfo_path}")
                
        except Exception as e:
            print(f"生成tvshow.nfo时出错: {e}")

    def _get_language_label(self, dir_name: str, is_mandarin: bool) -> str:
        """根据语言目录名生成标题中的语言标识。
        普通话目录返回目录本身的名称，方便区分多版本的普通话NFO。
        原版目录继续使用英语标识。
        """
        dir_name = (dir_name or "").strip()
        if dir_name in self.original_dir_names or dir_name == "原":
            return "英语"
        if is_mandarin:
            return dir_name or "普通话"
        return dir_name or "英语"

    def _generate_all_episode_nfos(self, language_path: Path, chapters: List[Chapter], language_label: str) -> None:
        """生成所有视频的NFO文件"""
        try:
            for chapter in chapters:
                self._generate_chapter_episode_nfos(language_path, chapter, language_label)
                
        except Exception as e:
            print(f"生成视频NFO文件时出错: {e}")
    
    def _generate_chapter_episode_nfos(self, language_path: Path, chapter: Chapter, 
                                     language_label: str, parent_chapter_name: str = "") -> None:
        """生成章节中所有视频的NFO文件"""
        try:
            # 处理当前章节的视频
            if chapter.videos:
                chapter_name = f"{parent_chapter_name} - {chapter.name}" if parent_chapter_name else chapter.name
                for video in chapter.videos:
                    self._generate_episode_nfo(video, chapter_name, language_label)
            
            # 处理子章节的视频
            if chapter.sub_chapters is not None:
                for sub_chapter in chapter.sub_chapters:
                    parent_name = f"{parent_chapter_name} - {chapter.name}" if parent_chapter_name else chapter.name
                    self._generate_chapter_episode_nfos(language_path, sub_chapter, language_label, parent_name)
                
        except Exception as e:
            print(f"生成章节视频NFO文件时出错: {e}")
    
    def _generate_episode_nfo(self, video: VideoFile, chapter_name: str, language_label: str) -> None:
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
                # 追加语言信息
                plot.text = f"{base}\n语言：{language_label}" if base else f"语言：{language_label}"
                
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
