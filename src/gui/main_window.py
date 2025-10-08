"""
主窗口模块
"""
import tkinter as tk
from tkinter import ttk, messagebox
from .nfo_gen import NFOGenTab
from .nfo_edit import NFOEditTab
from .nomedia import NoMediaTab
from .nfo_batch import NFOBatchTab
from .nfo_type4 import NFOType4Tab
from .variety_nfo import VarietyNfoTab
from .variety_nfo_manual import VarietyNfoManualTab
from .short_drama_nfo import ShortDramaNfoTab
from .course_batch_tab import CourseBatchTab
from .course_batch_nested_tab import CourseBatchNestedTab
from .single_course_tab import SingleCourseTab

class MainWindow:
    """主窗口"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("课程NFO管理器")
        self.root.geometry("1024x900")
        
        # 配置主题样式
        self._setup_theme()
        
        # 创建主容器
        main_container = ttk.Frame(self.root, style='Main.TFrame')
        main_container.pack(expand=True, fill='both')
        
        # 创建标题栏
        title_frame = ttk.Frame(main_container, style='Title.TFrame')
        title_frame.pack(fill='x', padx=32, pady=(32, 0))
        
        title_label = ttk.Label(
            title_frame,
            text="课程NFO管理器",
            style='Title.TLabel'
        )
        title_label.pack(side='left')
        
        # 创建标签页容器
        tab_container = ttk.Frame(main_container, style='TabContainer.TFrame')
        tab_container.pack(expand=True, fill='both', padx=32, pady=32)
        
        # 创建标签页控件
        self.notebook = ttk.Notebook(tab_container)
        self.notebook.pack(expand=True, fill='both')
        
        # 创建Single文件课程标签页（第一位）
        self.single_course_tab = SingleCourseTab(self.notebook)
        self.notebook.add(self.single_course_tab, text="Single文件课程")
        
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
        
        # 创建2层嵌套子目录标签页
        self.nfo_type4_tab = NFOType4Tab(self.notebook)
        self.notebook.add(self.nfo_type4_tab, text="2层嵌套子目录")
        
        # 创建综艺NFO生成标签页
        self.variety_nfo_tab = VarietyNfoTab(self.notebook)
        self.notebook.add(self.variety_nfo_tab, text="综艺NFO生成")
        
        # 创建短剧NFO生成标签页
        self.short_drama_nfo_tab = ShortDramaNfoTab(self.notebook)
        self.notebook.add(self.short_drama_nfo_tab, text="短剧NFO生成")
        
        # 创建综艺NFO手动排序标签页
        self.variety_nfo_manual_tab = VarietyNfoManualTab(self.notebook)
        self.notebook.add(self.variety_nfo_manual_tab, text="综艺NFO手动排序")
        
        # 创建课程批量查找标签页
        self.course_batch_tab = CourseBatchTab(self.notebook)
        self.notebook.add(self.course_batch_tab, text="课程批量查找")
        
        # 创建多级目录课程批量查找标签页（lession_2 + 可配置层级）
        self.course_batch_nested_tab = CourseBatchNestedTab(self.notebook)
        self.notebook.add(self.course_batch_nested_tab, text="课程批量查找(多级)")
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 绑定标签页切换事件
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)
    
    def _setup_theme(self):
        """配置主题样式"""
        style = ttk.Style()
        
        # 配置全局样式
        style.configure('.',
                       font=('Microsoft YaHei UI', 10))
        
        # 主容器样式
        style.configure('Main.TFrame')
        
        # 标题栏样式
        style.configure('Title.TFrame')
        style.configure('Title.TLabel',
                       font=('Microsoft YaHei UI', 16, 'bold'))
        
        # 标签页容器样式
        style.configure('TabContainer.TFrame')
        
        # 标签页样式
        style.configure('TNotebook')
        
        # 标签页标签样式
        style.configure('TNotebook.Tab',
                       padding=[6, 3])
        
        # 标签页内容区域样式
        style.configure('Tab.TFrame',
                       padding=10)
        
        # 框架样式
        style.configure('TFrame')
        style.configure('TLabelframe')
        style.configure('TLabelframe.Label',
                       font=('Microsoft YaHei UI', 10))
        
        # 按钮样式
        style.configure('TButton',
                       padding=[8, 4])
        
        # 输入框样式
        style.configure('TEntry',
                       padding=[4, 2])
        
        # 标签样式
        style.configure('TLabel',
                       font=('Microsoft YaHei UI', 10))
        
        # 滚动条样式
        style.configure('TScrollbar',
                       width=16)
    
    def _on_tab_changed(self, event):
        """标签页切换事件处理"""
        pass
    
    def run(self):
        """运行应用程序"""
        # 设置窗口最小尺寸
        self.root.minsize(800, 700)
        
        # 居中显示
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.root.mainloop()
    
    def _on_closing(self):
        """窗口关闭事件处理"""
        if messagebox.askokcancel("确认退出", "确定要退出程序吗？"):
            self.root.destroy() 
