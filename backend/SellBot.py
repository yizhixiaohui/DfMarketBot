from PyQt5.QtCore import QThread, pyqtSignal
import time
from backend.utils import mouse_click, find_and_click_image, ocr_and_parse_slot_usage, check_and_set_price, get_windowshot
import pyautogui

class SellBot(QThread):
    log_signal = pyqtSignal(str)
    selling_started = pyqtSignal()
    selling_finished = pyqtSignal()

    def __init__(self, sell_time_minutes, sell_price):
        super().__init__()
        self.sell_time_seconds = sell_time_minutes * 60
        self.sell_price = sell_price
        self.is_running = False
        self.item_image_path = "image/9x19RIP.png" # Placeholder path

    def run(self):
        self.is_running = True
        self.log_signal.emit(f"自动售卖已启动，每 {self.sell_time_seconds / 60:.1f} 分钟执行一次。")
        while self.is_running:
            self.execute_sell_cycle()
            if not self.is_running:
                break
            self.log_signal.emit(f"等待下一次执行...")
            for _ in range(int(self.sell_time_seconds)):
                if not self.is_running:
                    break
                time.sleep(1)

    def start_selling(self):
        if not self.isRunning():
            self.is_running = True
            self.start()

    def stop_selling(self):
        if self.is_running:
            self.is_running = False
            self.log_signal.emit("正在停止自动售卖线程...")

    def test_sell_once(self):
        self.log_signal.emit("正在执行单次售卖测试... (GUI将短暂无响应)")
        self.execute_sell_cycle()
        self.log_signal.emit("测试结束。")

    def execute_sell_cycle(self):
         # 1. 发出“我要开工了”的信号，让主程序暂停购买机器人
         self.selling_started.emit()

         try:
             # 2. 自己负责准备工作：返回大厅，进入交易行
             self.log_signal.emit("步骤 1/9: 准备环境，返回大厅...")
             pyautogui.press('esc', presses=2, interval=0.2)
             time.sleep(2)

             self.log_signal.emit("步骤 2/9: 进入交易行...")
             mouse_click([710, 55])
             time.sleep(2)
             mouse_click([710, 55])
             time.sleep(2)

             self.log_signal.emit("步骤 3/9: 进入出售页面...")
             mouse_click([328, 108])
             time.sleep(2)

             # 3. 自己负责后续所有售卖业务
             self.log_signal.emit("步骤 4/9: 点击一键整理")
             mouse_click([1205, 952])
             time.sleep(1)
             mouse_click([1740, 960])
             time.sleep(2)

             self.log_signal.emit("步骤 5/9: 点击进入子弹箱")
             mouse_click([1207, 250])
             time.sleep(1)

             self.log_signal.emit(f"步骤 6/9: 寻找物品 '{self.item_image_path}'")
             if find_and_click_image(self.item_image_path, region=(1200, 250, 700, 700)):
                 self.log_signal.emit("  -> 已找到并点击物品。")
                 time.sleep(1)

                 self.log_signal.emit("步骤 7/9: 点击最大化按钮并调整数量...")
                 mouse_click([1453, 560])
                 time.sleep(1.0)

                 required, available = ocr_and_parse_slot_usage(region=(1440, 495, 120, 50))
                 if required is not None and available is not None and required > available:
                     slider_width = 1453 - 1170
                     ratio = available / required
                     target_x = 1170 + int(slider_width * ratio)
                     mouse_click([target_x, 560])
                     time.sleep(0.5)

                 self.log_signal.emit(f"步骤 8/9: 设定价格为 {self.sell_price}")
                 check_and_set_price(region=(1311, 642, 80, 30), expected_price=self.sell_price)
                 time.sleep(0.5)

                 self.log_signal.emit("步骤 9/9: 点击出售按钮")
                 mouse_click([1309, 750])
                 self.log_signal.emit("操作成功完成！")
             else:
                 self.log_signal.emit("[信息] 在子弹箱内未找到指定物品。")

         except Exception as e:
             self.log_signal.emit(f"[售卖错误] {e}")
         finally:
             # 4. 发出“我完工了”的信号，让主程序恢复购买机器人
             self.log_signal.emit("[协调] 售卖流程结束，正在恢复购买页面...")
             time.sleep(2)
             mouse_click([201,112])
             time.sleep(2)
             mouse_click([201,112])
             time.sleep(1)
             self.log_signal.emit("[协调] 页面已恢复。")
             self.selling_finished.emit()