"""
.nomedia文件管理标签页模块
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from ..core.tags import TagManager

class NoMediaTab(ttk.Frame):
    """.nomedia文件管理标签页"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.tag_manager = TagManager()
        self.init_ui()
        self.processing = False
        
    def init_ui(self):
        """初始化界面"""
        # 目录选择框架
        dir_frame = ttk.LabelFrame(self, text="目录选择", padding=5)
        dir_frame.pack(fill='x', padx=5, pady=5)
        
        self.dir_path = tk.StringVar(value="未选择")
        ttk.Label(dir_frame, text="根目录：").pack(side='left')
        ttk.Label(dir_frame, textvariable=self.dir_path).pack(side='left', fill='x', expand=True)
        ttk.Button(dir_frame, text="选择目录", command=self._select_directory).pack(side='right')
        
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
            text="开始处理",
            command=self._start_processing,
            state='disabled'
        )
        self.start_button.pack(pady=5)
    
    def _select_directory(self):
        """选择目录"""
        directory = filedialog.askdirectory(
            title="选择根目录",
            initialdir=str(Path.home())
        )
        
        if directory:
            self.dir_path.set(directory)
            self.start_button['state'] = 'normal'
    
    def _start_processing(self):
        """开始处理"""
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
            root_path = Path(self.dir_path.get())
            self._append_log("开始扫描目录...")
            
            # 创建.nomedia文件
            created_count = self.tag_manager.create_nomedia_files(root_path)
            
            if created_count > 0:
                self._append_log(f"成功创建 {created_count} 个 .nomedia 文件")
            else:
                self._append_log("未找到需要创建 .nomedia 文件的目录")
            
            # 设置进度为100%
            self.progress_var.set(100)
            
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