# -*- coding: utf-8 -*-
import time

import cv2
import numpy as np

if __name__ == '__main__':
    from utils import *
    from ocr import Reader
else:
    from backend.utils import *
    from backend.ocr import Reader
import re

class BuyBot:
    def __init__(self):
        self.option_price = 0
        self._screenshot = None
        self.reader = Reader()
        self.range_isconvertible_lowest_price = [2179/2560, 1078/1440, 2308/2560, 1102/1440]
        self.range_notconvertible_lowest_price = [2179/2560, 1156/1440, 2308/2560, 1178/1440]
        self.postion_isconvertible_max_shopping_number = [0.9085, 0.7222]
        self.postion_isconvertible_min_shopping_number = [0.8095, 0.7222]  #"将Buybot.py中的"self.postion_isconvertible_min_shopping_number"临时改为[0.8095, 0.7222], 该值原本为[0.7921, 0.7222]"
        self.postion_notconvertiable_max_shopping_number = [2329/2560, 1112/1440]
        self.postion_notconvertiable_min_shopping_number = [2059/2560, 1112/1440] #"将Buybot.py中的"self.postion_notconvertiable_min_shopping_number"临时改为[2059/2560, 1112/1440], 该值原本为[2028/2560, 1112/1440]"
        self.postion_isconvertible_buy_button = [2189/2560, 0.7979]
        self.postion_notconvertiable_buy_button = [2186/2560, 1225/1440]
        self.postion_balance = [2200/2560, 70/1440]
        self.postion_balance_half_coin = [1912/2560, 363/1440, 2324/2560, 387/1440]

        # ------------- 滚仓模式 --------------
        self.postion_mode_1_option_1 = [244/2560, 404/1440]
        self.postion_mode_1_option_2 = [244/2560, 500/1440]
        self.postion_mode_1_option_3 = [244/2560, 591/1440]
        self.postion_mode_1_option_4 = [244/2560, 690/1440]
        self.postion_mode_1_price = [2128/2560, 1133/1440, 2413/2560, 1191/1440]
        self.postion_mode_1_buy = [2245/2560, 1165/1440]
        self.position_option_buy_failed = [418 / 2560, 280 / 1440, 867 / 2560, 387 / 1440]

        self.lowest_price = None
        self.balance_half_coin = None
        self.debug = True
        if self.debug:
            print('初始化完成')

    def identify_number(self, img, debug_mode = False):
        try:
            text = self.reader.image_to_string(img)
            text = re.sub(r'[^0-9]', '', text)
        except Exception as e:
            if self.debug or debug_mode:
                print(e)
            text = None
        if self.debug or debug_mode:
            print(f"identify number: {text}")
        return int(text) if text else None

    def detect_price(self, is_convertible, debug_mode = False):
        for i in range(50):
            if is_convertible:
                self._screenshot = get_windowshot(self.range_isconvertible_lowest_price, debug_mode=self.debug or debug_mode)
            else:
                self._screenshot = get_windowshot(self.range_notconvertible_lowest_price, debug_mode=self.debug or debug_mode)
                # 识别最低价格
            self.lowest_price = self.identify_number(self._screenshot)
            if self.lowest_price is not None:
                return self.lowest_price
            time.sleep(0.02)

        if self.lowest_price is None:
            print('识别失败, 建议检查物品是否可兑换')
            raise Exception('识别失败')
        return int(self.lowest_price)

    def detect_balance_half_coin(self, debug_mode = False):
        # 先把鼠标移到余额位置
        mouse_move(self.postion_balance)
        # 对哈夫币余额范围进行截图然后识别
        for i in range(50):
            self._screenshot = get_windowshot(self.postion_balance_half_coin, debug_mode=self.debug or debug_mode)
            self.balance_half_coin = self.identify_number(self._screenshot)
            if self.balance_half_coin is not None:
                # if self.debug or debug_mode:
                #     self._screenshot.save(f"debug/{self.balance_half_coin}.png")
                return self.balance_half_coin
            time.sleep(0.02)

        if self.balance_half_coin is None:
            print('哈夫币余额检测识别失败或不稳定，建议关闭余额识别相关功能')
        return self.balance_half_coin

    def detect_option_buy_failed(self, debug_mode=False):
        self._screenshot = get_windowshot(self.position_option_buy_failed)
        res = self.reader.detect_template(self._screenshot)
        if self.debug or debug_mode:
            print('检测购买失败结果:', res)
        return res

    def get_half_coin_diff(self):
        """
        获取右上角哈夫币具体金额
        :return:
        """
        previous_balance_half_coin = self.balance_half_coin
        self.detect_balance_half_coin()
        return self.balance_half_coin - previous_balance_half_coin

    def buy(self, is_convertible):
        if is_convertible:
            mouse_click(self.postion_isconvertible_max_shopping_number)
            mouse_click(self.postion_isconvertible_buy_button)
        else:
            mouse_click(self.postion_notconvertiable_max_shopping_number)
            mouse_click(self.postion_notconvertiable_buy_button)

    def refresh(self, is_convertible):
        if is_convertible:
            mouse_click(self.postion_isconvertible_min_shopping_number)
            mouse_click(self.postion_isconvertible_buy_button)
        else:
            mouse_click(self.postion_notconvertiable_min_shopping_number)
            mouse_click(self.postion_notconvertiable_buy_button)

    def freerefresh(self, good_postion):
        # esc回到商店页面
        pyautogui.press('esc')
        # 点击回到商品页面
        mouse_click(good_postion)

    def switch_to_option(self, option=0):
        if option == 0:
            mouse_click(self.postion_mode_1_option_1)
        elif option == 1:
            mouse_click(self.postion_mode_1_option_2)
        elif option == 2:
            mouse_click(self.postion_mode_1_option_3)
        elif option == 3:
            mouse_click(self.postion_mode_1_option_4)


    def detect_option_price(self, debug_mode=False):
        self._screenshot = get_windowshot(self.postion_mode_1_price, debug_mode=self.debug or debug_mode)
        self.option_price = self.identify_number(self._screenshot)
        return self.option_price

    def option_buy(self):
        mouse_click(self.postion_mode_1_buy)

    def option_refresh(self):
        pyautogui.press('esc')

def main():
    bot = BuyBot()
    # print(bot.detect_option_price(debug_mode=True))
    print(bot.detect_price(is_convertible=True,debug_mode=True))
    # print(bot.detect_option_buy_failed())
    # bot.detect_balance_half_coin()

if __name__ == '__main__':
    main()
