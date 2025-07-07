import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from ..core.nfo import NFOGenerator

class VarietyNfoManualTab(ttk.Frame):
    """综艺NFO手动排序标签页（左右分栏大排序区）"""
    def __init__(self, parent):
        super().__init__(parent)
        self.nfo_generator = NFOGenerator()
        self.video_files = []
        self.processing = False
        self._drag_data = {"item": None, "index": None}
        self.init_ui()

    def init_ui(self):
        # 主体分栏
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill='both', expand=True)

        # 左侧输入区
        left_frame = ttk.Frame(paned, width=320)
        paned.add(left_frame, weight=0)

        # 右侧排序区
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)

        # 左侧内容
        explanation = (
            "使用说明：\n"
            "1. 选择综艺目录（递归扫描所有视频）\n"
            "2. 可手动拖动右侧视频文件排序，按顺序自动编号为第几期\n"
            "3. 可手动输入综艺名称和季数，留空则自动填充\n"
            "4. 点击'生成NFO'，为每个视频生成同名nfo和tvshow.nfo\n"
        )
        explanation_text = tk.Text(left_frame, height=7, width=38, wrap=tk.WORD)
        explanation_text.pack(fill='x', padx=5, pady=5)
        explanation_text.insert("1.0", explanation)
        explanation_text.configure(state="disabled")

        # 目录选择
        dir_row = ttk.Frame(left_frame)
        dir_row.pack(fill='x', padx=5, pady=5)
        ttk.Label(dir_row, text="综艺目录:").pack(side='left')
        self.dir_path = tk.StringVar()
        ttk.Entry(dir_row, textvariable=self.dir_path, width=22).pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(dir_row, text="浏览", command=self.select_directory).pack(side='left')

        # 综艺名输入
        name_row = ttk.Frame(left_frame)
        name_row.pack(fill='x', padx=5, pady=5)
        ttk.Label(name_row, text="综艺名称:").pack(side='left')
        self.variety_name = tk.StringVar()
        ttk.Entry(name_row, textvariable=self.variety_name, width=22).pack(side='left', fill='x', expand=True, padx=5)

        # 季数输入
        season_row = ttk.Frame(left_frame)
        season_row.pack(fill='x', padx=5, pady=5)
        ttk.Label(season_row, text="季数:").pack(side='left')
        self.season_num = tk.StringVar()
        ttk.Entry(season_row, textvariable=self.season_num, width=22).pack(side='left', fill='x', expand=True, padx=5)

        # 按钮区
        btn_row = ttk.Frame(left_frame)
        btn_row.pack(fill='x', padx=5, pady=10)
        ttk.Button(btn_row, text="重新扫描", command=self.scan_videos).pack(side='left', padx=2)
        ttk.Button(btn_row, text="生成NFO", command=self.on_generate).pack(side='right', padx=2)

        # 日志区
        log_frame = ttk.LabelFrame(left_frame, text="处理日志", padding=5)
        log_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.log_text = tk.Text(log_frame, height=8)
        self.log_text.pack(fill='both', expand=True)

        # 右侧排序区（大面积Listbox+滚动条）
        sort_label = ttk.Label(right_frame, text="视频文件（可拖动排序）:")
        sort_label.pack(anchor='nw', padx=5, pady=(10, 0))
        listbox_frame = ttk.Frame(right_frame)
        listbox_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.listbox = tk.Listbox(listbox_frame, selectmode=tk.BROWSE, height=25, width=50)
        self.listbox.pack(side='left', fill='both', expand=True)
        scrollbar = ttk.Scrollbar(listbox_frame, orient='vertical', command=self.listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.listbox.config(yscrollcommand=scrollbar.set)
        self.listbox.bind('<Button-1>', self.on_listbox_click)
        self.listbox.bind('<B1-Motion>', self.on_listbox_drag)
        self.listbox.bind('<ButtonRelease-1>', self.on_listbox_drop)

    def select_directory(self):
        path = filedialog.askdirectory()
        if path:
            self.dir_path.set(path)
            self.scan_videos()

    def scan_videos(self):
        dir_path = self.dir_path.get().strip()
        if not dir_path or not Path(dir_path).is_dir():
            self._append_log("请选择有效的综艺目录！")
            return
        self.video_files = sorted([f for f in Path(dir_path).rglob("*") if f.is_file() and f.suffix.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv']])
        self.listbox.delete(0, tk.END)
        for video in self.video_files:
            self.listbox.insert(tk.END, video.name)
        self._append_log(f"共找到{len(self.video_files)}个视频文件。可拖动排序。")

    # 拖拽排序相关
    def on_listbox_click(self, event):
        idx = self.listbox.nearest(event.y)
        if idx >= 0:
            self._drag_data["item"] = self.listbox.get(idx)
            self._drag_data["index"] = idx

    def on_listbox_drag(self, event):
        idx = self.listbox.nearest(event.y)
        drag_index = self._drag_data["index"]
        if (
            self._drag_data["item"] is not None
            and drag_index is not None
            and idx != drag_index
            and 0 <= idx < self.listbox.size()
        ):
            item = self.listbox.get(drag_index)
            self.listbox.delete(drag_index)
            self.listbox.insert(idx, item)
            # 同步video_files顺序
            video = self.video_files.pop(drag_index)
            self.video_files.insert(idx, video)
            self._drag_data["index"] = idx

    def on_listbox_drop(self, event):
        self._drag_data = {"item": None, "index": None}

    def on_generate(self):
        if self.processing:
            return
        dir_path = self.dir_path.get().strip()
        if not dir_path or not Path(dir_path).is_dir():
            messagebox.showerror("错误", "请选择综艺目录！")
            return
        if not self.video_files:
            messagebox.showerror("错误", "未找到任何视频文件！")
            return
        self.processing = True
        self.log_text.delete('1.0', tk.END)
        thread = threading.Thread(target=self._generate_nfo_thread)
        thread.daemon = True
        thread.start()

    def _generate_nfo_thread(self):
        try:
            dir_path = Path(self.dir_path.get().strip())
            variety_name = self.variety_name.get().strip() or dir_path.name
            season_str = self.season_num.get().strip()
            try:
                season_num = int(season_str) if season_str else 1
                if season_num < 1:
                    raise ValueError
            except ValueError:
                self._append_log("季数输入无效，已自动设为1")
                season_num = 1
            self._append_log(f"生成tvshow.nfo（季数: {season_num}）")
            self.nfo_generator.generate_tvshow_nfo(str(dir_path), variety_name, season_num)
            for idx, video in enumerate(self.video_files, 1):
                title = video.stem
                self.nfo_generator.generate_episode_nfo(str(video), variety_name, idx, title, season_num)
                self._append_log(f"第{idx}期：{video.name} -> {video.with_suffix('.nfo').name}（季数: {season_num}）")
            self._append_log("全部NFO生成完成！")
        except Exception as e:
            self._append_log(f"错误: {e}")
        finally:
            self.processing = False

    def _append_log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END) 