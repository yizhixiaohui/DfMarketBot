# -*- coding: utf-8 -*-

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

if __name__ == '__main__':
    from utils import *
else:
    from backend.utils import *
import time
import easyocr
import numpy as np

class BuyBot:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=True)
        self.range_isconvertible_lowest_price = [2179/2560, 1078/1440, 2308/2560, 1102/1440]
        self.range_notconvertible_lowest_price = [2179/2560, 1156/1440, 2308/2560, 1178/1440]
        self.postion_isconvertible_max_shopping_number = [0.9085, 0.7222]
        self.postion_isconvertible_min_shopping_number = [0.7921, 0.7222]
        self.postion_notconvertiable_max_shopping_number = [2329/2560, 1112/1440]
        self.postion_notconvertiable_min_shopping_number = [2028/2560, 1112/1440]
        self.postion_isconvertible_buy_button = [2189/2560, 0.7979]
        self.postion_notconvertiable_buy_button = [2186/2560, 1225/1440]
        self.lowest_price = None
        print('初始化完成')
    
    def detect_price(self, is_convertible = False, debug_mode = False):
        try:
            if is_convertible:
                self._screenshot = get_windowshot(self.range_isconvertible_lowest_price, debug_mode=debug_mode)
            else:
                self._screenshot = get_windowshot(self.range_notconvertible_lowest_price, debug_mode=debug_mode)
            # 识别最低价格
            result = self.reader.readtext(np.array(self._screenshot))
            if debug_mode:
                print(result)
            self.lowest_price = int(result[-1][1].replace(',', ''))
            print('当前最低价格：',self.lowest_price)
        except:
            self.lowest_price = None
            print('识别失败, 建议检查物品是否可兑换')
        return self.lowest_price

    def buy(self, is_convertible = False):
        if is_convertible:
            mouse_click(self.postion_isconvertible_max_shopping_number)
            mouse_click(self.postion_isconvertible_buy_button)
        else:
            mouse_click(self.postion_notconvertiable_max_shopping_number)
            mouse_click(self.postion_notconvertiable_buy_button)
            
    def refresh(self, is_convertible = False):
        if is_convertible:
            mouse_click(self.postion_isconvertible_min_shopping_number)
            mouse_click(self.postion_isconvertible_buy_button)
        else:
            mouse_click(self.postion_notconvertiable_min_shopping_number)
            mouse_click(self.postion_notconvertiable_buy_button)

def main():
    bot = BuyBot()
    is_convertiable = False
    bot.detect_price(is_convertible=is_convertiable, debug_mode=True)

if __name__ == '__main__':
    main()