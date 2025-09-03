# -*- coding: utf-8 -*-
"""
屏幕捕获基础设施
"""
import time
from typing import List, Optional, Tuple

import numpy as np
import pyautogui
from mss import mss


class ScreenCapture:
    """屏幕捕获服务"""

    def __init__(self, resolution: Tuple[int, int] = None):
        if not resolution:
            self.width, self.height = pyautogui.size()
        else:
            self.width, self.height = resolution

    @staticmethod
    def capture_region(coordinates: List[float]) -> np.ndarray:
        """捕获指定区域的屏幕截图

        Args:
            coordinates: [x1_ratio, y1_ratio, x2_ratio, y2_ratio] 相对坐标

        Returns:
            截图的numpy数组
        """
        if len(coordinates) != 4:
            raise ValueError("坐标必须是4个元素的列表")

        # 转换为绝对坐标
        x1 = int(coordinates[0])
        y1 = int(coordinates[1])
        x2 = int(coordinates[2])
        y2 = int(coordinates[3])

        # 确保坐标有效
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        with mss() as sct:
            # 捕获屏幕区域
            return np.array(sct.grab({"left": x1, "top": y1, "width": x2 - x1, "height": y2 - y1}))

    @staticmethod
    def capture_window() -> np.ndarray:
        """捕获指定窗口的截图

        Args:
            window_title: 窗口标题，如果为None则捕获整个屏幕

        Returns:
            窗口截图的numpy数组
        """
        # 捕获整个屏幕
        screenshot = pyautogui.screenshot()
        return np.array(screenshot)

    def get_window_position(self, window_title: str) -> Optional[Tuple[int, int, int, int]]:
        """获取窗口位置

        Args:
            window_title: 窗口标题

        Returns:
            (left, top, right, bottom) 绝对坐标，或None
        """
        # 在跨平台环境中，返回None表示不支持窗口定位
        return None


if __name__ == "__main__":
    sc = ScreenCapture()
    start = time.time()
    count = 0
    for i in range(100):
        res = sc.capture_region([1628, 939, 1748, 971])
    print("fps:", 100 / (time.time() - start))
    print(count)
