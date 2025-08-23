# -*- coding: utf-8 -*-
"""
OCR引擎基础设施 - 基于模板匹配的图像识别
不使用三方OCR库，仅识别数字
"""
import os
import threading
from pathlib import Path
from typing import Tuple

import cv2
import numpy as np
import pyautogui

try:
    from src.core.exceptions import OCRException
    from src.core.interfaces import IOCREngine
except ImportError:
    from ..core.exceptions import OCRException
    from ..core.interfaces import IOCREngine


class TemplateOCREngine(IOCREngine):
    """基于模板匹配的OCR引擎"""

    def __init__(self, templates_dir: str = None, resolution: Tuple[int, int] = None):
        if templates_dir is None:
            if resolution is None:
                resolution = pyautogui.size()
            templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                         f"templates/{resolution[0]}x{resolution[1]}")

        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # 模板缓存
        self._templates = {}
        self._pic_templates = {}
        self._lock = threading.Lock()

        # 加载模板
        self._load_templates()

    def _load_pic(self, pic_name: str, threshold=127):
        sell_template_path = self.templates_dir / pic_name
        if sell_template_path.exists():
            template = cv2.imread(str(sell_template_path), cv2.IMREAD_GRAYSCALE)
            if template is not None:
                _, binary = cv2.threshold(template, threshold, 255, cv2.THRESH_BINARY)
                template_name = pic_name if not pic_name.endswith(".png") else pic_name[:-4]
                self._pic_templates[template_name] = binary

    def _load_templates(self):
        """加载所有数字模板"""
        try:
            with self._lock:
                # 加载默认数字模板 (0-9.png)
                default_group = {}
                for i in range(10):
                    template_path = self.templates_dir / f"{i}.png"
                    if template_path.exists():
                        template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
                        if template is not None:
                            _, binary = cv2.threshold(template, 127, 255, cv2.THRESH_BINARY)
                            default_group[i] = binary

                if default_group:
                    self._templates["default"] = default_group

                # 加载带前缀的模板 (prefix_0.png~prefix_9.png)
                font_prefixes = set()
                for template_file in self.templates_dir.glob("*_*.png"):
                    parts = template_file.stem.split("_")
                    if len(parts) == 2 and parts[1].isdigit():
                        font_prefixes.add(parts[0])

                for prefix in sorted(font_prefixes):
                    group = {}
                    for i in range(10):
                        template_path = self.templates_dir / f"{prefix}_{i}.png"
                        if template_path.exists():
                            template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
                            if template is not None:
                                _, binary = cv2.threshold(template, 127, 255, cv2.THRESH_BINARY)
                                group[i] = binary

                    if len(group) == 10:
                        self._templates[prefix] = group

                # 加载失败检测模板
                self._load_pic("option_failed.png")
                # 加载售卖框模板
                self._load_pic("sell.png")
                # 加载装备模板
                self._load_pic("equipment.png")
                self._load_pic("enter_teqingchu.png", 50)
                self._load_pic("equipment_scheme.png", 50)

                if not self._templates:
                    raise FileNotFoundError("未找到有效的数字模板文件")

        except Exception as e:
            raise OCRException(f"加载模板失败: {e}") from e

    def image_to_string(self, image: np.ndarray) -> str:
        """将图像转换为数字字符串"""
        try:
            # 确保图像是numpy数组
            if not isinstance(image, np.ndarray):
                image = np.array(image)

            # 转换为灰度图
            if len(image.shape) == 3:
                if image.shape[2] == 3:  # RGB
                    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                elif image.shape[2] == 4:  # RGBA
                    gray = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
                else:
                    gray = image
            else:
                gray = image

            digits_info = []

            # 对每个字体组进行模板匹配
            for font_name, templates in self._templates.items():
                for digit, template in templates.items():
                    # 模板匹配
                    result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
                    locations = np.where(result >= 0.7)  # 匹配阈值

                    for pt in zip(*locations[::-1]):
                        digits_info.append(
                            {"digit": digit, "x": pt[0], "score": result[pt[1], pt[0]], "font": font_name}
                        )

            # 非极大值抑制，去除重叠检测
            digits_info.sort(key=lambda x: -x["score"])
            filtered = []

            for info in digits_info:
                x = info["x"]
                overlap = False

                # 检查是否与已选区域重叠
                for selected in filtered:
                    template_width = self._templates[info["font"]][info["digit"]].shape[1]
                    selected_width = self._templates[selected["font"]][selected["digit"]].shape[1]
                    max_width = max(template_width, selected_width)

                    if abs(x - selected["x"]) < max_width * 0.7:  # 重叠阈值
                        overlap = True
                        break

                if not overlap:
                    filtered.append(info)

            # 按x坐标排序，拼接成字符串
            filtered.sort(key=lambda x: x["x"])
            return "".join(str(d["digit"]) for d in filtered)

        except Exception as e:
            raise OCRException(f"OCR识别失败: {e}") from e

    def detect_template(self, image: np.ndarray, template_name: str) -> bool:
        """检测模板是否存在于图像中"""
        try:
            if self._pic_templates is None or self._pic_templates[template_name] is None:
                return False
            # 确保图像是numpy数组
            if not isinstance(image, np.ndarray):
                image = np.array(image)

            # 转换为灰度图
            if len(image.shape) == 3:
                if image.shape[2] == 3:  # RGB
                    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                elif image.shape[2] == 4:  # RGBA
                    gray = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
                else:
                    gray = image
            else:
                gray = image

            # 模板匹配
            result = cv2.matchTemplate(gray, self._pic_templates[template_name], cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)

            return max_val >= 0.7

        except Exception as e:
            raise OCRException(f"模板检测失败: {e}") from e

    @staticmethod
    def get_pixel_color(img: np.ndarray, x: int, y: int):
        """
        获取NumPy数组图像中指定坐标点的颜色值
        :param img: NumPy数组形式的图像数据 (OpenCV格式)
        :param x: x坐标 (列)
        :param y: y坐标 (行)
        :return:
            BGR颜色值 (如果是彩色图像)
            灰度值 (如果是灰度图像)
            None (如果坐标超出范围)
        """
        # 检查图像是否有效
        if not isinstance(img, np.ndarray):
            print("错误: 输入必须是NumPy数组")
            return None

        # 检查坐标是否在图像范围内
        height, width = img.shape[:2]
        if x < 0 or x >= width or y < 0 or y >= height:
            print(f"坐标({x},{y})超出图片范围(宽{width},高{height})")
            return None

        # 获取颜色值
        if len(img.shape) == 3:  # 彩色图像
            return tuple(img[y, x])
        # 灰度图像
        return int(img[y, x])


