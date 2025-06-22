"""
2层嵌套子目录标签页模块
"""
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from typing import List, Tuple, Dict, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom
from ..core.scanner import DirectoryScanner
from ..core.tags import TagManager
from ..core.nfo import NFOGenerator
from ..utils.config import config

class Type4DirectoryScanner:
    """第4种格式目录扫描器"""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path  # 这是课程目录（如"普通话Deepl"）
        self.videos: List[Tuple[Path, int, int]] = []  # (视频路径, 章节序号, 视频序号)
        self.debug = True  # 是否输出调试信息
    
    def scan(self) -> List[Tuple[Path, int]]:
        """扫描目录
        返回：按顺序排列的(视频路径, 集数)列表
        """
        # 清空之前的结果
        self.videos.clear()
        
        self._log(f"开始扫描目录：{self.root_path}")
        
        # 直接遍历章节目录（如"1. WELCOME"）
        try:
            chapter_dirs = sorted(self.root_path.iterdir())
            self._log(f"找到 {len(chapter_dirs)} 个章节目录")
        except Exception as e:
            self._log(f"读取章节目录失败：{e}")
            return []
            
        for chapter_dir in chapter_dirs:
            if not chapter_dir.is_dir():
                self._log(f"跳过非目录：{chapter_dir}")
                continue
                
            # 提取章节序号
            chapter_num = self._extract_number(chapter_dir.name)
            if chapter_num is None:
                self._log(f"无法提取章节序号：{chapter_dir}")
                continue
                
            self._log(f"扫描章节目录：{chapter_dir} (序号: {chapter_num})")
            
            # 扫描视频文件（递归查找所有.mp4文件）
            try:
                video_files = list(chapter_dir.rglob("*.mp4"))
                self._log(f"在目录 {chapter_dir} 下找到 {len(video_files)} 个视频文件")
                
                # 按文件名排序
                video_files.sort(key=lambda x: self._extract_number(x.name) or 0)
                
            except Exception as e:
                self._log(f"扫描视频文件失败：{e}")
                continue
                
            for item in video_files:
                # 检查是否在.nomedia目录下
                if config.get("check_nomedia", True):
                    nomedia_found = False
                    for parent in item.parents:
                        if (parent / ".nomedia").exists():
                            self._log(f"视频在.nomedia目录下，跳过：{item}")
                            nomedia_found = True
                            break
                    if nomedia_found:
                        continue
                
                # 提取视频序号
                video_num = self._extract_number(item.name)
                if video_num is not None:
                    self._log(f"找到视频：{item} (章节序号: {chapter_num}, 视频序号: {video_num})")
                    self.videos.append((item, chapter_num, video_num))
                else:
                    self._log(f"无法提取视频序号：{item}")
    
        self._log(f"扫描完成，共找到 {len(self.videos)} 个视频文件")
        
        if not self.videos:
            return []
            
        # 按章节序号和视频序号排序
        self.videos.sort(key=lambda x: (x[1], x[2]))
        
        # 生成最终结果，添加集数
        result = []
        for i, (video_path, _, _) in enumerate(self.videos, 1):
            result.append((video_path, i))
            self._log(f"视频 {i}: {video_path}")
        
        return result
    
    def _extract_number(self, name: str) -> Optional[int]:
        """从名称中提取序号
        支持以下格式：
        1. 纯数字开头：1、01、001
        2. 带点的序号：2.1、2.1.1（取第一个数字）
        3. 带空格的序号：1 - 、1. 
        """
        # 尝试匹配开头的数字
        match = re.search(r"^(\d+)(?:\.|、|\s|$)", name)
        if match:
            return int(match.group(1))
            
        # 尝试匹配带点的序号
        match = re.search(r"^(\d+)\..*?(?:\.|、|\s|$)", name)
        if match:
            return int(match.group(1))
            
        return None
        
    def _log(self, message: str) -> None:
        """输出调试信息"""
        if self.debug:
            print(f"[Type4Scanner] {message}")

class NFOType4Tab(ttk.Frame):
    """第4种格式NFO生成标签页"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        # 创建并配置网格
        self.grid_columnconfigure(1, weight=1)
        
        # 说明文本
        explanation = """
使用说明：
1. 选择课程目录：选择包含视频文件的"普通话Deepl"目录
2. 输入课程标题：这将作为NFO文件中的标题
3. 点击"生成NFO文件"按钮开始处理

目录结构示例：
普通话Deepl/
    ├── 1. WELCOME/
    │   ├── 1 - 课程介绍.mp4
    │   └── 2 - 环境准备.mp4
    ├── 2. MODULE 1/
    │   ├── 1 - 基础知识.mp4
    │   └── 2 - 进阶内容.mp4
    └── tvshow.nfo（将自动生成）

注意事项：
• 目录名必须包含序号（如：1. WELCOME）
• 视频文件名必须包含序号（如：1 - 课程介绍.mp4）
• 序号支持多种格式：1、01、1.、1 -
• 将自动按目录序号和视频序号排序
"""
        explanation_text = tk.Text(self, height=15, width=50, wrap=tk.WORD)
        explanation_text.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        explanation_text.insert("1.0", explanation)
        explanation_text.configure(state="disabled")
        
        # 源目录选择
        ttk.Label(self, text="课程目录:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.source_path = tk.StringVar()
        ttk.Entry(self, textvariable=self.source_path).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(self, text="浏览", command=self.select_source).grid(row=1, column=2, sticky="w", padx=5, pady=5)
        
        # 课程标题输入
        ttk.Label(self, text="课程标题:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.course_title = tk.StringVar()
        ttk.Entry(self, textvariable=self.course_title).grid(row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # 生成按钮
        ttk.Button(self, text="生成NFO文件", command=self.generate_nfo).grid(row=3, column=1, pady=10)
        
    def select_source(self):
        """选择源目录"""
        path = filedialog.askdirectory()
        if path:
            self.source_path.set(path)
            # 自动从目录结构提取课程标题（用户可以修改）
            try:
                # 获取课程目录的父目录名称作为默认标题
                course_dir = Path(path).parent
                if course_dir.name not in ["普通话Deepl", "原"]:
                    self.course_title.set(course_dir.name)
            except Exception:
                pass
            
    def generate_nfo(self):
        """生成NFO文件"""
        source_path = self.source_path.get()
        course_title = self.course_title.get().strip()
        
        if not source_path:
            messagebox.showerror("错误", "请选择课程目录")
            return
            
        if not course_title:
            messagebox.showerror("错误", "请输入课程标题")
            return
            
        # 创建线程执行生成任务
        thread = threading.Thread(target=self._generate_nfo_thread, args=(source_path, course_title))
        thread.daemon = True
        thread.start()
        
    def _generate_nfo_thread(self, source_path: str, course_title: str):
        """在线程中执行NFO生成任务"""
        try:
            # 扫描目录
            scanner = Type4DirectoryScanner(Path(source_path))
            videos = scanner.scan()
            
            if not videos:
                messagebox.showerror("错误", "未找到视频文件")
                return
                
            # 生成NFO文件
            nfo_gen = NFOGenerator()
            nfo_gen.generate_tvshow_nfo(source_path, course_title)
            
            # 为每个视频生成episode NFO
            for video_path, episode_num in videos:
                nfo_gen.generate_episode_nfo(
                    str(video_path),
                    course_title,
                    episode_num,
                    Path(video_path).stem
                )
                
            messagebox.showinfo("成功", "NFO文件生成完成")
            
        except Exception as e:
            messagebox.showerror("错误", f"生成NFO文件时出错：{str(e)}") 