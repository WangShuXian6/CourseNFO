"""
配置管理模块
"""
from pathlib import Path
import json
from typing import Dict, Any

class Config:
    """配置管理类"""
    
    def __init__(self):
        self.config_file = Path('config.json')
        self.default_config = {
            'min_course_name_length': 10,  # 最小课程名长度
            'tag_file_extension': '.tag',  # 标签文件扩展名
            'overwrite_existing': False,   # 是否覆盖已有NFO
            'poster_dir': 'posters',      # 海报存储目录
            'video_extensions': ['.mp4', '.mkv', '.avi'],  # 支持的视频格式
            'course_types': [],  # 课程类型列表
            'check_nomedia': True,  # 是否检查 .nomedia 文件（开启后会忽略包含 .nomedia 的目录）
        }
        self.current_config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return {**self.default_config, **json.load(f)}
            except json.JSONDecodeError:
                print("配置文件格式错误，使用默认配置")
                return self.default_config.copy()
        return self.default_config.copy()
    
    def save_config(self) -> None:
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_config, f, indent=4, ensure_ascii=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        if default is not None:
            return self.current_config.get(key, default)
        return self.current_config.get(key, self.default_config.get(key))
    
    def set(self, key: str, value: Any) -> None:
        """设置配置项"""
        self.current_config[key] = value
        self.save_config()

# 创建全局配置实例
config = Config() 