"""
课程批量查找（多级目录）标签

说明：
- 参考 src\gui\course_batch_tab.py 的交互样式，但代码实现完全独立。
- 课程根目录的判定：包含名为 lession_2 的文件（不区分大小写）。
- 语言目录：默认支持 {"普通话Deepl", "普通话DeepL", "普通话DeepL[男声]", "普通话DeepL[女声]", "普通话OpenAI-4o-mini", "普通话gemini"}，也支持自定义（逗号分隔）。
- 目录结构：语言目录下存在 N 级子目录（默认 2 级），视频文件位于第 N 级子目录中。
- 允许自定义子目录层级（2、3、4、5...）。
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from queue import Queue
import time
from typing import List, Dict

from ..core.batch_nfo_generator import BatchNFOGenerator
from ..core.scanner import DirectoryScanner, Chapter, VideoFile
from ..core.course_batch_finder import CourseInfo  # 仅复用数据容器


class CourseBatchNestedTab(ttk.Frame):
    """课程批量查找（多级目录）标签"""

    def __init__(self, parent):
        super().__init__(parent)
        # 工具实例
        self.batch_nfo_generator = BatchNFOGenerator()
        self.scanner = DirectoryScanner()

        # 语言目录名集合（用于忽略语言目录的嵌套出现）
        self.default_mandarin_dir_names = {
            "普通话Deepl",
            "普通话DeepL",
            "普通话DeepL[男声]",
            "普通话DeepL[女声]",
            "普通话OpenAI-4o-mini",
            "普通话gemini",
        }
        self.mandarin_dir_names = set(self.default_mandarin_dir_names)
        # 原版目录名集合（兼容“原”字样，不强制要求）
        self.original_dir_names = {"原", "原版"}
        self.language_dir_names = self.mandarin_dir_names | self.original_dir_names

        # 自定义普通话目录输入
        self.custom_mandarin_var = tk.StringVar()
        # 子目录层级（默认2）
        self.depth_var = tk.IntVar(value=2)

        # 状态与任务线程
        self.courses: List[CourseInfo] = []
        self.progress_queue = Queue()
        self.scan_thread = None
        self.generate_thread = None

        self._create_widgets()
        self._setup_layout()

    # ---------- UI ----------
    def _create_widgets(self):
        # 目录选择区域
        self.path_frame = ttk.LabelFrame(self, text="目录选择", padding=10)
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(self.path_frame, textvariable=self.path_var, width=60)
        self.browse_btn = ttk.Button(self.path_frame, text="选择目录", command=self._browse_directory)
        self.scan_btn = ttk.Button(self.path_frame, text="开始扫描", command=self._start_scan, state='disabled')

        # 设置区域
        self.settings_frame = ttk.LabelFrame(self, text="设置", padding=10)
        # 自定义普通话目录
        self.custom_mandarin_label = ttk.Label(self.settings_frame, text="自定义普通话目录（逗号分隔）：")
        self.custom_mandarin_entry = ttk.Entry(self.settings_frame, textvariable=self.custom_mandarin_var, width=60)
        # 子目录层级
        self.depth_label = ttk.Label(self.settings_frame, text="子目录层级（默认2）：")
        self.depth_spin = ttk.Spinbox(self.settings_frame, from_=2, to=10, textvariable=self.depth_var, width=6)

        # 进度显示区域
        self.progress_frame = ttk.LabelFrame(self, text="进度", padding=10)
        self.status_var = tk.StringVar(value="请选择要扫描的目录")
        self.status_label = ttk.Label(self.progress_frame, textvariable=self.status_var)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100, mode='determinate')

        # 统计信息区域
        self.stats_frame = ttk.LabelFrame(self, text="统计", padding=10)
        self.stats_text = tk.Text(self.stats_frame, height=6, width=60, state='disabled')
        self.stats_scrollbar = ttk.Scrollbar(self.stats_frame, orient='vertical', command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=self.stats_scrollbar.set)

        # 课程列表区域
        self.courses_frame = ttk.LabelFrame(self, text="找到的课程", padding=10)
        columns = ('name', 'path', 'mandarin', 'original', 'lesson_files')
        self.courses_tree = ttk.Treeview(self.courses_frame, columns=columns, show='headings', height=10)
        self.courses_tree.heading('name', text='课程名称')
        self.courses_tree.heading('path', text='路径')
        self.courses_tree.heading('mandarin', text='普通话')
        self.courses_tree.heading('original', text='原版')
        self.courses_tree.heading('lesson_files', text='lession_2 文件')
        self.courses_tree.column('name', width=200)
        self.courses_tree.column('path', width=300)
        self.courses_tree.column('mandarin', width=60)
        self.courses_tree.column('original', width=60)
        self.courses_tree.column('lesson_files', width=100)
        self.courses_scrollbar = ttk.Scrollbar(self.courses_frame, orient='vertical', command=self.courses_tree.yview)
        self.courses_tree.configure(yscrollcommand=self.courses_scrollbar.set)

        # 操作按钮
        self.button_frame = ttk.Frame(self)
        self.generate_nfo_btn = ttk.Button(self.button_frame, text="生成NFO文件", command=self._generate_nfo_files, state='disabled')
        self.clear_btn = ttk.Button(self.button_frame, text="清空", command=self._clear_results)

    def _setup_layout(self):
        # 目录选择区域
        self.path_frame.pack(fill='x', padx=5, pady=5)
        self.path_entry.pack(side='left', expand=True, fill='x')
        self.browse_btn.pack(side='left', padx=(5, 5))
        self.scan_btn.pack(side='left')

        # 设置区域
        self.settings_frame.pack(fill='x', padx=5, pady=5)
        self.custom_mandarin_label.grid(row=0, column=0, sticky='w', padx=(0, 6))
        self.custom_mandarin_entry.grid(row=0, column=1, sticky='we')
        self.depth_label.grid(row=1, column=0, sticky='w', padx=(0, 6), pady=(6, 0))
        self.depth_spin.grid(row=1, column=1, sticky='w', pady=(6, 0))
        self.settings_frame.columnconfigure(1, weight=1)

        # 进度区域
        self.progress_frame.pack(fill='x', padx=5, pady=5)
        self.status_label.pack(fill='x')
        self.progress_bar.pack(fill='x', pady=5)

        # 统计信息
        self.stats_frame.pack(fill='x', padx=5, pady=5)
        self.stats_text.pack(side='left', expand=True, fill='both')
        self.stats_scrollbar.pack(side='right', fill='y')

        # 课程列表
        self.courses_frame.pack(expand=True, fill='both', padx=5, pady=5)
        self.courses_tree.pack(side='left', expand=True, fill='both')
        self.courses_scrollbar.pack(side='right', fill='y')

        # 按钮
        self.button_frame.pack(fill='x', padx=5, pady=5)
        self.generate_nfo_btn.pack(side='left', padx=(0, 5))
        self.clear_btn.pack(side='left')

    # ---------- 交互 ----------
    def _browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_var.set(directory)
            self.scan_btn.configure(state='normal')

    def _start_scan(self):
        if self.scan_thread and self.scan_thread.is_alive():
            return

        # 合并自定义普通话目录
        custom_names = self._parse_custom_mandarin_names()
        if custom_names:
            self.mandarin_dir_names = set(self.default_mandarin_dir_names) | custom_names
            self.language_dir_names = self.mandarin_dir_names | self.original_dir_names
            if hasattr(self.batch_nfo_generator, 'mandarin_dir_names'):
                self.batch_nfo_generator.mandarin_dir_names = set(self.mandarin_dir_names)

        # 准备状态
        self._reset_state()
        self.status_var.set("正在扫描目录...")

        # 启动线程
        self.scan_thread = threading.Thread(target=self._scan_courses, args=(Path(self.path_var.get()),))
        self.scan_thread.daemon = True
        self.scan_thread.start()

        # 启动进度更新
        self.after(100, self._update_progress)

    def _parse_custom_mandarin_names(self):
        text = (self.custom_mandarin_var.get() or "").strip()
        if not text:
            return set()
        return {part.strip() for part in text.split(',') if part.strip()}

    def _reset_state(self):
        self.courses.clear()
        self.progress_var.set(0)
        self.generate_nfo_btn.configure(state='disabled')
        self._clear_courses_tree()
        self._clear_stats()
        while not self.progress_queue.empty():
            try:
                self.progress_queue.get_nowait()
            except Exception:
                break

    # ---------- 扫描逻辑 ----------
    def _scan_courses(self, directory: Path):
        try:
            self.progress_queue.put(("scan_start", ""))
            courses = []
            self._scan_directory_recursive(directory, courses)
            self.progress_queue.put(("scan_complete", courses))
        except Exception as e:
            self.progress_queue.put(("error", str(e)))

    def _scan_directory_recursive(self, current_path: Path, courses: List[CourseInfo]):
        try:
            if self._is_course_directory_lession2(current_path):
                course_info = self._create_course_info(current_path)
                if course_info:
                    courses.append(course_info)
                return

            for item in current_path.iterdir():
                if item.is_dir():
                    self._scan_directory_recursive(item, courses)
        except PermissionError:
            print(f"权限不足，无法访问目录: {current_path}")
        except Exception as e:
            print(f"扫描目录时出错 {current_path}: {e}")

    def _is_course_directory_lession2(self, path: Path) -> bool:
        try:
            for item in path.iterdir():
                if item.is_file() and item.name.lower() == "lession_2":
                    return True
            return False
        except Exception:
            return False

    def _create_course_info(self, path: Path) -> CourseInfo | None:
        try:
            course_name = path.name
            lesson_files = [p for p in path.iterdir() if p.is_file() and p.name.lower() == "lession_2"]

            if not lesson_files:
                return None

            mandarin_paths = []
            original_path = None
            for item in path.iterdir():
                if not item.is_dir():
                    continue
                if item.name in self.mandarin_dir_names:
                    mandarin_paths.append(item)
                if item.name in self.original_dir_names and original_path is None:
                    original_path = item
            mandarin_paths.sort(key=lambda p: p.name)

            return CourseInfo(
                path=path,
                name=course_name,
                has_mandarin=bool(mandarin_paths),
                has_original=original_path is not None,
                lesson_files=lesson_files,
                mandarin_paths=mandarin_paths,
                original_path=original_path,
            )
        except Exception as e:
            print(f"创建课程信息时出错 {path}: {e}")
            return None

    # ---------- NFO 生成 ----------
    def _generate_nfo_files(self):
        if not self.courses:
            return
        if not messagebox.askyesno("确认生成", f"确定要为找到的 {len(self.courses)} 个课程生成NFO文件吗？"):
            return

        self.progress_var.set(0)
        self.generate_nfo_btn.configure(state='disabled')
        self.status_var.set("正在生成NFO文件...")

        self.generate_thread = threading.Thread(target=self._perform_nfo_generation, args=(self.courses[:],))
        self.generate_thread.daemon = True
        self.generate_thread.start()
        self.after(100, self._update_progress)

    def _perform_nfo_generation(self, courses_to_process: List[CourseInfo]):
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
                time.sleep(0.01)
            except Exception as e:
                print(f"生成课程NFO时出错 {course.name}: {e}")

        self.progress_queue.put(("generate_complete", processed))

    def _generate_course_nfo_for_language(self, course: CourseInfo, language_path: Path, is_mandarin: bool):
        try:
            depth = max(2, int(self.depth_var.get() or 2))
            chapters = self._build_chapters_with_depth(language_path, depth)
            if chapters:
                self.batch_nfo_generator.generate_course_nfos(course.path, language_path, chapters, is_mandarin)
                print(f"成功为 {course.name} 的 {language_path.name} 版本生成NFO文件")
            else:
                print(f"无法为 {course.name} 的 {language_path.name} 版本构建章节信息")
        except Exception as e:
            print(f"为语言版本生成NFO时出错 {e}")

    # ---------- 章节构建（可配置层级） ----------
    def _build_chapters_with_depth(self, language_path: Path, depth: int) -> List[Chapter]:
        try:
            # 收集叶子目录的视频
            # 规则调整：在不超过 depth 的任一层级，如果目录内存在视频则纳入（满足“1级目录直接是视频”的场景）
            all_videos = self._collect_videos_up_to_depth(language_path, depth)
            if not all_videos:
                return []

            # 依据层级排序并设置全局集数
            all_videos.sort(key=self._video_sort_key_with_dirs(language_path, depth))
            for i, v in enumerate(all_videos, 1):
                v.global_episode_number = i

            # 构建章节树
            return self._build_chapter_tree(language_path, depth, all_videos)
        except Exception as e:
            print(f"构建章节信息时出错 {e}")
            return []

    def _collect_videos_up_to_depth(self, root: Path, depth: int) -> List[VideoFile]:
        videos: List[VideoFile] = []

        def recurse(curr: Path, level: int):
            # 跳过语言目录名重复嵌套
            if level > 0 and curr.name in self.language_dir_names:
                return

            # 收集当前目录中的视频（level <= depth）
            if level <= depth:
                try:
                    for f in curr.iterdir():
                        if f.is_file() and self._is_video_file(f):
                            videos.append(VideoFile(path=f, name=f.stem, episode_number=1))
                except Exception:
                    pass

            # 超过深度则不再向下
            if level >= depth:
                return

            # 继续向下
            try:
                for item in sorted(curr.iterdir()):
                    if item.is_dir():
                        recurse(item, level + 1)
            except Exception:
                pass

        recurse(root, 0)
        return videos

    def _video_sort_key_with_dirs(self, language_root: Path, depth: int):
        def extract_numeric_tuple(name: str):
            import re
            s = name.strip()
            # 优先匹配点分层号，如 2.1.2、10.03.7
            m = re.match(r'^(\d+(?:\.\d+)+)', s)
            if m:
                try:
                    return tuple(int(p) for p in m.group(1).split('.'))
                except Exception:
                    pass
            # 退化为单个前导数字
            m2 = re.match(r'^(\d+)(?:\s*[-_\.]?\s*)?', s)
            if m2:
                try:
                    return (int(m2.group(1)),)
                except Exception:
                    pass
            # 无数字，返回大数以置后
            return (999999,)

        def key(video: VideoFile):
            # 组装（每级目录的数字元组..., 文件名数字元组, 名字稳定兜底）
            parts: List[int] = []
            rel = video.path.parent
            names: List[str] = []
            while rel != language_root and language_root in rel.parents and len(names) < depth:
                names.append(rel.name)
                rel = rel.parent
            names.reverse()
            if len(names) < depth:
                names = names + (["0"] * (depth - len(names)))
            # 目录层排序片段
            seq: List[int] = []
            for n in names:
                seq.extend(extract_numeric_tuple(n))
            # 文件名排序片段（支持 2.1.1 这种）
            seq.extend(extract_numeric_tuple(video.name))
            # 返回（数值序列, 名称小写）保证稳定
            return (tuple(seq), video.name.lower())

        return key

    def _build_chapter_tree(self, root: Path, depth: int, all_videos: List[VideoFile]) -> List[Chapter]:
        # 递归构建 Chapter 树：在 <= depth 的任一层，若目录中存在视频则直接挂载到该层对应的章节
        def build_children(parent: Path, level: int) -> List[Chapter]:
            result: List[Chapter] = []
            if level > 0 and parent.name in self.language_dir_names:
                return result

            # 首先处理每个直接子目录
            try:
                for sub in sorted(parent.iterdir()):
                    if not sub.is_dir() or sub.name in self.language_dir_names:
                        continue

                    # 收集该目录自身的视频
                    vids = [v for v in all_videos if v.path.parent == sub]

                    # 如果还未达到最大层级，继续构建子章节
                    sub_chapters: List[Chapter] = []
                    if level + 1 <= depth:
                        if level + 1 < depth:
                            sub_chapters = build_children(sub, level + 1)

                    if vids or sub_chapters:
                        result.append(Chapter(name=sub.name, videos=vids, sub_chapters=sub_chapters))
            except Exception:
                pass

            # 在根层，如果根目录自身包含视频（少见），作为一个无名章节放在最前
            if level == 0:
                root_videos = [v for v in all_videos if v.path.parent == parent]
                if root_videos:
                    result.insert(0, Chapter(name="", videos=root_videos, sub_chapters=[]))

            return result

        return build_children(root, 0)

    # ---------- 工具 ----------
    def _is_video_file(self, path: Path) -> bool:
        exts = getattr(self.scanner, 'video_extensions', None)
        if not exts:
            exts = ['.mp4', '.mkv', '.avi']
        return path.suffix.lower() in exts

    def _clear_results(self):
        self._reset_state()
        self.status_var.set("请选择要扫描的目录")

    def _clear_courses_tree(self):
        for item in self.courses_tree.get_children():
            self.courses_tree.delete(item)

    def _clear_stats(self):
        self.stats_text.configure(state='normal')
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.configure(state='disabled')

    # ---------- 进度/展示 ----------
    def _update_progress(self):
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
            print(f"更新进度时出错 {e}")

        if (self.scan_thread and self.scan_thread.is_alive()) or (self.generate_thread and self.generate_thread.is_alive()):
            self.after(100, self._update_progress)

    def _display_courses(self):
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
        if not self.courses:
            return

        total_courses = len(self.courses)
        mandarin_courses = sum(1 for c in self.courses if c.has_mandarin)
        original_courses = sum(1 for c in self.courses if c.has_original)
        both_languages = sum(1 for c in self.courses if c.has_mandarin and c.has_original)

        self.stats_text.configure(state='normal')
        self.stats_text.delete(1.0, tk.END)
        stats_text = (
            f"扫描统计信息\n"
            f"总课程数：{total_courses}\n"
            f"包含普通话版本：{mandarin_courses}\n"
            f"包含原版：{original_courses}\n"
            f"同时包含两种语言：{both_languages}\n"
            f"仅包含普通话：{mandarin_courses - both_languages}\n"
            f"仅包含原版：{original_courses - both_languages}"
        )
        self.stats_text.insert(1.0, stats_text)
        self.stats_text.configure(state='disabled')
