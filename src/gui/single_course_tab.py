"""
Single文件课程标签页
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from queue import Queue
import time
from ..core.single_course_finder import SingleCourseFinder, SingleCourseInfo
from ..core.single_nfo_generator import SingleNFOGenerator

class SingleCourseTab(ttk.Frame):
    """Single文件课程标签页"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.finder = SingleCourseFinder()
        self.single_nfo_generator = SingleNFOGenerator()
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
        self.stats_text = tk.Text(self.stats_frame, height=4, width=60, state='disabled')
        self.stats_scrollbar = ttk.Scrollbar(self.stats_frame, orient='vertical', command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=self.stats_scrollbar.set)
        
        # 课程列表区域
        self.courses_frame = ttk.LabelFrame(self, text="找到的Single文件课程", padding=10)
        
        # 创建Treeview用于显示课程列表
        columns = ('name', 'path', 'single_file', 'video_count')
        self.courses_tree = ttk.Treeview(self.courses_frame, columns=columns, show='headings', height=10)
        
        # 设置列标题
        self.courses_tree.heading('name', text='课程名称')
        self.courses_tree.heading('path', text='路径')
        self.courses_tree.heading('single_file', text='Single文件')
        self.courses_tree.heading('video_count', text='视频数量')
        
        # 设置列宽
        self.courses_tree.column('name', width=200)
        self.courses_tree.column('path', width=300)
        self.courses_tree.column('single_file', width=150)
        self.courses_tree.column('video_count', width=100)
        
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
            courses = self.finder.find_single_courses(directory)
            
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
            f"确定要为找到的 {len(self.courses)} 个Single文件课程生成NFO文件吗？"
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
                # 为Single文件课程生成NFO（单一版本）
                self._generate_single_course_nfo(course)
                
                processed += 1
                progress = (processed / total) * 100
                self.progress_queue.put(("generate", (processed, total, progress)))
                time.sleep(0.01)  # 避免界面卡顿
                
            except Exception as e:
                print(f"生成Single文件课程NFO时出错 {course.name}: {e}")
                
        # 生成完成
        self.progress_queue.put(("generate_complete", processed))
        
    def _generate_single_course_nfo(self, course: SingleCourseInfo):
        """为Single文件课程生成NFO"""
        try:
            # 使用独立的SingleNFOGenerator生成NFO
            self.single_nfo_generator.generate_course_nfos(
                course.path,  # 课程根目录
                course.chapters
            )
            print(f"成功为Single文件课程 {course.name} 生成NFO文件")
                
        except Exception as e:
            print(f"为Single文件课程生成NFO时出错: {e}")
        
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
                    self.status_var.set(f"扫描完成，共找到 {len(self.courses)} 个Single文件课程")
                    self.progress_var.set(100)
                    self.generate_nfo_btn.configure(state='normal' if self.courses else 'disabled')
                    
                elif action == "generate":
                    processed, total, progress = data
                    self.progress_var.set(progress)
                    self.status_var.set(f"正在生成NFO: {processed}/{total}")
                    
                elif action == "generate_complete":
                    self.status_var.set(f"NFO生成完成，共处理 {data} 个Single文件课程")
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
            self.courses_tree.insert('', 'end', values=(
                course.name,
                str(course.path),
                course.single_file.name,
                f"{course.video_count}个"
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
总视频数：{stats['total_videos']}
平均每课程视频数：{stats['average_videos_per_course']:.1f}"""
        
        self.stats_text.insert(1.0, stats_text)
        self.stats_text.configure(state='disabled')
