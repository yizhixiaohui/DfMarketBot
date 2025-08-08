# -*- coding: utf-8 -*-
"""
价格检测服务
"""
import re
import time
from abc import abstractmethod
from typing import Optional, List

import cv2
import numpy as np

if __name__ == '__main__':
    from src.config.settings import ResolutionConfig
    from src.core.exceptions import PriceDetectionException, BalanceDetectionException
    from src.core.interfaces import IPriceDetector
    from src.infrastructure.ocr_engine import TemplateOCREngine
    from src.infrastructure.screen_capture import ScreenCapture
else:
    from ..config.settings import ResolutionConfig
    from ..core.exceptions import PriceDetectionException, BalanceDetectionException
    from ..core.interfaces import IPriceDetector
    from ..infrastructure.ocr_engine import TemplateOCREngine
    from ..infrastructure.screen_capture import ScreenCapture


class PriceDetector(IPriceDetector):
    """价格检测器基类"""

    def __init__(self, screen_capture: ScreenCapture, ocr_engine: TemplateOCREngine):
        self.screen_capture = screen_capture
        self.ocr_engine = ocr_engine
        self.coordinates = ResolutionConfig.restore_coordinates(screen_capture.width, screen_capture.height)

    @abstractmethod
    def get_detection_coordinates(self) -> List[float]:
        """获取价格检测坐标 - 由子类实现"""
        pass

    def _detect_value(self, coords: List[float], value_name: str = "价格", max_attempts: int = 50) -> int:
        """通用的数值检测逻辑"""
        for attempt in range(max_attempts):
            screenshot = self.screen_capture.capture_region(coords)
            value = self._extract_number(screenshot)

            if value is not None:
                if value_name == "价格" and value < 100:  # 仅对价格进行异常过滤
                    print(f'检测{value_name}({value})异常，跳过检测')
                    continue
                print(f'detected {value_name}:', value)
                return value

            time.sleep(0.02)

        raise PriceDetectionException(f"{value_name}检测失败")

    def detect_price(self) -> int:
        """检测当前物品价格 - 使用模板方法模式"""
        try:
            coords = self.get_detection_coordinates()
            return self._detect_value(coords)
        except Exception as e:
            raise PriceDetectionException(f"价格检测异常: {e}")

    def detect_balance(self) -> Optional[int]:
        """检测当前哈夫币余额"""
        try:
            coords = self.coordinates["balance_detection"]
            return self._detect_value(coords, "余额", 50)
        except Exception as e:
            raise BalanceDetectionException(f"余额检测异常: {e}")

    def _extract_number(self, image: np.ndarray) -> Optional[int]:
        """从图像中提取数字"""
        try:
            text = self.ocr_engine.image_to_string(image)
            # 只保留数字
            numbers = re.sub(r'[^0-9]', '', text)
            return int(numbers) if numbers else None
        except:
            return None


class HoardingModeDetector(PriceDetector):
    """屯仓模式检测器"""

    def __init__(self, screen_capture: ScreenCapture, ocr_engine: TemplateOCREngine, item_convertible: bool = False):
        super().__init__(screen_capture, ocr_engine)
        self.item_convertible = item_convertible

    def get_detection_coordinates(self) -> dict:
        """获取价格检测坐标"""
        if self.item_convertible:
            return self.coordinates["price_detection"]["convertible"]
        return self.coordinates["price_detection"]["non_convertible"]


class RollingModeDetector(PriceDetector):
    """滚仓模式检测器"""

    def __init__(self, screen_capture: ScreenCapture, ocr_engine: TemplateOCREngine):
        super().__init__(screen_capture, ocr_engine)

    def get_detection_coordinates(self) -> dict:
        """获取价格检测坐标"""
        return self.coordinates["rolling_mode"]["price_area"]

    def check_purchase_failure(self) -> bool:
        """检查购买是否失败"""
        try:
            coords = self.coordinates["rolling_mode"]["failure_check"]
            screenshot = self.screen_capture.capture_region(coords)
            return self.ocr_engine.detect_template(screenshot)
        except:
            return False

    def detect_sellable_item(self):
        width = 9
        length = 10
        color_toleration = 10
        coords = self.coordinates["rolling_mode"]["wait_sell_item_area"]
        item_range = self.coordinates["rolling_mode"]["item_range"]
        item_center = [int(item_range[0]/2), int(item_range[1]/2)]
        screenshot = self.screen_capture.capture_region(coords)
        valid_color = [26, 31, 34]
        current_pos = [item_center[0], item_center[1]]
        for i in range(length):
            for j in range(width):
                color = self.ocr_engine.get_pixel_color(screenshot, current_pos[0], current_pos[1])
                if not (valid_color[0]-color_toleration < color[0] < valid_color[0]+color_toleration and valid_color[1]-color_toleration < color[1] < valid_color[1]+color_toleration and valid_color[2]-color_toleration < color[2] < valid_color[2]+color_toleration):
                    return [coords[0]+current_pos[0], coords[1]+current_pos[1]]
                current_pos[0] += item_range[0]+1
            current_pos[0] = item_center[0]
            current_pos[1] += item_range[1]+1
        return [0,0]


if __name__ == '__main__':
    sc = ScreenCapture()
    ocr = TemplateOCREngine("L:\workspace\github.com\XiaoGu-G2020\DeltaForceMarketBot\\templates")
    detector = RollingModeDetector(sc, ocr)
    res = detector.detect_sellable_item()
    print(res)
