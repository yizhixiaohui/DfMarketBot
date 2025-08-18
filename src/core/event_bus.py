# -*- coding: utf-8 -*-
"""
事件总线 - 实现组件间解耦通信
"""
from typing import Callable, Dict, List

from PyQt5.QtCore import QObject, pyqtSignal


class EventBus(QObject):
    """全局事件总线，用于组件间解耦通信"""

    # 定义事件类型
    OVERLAY_TEXT_UPDATED = "text_updated"
    STATUS_CHANGED = "status_changed"
    PRICE_UPDATED = "price_updated"
    BALANCE_UPDATED = "balance_updated"
    ERROR_OCCURRED = "error_occurred"
    TRADING_STARTED = "trading_started"
    TRADING_STOPPED = "trading_stopped"

    # 信号定义
    overlay_text_updated = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    price_updated = pyqtSignal(int)
    balance_updated = pyqtSignal(int)
    error_occurred = pyqtSignal(str)
    trading_started = pyqtSignal()
    trading_stopped = pyqtSignal()

    _instance = None

    def __init__(self):
        super().__init__()
        self._handlers: Dict[str, List[Callable]] = {}

    @classmethod
    def instance(cls) -> "EventBus":
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def emit_overlay_text_updated(self, text: str) -> None:
        """发送文本更新事件"""
        self.overlay_text_updated.emit(text)

    def emit_status_changed(self, status: str) -> None:
        """发送状态改变事件"""
        self.status_changed.emit(status)

    def emit_price_updated(self, price: int) -> None:
        """发送价格更新事件"""
        self.price_updated.emit(price)

    def emit_balance_updated(self, balance: int) -> None:
        """发送余额更新事件"""
        self.balance_updated.emit(balance)

    def emit_error_occurred(self, error: str) -> None:
        """发送错误事件"""
        self.error_occurred.emit(error)

    def emit_trading_started(self) -> None:
        """发送交易开始事件"""
        self.trading_started.emit()

    def emit_trading_stopped(self) -> None:
        """发送交易停止事件"""
        self.trading_stopped.emit()


# 全局事件总线实例
event_bus = EventBus.instance()
