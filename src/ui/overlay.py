from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication


class TransparentOverlay(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setGeometry(100, 100, 300, 50)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 180);
            color: white;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
        """)
        self.label.setGeometry(0, 0, self.width(), self.height())
        self.label.setText("测试")
        self.label.setWordWrap(True)

        self.oldPos = None

    def update_text(self, text: str):
        self.label.setText(text)
        self.label.adjustSize()
        self.resize(self.label.width(), self.label.height())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.oldPos and event.buttons() == Qt.LeftButton:
            delta = event.globalPos() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = None


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    overlay = TransparentOverlay()
    overlay.show()

    sys.exit(app.exec_())
