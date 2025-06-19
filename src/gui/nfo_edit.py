"""
NFO编辑标签页模块
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk
from typing import Set, Optional, Dict, List
from ..utils.poster import PosterManager
from ..core.tags import TagManager
from ..core.nfo import NFOGenerator
from ..core.scanner import DirectoryScanner
from ..core.course_types import CourseTypeManager
from .dialogs import TagDialog, CourseTypeDialog

class NFOEditTab(ttk.Frame):
    """NFO编辑标签页"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.poster_manager = PosterManager()
        self.tag_manager = TagManager()
        self.type_manager = CourseTypeManager()
        self.nfo_generator = NFOGenerator()
        self.scanner = DirectoryScanner()
        
        self.courses: Dict[str, Path] = {}  # 课程路径字典
        self.current_course: Optional[Path] = None
        self.current_tags = set()
        self.current_types = set()
        self.thumbnail_cache = {}  # 缩略图缓存
        
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        # 目录选择
        dir_frame = ttk.LabelFrame(self, text="课程目录", padding=5)
        dir_frame.pack(fill='x', padx=5, pady=5)
        
        self.dir_path = tk.StringVar(value="未选择")
        ttk.Label(dir_frame, textvariable=self.dir_path).pack(side='left', fill='x', expand=True)
        ttk.Button(dir_frame, text="选择目录", command=self._select_directory).pack(side='right')
        
        # 主要内容区域
        content_frame = ttk.Frame(self)
        content_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 左侧：课程列表
        course_frame = ttk.LabelFrame(content_frame, text="课程列表", padding=5)
        course_frame.pack(side='left', fill='y')
        
        # 创建课程列表
        self.course_tree = ttk.Treeview(course_frame, columns=('poster', 'types'), show='tree headings', height=15)
        self.course_tree.heading('poster', text='海报')
        self.course_tree.heading('types', text='类型')
        self.course_tree.column('poster', width=80, anchor='center')  # 设置海报列宽度
        self.course_tree.column('types', width=150)
        
        course_scroll = ttk.Scrollbar(course_frame, orient='vertical', command=self.course_tree.yview)
        self.course_tree.configure(yscrollcommand=course_scroll.set)
        
        self.course_tree.pack(side='left', fill='both', expand=True)
        course_scroll.pack(side='right', fill='y')
        
        # 绑定选择事件
        self.course_tree.bind('<<TreeviewSelect>>', self._on_course_select)
        
        # 创建默认的占位图标
        self._create_placeholder_image()
        
        # 中间：海报预览
        poster_frame = ttk.LabelFrame(content_frame, text="海报", padding=5)
        poster_frame.pack(side='left', fill='y', padx=5)
        
        self.poster_label = ttk.Label(poster_frame)
        self.poster_label.pack(pady=5)
        
        poster_buttons = ttk.Frame(poster_frame)
        poster_buttons.pack(fill='x')
        
        ttk.Button(poster_buttons, text="选择海报", command=self._select_poster).pack(side='left', expand=True)
        ttk.Button(poster_buttons, text="移除海报", command=self._remove_poster).pack(side='left', expand=True)
        
        # 右侧：编辑区域
        edit_frame = ttk.LabelFrame(content_frame, text="编辑", padding=5)
        edit_frame.pack(side='left', fill='both', expand=True)
        
        # 课程类型选择
        type_frame = ttk.Frame(edit_frame)
        type_frame.pack(fill='x', pady=5)
        
        ttk.Label(type_frame, text="课程类型：").pack(side='left')
        
        # 创建多选列表框
        self.type_listbox = tk.Listbox(type_frame, selectmode=tk.MULTIPLE, height=4)
        type_scroll = ttk.Scrollbar(type_frame, orient='vertical', command=self.type_listbox.yview)
        self.type_listbox.configure(yscrollcommand=type_scroll.set)
        
        self.type_listbox.pack(side='left', fill='x', expand=True)
        type_scroll.pack(side='left', fill='y')
        
        ttk.Button(type_frame, text="管理类型", command=self._manage_types).pack(side='left', padx=5)
        
        # 标签编辑
        tag_frame = ttk.Frame(edit_frame)
        tag_frame.pack(fill='x', pady=5)
        
        ttk.Label(tag_frame, text="标签：").pack(side='left')
        self.tag_label = ttk.Label(tag_frame, text="")
        self.tag_label.pack(side='left', fill='x', expand=True)
        ttk.Button(tag_frame, text="编辑标签", command=self._edit_tags).pack(side='right')
        
        # 描述编辑
        ttk.Label(edit_frame, text="描述：").pack(anchor='w')
        self.plot_text = tk.Text(edit_frame, height=5)
        self.plot_text.pack(fill='both', expand=True, pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(edit_frame)
        button_frame.pack(fill='x', pady=5)
        
        ttk.Button(button_frame, text="保存更改", command=self._save_changes).pack(side='right')
        ttk.Button(button_frame, text="批量保存", command=self._batch_save).pack(side='right', padx=5)
        
        # 初始化状态
        self._set_ui_enabled(False)
        self._update_type_list()
    
    def _set_ui_enabled(self, enabled: bool):
        """设置界面启用状态"""
        state = 'normal' if enabled else 'disabled'
        for widget in self.winfo_children():
            if isinstance(widget, (ttk.Button, tk.Text)):
                widget.configure(state=state)
    
    def _select_directory(self):
        """选择目录"""
        directory = filedialog.askdirectory(
            title="选择课程目录",
            initialdir=str(Path.home())
        )
        
        if directory:
            self.dir_path.set(directory)
            self._scan_directory(Path(directory))
            self._set_ui_enabled(True)
    
    def _scan_directory(self, root_path: Path):
        """扫描目录"""
        # 清空课程列表和缩略图缓存
        for item in self.course_tree.get_children():
            self.course_tree.delete(item)
        self.courses.clear()
        self.thumbnail_cache.clear()
        
        # 扫描课程
        courses = self.scanner.scan_directory(root_path)
        
        # 添加到列表
        for course in courses:
            # 读取NFO文件
            nfo_path = course.path / "tvshow.nfo"
            course_types = set()
            if nfo_path.exists():
                nfo_data = self.nfo_generator.read_course_nfo(nfo_path)
                if nfo_data and nfo_data.course_types:
                    course_types = nfo_data.course_types
            
            # 获取海报缩略图
            poster_path = self.poster_manager.get_poster_path(course.path)
            thumbnail = self._create_thumbnail(poster_path)
            
            # 添加到树形列表
            item = self.course_tree.insert('', tk.END, text=course.name,
                                         values=('', ', '.join(sorted(course_types))))
            # 设置图片
            self.course_tree.set(item, 'poster', '')  # 清空文本
            self.course_tree.item(item, image=thumbnail)  # 设置图片
            
            self.courses[course.name] = course.path
    
    def _on_course_select(self, event):
        """课程选择事件处理"""
        selection = self.course_tree.selection()
        if selection:
            item = selection[0]
            course_name = self.course_tree.item(item)['text']
            self.current_course = self.courses[course_name]
            self._load_course_data()
    
    def _load_course_data(self):
        """加载课程数据"""
        if not self.current_course:
            return
            
        # 加载海报
        poster_path = self.poster_manager.get_poster_path(self.current_course)
        self._display_poster(poster_path)
        
        # 加载NFO数据
        nfo_path = self.current_course / "tvshow.nfo"
        if nfo_path.exists():
            nfo_data = self.nfo_generator.read_course_nfo(nfo_path)
            if nfo_data:
                # 设置类型
                self.current_types = nfo_data.course_types or set()
                self._set_selected_types(self.current_types)
                
                # 设置标签
                self.current_tags = nfo_data.tags
                self._update_tag_display()
                
                # 设置描述
                self.plot_text.delete('1.0', tk.END)
                if nfo_data.plot:
                    self.plot_text.insert('1.0', nfo_data.plot)
        else:
            # 清空数据
            self.current_types = set()
            self._set_selected_types(set())
            self.current_tags = set()
            self._update_tag_display()
            self.plot_text.delete('1.0', tk.END)
    
    def _display_poster(self, poster_path: Optional[Path]):
        """显示海报"""
        if poster_path and poster_path.exists():
            try:
                # 加载并缩放图片
                image = Image.open(poster_path)
                image.thumbnail((200, 300))
                photo = ImageTk.PhotoImage(image)
                
                self.poster_label.configure(image=photo)
                self.poster_label.image = photo  # 保持引用
            except Exception as e:
                print(f"加载海报出错: {e}")
                self.poster_label.configure(text="加载海报失败")
        else:
            self.poster_label.configure(text="无海报", image="")
    
    def _select_poster(self):
        """选择海报"""
        if not self.current_course:
            return
            
        file_name = filedialog.askopenfilename(
            title="选择海报图片",
            initialdir=str(Path.home()),
            filetypes=[("图片文件", "*.jpg *.jpeg *.png")]
        )
        
        if file_name:
            poster_path = self.poster_manager.save_poster(
                self.current_course,
                Path(file_name)
            )
            if poster_path:
                self._display_poster(poster_path)
                # 更新课程列表中的缩略图
                self._update_course_thumbnail()
    
    def _remove_poster(self):
        """移除海报"""
        if not self.current_course:
            return
            
        if self.poster_manager.delete_poster(self.current_course):
            self.poster_label.configure(text="无海报", image="")
            # 更新课程列表中的缩略图
            self._update_course_thumbnail()
    
    def _update_course_thumbnail(self):
        """更新课程列表中的缩略图"""
        if not self.current_course:
            return
            
        # 获取新的缩略图
        poster_path = self.poster_manager.get_poster_path(self.current_course)
        thumbnail = self._create_thumbnail(poster_path)
        
        # 更新列表中的图片
        for item in self.course_tree.selection():
            self.course_tree.set(item, 'poster', '')  # 清空文本
            self.course_tree.item(item, image=thumbnail)  # 设置图片
    
    def _update_tag_display(self):
        """更新标签显示"""
        self.tag_label.configure(text=", ".join(sorted(self.current_tags)))
    
    def _edit_tags(self):
        """编辑标签"""
        dialog = TagDialog(self, self.current_tags)
        self.wait_window(dialog)
        if dialog.result is not None:
            self.current_tags = dialog.result
            self._update_tag_display()
    
    def _manage_types(self):
        """管理课程类型"""
        dialog = CourseTypeDialog(self)
        self.wait_window(dialog)
        self._update_type_list()
    
    def _update_type_list(self):
        """更新类型列表"""
        self.type_listbox.delete(0, tk.END)
        types = self.type_manager.get_all_types()
        for t in types:
            self.type_listbox.insert(tk.END, t.name)
    
    def _get_selected_types(self) -> Set[str]:
        """获取选中的课程类型"""
        return {self.type_listbox.get(i) for i in self.type_listbox.curselection()}
    
    def _set_selected_types(self, types: Set[str]):
        """设置选中的课程类型"""
        self.type_listbox.selection_clear(0, tk.END)
        for i in range(self.type_listbox.size()):
            if self.type_listbox.get(i) in types:
                self.type_listbox.selection_set(i)
    
    def _save_changes(self):
        """保存更改"""
        if not self.current_course:
            return
            
        # 保存标签
        self.tag_manager.save_tags(self.current_course, self.current_tags)
        
        # 更新NFO文件
        nfo_path = self.current_course / "tvshow.nfo"
        try:
            if nfo_path.exists():
                tree = ET.parse(nfo_path)
                root = tree.getroot()
            else:
                root = ET.Element("tvshow")
                
            # 更新描述
            plot = root.find("plot")
            if plot is None:
                plot = ET.SubElement(root, "plot")
            plot.text = self.plot_text.get('1.0', 'end-1c')
            
            # 更新类型
            for type_elem in root.findall("coursetype"):
                root.remove(type_elem)
            for type_name in sorted(self._get_selected_types()):
                type_elem = ET.SubElement(root, "coursetype")
                type_elem.text = type_name
            
            # 更新标签
            for genre in root.findall("genre"):
                root.remove(genre)
            for tag in sorted(self.current_tags):
                genre = ET.SubElement(root, "genre")
                genre.text = tag
            
            # 保存文件
            xml_str = ET.tostring(root, encoding='unicode')
            with open(nfo_path, 'w', encoding='utf-8') as f:
                f.write(xml_str)
                
            # 更新课程列表显示
            for item in self.course_tree.selection():
                self.course_tree.set(item, 'types', ', '.join(sorted(self._get_selected_types())))
                
            messagebox.showinfo("成功", "保存成功！")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存NFO文件时出错: {e}")
    
    def _batch_save(self):
        """批量保存"""
        if not self.courses:
            messagebox.showwarning("警告", "请先选择目录！")
            return
            
        if not messagebox.askyesno("确认", "确定要将当前设置应用到所有课程吗？"):
            return
            
        try:
            current_types = self._get_selected_types()
            current_tags = self.current_tags.copy()
            current_plot = self.plot_text.get('1.0', 'end-1c')
            
            for course_name, course_path in self.courses.items():
                nfo_path = course_path / "tvshow.nfo"
                if nfo_path.exists():
                    tree = ET.parse(nfo_path)
                    root = tree.getroot()
                else:
                    root = ET.Element("tvshow")
                    title = ET.SubElement(root, "title")
                    title.text = course_name
                
                # 更新描述
                plot = root.find("plot")
                if plot is None:
                    plot = ET.SubElement(root, "plot")
                plot.text = current_plot
                
                # 更新类型
                for type_elem in root.findall("coursetype"):
                    root.remove(type_elem)
                for type_name in sorted(current_types):
                    type_elem = ET.SubElement(root, "coursetype")
                    type_elem.text = type_name
                
                # 更新标签
                for genre in root.findall("genre"):
                    root.remove(genre)
                for tag in sorted(current_tags):
                    genre = ET.SubElement(root, "genre")
                    genre.text = tag
                
                # 保存文件
                xml_str = ET.tostring(root, encoding='unicode')
                with open(nfo_path, 'w', encoding='utf-8') as f:
                    f.write(xml_str)
                    
                # 保存标签
                self.tag_manager.save_tags(course_path, current_tags)
                
                # 更新课程列表显示
                for item in self.course_tree.get_children():
                    if self.course_tree.item(item)['text'] == course_name:
                        self.course_tree.set(item, 'types', ', '.join(sorted(current_types)))
                        break
            
            messagebox.showinfo("成功", "批量保存成功！")
            
        except Exception as e:
            messagebox.showerror("错误", f"批量保存时出错: {e}")

    def _create_placeholder_image(self):
        """创建占位图标"""
        # 创建一个 60x80 的灰色图像
        img = Image.new('RGB', (60, 80), '#E0E0E0')
        self.placeholder_image = ImageTk.PhotoImage(img)

    def _create_thumbnail(self, poster_path: Optional[Path]) -> ImageTk.PhotoImage:
        """创建缩略图"""
        if not poster_path or not poster_path.exists():
            return self.placeholder_image
            
        try:
            # 检查缓存
            if poster_path in self.thumbnail_cache:
                return self.thumbnail_cache[poster_path]
                
            # 加载并缩放图片
            with Image.open(poster_path) as img:
                # 计算缩放比例，保持宽高比
                width, height = img.size
                target_height = 80
                scale = target_height / height
                new_width = int(width * scale)
                
                # 缩放图片
                thumbnail = img.resize((new_width, target_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(thumbnail)
                
                # 保存到缓存
                self.thumbnail_cache[poster_path] = photo
                return photo
                
        except Exception as e:
            print(f"创建缩略图时出错: {e}")
            return self.placeholder_image 