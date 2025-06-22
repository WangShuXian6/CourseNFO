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
        self.processing = False
        self.progress_var = tk.DoubleVar()
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        # 设置内边距
        self.configure(padding=20)
        
        # 目录选择框架
        dir_frame = ttk.LabelFrame(self, text="目录选择", padding=15)
        dir_frame.pack(fill='x', pady=(0, 15))
        
        dir_content = ttk.Frame(dir_frame)
        dir_content.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(dir_content, text="根目录：").pack(side='left')
        self.dir_path = ttk.Entry(dir_content)
        self.dir_path.pack(side='left', fill='x', expand=True, padx=(5, 10))
        
        browse_btn = ttk.Button(dir_content, text="浏览", command=self._browse_dir)
        browse_btn.pack(side='left')
        
        # 控制按钮框架 - 使用Frame而不是LabelFrame以匹配Figma设计
        control_frame = ttk.Frame(self)
        control_frame.pack(fill='x', pady=64)  # 使用Figma的间距
        
        # 使用Figma风格按钮
        self.start_btn = ttk.Button(
            control_frame,
            text="开始处理",
            command=self._start_process,
            style='Figma.TButton'  # 使用Figma按钮样式
        )
        self.start_btn.pack(expand=True)  # 居中对齐
        
        # 进度条
        self.progress = ttk.Progressbar(
            control_frame,
            mode='determinate',
            variable=self.progress_var
        )
        self.progress.pack(fill='x', expand=True, pady=(64, 0))  # 使用Figma的间距
        
        # 配置选项框架
        config_frame = ttk.LabelFrame(self, text="配置选项", padding=15)
        config_frame.pack(fill='x', pady=(0, 15))
        
        config_content = ttk.Frame(config_frame)
        config_content.pack(fill='x', padx=10, pady=5)
        
        # 最小课程名长度
        length_frame = ttk.Frame(config_content)
        length_frame.pack(fill='x', pady=5)
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
        length_spin.pack(side='left', padx=(5, 0))
        
        # 是否覆盖已有NFO
        self.overwrite_var = tk.BooleanVar(value=config.get('overwrite_existing'))
        overwrite_check = ttk.Checkbutton(
            config_content,
            text="覆盖已有NFO",
            variable=self.overwrite_var,
            command=self._on_overwrite_changed,
            style='Switch.TCheckbutton'  # iOS风格开关
        )
        overwrite_check.pack(anchor='w', pady=5)
        
        # 是否检测.nomedia文件
        self.check_nomedia_var = tk.BooleanVar(value=config.get('check_nomedia'))
        nomedia_check = ttk.Checkbutton(
            config_content,
            text="检测.nomedia文件",
            variable=self.check_nomedia_var,
            command=self._on_check_nomedia_changed,
            style='Switch.TCheckbutton'  # iOS风格开关
        )
        nomedia_check.pack(anchor='w', pady=5)
        
        # 日志区域
        log_frame = ttk.LabelFrame(self, text="处理日志", padding=15)
        log_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        log_content = ttk.Frame(log_frame)
        log_content.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 创建带样式的文本框
        self.log_text = tk.Text(
            log_content,
            height=10,
            wrap='word',
            font=('Microsoft YaHei UI', 9),
            background='#f5f5f7',
            relief='flat',
            padx=10,
            pady=10
        )
        scrollbar = ttk.Scrollbar(log_content, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def _browse_dir(self):
        """浏览选择目录"""
        directory = filedialog.askdirectory(
            title="选择根目录",
            initialdir=str(Path.home())
        )
        if directory:
            self.dir_path.delete(0, tk.END)
            self.dir_path.insert(0, directory)
            
    def _start_process(self):
        """开始处理"""
        if self.processing:
            return
            
        directory = self.dir_path.get().strip()
        if not directory:
            messagebox.showerror("错误", "请先选择根目录")
            return
            
        if not Path(directory).exists():
            messagebox.showerror("错误", "所选目录不存在")
            return
            
        self.processing = True
        self._set_ui_state(False)
        self.progress_var.set(0)
        
        # 在新线程中执行处理
        thread = threading.Thread(target=self._process_directory)
        thread.daemon = True
        thread.start()
        
    def _process_directory(self):
        """处理目录"""
        try:
            directory = self.dir_path.get().strip()
            # TODO: 实现目录处理逻辑
            self.progress_var.set(100)
            messagebox.showinfo("完成", "处理完成")
        except Exception as e:
            messagebox.showerror("错误", f"处理过程中出错：{str(e)}")
        finally:
            self.processing = False
            self._set_ui_state(True)
            
    def _set_ui_state(self, enabled: bool):
        """设置界面启用状态"""
        state = 'normal' if enabled else 'disabled'
        self.start_btn['state'] = state
        self.dir_path['state'] = state
        
    def _append_log(self, message: str):
        """添加日志"""
        self.log_text.insert('end', f"{message}\n")
        self.log_text.see('end')
        
        self.processing = False
        
        # 配置开关按钮样式
        style = ttk.Style()
        style.configure('Switch.TCheckbutton', font=('Microsoft YaHei UI', 10))
        
        # 配置主要按钮样式
        style.configure('Accent.TButton',
                       font=('Microsoft YaHei UI', 10, 'bold'),
                       background='#007aff',
                       foreground='#ffffff')
    
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
        self.start_btn['state'] = state
    
    def _append_log(self, message: str):
        """添加日志"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        
        # 根据消息类型设置不同的标签样式
        if "错误" in message:
            self.log_text.tag_add("error", "end-2c linestart", "end-1c")
            self.log_text.tag_configure("error", foreground="#ff3b30")  # iOS红色
        elif "完成" in message:
            self.log_text.tag_add("success", "end-2c linestart", "end-1c")
            self.log_text.tag_configure("success", foreground="#34c759")  # iOS绿色
    
    def _on_complete(self):
        """完成处理"""
        self.processing = False
        self._set_ui_enabled(True) 