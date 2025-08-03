# -*- coding: utf-8 -*-
import numpy as np
import pyautogui
screen_size = pyautogui.size()

def is_windowized(window_title:str):
    '''
    判断目标是否窗口化
    '''
    # 获取当前所有窗口的标题
    window_titles = [window.title for window in pyautogui.getAllWindows()]
    
    # 检查是否存在deltaforce窗口
    if window_title in window_titles:
        return True
    else:
        return False

def get_window_postion(target_app:str):
    '''
    获取目标窗口的坐标
    '''
    window_info = pyautogui.getWindowsWithTitle(target_app)[0]
    return [window_info.left, window_info.top, window_info.right, window_info.bottom]

def get_screenshot(debug_mode = False):
    '''
    全屏截图函数
    '''
    # 对整个屏幕进行截图
    screenshot = pyautogui.screenshot()
    if debug_mode:
        screenshot.save('screenshot.png')
    return screenshot

def get_windowshot(range:list, debug_mode = False):
    '''
    范围截图函数

    range：截图范围，[left, top, right, bottom]
    '''
    # 对范围内截图
    if range[0] < 1:
        range = [int(screen_size.width * range[0]),
                 int(screen_size.height * range[1]), 
                 int(screen_size.width * range[2]), 
                 int(screen_size.height * range[3])]
    screenshot = pyautogui.screenshot(region=(range[0], range[1], range[2]-range[0], range[3]-range[1]))
    if debug_mode:
        screenshot.save('screenshot.png')
    return screenshot

def mouse_move(positon:list):
    '''
    postion：鼠标移动位置，[x, y]
    '''
    x = positon[0]
    y = positon[1]
    if x < 1:
        x = int(screen_size.width * x)
        y = int(screen_size.height * y)
    pyautogui.moveTo(x, y)

def mouse_click(positon:list, num:int = 1):
    '''
    postion：鼠标点击位置，[x, y]

    num：点击次数，默认点击一次
    '''
    x = positon[0]
    y = positon[1]
    if x < 1:
        x = int(screen_size.width * x)
        y = int(screen_size.height * y)
    for i in range(num):
        pyautogui.moveTo(x, y)
        pyautogui.click(x, y)

def get_mouse_position():
    '''
    获取鼠标当前位置
    '''
    return list(pyautogui.position())

def main():
    mouse_move([2218/2560, 72/1440])

if __name__ == "__main__":
    # main()
    import pyocr
    import re
    import time
    img = get_windowshot([2128, 1133, 2413, 1191])
    # img = get_windowshot([2098, 356, 2361, 389])
    # img = get_windowshot([2179, 1078, 2308, 1102])
    # img = get_windowshot([2161, 49, 2295, 87])
    # res = pytesseract.image_to_string(img)
    # print(res)
    tools = pyocr.get_available_tools()
    tool = tools[0]
    # ocr = cnocr.CnOcr()
    # res = ocr.ocr(img)
    t = time.time()
    res = tool.image_to_string(img)
    print(res, time.time() - t)