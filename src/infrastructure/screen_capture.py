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

        # 窗口区域信息 (x, y, width, height)
        self.window_region: Optional[Tuple[int, int, int, int]] = None

    def set_window_region(self, x: int, y: int, width: int, height: int) -> None:
        """设置窗口区域信息

        Args:
            x: 窗口左上角X坐标
            y: 窗口左上角Y坐标
            width: 窗口宽度
            height: 窗口高度
        """
        self.window_region = (x, y, width, height)
        self.width, self.height = width, height

    def clear_window_region(self) -> None:
        """清除窗口区域信息，回退到全屏模式"""
        self.window_region = None
        self.width, self.height = pyautogui.size()

    def _convert_region(self, region: List[int]) -> List[int]:
        """转换截图区域坐标

        Args:
            region: [x, y, width, height] 相对于窗口的坐标

        Returns:
            转换后的绝对屏幕坐标
        """
        if self.window_region:
            x, y, w, h = region
            return [
                x + self.window_region[0],  # 窗口偏移X
                y + self.window_region[1],  # 窗口偏移Y
                w,
                h,  # 尺寸保持不变
            ]
        return region

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

        # 转换为 [x, y, width, height] 格式
        region = [x1, y1, x2 - x1, y2 - y1]

        # 应用窗口偏移（如果设置了窗口区域）
        converted_region = self._convert_region(region)

        # 提取转换后的坐标
        final_x, final_y, final_width, final_height = converted_region

        with mss() as sct:
            # 捕获屏幕区域
            return np.array(sct.grab({"left": final_x, "top": final_y, "width": final_width, "height": final_height}))

    @staticmethod
    def capture_window() -> np.ndarray:
        """捕获指定窗口的截图

        Returns:
            窗口截图的numpy数组
        """
        # 捕获整个屏幕
        screenshot = pyautogui.screenshot()
        return np.array(screenshot)


if __name__ == "__main__":
    sc = ScreenCapture()
    start = time.time()
    count = 0
    for i in range(100):
        res = sc.capture_region([1628, 939, 1748, 971])
    print("fps:", 100 / (time.time() - start))
    print(count)
