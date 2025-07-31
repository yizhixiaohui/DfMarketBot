# -*- coding: utf-8 -*-

import pyautogui
import time
import cv2
import numpy as np
import easyocr
import re
from PIL import ImageGrab

# --- Original Functions ---

def is_windowized(window_title:str):
    '''
    判断目标是否窗口化
    '''
    window_titles = [window.title for window in pyautogui.getAllWindows()]
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
    screenshot = pyautogui.screenshot()
    if debug_mode:
        screenshot.save('screenshot.png')
    return screenshot

def get_windowshot(range:list, debug_mode = False):
    '''
    范围截图函数

    range：截图范围，[left, top, right, bottom]
    '''
    if range[0] < 1:
        screen_size = pyautogui.size()
        range = [int(screen_size.width * range[0]), 
                 int(screen_size.height * range[1]), 
                 int(screen_size.width * range[2]), 
                 int(screen_size.height * range[3])]
    screenshot = pyautogui.screenshot(region=(range[0], range[1], range[2]-range[0], range[3]-range[1]))
    if debug_mode:
        screenshot.save('debug_screenshot_buy.png')
    return screenshot

def mouse_move(positon:list):
    '''
    postion：鼠标移动位置，[x, y]
    '''
    x = positon[0]
    y = positon[1]
    if x < 1:
        screen_size = pyautogui.size()
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
        screen_size = pyautogui.size()
        x = int(screen_size.width * x)
        y = int(screen_size.height * y)
    for i in range(num):
        pyautogui.moveTo(x, y)
        pyautogui.click()

def get_mouse_position():
    '''
    获取鼠标当前位置
    '''
    return list(pyautogui.position())

# --- New and Upgraded Functions ---

# This single reader is now used by all OCR functions
ocr_reader = easyocr.Reader(['en', 'ch_sim'], gpu=True)

def ocr_number_from_image(img):
    """The master function to reliably read a number from any given image object."""
    try:
        result = ocr_reader.readtext(np.array(img))
        if result:
            text = result[0][1]
            # Clean up the text to get only digits
            cleaned_text = re.sub(r'[^0-9]', '', text)
            if cleaned_text:
                return int(cleaned_text)
        return None
    except Exception as e:
        print(f"[OCR Master] Error: {e}")
        return None

def find_and_click_image(image_path, confidence=0.8, region=None):
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence, region=region)
        if location:
            pyautogui.click(location)
            return True
        return False
    except Exception as e:
        print(f"[SellBot] Error finding image: {e}")
        return False

def ocr_and_parse_slot_usage(region):
    try:
        screenshot = pyautogui.screenshot(region=region)
        screenshot.save('ocr_debug_slot.png')
        result = ocr_reader.readtext(np.array(screenshot))
        if result:
            text = result[0][1]
            match = re.search(r'(\d+)/(\d+)', text)
            if match:
                return int(match.group(1)), int(match.group(2))
        return None, None
    except Exception as e:
        print(f"[SellBot] Slot OCR Error: {e}")
        return None, None

def check_and_set_price(region, expected_price):
    # This function now uses the master OCR function via a wrapper
    def ocr_price_wrapper(r):
        img = pyautogui.screenshot(region=r)
        return ocr_number_from_image(img)

    current_price = ocr_price_wrapper(region)
    if current_price != expected_price:
        pyautogui.click(region[0] + 20, region[1] + 10)
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.2)
        pyautogui.typewrite(str(expected_price))