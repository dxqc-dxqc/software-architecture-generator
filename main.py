# main.py
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from ui.main_window import ArchitectureBuilder

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 强制注入无衬线微软雅黑，贯彻高大上企业界面视觉
    app.setFont(QFont("Microsoft YaHei", 10))

    # 拉起高度解耦的主业务视窗
    window = ArchitectureBuilder()
    window.show()

    sys.argv.append('--style=fusion')
    sys.exit(app.exec())