"""
课程批量查找标签页
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from queue import Queue
import time
from ..core.course_batch_finder import CourseBatchFinder, CourseInfo
from ..core.batch_nfo_generator import BatchNFOGenerator
from ..core.scanner import DirectoryScanner
from ..utils.config import config

class CourseBatchTab(ttk.Frame):
    """课程批量查找标签页"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.finder = CourseBatchFinder()
        self.batch_nfo_generator = BatchNFOGenerator()
        self.scanner = DirectoryScanner()
        # 语言目录名集合（用于忽略语言目录的嵌套出现）
        self.default_mandarin_dir_names = {"普通话Deepl", "普通话DeepL", "普通话DeepL[男声]", "普通话DeepL[女声]", "普通话OpenAI-4o-mini", "普通话gemini"}
        self.mandarin_dir_names = set(self.default_mandarin_dir_names)
        self.original_dir_names = {"原"}
        self.language_dir_names = self.mandarin_dir_names | self.original_dir_names
        if hasattr(self.finder, 'mandarin_dir_names'):
            self.finder.mandarin_dir_names = set(self.mandarin_dir_names)
        if hasattr(self.batch_nfo_generator, 'mandarin_dir_names'):
            self.batch_nfo_generator.mandarin_dir_names = set(self.mandarin_dir_names)
        # 自定义普通话目录输入
        self.custom_mandarin_var = tk.StringVar()
        self.courses = []
        self.progress_queue = Queue()
        self.scan_thread = None
        self.generate_thread = None
        
        self._create_widgets()
        self._setup_layout()
        
    def _create_widgets(self):
        """创建控件"""
        # 目录选择区域
        self.path_frame = ttk.LabelFrame(self, text="目录选择", padding=10)
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(self.path_frame, textvariable=self.path_var, width=60)
        self.browse_btn = ttk.Button(self.path_frame, text="选择目录", command=self._browse_directory)
        self.scan_btn = ttk.Button(self.path_frame, text="开始扫描", command=self._start_scan, state='disabled')

        # 语言目录设置
        self.settings_frame = ttk.LabelFrame(self, text="语言目录设置", padding=10)
        self.custom_mandarin_label = ttk.Label(self.settings_frame, text="自定义普通话目录（逗号分隔）：")
        self.custom_mandarin_entry = ttk.Entry(self.settings_frame, textvariable=self.custom_mandarin_var, width=60)
        
        # 进度显示区域
        self.progress_frame = ttk.LabelFrame(self, text="扫描进度", padding=10)
        self.status_var = tk.StringVar(value="请选择要扫描的目录")
        self.status_label = ttk.Label(self.progress_frame, textvariable=self.status_var)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, 
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        
        # 统计信息区域
        self.stats_frame = ttk.LabelFrame(self, text="扫描统计", padding=10)
        self.stats_text = tk.Text(self.stats_frame, height=6, width=60, state='disabled')
        self.stats_scrollbar = ttk.Scrollbar(self.stats_frame, orient='vertical', command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=self.stats_scrollbar.set)
        
        # 课程列表区域
        self.courses_frame = ttk.LabelFrame(self, text="找到的课程", padding=10)
        
        # 创建Treeview用于显示课程列表
        columns = ('name', 'path', 'mandarin', 'original', 'lesson_files')
        self.courses_tree = ttk.Treeview(self.courses_frame, columns=columns, show='headings', height=10)
        
        # 设置列标题
        self.courses_tree.heading('name', text='课程名称')
        self.courses_tree.heading('path', text='路径')
        self.courses_tree.heading('mandarin', text='普通话')
        self.courses_tree.heading('original', text='原版')
        self.courses_tree.heading('lesson_files', text='Lession文件')
        
        # 设置列宽
        self.courses_tree.column('name', width=200)
        self.courses_tree.column('path', width=300)
        self.courses_tree.column('mandarin', width=60)
        self.courses_tree.column('original', width=60)
        self.courses_tree.column('lesson_files', width=100)
        
        # 添加滚动条
        self.courses_scrollbar = ttk.Scrollbar(self.courses_frame, orient='vertical', command=self.courses_tree.yview)
        self.courses_tree.configure(yscrollcommand=self.courses_scrollbar.set)
        
        # 操作按钮区域
        self.button_frame = ttk.Frame(self)
        self.generate_nfo_btn = ttk.Button(
            self.button_frame,
            text="生成NFO文件",
            command=self._generate_nfo_files,
            state='disabled'
        )
        self.clear_btn = ttk.Button(
            self.button_frame,
            text="清空结果",
            command=self._clear_results
        )
        
    def _setup_layout(self):
        """设置布局"""
        # 目录选择区域
        self.path_frame.pack(fill='x', padx=5, pady=5)
        self.path_entry.pack(side='left', expand=True, fill='x', padx=(0, 5))
        self.browse_btn.pack(side='left', padx=(0, 5))
        self.scan_btn.pack(side='left')

        # 语言目录设置
        self.settings_frame.pack(fill='x', padx=5, pady=5)
        self.custom_mandarin_label.pack(side='left')
        self.custom_mandarin_entry.pack(side='left', expand=True, fill='x', padx=(5, 0))
        
        # 进度显示区域
        self.progress_frame.pack(fill='x', padx=5, pady=5)
        self.status_label.pack(fill='x')
        self.progress_bar.pack(fill='x', pady=5)
        
        # 统计信息区域
        self.stats_frame.pack(fill='x', padx=5, pady=5)
        self.stats_text.pack(side='left', expand=True, fill='both')
        self.stats_scrollbar.pack(side='right', fill='y')
        
        # 课程列表区域
        self.courses_frame.pack(expand=True, fill='both', padx=5, pady=5)
        self.courses_tree.pack(side='left', expand=True, fill='both')
        self.courses_scrollbar.pack(side='right', fill='y')
        
        # 操作按钮区域
        self.button_frame.pack(fill='x', padx=5, pady=5)
        self.generate_nfo_btn.pack(side='left', padx=(0, 5))
        self.clear_btn.pack(side='left')
        
    def _browse_directory(self):
        """选择目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.path_var.set(directory)
            self.scan_btn.configure(state='normal')
            
    def _start_scan(self):
        """开始扫描"""
        if self.scan_thread and self.scan_thread.is_alive():
            return
            
        # 合并自定义普通话目录名
        custom_names = self._parse_custom_mandarin_names()
        if custom_names:
            self.mandarin_dir_names = set(self.default_mandarin_dir_names) | custom_names
            self.language_dir_names = self.mandarin_dir_names | self.original_dir_names
            # 同步到查找器，确保只匹配课程根目录的直接子目录
            if hasattr(self.finder, 'mandarin_dir_names'):
                self.finder.mandarin_dir_names = set(self.mandarin_dir_names)
            if hasattr(self.batch_nfo_generator, 'mandarin_dir_names'):
                self.batch_nfo_generator.mandarin_dir_names = set(self.mandarin_dir_names)

        self._reset_state()
        self.status_var.set("正在扫描目录...")
        
        self.scan_thread = threading.Thread(
            target=self._scan_courses,
            args=(Path(self.path_var.get()),)
        )
        self.scan_thread.daemon = True
        self.scan_thread.start()
        
        # 启动进度更新
        self.after(100, self._update_progress)

    def _parse_custom_mandarin_names(self):
        """解析自定义普通话目录名，返回集合"""
        text = (self.custom_mandarin_var.get() or "").strip()
        if not text:
            return set()
        # 逗号分隔，去除首尾空白，过滤空项
        names = {part.strip() for part in text.split(',') if part.strip()}
        return names
        
    def _reset_state(self):
        """重置所有状态"""
        self.courses.clear()
        self.progress_var.set(0)
        self.generate_nfo_btn.configure(state='disabled')
        self._clear_courses_tree()
        self._clear_stats()
        # 清空进度队列
        while not self.progress_queue.empty():
            try:
                self.progress_queue.get_nowait()
            except:
                pass
        
    def _scan_courses(self, directory: Path):
        """扫描课程"""
        try:
            # 开始扫描
            self.progress_queue.put(("scan_start", ""))
            
            # 执行扫描
            courses = self.finder.find_courses_with_lession(directory)
            
            # 扫描完成
            self.progress_queue.put(("scan_complete", courses))
            
        except Exception as e:
            self.progress_queue.put(("error", str(e)))
            
    def _generate_nfo_files(self):
        """生成NFO文件"""
        if not self.courses:
            return
            
        if not messagebox.askyesno(
            "确认生成",
            f"确定要为找到的 {len(self.courses)} 个课程生成NFO文件吗？"
        ):
            return
            
        self.progress_var.set(0)
        self.generate_nfo_btn.configure(state='disabled')
        self.status_var.set("正在生成NFO文件...")
        
        self.generate_thread = threading.Thread(
            target=self._perform_nfo_generation,
            args=(self.courses[:],)
        )
        self.generate_thread.daemon = True
        self.generate_thread.start()
        
        # 启动进度更新
        self.after(100, self._update_progress)
        
    def _perform_nfo_generation(self, courses_to_process):
        """执行NFO生成"""
        total = len(courses_to_process)
        processed = 0
        
        for course in courses_to_process:
            try:
                # 为每个语言版本生成NFO
                if course.has_mandarin and getattr(course, "mandarin_paths", None):
                    for mandarin_path in course.mandarin_paths:
                        self._generate_course_nfo_for_language(course, mandarin_path, True)
                
                if course.has_original and course.original_path:
                    self._generate_course_nfo_for_language(course, course.original_path, False)
                
                processed += 1
                progress = (processed / total) * 100
                self.progress_queue.put(("generate", (processed, total, progress)))
                time.sleep(0.01)  # 避免界面卡顿
                
            except Exception as e:
                print(f"生成课程NFO时出错 {course.name}: {e}")
                
        # 生成完成
        self.progress_queue.put(("generate_complete", processed))
        
    def _generate_course_nfo_for_language(self, course: CourseInfo, language_path: Path, is_mandarin: bool):
        """为特定语言版本生成课程NFO"""
        try:
            # 为语言目录构建章节信息
            chapters = self._build_chapters_for_language_directory(language_path)
            
            if chapters:
                # 使用独立的NFO生成器
                self.batch_nfo_generator.generate_course_nfos(
                    course.path, 
                    language_path, 
                    chapters, 
                    is_mandarin
                )
                print(f"成功为 {course.name} 的 {language_path.name} 版本生成NFO文件")
            else:
                print(f"无法为 {course.name} 的 {language_path.name} 版本构建章节信息")
                
        except Exception as e:
            print(f"为语言版本生成NFO时出错: {e}")
    
    def _build_chapters_for_language_directory(self, language_path: Path):
        """为语言目录构建章节信息"""
        try:
            from ..core.scanner import Chapter, VideoFile
            
            # 检测目录结构类型
            structure_type = self._detect_structure_type(language_path)
            if structure_type == 0:
                return []
            
            # 获取所有视频文件并排序
            all_videos = self._get_video_files_sorted(language_path)
            if not all_videos:
                return []
            
            # 根据结构类型组织章节
            chapters = self._scan_chapters(language_path, structure_type, all_videos)
            return chapters
            
        except Exception as e:
            print(f"构建语言目录章节信息时出错: {e}")
            return []
    
    def _detect_structure_type(self, path: Path) -> int:
        """检测目录结构类型"""
        # 检查是否为一级结构（直接包含视频）
        has_videos = any(self._is_video_file(f) for f in path.iterdir())
        if has_videos:
            return 1
            
        # 检查二级结构
        for item in path.iterdir():
            if item.is_dir():
                # 跳过再次出现的语言目录
                if item.name in self.language_dir_names:
                    continue
                # 如果章节目录下有子目录（且不是语言目录），则为三级结构
                has_subdirs = any(f.is_dir() and f.name not in self.language_dir_names for f in item.iterdir())
                if has_subdirs:
                    return 3
                # 如果章节目录下直接有视频（排除语言目录中的），则为二级结构
                has_videos = any(self._is_video_file(f) for f in item.iterdir())
                if has_videos:
                    return 2
        
        return 0
    
    def _is_video_file(self, path: Path) -> bool:
        """判断是否为视频文件"""
        video_extensions = ['.mp4', '.mkv', '.avi']
        return path.suffix.lower() in video_extensions
    
    def _get_video_files_sorted(self, path: Path):
        """获取目录下所有视频文件并排序"""
        from ..core.scanner import VideoFile
        import re
        
        video_files = []
        for file in path.rglob("*"):
            if self._is_video_file(file):
                # 如果视频位于更深层嵌套的语言目录中，则跳过
                if self._is_under_nested_language_dir(file.parent, path):
                    continue
                video_files.append(VideoFile(
                    path=file,
                    name=file.stem,
                    episode_number=1  # 临时值，稍后更新
                ))
        
        # 按最顶层目录名称中的数字和文件名中的数字排序
        def sort_key(video: VideoFile) -> tuple:
            # 获取视频文件的所有父目录路径（从下往上）
            parents = list(video.path.parents)
            # 找到最顶层目录（在path目录下的第一级目录）
            top_level_dir = None
            for parent in reversed(parents):
                if parent.parent == path:
                    top_level_dir = parent
                    break
            
            # 获取最顶层目录的序号（如果存在）
            top_dir_num = self._extract_number(top_level_dir.name) if top_level_dir else 999999
            
            # 获取文件名中的数字
            file_num = self._extract_number(video.name)
            
            # 返回排序元组：(最顶层目录数字, 文件名数字, 完整文件名)
            return (top_dir_num, file_num, video.name)
        
        # 按复合键排序
        video_files.sort(key=sort_key)
        
        # 更新全局集数
        for i, video in enumerate(video_files, 1):
            video.global_episode_number = i
            
        return video_files
    
    def _extract_number(self, filename: str) -> int:
        """从文件名中提取数字"""
        import re
        # 匹配文件名开头的数字部分
        match = re.match(r'^(\d+)(?:\s*-\s*|\s+|\-)?', filename)
        if match:
            return int(match.group(1))
        return 999999
    
    def _scan_chapters(self, path: Path, structure_type: int, all_videos):
        """扫描章节"""
        from ..core.scanner import Chapter
        
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
                # 跳过内部再次出现的语言目录
                if chapter_dir.name in self.language_dir_names:
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
                # 跳过内部再次出现的语言目录
                if major_chapter.name in self.language_dir_names:
                    continue
                    
                sub_chapters = []
                for minor_chapter in sorted(major_chapter.iterdir()):
                    if not minor_chapter.is_dir():
                        continue
                    # 跳过内部再次出现的语言目录
                    if minor_chapter.name in self.language_dir_names:
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

    def _is_under_nested_language_dir(self, current_dir: Path, language_root: Path) -> bool:
        """判断目录是否位于语言根目录之下的再次出现的语言目录中（应忽略）
        规则：如果从 current_dir 向上直到 language_root（不含）之间存在名称为语言目录名的任一目录，则认为是嵌套的语言目录。
        """
        try:
            while current_dir != language_root and language_root in current_dir.parents:
                if current_dir.name in self.language_dir_names:
                    return True
                current_dir = current_dir.parent
        except Exception:
            return False
        return False
        
    def _clear_results(self):
        """清空结果"""
        self._reset_state()
        self.status_var.set("请选择要扫描的目录")
        
    def _clear_courses_tree(self):
        """清空课程列表"""
        for item in self.courses_tree.get_children():
            self.courses_tree.delete(item)
            
    def _clear_stats(self):
        """清空统计信息"""
        self.stats_text.configure(state='normal')
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.configure(state='disabled')
        
    def _update_progress(self):
        """更新进度显示"""
        try:
            while not self.progress_queue.empty():
                action, data = self.progress_queue.get_nowait()
                
                if action == "scan_start":
                    self.status_var.set("正在扫描目录...")
                    self.progress_var.set(0)
                    
                elif action == "scan_complete":
                    self.courses = data
                    self._display_courses()
                    self._display_statistics()
                    self.status_var.set(f"扫描完成，共找到 {len(self.courses)} 个课程")
                    self.progress_var.set(100)
                    self.generate_nfo_btn.configure(state='normal' if self.courses else 'disabled')
                    
                elif action == "generate":
                    processed, total, progress = data
                    self.progress_var.set(progress)
                    self.status_var.set(f"正在生成NFO: {processed}/{total}")
                    
                elif action == "generate_complete":
                    self.status_var.set(f"NFO生成完成，共处理 {data} 个课程")
                    self.progress_var.set(100)
                    self.generate_nfo_btn.configure(state='normal')
                    
                elif action == "error":
                    messagebox.showerror("错误", f"操作出错: {data}")
                    self.status_var.set("操作出错")
                    self._reset_state()
                    
        except Exception as e:
            print(f"更新进度时出错: {e}")
            
        # 如果还有线程在运行，继续更新
        if (self.scan_thread and self.scan_thread.is_alive()) or \
           (self.generate_thread and self.generate_thread.is_alive()):
            self.after(100, self._update_progress)
            
    def _display_courses(self):
        """显示课程列表"""
        self._clear_courses_tree()
        
        for course in self.courses:
            mandarin_text = "是" if course.has_mandarin else "否"
            original_text = "是" if course.has_original else "否"
            lesson_count = len(course.lesson_files)
            
            self.courses_tree.insert('', 'end', values=(
                course.name,
                str(course.path),
                mandarin_text,
                original_text,
                f"{lesson_count}个"
            ))
            
    def _display_statistics(self):
        """显示统计信息"""
        if not self.courses:
            return
            
        stats = self.finder.get_scan_statistics(self.courses)
        
        self.stats_text.configure(state='normal')
        self.stats_text.delete(1.0, tk.END)
        
        stats_text = f"""扫描统计信息：
总课程数：{stats['total_courses']}
包含普通话版本：{stats['mandarin_courses']}
包含原版：{stats['original_courses']}
同时包含两种语言：{stats['both_languages']}
仅包含普通话：{stats['mandarin_only']}
仅包含原版：{stats['original_only']}"""
        
        self.stats_text.insert(1.0, stats_text)
        self.stats_text.configure(state='disabled')
