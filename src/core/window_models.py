# -*- coding: utf-8 -*-
"""
窗口相关数据模型和枚举
"""
from dataclasses import dataclass
from enum import Enum


class WindowState(Enum):
    """窗口状态枚举"""

    NOT_FOUND = "not_found"
    DETECTED = "detected"
    MINIMIZED = "minimized"
    OCCLUDED = "occluded"
    INVALID_SIZE = "invalid_size"


@dataclass
class WindowInfo:
    """窗口信息数据模型"""

    hwnd: int
    title: str
    x: int
    y: int
    width: int
    height: int
    is_visible: bool
    is_foreground: bool

    @property
    def position(self) -> tuple[int, int]:
        """获取窗口位置"""
        return self.x, self.y

    @property
    def size(self) -> tuple[int, int]:
        """获取窗口尺寸"""
        return self.width, self.height

    @property
    def rect(self) -> tuple[int, int, int, int]:
        """获取窗口矩形区域 (x, y, width, height)"""
        return self.x, self.y, self.width, self.height
