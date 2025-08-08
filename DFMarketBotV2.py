#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DFMarketBotV2 - 重构后的主程序入口
基于新的分层架构，保持与现有UI的兼容性
"""
import sys
import os
import signal
import ctypes
import keyboard
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from GUIV2.AppGUI import Ui_MainWindow
from GUIV2.RollingConfigUI import RollingConfigUI
from src.ui.adapter import UIAdapter


def is_admin():
    """
    检查当前是否以管理员权限运行
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # 初始化UI适配器
        self.ui_adapter = UIAdapter(self.ui)
        
        # 设置窗口属性
        self.setWindowTitle("V2")
        self.setFixedSize(self.size())
        
        # 添加滚仓配置按钮
        self._add_rolling_config_button()
        
        # 设置热键
        self._setup_hotkeys()
        
        # 设置定时器用于状态检查
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._check_status)
        self.status_timer.start(1000)  # 每秒检查一次
        
    def _setup_hotkeys(self):
        """设置全局热键"""
        import platform
        
        # 在Windows上使用keyboard库，macOS上跳过
        if platform.system() == "Windows":
            try:
                # F8 - 开始
                keyboard.add_hotkey('f8', self._start_trading)
                
                # F9 - 停止
                keyboard.add_hotkey('f9', self._stop_trading)
                print("全局热键已设置 (F8开始, F9停止)")
            except Exception as e:
                print(f"设置全局热键失败: {e}")
        else:
            print("非Windows系统，跳过全局热键设置")
            # 使用按钮点击代替热键
            if hasattr(self.ui, 'pushButton_start'):
                self.ui.pushButton_start.clicked.connect(self._start_trading)
            if hasattr(self.ui, 'pushButton_stop'):
                self.ui.pushButton_stop.clicked.connect(self._stop_trading)
        
    def _start_trading(self):
        """开始交易"""
        try:
            self.ui_adapter.start_trading()
            if hasattr(self.ui, 'label_status'):
                self.ui.label_status.setText("状态: 运行中 (F8)")
        except Exception as e:
            if hasattr(self.ui, 'label_status'):
                self.ui.label_status.setText(f"状态: 启动失败 - {e}")
    
    def _stop_trading(self):
        """停止交易"""
        try:
            self.ui_adapter.stop_trading()
            if hasattr(self.ui, 'label_status'):
                self.ui.label_status.setText("状态: 已停止 (F9)")
        except Exception as e:
            if hasattr(self.ui, 'label_status'):
                self.ui.label_status.setText(f"状态: 停止失败 - {e}")
    
    def _check_status(self):
        """检查状态"""
        # 这里可以添加状态检查逻辑
        pass
    
    def _add_rolling_config_button(self):
        """添加滚仓配置按钮"""
        from PyQt5.QtWidgets import QPushButton
        
        # 创建滚仓配置按钮
        self.rolling_config_btn = QPushButton("滚仓配置", self)
        self.rolling_config_btn.setGeometry(240, 160, 191, 31)
        
        # 设置按钮样式
        font = self.rolling_config_btn.font()
        font.setFamily("微软雅黑")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.rolling_config_btn.setFont(font)
        
        # 连接点击事件
        self.rolling_config_btn.clicked.connect(self._open_rolling_config)
    
    def _open_rolling_config(self):
        """打开滚仓配置界面"""
        try:
            self.rolling_config_window = RollingConfigUI()
            self.rolling_config_window.show()
        except Exception as e:
            print(f"打开滚仓配置界面失败: {e}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            # 停止交易
            self.ui_adapter.cleanup()
            
            # 清理热键
            keyboard.unhook_all_hotkeys()
            
            event.accept()
        except Exception as e:
            print(f"关闭窗口时出错: {e}")
            event.accept()


def signal_handler(signum, frame):
    """信号处理函数"""
    print("\n收到退出信号，正在清理...")
    QApplication.quit()


def main():
    """主函数"""
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")


if __name__ == '__main__':
    if not is_admin():
        # 尝试重新以管理员身份启动
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)
    sys.exit(main())