class MockOCREngine(IOCREngine):
    """OCR引擎的模拟实现，用于测试"""

    def __init__(self, **kwargs):
        self.recognized_text = "1234"  # 默认返回的文本
        self.template_detected = False

    def image_to_string(self, image: np.ndarray) -> str:
        """模拟OCR识别"""
        return self.recognized_text

    def detect_template(self, image: np.ndarray, template_name: str) -> bool:
        """模拟模板检测"""
        return self.template_detected

    def recognize_price(self, image: np.ndarray) -> int:
        """模拟价格识别"""
        return int(self.recognized_text) if self.recognized_text.isdigit() else 0

    def set_recognized_text(self, text: str):
        """设置模拟返回的文本"""
        self.recognized_text = text

    def set_template_detected(self, detected: bool):
        """设置模板检测结果"""
        self.template_detected = detected


class OCREngineFactory:
    """OCR引擎工厂"""

    @staticmethod
    def create_engine(engine_type: str = "template", **kwargs) -> IOCREngine:
        """创建OCR引擎"""
        if engine_type == "template":
            return TemplateOCREngine(**kwargs)
        if engine_type == "mock":
            return MockOCREngine(**kwargs)
        raise ValueError(f"不支持的OCR引擎类型: {engine_type}")


if __name__ == "__main__":
    a = "test.png"
    print(a[:-4])
