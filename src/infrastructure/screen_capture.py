# -*- coding: utf-8 -*-
"""
屏幕捕获基础设施
"""
from typing import List, Tuple, Optional

import numpy as np
import pyautogui


class ScreenCapture:
    """屏幕捕获服务"""

    def __init__(self):
        self.width, self.height = pyautogui.size()

    def capture_region(self, coordinates: List[float]) -> np.ndarray:
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

        # 捕获屏幕区域
        screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))

        # 转换为numpy数组
        return np.array(screenshot)

    def capture_window(self, window_title: str = None) -> np.ndarray:
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
