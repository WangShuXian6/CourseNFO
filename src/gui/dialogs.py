"""
对话框模块
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Set, Optional, List, Tuple
from ..core.course_types import CourseType, CourseTypeManager

class TagDialog(tk.Toplevel):
    """标签编辑对话框"""
    
    def __init__(self, parent, current_tags: Set[str] = None):
        super().__init__(parent)
        self.title("编辑标签")
        self.geometry("300x400")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.result = None
        self.current_tags = current_tags or set()
        
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        # 标签输入
        input_frame = ttk.Frame(self, padding=5)
        input_frame.pack(fill='x')
        
        self.tag_entry = ttk.Entry(input_frame)
        self.tag_entry.pack(side='left', fill='x', expand=True)
        self.tag_entry.bind('<Return>', lambda e: self._add_tag())
        
        ttk.Button(input_frame, text="添加", command=self._add_tag).pack(side='right')
        
        # 标签列表
        list_frame = ttk.Frame(self, padding=5)
        list_frame.pack(fill='both', expand=True)
        
        self.tag_listbox = tk.Listbox(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tag_listbox.yview)
        self.tag_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.tag_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 添加现有标签
        for tag in sorted(self.current_tags):
            self.tag_listbox.insert(tk.END, tag)
        
        # 删除按钮
        ttk.Button(self, text="删除选中", command=self._remove_tag).pack(pady=5)
        
        # 确定/取消按钮
        button_frame = ttk.Frame(self, padding=5)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="确定", command=self._on_ok).pack(side='right')
        ttk.Button(button_frame, text="取消", command=self._on_cancel).pack(side='right', padx=5)
    
    def _add_tag(self):
        """添加标签"""
        tag = self.tag_entry.get().strip()
        if tag and tag not in self.current_tags:
            self.tag_listbox.insert(tk.END, tag)
            self.current_tags.add(tag)
        self.tag_entry.delete(0, tk.END)
    
    def _remove_tag(self):
        """删除选中的标签"""
        selection = self.tag_listbox.curselection()
        if selection:
            tag = self.tag_listbox.get(selection[0])
            self.tag_listbox.delete(selection[0])
            self.current_tags.remove(tag)
    
    def _on_ok(self):
        """确定按钮事件"""
        self.result = self.current_tags
        self.destroy()
    
    def _on_cancel(self):
        """取消按钮事件"""
        self.destroy()

class CourseTypeDialog(tk.Toplevel):
    """课程类型管理对话框"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("课程类型管理")
        self.geometry("400x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.type_manager = CourseTypeManager()
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        # 类型列表
        list_frame = ttk.LabelFrame(self, text="课程类型列表", padding=5)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 创建表格
        columns = ('name', 'description')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # 设置列
        self.tree.heading('name', text='类型名称')
        self.tree.heading('description', text='描述')
        
        self.tree.column('name', width=100)
        self.tree.column('description', width=250)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 编辑区域
        edit_frame = ttk.LabelFrame(self, text="编辑", padding=5)
        edit_frame.pack(fill='x', padx=5, pady=5)
        
        # 类型名称
        name_frame = ttk.Frame(edit_frame)
        name_frame.pack(fill='x', pady=2)
        ttk.Label(name_frame, text="类型名称：").pack(side='left')
        self.name_entry = ttk.Entry(name_frame)
        self.name_entry.pack(side='left', fill='x', expand=True)
        
        # 类型描述
        desc_frame = ttk.Frame(edit_frame)
        desc_frame.pack(fill='x', pady=2)
        ttk.Label(desc_frame, text="类型描述：").pack(side='left')
        self.desc_entry = ttk.Entry(desc_frame)
        self.desc_entry.pack(side='left', fill='x', expand=True)
        
        # 操作按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="添加", command=self._add_type).pack(side='left', padx=5)
        ttk.Button(button_frame, text="更新", command=self._update_type).pack(side='left', padx=5)
        ttk.Button(button_frame, text="删除", command=self._delete_type).pack(side='left', padx=5)
        ttk.Button(button_frame, text="关闭", command=self.destroy).pack(side='right')
        
        # 绑定选择事件
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        
        # 加载数据
        self._load_types()
    
    def _load_types(self):
        """加载类型数据"""
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加数据
        for course_type in self.type_manager.get_all_types():
            self.tree.insert('', tk.END, values=(course_type.name, course_type.description))
    
    def _on_select(self, event):
        """选择事件处理"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item)['values']
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, values[0])
            self.desc_entry.delete(0, tk.END)
            self.desc_entry.insert(0, values[1])
    
    def _add_type(self):
        """添加类型"""
        name = self.name_entry.get().strip()
        description = self.desc_entry.get().strip()
        
        if not name:
            messagebox.showwarning("警告", "请输入类型名称！")
            return
            
        if self.type_manager.get_type_by_name(name):
            messagebox.showwarning("警告", "类型名称已存在！")
            return
            
        self.type_manager.add_type(name, description)
        self._load_types()
        self.name_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
    
    def _update_type(self):
        """更新类型"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要更新的类型！")
            return
            
        item = selection[0]
        old_name = self.tree.item(item)['values'][0]
        new_name = self.name_entry.get().strip()
        new_description = self.desc_entry.get().strip()
        
        if not new_name:
            messagebox.showwarning("警告", "请输入类型名称！")
            return
            
        if new_name != old_name and self.type_manager.get_type_by_name(new_name):
            messagebox.showwarning("警告", "类型名称已存在！")
            return
            
        if self.type_manager.update_type(old_name, new_name, new_description):
            self._load_types()
        else:
            messagebox.showerror("错误", "更新类型失败！")
    
    def _delete_type(self):
        """删除类型"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的类型！")
            return
            
        item = selection[0]
        name = self.tree.item(item)['values'][0]
        
        if messagebox.askyesno("确认", f'确定要删除类型"{name}"吗？'):
            if self.type_manager.remove_type(name):
                self._load_types()
                self.name_entry.delete(0, tk.END)
                self.desc_entry.delete(0, tk.END)
            else:
                messagebox.showerror("错误", "删除类型失败！") 