"""
课程NFO管理器入口
"""
import sys
from pathlib import Path
from src.gui.main_window import MainWindow

def main():
    """程序入口"""
    # 创建并显示主窗口
    window = MainWindow()
    window.run()

if __name__ == "__main__":
    main()
