# -*- coding: utf-8 -*-
"""
核心异常定义
"""


class DfMarketException(Exception):
    """基础异常类"""


class DetectionException(DfMarketException):
    """检测异常"""


class PriceDetectionException(DetectionException):
    """价格检测异常"""


class BalanceDetectionException(DetectionException):
    """余额检测异常"""


class ActionException(DfMarketException):
    """动作执行异常"""


class ActionExecutionException(ActionException):
    """动作执行异常"""


class ConfigurationException(DfMarketException):
    """配置异常"""


class TradingException(DfMarketException):
    """交易异常"""


class OCRException(DfMarketException):
    """OCR异常"""


class WindowDetectionException(DfMarketException):
    """窗口检测相关异常"""


class WindowSizeException(WindowDetectionException):
    """窗口尺寸不支持异常"""


class WindowNotFoundException(WindowDetectionException):
    """窗口未找到异常"""
