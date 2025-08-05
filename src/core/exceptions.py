# -*- coding: utf-8 -*-
"""
核心异常定义
"""


class DfMarketException(Exception):
    """基础异常类"""
    pass


class DetectionException(DfMarketException):
    """检测异常"""
    pass


class PriceDetectionException(DetectionException):
    """价格检测异常"""
    pass


class BalanceDetectionException(DetectionException):
    """余额检测异常"""
    pass


class ActionException(DfMarketException):
    """动作执行异常"""
    pass


class ActionExecutionException(ActionException):
    """动作执行异常"""
    pass


class ConfigurationException(DfMarketException):
    """配置异常"""
    pass


class TradingException(DfMarketException):
    """交易异常"""
    pass


class OCRException(DfMarketException):
    """OCR异常"""
    pass