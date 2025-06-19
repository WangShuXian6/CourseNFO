"""
NFO生成标签页模块
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from ..core.scanner import DirectoryScanner
from ..core.tags import TagManager
from ..core.nfo import NFOGenerator
from ..utils.config import config

class NFOGenTab(ttk.Frame):
    """NFO生成标签页"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        # 目录选择框架
        dir_frame = ttk.LabelFrame(self, text="目录选择", padding=5)
        dir_frame.pack(fill='x', padx=5, pady=5)
        
        self.dir_path = tk.StringVar(value="未选择")
        ttk.Label(dir_frame, text="根目录：").pack(side='left')
        ttk.Label(dir_frame, textvariable=self.dir_path).pack(side='left', fill='x', expand=True)
        ttk.Button(dir_frame, text="选择目录", command=self._select_directory).pack(side='right')
        
        # 配置选项框架
        config_frame = ttk.LabelFrame(self, text="配置选项", padding=5)
        config_frame.pack(fill='x', padx=5, pady=5)
        
        # 最小课程名长度
        length_frame = ttk.Frame(config_frame)
        length_frame.pack(fill='x', pady=2)
        ttk.Label(length_frame, text="最小课程名长度：").pack(side='left')
        self.length_var = tk.IntVar(value=config.get('min_course_name_length'))
        length_spin = ttk.Spinbox(
            length_frame,
            from_=1,
            to=100,
            textvariable=self.length_var,
            width=5,
            command=self._on_length_changed
        )
        length_spin.pack(side='left')
        
        # 是否覆盖已有NFO
        self.overwrite_var = tk.BooleanVar(value=config.get('overwrite_existing'))
        ttk.Checkbutton(
            config_frame,
            text="覆盖已有NFO",
            variable=self.overwrite_var,
            command=self._on_overwrite_changed
        ).pack(pady=2)
        
        # 是否检测.nomedia文件
        self.check_nomedia_var = tk.BooleanVar(value=config.get('check_nomedia'))
        ttk.Checkbutton(
            config_frame,
            text="检测.nomedia文件",
            variable=self.check_nomedia_var,
            command=self._on_check_nomedia_changed
        ).pack(pady=2)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill='x', padx=5, pady=5)
        
        # 日志文本框
        log_frame = ttk.LabelFrame(self, text="处理日志", padding=5)
        log_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10)
        scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 开始按钮
        self.start_button = ttk.Button(
            self,
            text="开始生成",
            command=self._start_generation,
            state='disabled'
        )
        self.start_button.pack(pady=5)
        
        self.processing = False
    
    def _select_directory(self):
        """选择目录"""
        directory = filedialog.askdirectory(
            title="选择根目录",
            initialdir=str(Path.home())
        )
        
        if directory:
            self.dir_path.set(directory)
            self.start_button['state'] = 'normal'
    
    def _on_length_changed(self):
        """课程名长度改变事件"""
        try:
            value = self.length_var.get()
            config.set('min_course_name_length', value)
        except:
            pass
    
    def _on_overwrite_changed(self):
        """覆盖选项改变事件"""
        config.set('overwrite_existing', self.overwrite_var.get())
    
    def _on_check_nomedia_changed(self):
        """检测.nomedia选项改变事件"""
        config.set('check_nomedia', self.check_nomedia_var.get())
    
    def _start_generation(self):
        """开始生成NFO"""
        if self.processing:
            return
            
        if self.dir_path.get() == "未选择":
            messagebox.showwarning("警告", "请先选择目录！")
            return
        
        self.processing = True
        self._set_ui_enabled(False)
        self.log_text.delete('1.0', tk.END)
        self.progress_var.set(0)
        
        # 创建工作线程
        thread = threading.Thread(target=self._process_directory)
        thread.daemon = True
        thread.start()
    
    def _process_directory(self):
        """处理目录（工作线程）"""
        try:
            scanner = DirectoryScanner()
            tag_manager = TagManager()
            nfo_generator = NFOGenerator()
            
            # 扫描课程
            self._append_log("开始扫描目录...")
            courses = scanner.scan_directory(Path(self.dir_path.get()))
            
            if not courses:
                self._append_log("错误: 未找到符合条件的课程目录")
                self._on_complete()
                return
            
            total = len(courses)
            self._append_log(f"找到 {total} 个课程")
            
            # 处理每个课程
            for i, course in enumerate(courses, 1):
                self._append_log(f"正在处理课程 ({i}/{total}): {course.name}")
                
                # 收集标签
                tags = tag_manager.collect_tags(course.path)
                
                # 生成NFO
                nfo_generator.generate_course_nfo(course, tags)
                
                # 更新进度
                self.progress_var.set(i * 100 / total)
            
            self._append_log("NFO生成完成！")
            
        except Exception as e:
            self._append_log(f"错误: {str(e)}")
            
        finally:
            self._on_complete()
    
    def _set_ui_enabled(self, enabled: bool):
        """设置界面启用状态"""
        state = 'normal' if enabled else 'disabled'
        self.start_button['state'] = state
    
    def _append_log(self, message: str):
        """添加日志"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
    
    def _on_complete(self):
        """完成处理"""
        self.processing = False
        self._set_ui_enabled(True) 