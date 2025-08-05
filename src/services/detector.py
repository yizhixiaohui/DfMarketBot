# -*- coding: utf-8 -*-
"""
价格检测服务
"""
import time
import re
from abc import abstractmethod
from typing import Optional
import numpy as np

from ..core.interfaces import IPriceDetector, ItemType
from ..core.exceptions import PriceDetectionException, BalanceDetectionException
from ..config.settings import ResolutionConfig
from ..infrastructure.screen_capture import ScreenCapture
from ..infrastructure.ocr_engine import TemplateOCREngine


class PriceDetector(IPriceDetector):
    """价格检测器基类"""
    
    def __init__(self, screen_capture: ScreenCapture, ocr_engine: TemplateOCREngine):
        self.screen_capture = screen_capture
        self.ocr_engine = ocr_engine
        self.coordinates = ResolutionConfig.scale_coordinates(
            screen_capture.width, screen_capture.height
        )

    @abstractmethod
    def detect_price(self) -> int:
        """检测当前物品价格 - 由子类实现"""
        pass

    def detect_balance(self) -> Optional[int]:
        """检测当前哈夫币余额"""
        try:
            coords = self.coordinates["balance_detection"]
            
            for attempt in range(50):
                screenshot = self.screen_capture.capture_region(coords)
                balance = self._extract_number(screenshot)
                
                if balance is not None:
                    return balance
                
                time.sleep(0.02)
            
            return None
            
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

    def __init__(self, screen_capture: ScreenCapture, ocr_engine: TemplateOCREngine, item_convertible: bool=False):
        super().__init__(screen_capture, ocr_engine)
        self.item_convertible = item_convertible

    def detect_price(self) -> int:
        """检测当前物品价格"""
        try:
            if self.item_convertible:
                coords = self.coordinates["price_detection"]["convertible"]
            else:
                coords = self.coordinates["price_detection"]["non_convertible"]

            for attempt in range(50):
                screenshot = self.screen_capture.capture_region(coords)
                price = self._extract_number(screenshot)

                if price is not None and price >= 200:  # 过滤异常价格
                    return price

                time.sleep(0.02)

            raise PriceDetectionException("价格检测失败，建议检查物品是否可兑换")

        except Exception as e:
            raise PriceDetectionException(f"价格检测异常: {e}")


class RollingModeDetector(PriceDetector):
    """滚仓模式检测器"""
    
    def __init__(self, screen_capture: ScreenCapture, ocr_engine: TemplateOCREngine):
        super().__init__(screen_capture, ocr_engine)

    def detect_price(self) -> int:
        """检测指定配装选项的价格"""
        try:
            coords = self.coordinates["rolling_mode"]["price_area"]
            screenshot = self.screen_capture.capture_region(coords)
            price = self._extract_number(screenshot)
            
            if price is None:
                raise PriceDetectionException(f"配装选项价格检测失败")
            
            return price
            
        except Exception as e:
            raise PriceDetectionException(f"配装价格检测异常: {e}")
    
    def check_purchase_failure(self) -> bool:
        """检查购买是否失败"""
        try:
            coords = self.coordinates["rolling_mode"]["failure_check"]
            screenshot = self.screen_capture.capture_region(coords)
            return self.ocr_engine.detect_template(screenshot)
        except:
            return False