import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, Qt, QThread
from GUI.AppGUI import Ui_MainWindow
from backend.BuyBot import BuyBot
import keyboard

class KeyMonitor(QObject):
    key_pressed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        keyboard.on_press(self.handle_key)

    def handle_key(self, event):
        if event.name == 'f8':
            self.key_pressed.emit(0)
            print('开始循环')
        elif event.name == 'f9':
            self.key_pressed.emit(1)
            print('停止循环')

class Worker(QThread):
    update_signal = pyqtSignal(int)
    param_update = pyqtSignal(int)  # 新增参数更新信号

    def __init__(self, buybot):
        super().__init__()
        self.buybot = buybot
        self._is_running = False
        self.lock = QtCore.QMutex()
        self.ideal_price = 0
        self.unacceptable_price = 0
        self.is_convertible = True
        self.is_key_mode = False
        self.param_lock = QtCore.QMutex()  # 参数专用锁

    def run(self):
        while True:
            # 获取运行状态
            self.lock.lock()
            running = self._is_running
            self.lock.unlock()

            if running:
                try:
                    # 获取当前参数值
                    self.param_lock.lock()
                    current_ideal = self.ideal_price
                    current_unacceptable = self.unacceptable_price
                    self.param_lock.unlock()
                    
                    # 检测逻辑
                    lowest_price = self.buybot.detect_price(is_convertible=self.is_convertible, debug_mode=False)
                    self.update_signal.emit(lowest_price)

                    if lowest_price <= current_ideal:
                        print('当前价格：', lowest_price, '低于理想价格', current_ideal, '，开始购买')
                        self.buybot.buy(is_convertible=self.is_convertible)
                    else:
                        print('当前价格：', lowest_price, '高于理想价格', current_ideal, '，刷新价格')
                        self.buybot.refresh(is_convertible=self.is_convertible)
                except Exception as e:
                    print(f"操作失败: {str(e)}")
                self.msleep(100)
            else:
                self.msleep(100)

    def update_params(self, ideal, unacceptable, convertible, key_mode):
        """线程安全更新参数"""
        self.param_lock.lock()
        self.ideal_price = ideal
        self.unacceptable_price = unacceptable
        self.is_convertible = convertible
        self.is_key_mode = key_mode
        self.param_lock.unlock()
    def set_running(self, state):
        """线程安全更新运行状态"""
        self.lock.lock()
        self._is_running = state
        self.lock.unlock()

def runApp():
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    mainWindow = Ui_MainWindow()
    mainWindow.setupUi(window)

    # 初始化输入部分
    mainWindow.textEdit_ideal_price.setText('0')
    mainWindow.textEdit_unacceptable_price.setText('0')
    mainWindow.is_convertiable.setChecked(True)
    # 钥匙卡模式还没做出来，先禁用掉
    mainWindow.is_key_mode.setCheckable(False)
    mainWindow.is_key_mode.setChecked(False)

    # 创建监控线程
    key_monitor = KeyMonitor()
    worker = Worker(BuyBot())
    
    # 信号连接
    key_monitor.key_pressed.connect(lambda x: worker.set_running(x == 0))
    
    def handle_text_change():
        try:
            ideal = int(mainWindow.textEdit_ideal_price.toPlainText())
            unaccept = int(mainWindow.textEdit_unacceptable_price.toPlainText())
            is_convertible = mainWindow.is_convertiable.isChecked()
            is_key_mode = mainWindow.is_key_mode.isChecked()
            worker.update_params(ideal, unaccept, is_convertible, is_key_mode)
            mainWindow.label_lowest_price_value.setStyleSheet("color: black;")
        except ValueError:
            mainWindow.label_lowest_price_value.setStyleSheet("color: red;")

    # 确保两个输入框都连接
    mainWindow.textEdit_ideal_price.textChanged.connect(handle_text_change)
    mainWindow.textEdit_unacceptable_price.textChanged.connect(handle_text_change)
    mainWindow.is_convertiable.stateChanged.connect(handle_text_change)
    mainWindow.is_key_mode.stateChanged.connect(handle_text_change)

    window.show()
    worker.start()
    app.exec_()

def main():
    return runApp()

if __name__ == "__main__":
    print("正在初始化")
    sys.exit(main())