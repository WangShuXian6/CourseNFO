import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from ..core.nfo import NFOGenerator

class ShortDramaNfoTab(ttk.Frame):
    """
    短剧NFO生成标签页
    用于批量扫描短剧目录，自动生成tvshow.nfo和每集nfo文件。
    目录结构要求：
      - 总目录下每个短剧为一个子目录，命名规则：字母-短剧名称（
      - 每个短剧目录下视频文件名为纯数字（如01.mp4），可选封面文件名（如0.jpg）
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.nfo_generator = NFOGenerator()
        self.init_ui()
        self.processing = False

    def init_ui(self):
        """
        初始化UI，包括目录选择、封面名输入、生成按钮和日志区。
        """
        self.grid_columnconfigure(1, weight=1)
        # 说明
        explanation = (
            "使用说明：\n"
            "1. 选择包含多个短剧的目录（每个短剧为一个子目录）\n"
            "2. 可手动输入封面文件名（多个用逗号分隔），留空则默认0.jpg\n"
            "3. 可自定义原始海报名和目标海报名，默认0→poster\n"
            "4. 点击'生成NFO'，为每个短剧下的视频生成nfo\n"
            "5. 点击'生成竖版海报'，批量重命名海报文件\n"
            "\n目录结构示例：\n"
            "短剧总目录/\n"
            "  ├─ C-池中之物（44集）杨骐远&苏文文/\n"
            "  │    ├─ 01.mp4\n"
            "  │    ├─ 02.mp4\n"
            "  │    ├─ 0.jpg（原始海报）\n"
            "  │    └─ poster.jpg（竖版海报）\n"
            "  ├─ C-穿书后我靠撒娇续命（77集）大宝（孙志强）&项云/\n"
            "  │    ├─ 01.mp4\n"
            "  │    ├─ 0.jpg\n"
            "  │    └─ poster.jpg\n"
        )
        explanation_text = tk.Text(self, height=13, width=60, wrap=tk.WORD)
        explanation_text.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        explanation_text.insert("1.0", explanation)
        explanation_text.configure(state="disabled")

        # 目录选择
        ttk.Label(self, text="短剧总目录:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.dir_path = tk.StringVar()
        ttk.Entry(self, textvariable=self.dir_path).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(self, text="浏览", command=self.select_directory).grid(row=1, column=2, sticky="w", padx=5, pady=5)

        # 封面文件名输入
        ttk.Label(self, text="封面文件名(逗号分隔):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.cover_names = tk.StringVar()
        ttk.Entry(self, textvariable=self.cover_names).grid(row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        # 原始海报名输入
        ttk.Label(self, text="原始海报名:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.poster_src = tk.StringVar(value="0")
        ttk.Entry(self, textvariable=self.poster_src).grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        # 目标海报名输入
        ttk.Label(self, text="目标海报名:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.poster_dst = tk.StringVar(value="poster")
        ttk.Entry(self, textvariable=self.poster_dst).grid(row=4, column=1, sticky="ew", padx=5, pady=5)

        # 生成竖版海报按钮
        ttk.Button(self, text="生成竖版海报", command=self.on_generate_poster).grid(row=5, column=1, pady=5)

        # 生成NFO按钮
        ttk.Button(self, text="生成NFO", command=self.on_generate).grid(row=6, column=1, pady=10)

        # 日志区
        log_frame = ttk.LabelFrame(self, text="处理日志", padding=5)
        log_frame.grid(row=7, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        self.log_text = tk.Text(log_frame, height=10)
        self.log_text.pack(fill='both', expand=True)

    def select_directory(self):
        """
        弹出目录选择对话框，设置目录路径。
        """
        path = filedialog.askdirectory()
        if path:
            self.dir_path.set(path)

    def on_generate(self):
        """
        启动NFO生成线程，避免界面卡死。
        """
        if self.processing:
            return
        dir_path = self.dir_path.get().strip()
        if not dir_path:
            messagebox.showerror("错误", "请选择短剧总目录！")
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
        """
        扫描总目录下所有短剧子目录，按规则提取短剧名，
        对每个短剧目录下所有视频按数字顺序生成nfo，支持多种封面名。
        日志区实时反馈进度和异常。
        """
        try:
            dir_path = Path(dir_path)
            self._append_log(f"扫描总目录: {dir_path}")
            # 获取所有一级子目录
            subdirs = [d for d in dir_path.iterdir() if d.is_dir()]
            if not subdirs:
                self._append_log("未找到任何短剧子目录！")
                self.processing = False
                return
            found_any = False
            for subdir in subdirs:
                name = subdir.name
                # 按规则提取短剧名：字母-短剧名称（
                if '-' in name and '（' in name:
                    dash_idx = name.find('-')
                    paren_idx = name.find('（')
                    if dash_idx < paren_idx:
                        short_drama_name = name[dash_idx+1:paren_idx].strip()
                        self._append_log(f"发现短剧目录: {name}，短剧名: {short_drama_name}")
                        found_any = True
                        try:
                            # 处理视频文件
                            video_files = [f for f in subdir.iterdir() if f.is_file() and f.suffix.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv']]
                            # 只保留纯数字文件名
                            video_files = [f for f in video_files if f.stem.isdigit()]
                            # 按数字顺序排序
                            video_files.sort(key=lambda x: int(x.stem))
                            if not video_files:
                                self._append_log(f"  未找到视频文件，跳过: {name}")
                                continue
                            self._append_log(f"  共{len(video_files)}集，开始生成NFO...")
                            # 处理封面文件名
                            cover_input = self.cover_names.get().strip()
                            cover_names = [n.strip() for n in cover_input.split(',') if n.strip()] if cover_input else ['0.jpg']
                            cover_file = None
                            for cname in cover_names:
                                cpath = subdir / cname
                                if cpath.exists() and cpath.is_file():
                                    cover_file = cpath
                                    break
                            if cover_file:
                                self._append_log(f"  使用封面: {cover_file.name}")
                            else:
                                self._append_log(f"  未找到封面文件，已跳过封面关联")
                            # 生成tvshow.nfo
                            self.nfo_generator.generate_tvshow_nfo(str(subdir), short_drama_name, 1)
                            self._append_log(f"  已生成tvshow.nfo")
                            # 生成每集nfo
                            for idx, video in enumerate(video_files, 1):
                                try:
                                    self.nfo_generator.generate_episode_nfo(str(video), short_drama_name, idx, video.stem, 1)
                                    self._append_log(f"    第{idx}集：{video.name} -> {video.with_suffix('.nfo').name}")
                                except Exception as ve:
                                    self._append_log(f"    生成第{idx}集NFO失败: {ve}")
                            self._append_log(f"  短剧NFO生成完成: {short_drama_name}")
                        except Exception as sub_e:
                            self._append_log(f"  处理短剧目录时出错: {sub_e}")
                    else:
                        self._append_log(f"目录名格式异常，跳过: {name}")
                else:
                    self._append_log(f"目录名不符合规则，跳过: {name}")
            if not found_any:
                self._append_log("未发现任何符合规则的短剧目录！")
        except Exception as e:
            self._append_log(f"错误: {e}")
        finally:
            self.processing = False

    def _append_log(self, message):
        """
        向日志区追加消息并自动滚动。
        """
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def on_generate_poster(self):
        """
        竖版海报批量生成处理函数
        遍历所有短剧子目录，将原始海报文件（如0.jpg/0.png）重命名为目标名（如poster.jpg/poster.png），不覆盖已存在目标。
        """
        dir_path = self.dir_path.get().strip()
        if not dir_path:
            self._append_log("[竖版海报] 请选择短剧总目录！")
            return
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            self._append_log("[竖版海报] 目录不存在！")
            return
        poster_src = self.poster_src.get().strip() or "0"
        poster_dst = self.poster_dst.get().strip() or "poster"
        exts = [".jpg", ".png"]
        subdirs = [d for d in dir_path.iterdir() if d.is_dir()]
        if not subdirs:
            self._append_log("[竖版海报] 未找到任何短剧子目录！")
            return
        for subdir in subdirs:
            name = subdir.name
            # 只处理符合短剧命名规则的目录
            if '-' in name and '（' in name:
                dash_idx = name.find('-')
                paren_idx = name.find('（')
                if dash_idx < paren_idx:
                    found = False
                    for ext in exts:
                        src_file = subdir / f"{poster_src}{ext}"
                        dst_file = subdir / f"{poster_dst}{ext}"
                        if src_file.exists():
                            if dst_file.exists():
                                self._append_log(f"[{name}] 目标海报已存在({dst_file.name})，跳过")
                                found = True
                                break
                            try:
                                src_file.rename(dst_file)
                                self._append_log(f"[{name}] {src_file.name} → {dst_file.name} 成功")
                                found = True
                                break
                            except Exception as e:
                                self._append_log(f"[{name}] 重命名失败: {e}")
                                found = True
                                break
                    if not found:
                        self._append_log(f"[{name}] 未找到原始海报({poster_src}.jpg/.png)")
                else:
                    self._append_log(f"[{name}] 目录名格式异常，跳过")
            else:
                self._append_log(f"[{name}] 目录名不符合规则，跳过") 