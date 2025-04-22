# -*- coding: utf-8 -*-

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from backend.utils import *
import time
import easyocr
import numpy as np

class BuyBot:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=True)
        self.range_lowest_price = [0.8664, 0.7486, 0.8847, 0.7652]
        self.postion_max_shopping_number = [0.9085, 0.7222]
        self.postion_min_shopping_number = [0.7921, 0.7222]
        self.postion_buy_button = [2189/2560, 0.7979]
        self.lowest_price = None
        print('初始化完成')
    
    def detect_price(self):
        try:
            self._screenshot = get_windowshot(self.range_lowest_price, debug_mode=False)
            # 识别最低价格
            result = self.reader.readtext(np.array(self._screenshot))
            self.lowest_price = int(result[0][1])
            print('当前最低价格：',self.lowest_price)
        except:
            self.lowest_price = None
            print('识别失败')
        return self.lowest_price

    def buy(self):
        # 选择最大商品数量
        mouse_click(self.postion_max_shopping_number)
        # 下单
        mouse_click(self.postion_buy_button)
            
    def refresh(self):
        # 选择最小商品数量
        mouse_click(self.postion_min_shopping_number)
        # 下单
        mouse_click(self.postion_buy_button)
