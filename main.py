# -*- coding: utf-8 -*-

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from utils import *
import pyautogui
import time
import easyocr
import keyboard


is_running = False
reader = easyocr.Reader(['en'], gpu=True)
range_lowest_price = [0.8664, 0.7486, 0.8847, 0.7652]
postion_max_shopping_number = [0.9085, 0.7222]
postion_min_shopping_number = [0.7921, 0.7222]
postion_buy_button = [2189/2560, 0.7979]
ideal_price = 638

def _start_loop():
    global is_running
    if not is_running:
        is_running = True
        print("开始循环")
        
def _stop_loop():
    global is_running
    if is_running:
        is_running = False
        print("停止循环")

def main():
    global is_running

    # 监听键盘事件
    keyboard.add_hotkey('f8', _start_loop)  # 按 F8 开始循环
    keyboard.add_hotkey('f9', _stop_loop)   # 按 F9 暂停循环
    
    print("按下 F8 开始循环，按下 F9 暂停循环")
    while True:
        if is_running:
            try:
                # 价格识别部分
                _screenshot_lowest_price = get_windowshot(range_lowest_price, debug_mode=False)
                # 识别最低价格
                result = reader.readtext(_screenshot_lowest_price)
                lowest_price = int(result[0][1])
                # lowest_price = 658
                print('当前最低价格：',lowest_price)
                
                # 下单部分
                if lowest_price <= ideal_price:
                    print('当前价格：', lowest_price, '低于理想价格，开始购买')
                    # 选择最大商品数量
                    mouse_click(postion_max_shopping_number, num = 1)
                    time.sleep(0.4)
                    # 下单
                    mouse_click(postion_buy_button, num = 1)
                    time.sleep(0.2)
                    
                else:
                    print('当前价格：', lowest_price, '高于理想价格，刷新价格')
                    # 选择最小商品数量
                    mouse_click(postion_min_shopping_number, num = 1)
                    time.sleep(0.4)
                    # 下单
                    mouse_click(postion_buy_button, num = 1)
                    time.sleep(0.2)
            except IndexError:
                print('识别失败')
                continue
        else:
            # 暂停时降低循环频率
            time.sleep(1)
        time.sleep(0.4)

if __name__ == "__main__":
    main()