# -*- coding: utf-8 -*-

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from utils import *
import pyautogui
import time
import easyocr
import keyboard


is_running = False
postion_t = [0, 0]
reader = easyocr.Reader(['ch_sim','en'], gpu=True)
range_lowest_price = [0.1042, 0.8638, 0.1222, 0.8833]
postion_max_shopping_number = [0.9085, 0.7222]
postion_buy_button = [0.8535, 0.7979]
ideal_price = 638

def _start_loop():
    global is_running
    global postion_t
    if not is_running:
        is_running = True
        # 记录鼠标位置
        t = pyautogui.position()
        postion_t = [t.x, t.y]
        print("开始循环，商品位置为：", postion_t)
        
def _stop_loop():
    global is_running
    if is_running:
        is_running = False
        print("停止循环")

def main():
    global is_running
    target_app = '三角洲行动'
    first_loop = True

    # 监听键盘事件
    keyboard.add_hotkey('f8', _start_loop)  # 按 F8 开始循环
    keyboard.add_hotkey('f9', _stop_loop)   # 按 F9 暂停循环
    
    print("按下 F8 开始循环，按下 F9 暂停循环")
    while True:
        if is_running:
            # # 全屏截图
            # _screenshot = get_screenshot()
            # print("识别中...")
            # # screenshot = cv.imread('screenshot.png')
            # result = reader.readtext(_screenshot)
            # print('商品识别结果:')
            # # 获取商品名字在截图中的offset
            # postion_t = [0, 0]
            # for item in result:
            #     if 'RIP' in item[1]:
            #         # 计算中心点的坐标
            #         postion_t[0] = (item[0][0][0] + item[0][2][0]) / 2
            #         postion_t[1] = (item[0][0][1] + item[0][2][1]) / 2
            #         print(item[1]+':',postion_t[0],postion_t[1])
            #         break
            
            # 进入商品详情页面
            if postion_t != [0,0]:
                pyautogui.moveTo(postion_t[0], postion_t[1])
                pyautogui.click()

            # 进行范围截图，截取最低价格
            time.sleep(0.1)
            _screenshot_lowest_price = get_windowshot(range_lowest_price, debug_mode=False)
            # 识别最低价格
            result = reader.readtext(_screenshot_lowest_price)
            try:
                lowest_price = int(result[0][1])
                print('当前最低价格：',lowest_price)
            except IndexError:
                print('识别失败')
                continue
            
            if lowest_price <= ideal_price:
                print('当前价格低于理想价格，开始购买')
                # 选择最大商品数量
                mouse_click(x = postion_max_shopping_number[0], y = postion_max_shopping_number[1], num = 3)
                time.sleep(0.1)
                # 下单
                mouse_click(x = postion_buy_button[0], y = postion_buy_button[1], num = 4)
                time.sleep(0.2)
            
            # 点击esc返回到商品列表界面
            pyautogui.press('esc')
            # 之后每次刷新使用第一次获取到的商品offset进行点击
        else:
            # 暂停时降低循环频率
            time.sleep(1)
        time.sleep(0.1)

if __name__ == "__main__":
    main()