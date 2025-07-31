import sys
import ctypes
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, Qt, QThread
from GUI.AppGUI import Ui_MainWindow
from backend.BuyBot import BuyBot
from backend.SellBot import SellBot
from backend.utils import *
import keyboard
import pyautogui

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

class KeyMonitor(QObject):
    key_pressed = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        keyboard.on_press(self.handle_key)

    def handle_key(self, event):
        if event.name == 'f8': self.key_pressed.emit(0)
        elif event.name == 'f9': self.key_pressed.emit(1)

# This Worker class is restored to the user's original, correct logic,
# with the only change being that `print` is replaced by `log_signal.emit`.
class Worker(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, buybot):
        super().__init__()
        self.buybot = buybot
        self._is_running = False
        self.lock = QtCore.QMutex()
        self.ideal_price = 0
        self.unacceptable_price = 0
        self.loop_gap = 150
        self.is_convertible = True
        self.is_key_mode = False
        self.is_half_coin_mode = False
        self.mouse_position = []
        self.param_lock = QtCore.QMutex()

    def record_mouse_position(self):
        with QtCore.QMutexLocker(self.param_lock):
            self.mouse_position = get_mouse_position()
        self.log_signal.emit(f"已记录购买鼠标位置: {self.mouse_position}")

    def run(self):
        first_loop = True
        buy_number = 0
        while True:
            self.lock.lock()
            running = self._is_running
            self.lock.unlock()
            if not running:
                self.msleep(100)
                continue

            try:
                with QtCore.QMutexLocker(self.param_lock):
                    current_ideal = self.ideal_price
                    current_unacceptable = self.unacceptable_price
                    current_convertible = self.is_convertible
                    current_key_mode = self.is_key_mode
                    current_half_coin_mode = self.is_half_coin_mode
                    current_mouse_pos = self.mouse_position

                if not current_mouse_pos:
                    self.log_signal.emit("[等待] 请将鼠标移动到物品上, 然后按F8启动")
                    self.set_running(False)
                    continue

                mouse_click(current_mouse_pos)
                time.sleep(0.9)

                if current_half_coin_mode and (not first_loop) and (buy_number != 0):
                    try:
                        previous_balance_half_coin = self.buybot.balance_half_coin
                        current_balance_half_coin = self.buybot.detect_balance_half_coin()
                        lowest_price = (previous_balance_half_coin - current_balance_half_coin)/buy_number
                        if lowest_price == 0:
                            lowest_price = self.buybot.detect_price(is_convertible=current_convertible, debug_mode=True)
                            self.log_signal.emit(f"上一次购买失败，直接看市场底价: {lowest_price}")
                        else:
                            self.log_signal.emit(f"哈夫币余额差值计算价格: {lowest_price}")
                    except:
                        lowest_price = self.buybot.detect_price(is_convertible=current_convertible, debug_mode=True)
                        self.log_signal.emit(f"余额计算出现异常，直接看市场底价: {lowest_price}")
                else:
                    lowest_price = self.buybot.detect_price(is_convertible=current_convertible, debug_mode=True)
                    self.log_signal.emit(f"直接看市场底价: {lowest_price}")
                
                if current_key_mode:
                    if lowest_price > current_ideal:
                        self.log_signal.emit(f'当前价格：{lowest_price}，高于理想价格 {current_ideal}，免费刷新价格')
                        self.buybot.freerefresh(good_postion=current_mouse_pos)
                    else:
                        self.log_signal.emit(f'当前价格：{lowest_price}，低于理想价格 {current_ideal}，购买一张后循环结束')
                        self.buybot.refresh(is_convertible=False)
                        self.set_running(False)
                else:
                    if lowest_price > current_unacceptable:
                        self.log_signal.emit(f'高于最高价格 {current_unacceptable}，免费刷新价格')
                        self.buybot.freerefresh(good_postion=current_mouse_pos)
                        buy_number = 0
                    elif lowest_price > current_ideal:
                        self.log_signal.emit(f'高于理想价格 {current_ideal}，刷新价格')
                        self.buybot.refresh(is_convertible=current_convertible)
                        buy_number = 31
                    else:
                        self.log_signal.emit(f'低于理想价格 {current_ideal}，开始购买')
                        self.buybot.buy(is_convertible=current_convertible)
                        buy_number = 200

                if first_loop:
                    first_loop = False

            except Exception as e:
                if str(e) == '识别失败':
                    get_screenshot(debug_mode=True)
                    self.log_signal.emit("识别失败, 建议检查物品是否可兑换")
                    self.msleep(self.loop_gap)
                    self.buybot.freerefresh(good_postion=current_mouse_pos)
                else:
                    self.log_signal.emit(f"[购买错误] {e}")
            
            self.msleep(self.loop_gap)

    def update_params(self, ideal, unacceptable, convertible, key_mode, half_coin_mode, loop_gap):
        with QtCore.QMutexLocker(self.param_lock):
            self.ideal_price = ideal
            self.unacceptable_price = unacceptable
            self.loop_gap = loop_gap
            self.is_convertible = convertible
            self.is_key_mode = key_mode
            self.is_half_coin_mode = half_coin_mode

    def set_running(self, state):
        with QtCore.QMutexLocker(self.lock):
            self._is_running = state

