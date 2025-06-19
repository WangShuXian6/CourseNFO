"""
海报处理模块
"""
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import shutil

class PosterManager:
    """海报管理器"""
    
    def __init__(self):
        self.mandarin_dir_name = "普通话Deepl"  # 普通话目录名称
        self.poster_name = "background.jpg"  # 海报文件名
        
    def save_poster(self, course_path: Path, image_path: Path) -> Optional[Path]:
        """保存课程海报
        
        Args:
            course_path: 课程目录路径
            image_path: 图片文件路径
            
        Returns:
            保存后的海报路径，失败返回None
        """
        try:
            # 确保是图片文件
            if not self._is_image_file(image_path):
                print(f"文件 {image_path} 不是有效的图片文件")
                return None
            
            # 获取普通话目录路径
            mandarin_dir = course_path / self.mandarin_dir_name
            if not mandarin_dir.exists() or not mandarin_dir.is_dir():
                print(f"目录 {mandarin_dir} 不存在或不是目录")
                return None
                
            # 生成目标路径
            target_path = mandarin_dir / self.poster_name
            
            # 处理图片
            with Image.open(image_path) as img:
                # 调整大小，保持宽高比
                img = self._resize_image(img)
                # 保存处理后的图片
                img.save(target_path, quality=95)
            
            return target_path
            
        except Exception as e:
            print(f"处理海报图片时出错: {e}")
            return None
    
    def copy_poster(self, source_path: Path, course_path: Path) -> Optional[Path]:
        """复制已有海报"""
        try:
            if not source_path.exists():
                return None
                
            # 获取普通话目录路径
            mandarin_dir = course_path / self.mandarin_dir_name
            if not mandarin_dir.exists() or not mandarin_dir.is_dir():
                return None
                
            target_path = mandarin_dir / self.poster_name
            shutil.copy2(source_path, target_path)
            return target_path
            
        except Exception as e:
            print(f"复制海报时出错: {e}")
            return None
    
    def delete_poster(self, course_path: Path) -> bool:
        """删除课程海报"""
        try:
            # 获取普通话目录路径
            mandarin_dir = course_path / self.mandarin_dir_name
            if not mandarin_dir.exists() or not mandarin_dir.is_dir():
                return False
                
            poster_path = mandarin_dir / self.poster_name
            if poster_path.exists():
                poster_path.unlink()
            return True
            
        except Exception as e:
            print(f"删除海报时出错: {e}")
            return False
    
    def get_poster_path(self, course_path: Path) -> Optional[Path]:
        """获取课程海报路径"""
        try:
            # 获取普通话目录路径
            mandarin_dir = course_path / self.mandarin_dir_name
            if not mandarin_dir.exists() or not mandarin_dir.is_dir():
                return None
                
            poster_path = mandarin_dir / self.poster_name
            return poster_path if poster_path.exists() else None
            
        except Exception as e:
            print(f"获取海报路径时出错: {e}")
            return None
    
    def _is_image_file(self, path: Path) -> bool:
        """检查是否为图片文件"""
        try:
            Image.open(path)
            return True
        except:
            return False
    
    def _resize_image(self, img: Image.Image, max_size: Tuple[int, int] = (800, 1200)) -> Image.Image:
        """调整图片大小，保持宽高比"""
        # 获取原始尺寸
        width, height = img.size
        
        # 计算缩放比例
        scale = min(max_size[0] / width, max_size[1] / height)
        
        # 如果图片小于最大尺寸，不进行缩放
        if scale >= 1:
            return img
            
        # 计算新尺寸
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # 调整大小
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS) 