"""
课程类型管理模块
"""
from dataclasses import dataclass
from typing import List, Optional
from ..utils.config import config

@dataclass
class CourseType:
    """课程类型"""
    name: str
    description: str

class CourseTypeManager:
    """课程类型管理器"""
    
    def __init__(self):
        self.types = self._load_types()
    
    def _load_types(self) -> List[CourseType]:
        """从配置加载课程类型"""
        types_data = config.get('course_types', [])
        return [CourseType(**type_data) for type_data in types_data]
    
    def save_types(self, types: List[CourseType]) -> None:
        """保存课程类型到配置"""
        self.types = types
        config.set('course_types', [
            {'name': t.name, 'description': t.description}
            for t in types
        ])
    
    def get_all_types(self) -> List[CourseType]:
        """获取所有课程类型"""
        return self.types
    
    def get_type_by_name(self, name: str) -> Optional[CourseType]:
        """根据名称获取课程类型"""
        for course_type in self.types:
            if course_type.name == name:
                return course_type
        return None
    
    def add_type(self, name: str, description: str) -> None:
        """添加课程类型"""
        if not self.get_type_by_name(name):
            self.types.append(CourseType(name, description))
            self.save_types(self.types)
    
    def remove_type(self, name: str) -> bool:
        """删除课程类型"""
        course_type = self.get_type_by_name(name)
        if course_type:
            self.types.remove(course_type)
            self.save_types(self.types)
            return True
        return False
    
    def update_type(self, name: str, new_name: str, new_description: str) -> bool:
        """更新课程类型"""
        course_type = self.get_type_by_name(name)
        if course_type:
            course_type.name = new_name
            course_type.description = new_description
            self.save_types(self.types)
            return True
        return False 