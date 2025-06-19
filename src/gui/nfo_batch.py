"""
NFO批量管理标签页
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from queue import Queue
import time

class NFOBatchTab(ttk.Frame):
    """NFO批量管理标签页"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.search_thread = None
        self.delete_thread = None
        self.nfo_files = []
        self.progress_queue = Queue()
        self._create_widgets()
        self._setup_layout()
        
    def _create_widgets(self):
        """创建控件"""
        # 目录选择区域
        self.path_frame = ttk.Frame(self)
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(self.path_frame, textvariable=self.path_var, width=50)
        self.browse_btn = ttk.Button(self.path_frame, text="选择目录", command=self._browse_directory)
        
        # 进度显示区域
        self.progress_frame = ttk.Frame(self)
        self.status_var = tk.StringVar(value="未开始搜索")
        self.status_label = ttk.Label(self.progress_frame, textvariable=self.status_var)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, 
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        
        # 操作按钮
        self.button_frame = ttk.Frame(self)
        self.delete_btn = ttk.Button(
            self.button_frame,
            text="批量删除",
            command=self._delete_files,
            state='disabled'
        )
        
    def _setup_layout(self):
        """设置布局"""
        # 目录选择区域
        self.path_frame.pack(fill='x', padx=5, pady=5)
        self.path_entry.pack(side='left', expand=True, fill='x', padx=(0, 5))
        self.browse_btn.pack(side='left')
        
        # 进度显示区域
        self.progress_frame.pack(fill='x', padx=5, pady=5)
        self.status_label.pack(fill='x')
        self.progress_bar.pack(fill='x', pady=5)
        
        # 操作按钮
        self.button_frame.pack(fill='x', padx=5, pady=5)
        self.delete_btn.pack(side='left')
        
    def _browse_directory(self):
        """选择目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.path_var.set(directory)
            self._start_search()
            
    def _start_search(self):
        """开始搜索NFO文件"""
        if self.search_thread and self.search_thread.is_alive():
            return
            
        self._reset_state()
        self.status_var.set("正在搜索...")
        
        self.search_thread = threading.Thread(
            target=self._search_nfo_files,
            args=(Path(self.path_var.get()),)
        )
        self.search_thread.daemon = True
        self.search_thread.start()
        
        # 启动进度更新
        self.after(100, self._update_progress)
        
    def _reset_state(self):
        """重置所有状态"""
        self.nfo_files.clear()
        self.progress_var.set(0)
        self.delete_btn.configure(state='disabled')
        # 清空进度队列
        while not self.progress_queue.empty():
            try:
                self.progress_queue.get_nowait()
            except:
                pass
        
    def _search_nfo_files(self, directory: Path):
        """搜索NFO文件"""
        try:
            for file in directory.rglob("*.nfo"):
                self.nfo_files.append(file)
                # 更新状态
                self.progress_queue.put(("search", len(self.nfo_files)))
                
            # 搜索完成
            self.progress_queue.put(("search_complete", len(self.nfo_files)))
        except Exception as e:
            self.progress_queue.put(("error", str(e)))
            
    def _delete_files(self):
        """删除NFO文件"""
        if not self.nfo_files:
            return
            
        if not messagebox.askyesno(
            "确认删除",
            f"确定要删除找到的 {len(self.nfo_files)} 个NFO文件吗？"
        ):
            return
            
        self.progress_var.set(0)
        self.delete_btn.configure(state='disabled')
        self.status_var.set("正在删除...")
        
        # 创建文件列表的副本
        files_to_delete = self.nfo_files[:]
        
        self.delete_thread = threading.Thread(
            target=self._perform_delete,
            args=(files_to_delete,)
        )
        self.delete_thread.daemon = True
        self.delete_thread.start()
        
        # 启动进度更新
        self.after(100, self._update_progress)
        
    def _perform_delete(self, files_to_delete):
        """执行删除操作"""
        total = len(files_to_delete)
        deleted = 0
        
        for file in files_to_delete:
            try:
                file.unlink()
                deleted += 1
                # 更新进度
                progress = (deleted / total) * 100
                self.progress_queue.put(("delete", (deleted, total, progress)))
                time.sleep(0.01)  # 避免界面卡顿
            except Exception as e:
                print(f"删除文件 {file} 时出错: {e}")
                
        # 删除完成
        self.progress_queue.put(("delete_complete", deleted))
        
    def _update_progress(self):
        """更新进度显示"""
        try:
            while not self.progress_queue.empty():
                action, data = self.progress_queue.get_nowait()
                
                if action == "search":
                    self.status_var.set(f"已找到 {data} 个NFO文件")
                elif action == "search_complete":
                    self.status_var.set(f"搜索完成，共找到 {data} 个NFO文件")
                    self.delete_btn.configure(state='normal' if data > 0 else 'disabled')
                    self.progress_var.set(100)
                elif action == "delete":
                    deleted, total, progress = data
                    self.progress_var.set(progress)
                    self.status_var.set(f"正在删除: {deleted}/{total}")
                elif action == "delete_complete":
                    self.status_var.set(f"删除完成，共删除 {data} 个文件")
                    self.progress_var.set(100)
                    self.nfo_files.clear()
                    self.delete_btn.configure(state='disabled')
                elif action == "error":
                    messagebox.showerror("错误", f"操作出错: {data}")
                    self.status_var.set("操作出错")
                    self._reset_state()
        except Exception as e:
            print(f"更新进度时出错: {e}")
            
        # 如果还有线程在运行，继续更新
        if (self.search_thread and self.search_thread.is_alive()) or \
           (self.delete_thread and self.delete_thread.is_alive()):
            self.after(100, self._update_progress) 