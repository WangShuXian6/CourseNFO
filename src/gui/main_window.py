"""
主窗口模块
"""
import tkinter as tk
from tkinter import ttk, messagebox
from .nfo_gen import NFOGenTab
from .nfo_edit import NFOEditTab
from .nomedia import NoMediaTab
from .nfo_batch import NFOBatchTab

class MainWindow:
    """主窗口"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("课程NFO管理器")
        self.root.geometry("800x600")
        
        # 创建标签页控件
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # 创建NFO生成标签页
        self.nfo_gen_tab = NFOGenTab(self.notebook)
        self.notebook.add(self.nfo_gen_tab, text="NFO生成")
        
        # 创建NFO编辑标签页
        self.nfo_edit_tab = NFOEditTab(self.notebook)
        self.notebook.add(self.nfo_edit_tab, text="NFO编辑")
        
        # 创建.nomedia管理标签页
        self.nomedia_tab = NoMediaTab(self.notebook)
        self.notebook.add(self.nomedia_tab, text=".nomedia管理")
        
        # 创建NFO批量管理标签页
        self.nfo_batch_tab = NFOBatchTab(self.notebook)
        self.notebook.add(self.nfo_batch_tab, text="NFO批量管理")
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()
    
    def _on_closing(self):
        """窗口关闭事件处理"""
        if messagebox.askokcancel("确认退出", "确定要退出程序吗？"):
            self.root.destroy() 