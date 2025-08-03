import ctypes
import sys

import keyboard
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QThread

from GUI.AppGUI import Ui_MainWindow
from backend.BuyBot import BuyBot
from backend.utils import *

pyautogui.PAUSE = 0.04


def is_admin():
    """
    检查当前是否以管理员权限运行
    """
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
        # 0: 交易页面购买，屯仓模式， 1: 配装页面购买，滚仓模式
        self.mode = 1
        self.buybot = buybot
        self._is_running = False
        self.lock = QtCore.QMutex()
        self.ideal_price = 0
        self.unacceptable_price = 0
        self.loop_gap = 0
        # 物品可兑换
        self.is_convertible = True
        # 钥匙卡模式
        self.is_key_mode = False
        # 使用哈夫币计算余额
        self.is_half_coin_mode = False
        self.mouse_position = []
        self.mouse_position_lock = QtCore.QMutex()
        self.param_lock = QtCore.QMutex()  # 参数专用锁

    def record_mouse_position(self):
        """记录鼠标位置"""
        self.mouse_position_lock.lock()
        self.mouse_position = get_mouse_position()
        self.mouse_position_lock.unlock()

    def run(self):
        first_loop = True
        buy_number = 0
        while True:
            # 获取运行状态
            self.lock.lock()
            running = self._is_running
            self.lock.unlock()
            if running:
                try:
                    if self.mode == 0:
                        t = time.time()
                        buy_number = self.mode_0(first_loop, buy_number)
                        print('cost', time.time() - t)
                    if self.mode == 1:
                        self.mode_1()
                    # 标记为非第一次循环
                    if first_loop:
                        first_loop = False
                except Exception as e:
                    if str(e) == '识别失败':  # 识别失败, 建议检查物品是否可兑换
                        self.msleep(self.loop_gap)
                        self.buybot.freerefresh(good_postion=self.mouse_position)
                    else:
                        print(f"操作失败: {str(e)}")
                self.msleep(self.loop_gap)
            else:
                self.msleep(100)
                # 标记为第一次循环
                if first_loop == False:
                    first_loop = True
                    buy_number = 0

    def update_params(self, ideal, unacceptable, convertible, key_mode, half_coin_mode, loop_gap):
        """线程安全更新参数"""
        self.param_lock.lock()
        self.ideal_price = ideal
        self.unacceptable_price = unacceptable
        self.loop_gap = loop_gap
        self.is_convertible = convertible
        self.is_key_mode = key_mode
        self.is_half_coin_mode = half_coin_mode
        self.param_lock.unlock()

    def set_running(self, state):
        """线程安全更新运行状态"""
        self.lock.lock()
        self._is_running = state
        self.lock.unlock()

    def mode_0(self, first_loop, buy_number):
        # 获取当前参数值
        self.param_lock.lock()
        current_ideal = self.ideal_price
        current_unacceptable = self.unacceptable_price
        current_convertible = self.is_convertible
        current_key_mode = self.is_key_mode
        current_half_coin_mode = self.is_half_coin_mode
        self.param_lock.unlock()

        # 进入商品页面
        t = time.time()
        mouse_click(self.mouse_position, num=1)
        print('mouse click cost', time.time() - t)

        # 获取商品价格
        if current_half_coin_mode and (not first_loop) and (buy_number != 0):
            # 使用哈夫币余额差值计算价格
            try:
                previous_balance_half_coin = self.buybot.balance_half_coin
                current_balance_half_coin = self.buybot.detect_balance_half_coin()
                lowest_price = (previous_balance_half_coin - current_balance_half_coin) / buy_number
                if lowest_price == 0:
                    # 直接看市场底价
                    lowest_price = self.buybot.detect_price(is_convertible=current_convertible, debug_mode=False)
                    print("上一次购买失败，直接看市场底价:", lowest_price, end=" ")
                else:
                    print("哈夫币余额差值计算价格:", lowest_price, end=" ")
            except:
                # 直接看市场底价
                lowest_price = self.buybot.detect_price(is_convertible=current_convertible, debug_mode=False)
                print("余额计算出现异常，直接看市场底价:", lowest_price, end=" ")
        else:
            # 直接看市场底价
            lowest_price = self.buybot.detect_price(is_convertible=current_convertible, debug_mode=False)
            print("直接看市场底价:", lowest_price, end=" ")

        if current_key_mode:
            # 钥匙卡模式
            if lowest_price > current_ideal:
                print('当前价格：', lowest_price, '高于理想价格', current_ideal, ' 免费刷新价格')
                self.buybot.freerefresh(good_postion=self.mouse_position)
            else:
                print('当前价格：', lowest_price, '低于理想价格', current_ideal, ' 购买一张后循环结束')
                self.buybot.refresh(is_convertible=False)
                self.set_running(False)
                print('停止循环')
        else:
            # 正常模式
            if lowest_price > current_unacceptable:
                print('高于最高价格', current_unacceptable, ' 免费刷新价格')
                self.buybot.freerefresh(good_postion=self.mouse_position)
                buy_number = 0
            elif lowest_price > current_ideal:
                print('高于理想价格', current_ideal, ' 刷新价格')
                self.buybot.refresh(is_convertible=current_convertible)
                buy_number = 31  # 原始值为 购买子弹价格/1 ，修改为 购买子弹价格/31
            else:
                print('低于理想价格', current_ideal, ' 开始购买')
                self.buybot.buy(is_convertible=current_convertible)
                buy_number = 200
        return buy_number

    def mode_1(self, option=0):
        options = [
            {
                "buy_price": 520,  # 9x19
                "min_buy_price": 300,
                "buy_count": 4980
            },
            {
                "buy_price": 450,  # 5.7x28
                "min_buy_price": 270,
                "buy_count": 4980
            }
        ]
        buy_price, min_buy_price, buy_count = (options[option]["buy_price"], options[option]["min_buy_price"],
                                               options[option]["buy_count"])
        target_price = buy_price * buy_count
        min_price = min_buy_price * buy_count
        print(f'单价: {buy_price}, 数量: {buy_count}, 总价: {target_price}, 最低价: {min_price}')
        pyautogui.press('l')
        self.msleep(50)
        t = time.time()
        self.buybot.switch_to_option(option)
        print(f't1 cost {int((time.time() - t) * 1000)}ms')
        # 避免数字还没切过来就检测了，导致检测到上次配装的价格
        self.msleep(100)
        print(f't1.5 cost {int((time.time() - t) * 1000)}ms')
        price = self.buybot.detect_option_price()
        print(f't2 cost {int((time.time() - t) * 1000)}ms')
        if min_price < int(price) <= target_price:
            self.buybot.option_buy()
            # TODO 检测购买是否成功
            self.msleep(3000)
            if self.buybot.detect_option_buy_failed():
                pyautogui.press('esc')
                self.msleep(100)
            else:
                self._is_running = False
                print('购买完毕，手动检查购买是否成功')
        else:
            self.buybot.option_refresh()
        print(f'cost {int((time.time() - t) * 1000)}ms')


