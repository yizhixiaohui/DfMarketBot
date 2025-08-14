from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication


class TransparentOverlay(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pending_text = None
        self.initUI()

    def initUI(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        screen = QGuiApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2 - 150
        self.setGeometry(x, 5, 300, 50)

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

        QTimer.singleShot(0, self._process_pending_text)

    def update_text(self, text: str):
        self._pending_text = text
        QTimer.singleShot(0, self._process_pending_text)

    def _process_pending_text(self):
        """实际处理文本更新"""
        if self._pending_text is None or not self.isVisible():
            return

        try:
            self.label.setText(self._pending_text)
            self.label.adjustSize()
            self.label.setMinimumWidth(350)
            new_width = max(350, self.label.width())  # 设置最小宽度
            new_height = max(50, self.label.height())  # 设置最小高度
            self.resize(new_width, new_height)
        finally:
            self._pending_text = None

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
