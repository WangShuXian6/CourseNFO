import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from ..core.nfo import NFOGenerator

class VarietyNfoTab(ttk.Frame):
    """综艺NFO生成标签页"""
    def __init__(self, parent):
        super().__init__(parent)
        self.nfo_generator = NFOGenerator()
        self.init_ui()
        self.processing = False

    def init_ui(self):
        self.grid_columnconfigure(1, weight=1)
        # 说明
        explanation = (
            "使用说明：\n"
            "1. 选择综艺目录（递归扫描所有视频）\n"
            "2. 可手动输入综艺名称和季数，留空则自动填充\n"
            "3. 点击'生成NFO'，为每个视频生成同名nfo和tvshow.nfo\n"
        )
        explanation_text = tk.Text(self, height=6, width=60, wrap=tk.WORD)
        explanation_text.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        explanation_text.insert("1.0", explanation)
        explanation_text.configure(state="disabled")

        # 目录选择
        ttk.Label(self, text="综艺目录:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.dir_path = tk.StringVar()
        ttk.Entry(self, textvariable=self.dir_path).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(self, text="浏览", command=self.select_directory).grid(row=1, column=2, sticky="w", padx=5, pady=5)

        # 综艺名输入
        ttk.Label(self, text="综艺名称:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.variety_name = tk.StringVar()
        ttk.Entry(self, textvariable=self.variety_name).grid(row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        # 季数输入
        ttk.Label(self, text="季数:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.season_num = tk.StringVar()
        ttk.Entry(self, textvariable=self.season_num).grid(row=3, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        # 生成按钮
        ttk.Button(self, text="生成NFO", command=self.on_generate).grid(row=4, column=1, pady=10)

        # 日志区
        log_frame = ttk.LabelFrame(self, text="处理日志", padding=5)
        log_frame.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        self.log_text = tk.Text(log_frame, height=10)
        self.log_text.pack(fill='both', expand=True)

    def select_directory(self):
        path = filedialog.askdirectory()
        if path:
            self.dir_path.set(path)

    def on_generate(self):
        if self.processing:
            return
        dir_path = self.dir_path.get().strip()
        if not dir_path:
            messagebox.showerror("错误", "请选择综艺目录！")
            return
        if not Path(dir_path).is_dir():
            messagebox.showerror("错误", "目录不存在！")
            return
        self.processing = True
        self.log_text.delete('1.0', tk.END)
        thread = threading.Thread(target=self._generate_nfo_thread, args=(dir_path,))
        thread.daemon = True
        thread.start()

    def _generate_nfo_thread(self, dir_path):
        try:
            dir_path = Path(dir_path)
            # 综艺名
            variety_name = self.variety_name.get().strip() or dir_path.name
            # 季数
            season_str = self.season_num.get().strip()
            try:
                season_num = int(season_str) if season_str else 1
                if season_num < 1:
                    raise ValueError
            except ValueError:
                self._append_log("季数输入无效，已自动设为1")
                season_num = 1
            self._append_log(f"扫描目录: {dir_path}")
            # 扫描所有视频
            video_files = sorted([f for f in dir_path.rglob("*") if f.is_file() and f.suffix.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv']])
            if not video_files:
                self._append_log("未找到任何视频文件！")
                self.processing = False
                return
            self._append_log(f"共找到{len(video_files)}个视频文件，开始生成NFO...")
            # 生成tvshow.nfo
            self.nfo_generator.generate_tvshow_nfo(str(dir_path), variety_name, season_num)
            self._append_log(f"已生成tvshow.nfo（季数: {season_num}）")
            # 生成每集nfo
            for idx, video in enumerate(video_files, 1):
                title = video.stem
                self.nfo_generator.generate_episode_nfo(str(video), variety_name, idx, title, season_num)
                self._append_log(f"第{idx}集：{video.name} -> {video.with_suffix('.nfo').name}（季数: {season_num}）")
            self._append_log("全部NFO生成完成！")
        except Exception as e:
            self._append_log(f"错误: {e}")
        finally:
            self.processing = False

    def _append_log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END) 