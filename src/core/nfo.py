"""
NFO生成模块
"""
from pathlib import Path
from typing import Set, List, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom
from dataclasses import dataclass, field
from .scanner import Course, Chapter, VideoFile
from .course_types import CourseType, CourseTypeManager
from ..utils.config import config

@dataclass
class NFOData:
    """NFO数据类"""
    title: str
    plot: str = ""
    tags: Set[str] = field(default_factory=set)
    poster: Optional[Path] = None
    season: int = 1
    episode: int = 1
    course_types: Set[str] = field(default_factory=set)

class NFOGenerator:
    """NFO生成器"""
    
    def __init__(self):
        self.overwrite = config.get('overwrite_existing')
        self.type_manager = CourseTypeManager()
        self.mandarin_dir_name = "普通话Deepl"  # 普通话目录名称
        self.original_dir_name = "原"  # 原始目录名称（英文版）
        
    def generate_course_nfo(self, course: Course, tags: Set[str], course_types: Optional[Set[str]] = None) -> None:
        """生成课程NFO文件
        
        同时在"普通话Deepl"和"原"目录下生成NFO文件，分别使用不同的标题
        """
        # 检查并生成"普通话Deepl"目录的NFO
        mandarin_dir = course.path / self.mandarin_dir_name
        if mandarin_dir.exists() and mandarin_dir.is_dir():
            tvshow_nfo = mandarin_dir / "tvshow.nfo"
            if not tvshow_nfo.exists() or self.overwrite:
                self._generate_tvshow_nfo(course, tags, tvshow_nfo, course_types, is_mandarin=True)
        
        # 检查并生成"原"目录的NFO
        original_dir = course.path / "原"
        if original_dir.exists() and original_dir.is_dir():
            tvshow_nfo = original_dir / "tvshow.nfo"
            if not tvshow_nfo.exists() or self.overwrite:
                self._generate_tvshow_nfo(course, tags, tvshow_nfo, course_types, is_mandarin=False)
        
        # 生成视频NFO文件
        self._generate_episode_nfos(course)
    
    def _generate_tvshow_nfo(self, course: Course, tags: Set[str], nfo_path: Path, course_types: Optional[Set[str]] = None, is_mandarin: bool = True) -> None:
        """生成课程主NFO文件
        
        Args:
            course: 课程信息
            tags: 标签集合
            nfo_path: NFO文件路径
            course_types: 课程类型集合
            is_mandarin: 是否为普通话版本
        """
        root = ET.Element("tvshow")
        
        # 添加基本信息
        title = ET.SubElement(root, "title")
        # 使用课程名作为标题（不包含目录名）
        course_name = course.name
        if "[" in course_name:
            # 如果课程名包含方括号，提取方括号前的部分作为标题
            course_name = course_name.split("[")[0].strip()
        
        # 根据目录类型在标题后添加语言标识
        if is_mandarin:
            title.text = f"{course_name} 普通话"
        else:
            title.text = f"{course_name} 英语"
        
        plot = ET.SubElement(root, "plot")
        plot.text = f"课程：{course.name}\n总集数：{course.video_count}"
        
        # 添加课程类型
        if course_types:
            for course_type in sorted(course_types):
                type_elem = ET.SubElement(root, "coursetype")
                type_elem.text = course_type
        
        # 添加标签
        all_tags = {tag for tag in tags if tag not in {"显示", "隐藏"}}  # 过滤掉"显示"和"隐藏"标签
        
        # 根据目录类型添加不同的标签
        if is_mandarin:
            all_tags.add("普通话")
            # 确保没有"英语"标签
            all_tags.discard("英语")
        else:
            all_tags.add("英语")
            # 确保没有"普通话"标签
            all_tags.discard("普通话")
        
        # 添加所有标签
        for tag in sorted(all_tags):
            genre = ET.SubElement(root, "genre")
            genre.text = tag
        
        # 写入文件
        self._write_xml(root, nfo_path)
    
    def _generate_episode_nfos(self, course: Course) -> None:
        """生成视频NFO文件"""
        def process_videos(videos: List[VideoFile], chapter_name: str = "") -> None:
            for video in videos:
                # 检查视频文件是否在指定目录或其子目录下
                current_dir = video.path.parent
                found_language_dir = False
                language_dir_name = None
                
                # 向上遍历目录直到找到课程根目录
                while current_dir.name != course.path.name:
                    # 记录是否找到语言目录
                    if current_dir.name in {self.mandarin_dir_name, "原"}:
                        found_language_dir = True
                        language_dir_name = current_dir.name
                    current_dir = current_dir.parent
                    if current_dir == course.path:  # 到达课程根目录，停止搜索
                        break
                
                # 如果在正确的语言目录下找到了视频文件，生成NFO
                if found_language_dir:
                    nfo_path = video.path.with_suffix('.nfo')
                    if not nfo_path.exists() or self.overwrite:
                        print(f"生成视频NFO: {video.name} (集数: {video.global_episode_number}, 语言: {language_dir_name})")
                        self._generate_episode_nfo(
                            NFOData(
                                title=video.name,
                                plot=f"章节：{chapter_name}\n" if chapter_name else "",
                                season=1,
                                episode=video.global_episode_number  # 使用全局集数
                            ),
                            nfo_path
                        )
        
        if course.structure_type == 1:
            # 一级结构
            for chapter in course.chapters:
                process_videos(chapter.videos)
                
        elif course.structure_type == 2:
            # 二级结构
            for chapter in course.chapters:
                process_videos(chapter.videos, chapter.name)
                
        else:  # structure_type == 3
            # 三级结构
            for major_chapter in course.chapters:
                for minor_chapter in major_chapter.sub_chapters:
                    process_videos(
                        minor_chapter.videos,
                        f"{major_chapter.name} - {minor_chapter.name}"
                    )
    
    def _generate_episode_nfo(self, data: NFOData, nfo_path: Path) -> None:
        """生成单个视频的NFO文件"""
        root = ET.Element("episodedetails")
        
        # 添加基本信息
        title = ET.SubElement(root, "title")
        title.text = data.title
        
        plot = ET.SubElement(root, "plot")
        plot.text = data.plot
        
        season = ET.SubElement(root, "season")
        season.text = str(data.season)
        
        episode = ET.SubElement(root, "episode")
        episode.text = str(data.episode)
        
        # 写入文件
        self._write_xml(root, nfo_path)
    
    def _write_xml(self, root: ET.Element, path: Path) -> None:
        """格式化并写入XML文件"""
        # 转换为字符串并格式化
        xml_str = minidom.parseString(ET.tostring(root, 'utf-8')).toprettyxml(indent="  ")
        
        # 写入文件
        with open(path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
            
    def read_course_nfo(self, nfo_path: Path) -> Optional[NFOData]:
        """读取课程NFO文件"""
        if not nfo_path.exists():
            return None
            
        try:
            tree = ET.parse(nfo_path)
            root = tree.getroot()
            
            # 读取基本信息
            title_elem = root.find("title")
            plot_elem = root.find("plot")
            
            # 确保标题和描述不为 None
            title = title_elem.text if title_elem is not None and title_elem.text is not None else ""
            plot = plot_elem.text if plot_elem is not None and plot_elem.text is not None else ""
            
            # 读取课程类型
            course_types = set()
            for type_elem in root.findall("coursetype"):
                if type_elem.text:
                    course_types.add(type_elem.text)
            
            # 读取标签
            tags = set()
            for genre in root.findall("genre"):
                if genre.text:
                    tags.add(genre.text)
            
            return NFOData(
                title=title,
                plot=plot,
                tags=tags,
                course_types=course_types
            )
            
        except Exception as e:
            print(f"读取NFO文件时出错: {e}")
            return None

    def generate_tvshow_nfo(self, show_path: str, title: str) -> None:
        """生成剧集NFO文件
        
        Args:
            show_path: 剧集目录路径
            title: 剧集标题
        """
        # 创建XML根节点
        root = ET.Element("tvshow")
        
        # 添加标题
        title_elem = ET.SubElement(root, "title")
        title_elem.text = title
        
        # 格式化XML
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        
        # 保存文件
        nfo_path = Path(show_path) / "tvshow.nfo"
        nfo_path.write_text(xml_str, encoding="utf-8")
    
    def generate_episode_nfo(self, video_path: str, show_title: str, episode_num: int, title: str) -> None:
        """生成单集NFO文件
        
        Args:
            video_path: 视频文件路径
            show_title: 剧集标题
            episode_num: 集数
            title: 本集标题
        """
        # 创建XML根节点
        root = ET.Element("episodedetails")
        
        # 添加剧集标题
        show_title_elem = ET.SubElement(root, "showtitle")
        show_title_elem.text = show_title
        
        # 添加本集标题
        title_elem = ET.SubElement(root, "title")
        title_elem.text = title
        
        # 添加集数
        episode_elem = ET.SubElement(root, "episode")
        episode_elem.text = str(episode_num)
        
        # 格式化XML
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        
        # 保存文件
        nfo_path = Path(video_path).with_suffix(".nfo")
        nfo_path.write_text(xml_str, encoding="utf-8")