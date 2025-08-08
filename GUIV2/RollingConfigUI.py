# -*- coding: utf-8 -*-
"""
滚仓配置管理UI
用于管理滚仓模式下的配装选项配置
"""
import os
import sys

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox)

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.config_factory import get_config_manager


class RollingConfigUI(QMainWindow):
    """滚仓配置管理主界面"""

    def __init__(self):
        super().__init__()
        self.config_manager = get_config_manager()
        self.rolling_options = []
        self.init_ui()
        self.load_config()

    def init_ui(self):
        self.setWindowTitle("滚仓配置管理")
        self.setGeometry(100, 100, 600, 400)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # 标题
        title_label = QLabel("滚仓模式配装选项配置")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QtGui.QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        # 说明文字
        desc_label = QLabel("双击表格单元格可直接编辑数值，修改后点击保存配置生效")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(desc_label)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["选项", "购买价格", "最低价格", "购买数量"])

        # 设置表格样式
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.DoubleClicked)

        # 连接单元格修改事件
        self.table.cellChanged.connect(self.on_cell_changed)
        self._updating_table = False  # 用于防止递归调用

        main_layout.addWidget(self.table)

        # 按钮布局
        button_layout = QHBoxLayout()

        # 保存按钮
        self.save_btn = QPushButton("保存配置")
        self.save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_btn)

        # 重置按钮
        self.reset_btn = QPushButton("重置为默认")
        self.reset_btn.clicked.connect(self.reset_to_default)
        button_layout.addWidget(self.reset_btn)

        main_layout.addLayout(button_layout)

        # 状态栏
        self.statusBar().showMessage("就绪")

    def load_config(self):
        """加载配置"""
        try:
            config = self.config_manager.load_config()
            self.rolling_options = config.rolling_options.copy()
            self.refresh_table()
            self.statusBar().showMessage("配置加载成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载配置失败: {str(e)}")
            self.rolling_options = [
                {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980},
                {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980},
                {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980},
                {"buy_price": 1700, "min_buy_price": 700, "buy_count": 1740}
            ]
            self.refresh_table()

    def refresh_table(self):
        """刷新表格显示"""
        self._updating_table = True  # 标记正在更新表格
        try:
            self.table.setRowCount(len(self.rolling_options))

            for row, option in enumerate(self.rolling_options):
                # 选项名称
                item = QTableWidgetItem(f"配装 {row + 1}")
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 0, item)

                # 购买价格
                price_item = QTableWidgetItem(str(option["buy_price"]))
                price_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 1, price_item)

                # 最低价格
                min_price_item = QTableWidgetItem(str(option["min_buy_price"]))
                min_price_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 2, min_price_item)

                # 购买数量
                count_item = QTableWidgetItem(str(option["buy_count"]))
                count_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 3, count_item)
        finally:
            self._updating_table = False  # 更新完成

    def save_config(self):
        """保存配置"""
        try:
            self.config_manager.update_config({"rolling_options": self.rolling_options})
            QMessageBox.information(self, "成功", "配置已保存")
            self.statusBar().showMessage("配置保存成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败: {str(e)}")

    def on_cell_changed(self, row, column):
        """单元格内容修改后的处理"""
        if self._updating_table:  # 如果是程序更新表格，直接返回
            return

        if row < 0 or row >= len(self.rolling_options):
            return

        try:
            item = self.table.item(row, column)
            if item is None:
                return

            value = int(item.text())

            # 根据列更新对应的配置值
            if column == 1:  # 购买价格
                self.rolling_options[row]["buy_price"] = value
            elif column == 2:  # 最低价格
                self.rolling_options[row]["min_buy_price"] = value
            elif column == 3:  # 购买数量
                self.rolling_options[row]["buy_count"] = value

            self.statusBar().showMessage(f"已更新配装 {row + 1} 的配置")

        except ValueError:
            # 如果输入无效，恢复原来的值
            self._updating_table = True  # 防止递归
            try:
                self.refresh_table()
            finally:
                self._updating_table = False
            QMessageBox.warning(self, "警告", "请输入有效的数字")

    def reset_to_default(self):
        """重置为默认配置"""
        reply = QMessageBox.question(self, "确认", "确定要重置为默认配置吗？这将覆盖当前所有配置。")
        if reply == QMessageBox.Yes:
            self.rolling_options = [
                {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980},
                {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980},
                {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980},
                {"buy_price": 1700, "min_buy_price": 700, "buy_count": 1740}
            ]
            self.refresh_table()
            self.save_config()


def main():
    app = QApplication(sys.argv)
    window = RollingConfigUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
