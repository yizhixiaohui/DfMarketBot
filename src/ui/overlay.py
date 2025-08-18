from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow

try:
    from src.core.event_bus import event_bus
except ImportError:
    from ..core.event_bus import event_bus


class TransparentOverlay(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.old_pos = None
        self.label = None
        self._pending_text = None
        self.init_ui()
        self._connect_events()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        screen = QGuiApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2 - 150
        self.setGeometry(x, 5, 300, 50)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            """
            background-color: rgba(0, 0, 0, 180);
            color: white;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
        """
        )
        self.label.setGeometry(0, 0, self.width(), self.height())
        self.label.setText("准备就绪")
        self.label.setWordWrap(True)

        self.old_pos = None

    def _connect_events(self):
        """连接事件总线信号"""
        event_bus.overlay_text_updated.connect(self._on_overlay_text_updated)

    def _on_overlay_text_updated(self, text: str):
        """处理文本更新事件"""
        self._pending_text = text
        QTimer.singleShot(0, self._process_pending_text)

    def update_text(self, text: str):
        """兼容旧接口的方法, 计划废弃"""
        event_bus.emit_overlay_text_updated(text)

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
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos and event.buttons() == Qt.LeftButton:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    overlay = TransparentOverlay()
    overlay.show()

    sys.exit(app.exec_())
