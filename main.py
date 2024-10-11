import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from file_manager_ui import FileManagerUI

def main():
    app = QApplication(sys.argv)
    
    # 设置应用图标
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'anymm-x2yaz-001.ico')
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    else:
        print(f"Icon file not found: {icon_path}")
    
    window = FileManagerUI()
    window.setWindowIcon(app.windowIcon())  # 确保主窗口也使用相同的图标
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()