def runApp():
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    mainWindow = Ui_MainWindow()
    mainWindow.setupUi(window)

    # 初始化输入部分
    mainWindow.textEdit_ideal_price.setText('0')
    mainWindow.textEdit_unacceptable_price.setText('0')
    mainWindow.textEdit_loop_gap.setText('50')
    mainWindow.is_convertiable.setChecked(True)
    mainWindow.is_key_mode.setChecked(False)
    mainWindow.is_half_coin_mode.setChecked(False)

    # 创建监控线程
    key_monitor = KeyMonitor()
    worker = Worker(BuyBot())

    # 信号连接
    def handle_key_event(x):
        if x == 0:
            worker.record_mouse_position()
        worker.set_running(x == 0)

    key_monitor.key_pressed.connect(handle_key_event)

    def handle_text_change():
        ideal = int(mainWindow.get_plain_number(mainWindow.textEdit_ideal_price))
        unaccept = int(mainWindow.get_plain_number(mainWindow.textEdit_unacceptable_price))
        loop_gap = int(mainWindow.textEdit_loop_gap.toPlainText())
        is_convertible = mainWindow.is_convertiable.isChecked()
        is_key_mode = mainWindow.is_key_mode.isChecked()
        is_half_coin_mode = mainWindow.is_half_coin_mode.isChecked()
        worker.update_params(ideal, unaccept, is_convertible, is_key_mode, is_half_coin_mode, loop_gap)

    # 确保两个输入框都连接
    mainWindow.textEdit_ideal_price.textChanged.connect(handle_text_change)
    mainWindow.textEdit_unacceptable_price.textChanged.connect(handle_text_change)
    mainWindow.textEdit_loop_gap.textChanged.connect(handle_text_change)
    mainWindow.is_convertiable.stateChanged.connect(handle_text_change)
    mainWindow.is_key_mode.stateChanged.connect(handle_text_change)
    mainWindow.is_half_coin_mode.stateChanged.connect(handle_text_change)

    window.show()
    worker.start()
    app.exec_()


def main():
    return runApp()


if __name__ == "__main__":
    if not is_admin():
        # 尝试重新以管理员身份启动
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)
    print("正在初始化")
    sys.exit(main())