class MainApplication(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.init_ui_values()
        self.setup_workers()
        self.connect_signals()

    def init_ui_values(self):
        self.ui.textEdit_ideal_price.setText('338')
        self.ui.textEdit_unacceptable_price.setText('0')
        self.ui.textEdit_loop_gap.setText('150')
        self.ui.is_convertiable.setChecked(True)
        self.ui.textEdit_sell_time.setText('10')
        self.ui.textEdit_sell_price.setText('1000')

    def setup_workers(self):
        self.key_monitor = KeyMonitor()
        self.buy_bot_instance = BuyBot()
        self.buy_worker = Worker(self.buy_bot_instance)
        self.sell_bot = SellBot(10, 1000)
        
        self.buy_worker.log_signal.connect(self.ui.log_browser.append)
        self.sell_bot.log_signal.connect(self.ui.log_browser.append)

        self.handle_buy_text_change() # Sync initial params
        self.buy_worker.start()

    def connect_signals(self):
        self.key_monitor.key_pressed.connect(self.handle_key_event)
        self.ui.textEdit_ideal_price.textChanged.connect(self.handle_buy_text_change)
        self.ui.textEdit_unacceptable_price.textChanged.connect(self.handle_buy_text_change)
        self.ui.textEdit_loop_gap.textChanged.connect(self.handle_buy_text_change)
        self.ui.is_convertiable.stateChanged.connect(self.handle_buy_text_change)
        self.ui.is_key_mode.stateChanged.connect(self.handle_buy_text_change)
        self.ui.is_half_coin_mode.stateChanged.connect(self.handle_buy_text_change)
        self.ui.button_start_selling.clicked.connect(self.start_selling_process)
        self.ui.button_stop_selling.clicked.connect(self.sell_bot.stop_selling)
        self.ui.button_test_sell.clicked.connect(self.test_selling_process)
        self.sell_bot.selling_started.connect(self.handle_selling_started)
        self.sell_bot.selling_finished.connect(self.handle_selling_finished)

    def handle_key_event(self, key_code):
        if key_code == 0 and not self.buy_worker._is_running:
            self.buy_worker.record_mouse_position()
        self.buy_worker.set_running(key_code == 0)
        status = "启动" if key_code == 0 else "停止"
        self.ui.log_browser.append(f"购买循环已{status}。")

    def handle_buy_text_change(self):
        try:
            ideal = int(self.ui.get_plain_number(self.ui.textEdit_ideal_price))
            unaccept = int(self.ui.get_plain_number(self.ui.textEdit_unacceptable_price))
            loop_gap = int(self.ui.textEdit_loop_gap.toPlainText())
            is_convertible = self.ui.is_convertiable.isChecked()
            is_key_mode = self.ui.is_key_mode.isChecked()
            is_half_coin_mode = self.ui.is_half_coin_mode.isChecked()
            self.buy_worker.update_params(ideal, unaccept, is_convertible, is_key_mode, is_half_coin_mode, loop_gap)
        except ValueError:
            pass

    def start_selling_process(self):
        self.ui.log_browser.append("10秒后开始自动售卖...")
        for i in range(10, 0, -1):
            self.ui.log_browser.append(f"{i}...")
            QtWidgets.QApplication.processEvents()
            time.sleep(1)
        try:
            # Correctly update the single instance, do not create a new one.
            self.sell_bot.sell_time_seconds = int(self.ui.textEdit_sell_time.toPlainText()) * 60
            self.sell_bot.sell_price = int(self.ui.get_plain_number(self.ui.textEdit_sell_price))
            self.sell_bot.start_selling()
        except ValueError:
            self.ui.log_browser.append("[错误] 请确保售卖时间和价格是有效的数字。")

    def test_selling_process(self):
        self.ui.log_browser.append("10秒后开始测试单次售卖...")
        for i in range(10, 0, -1):
            self.ui.log_browser.append(f"{i}...")
            QtWidgets.QApplication.processEvents()
            time.sleep(1)
        try:
            sell_price = int(self.ui.get_plain_number(self.ui.textEdit_sell_price))
            self.sell_bot.sell_price = sell_price
            self.sell_bot.test_sell_once()
        except ValueError:
            self.ui.log_browser.append("[错误] 请确保售卖价格是有效的数字。")

    def handle_selling_started(self):
        self.ui.log_browser.append("[协调] 售卖流程开始，暂停购买流程...")
        self.buy_worker.set_running(False)

    def handle_selling_finished(self):
        self.ui.log_browser.append("[协调] 售卖流程结束，5秒后恢复购买流程...")
        self.buy_worker.set_running(True)


    def closeEvent(self, event):
        self.ui.log_browser.append("正在关闭应用程序，请稍候...")
        self.buy_worker.set_running(False)
        self.sell_bot.stop_selling()
        self.ui.log_browser.append("等待购买线程停止...")
        self.buy_worker.wait(3000)
        self.ui.log_browser.append("等待售卖线程停止...")
        self.sell_bot.wait(3000)
        self.ui.log_browser.append("所有线程已停止，程序退出。")
        event.accept()

def main():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return
    print("正在初始化...")
    app = QtWidgets.QApplication(sys.argv)
    main_win = MainApplication()
    main_win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()