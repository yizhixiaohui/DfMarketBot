# -*- coding: utf-8 -*-
"""
延迟操作辅助类
提供便捷的延迟获取和执行方法
"""
import threading
import time
from typing import Optional

from ..config.trading_config import TradingMode

try:
    from src.config.config_factory import ConfigFactory
    from src.config.delay_config import DelayConfig
    from src.core.interfaces import IConfigManager
except ImportError:
    from ..config.config_factory import ConfigFactory
    from ..config.delay_config import DelayConfig
    from ..core.interfaces import IConfigManager


class DelayHelper:
    """延迟操作辅助类，提供便捷的延迟获取和执行方法"""
    MODE_MAPPING = {
        TradingMode.ROLLING: "rolling_mode",
        TradingMode.HOARDING: "hoarding_mode"
    }

    def __init__(self, mode: TradingMode = TradingMode.ROLLING):
        """初始化DelayHelper"""
        self.mode = self.MODE_MAPPING[mode]
        self._config_manager: IConfigManager[DelayConfig] = ConfigFactory.get_config_manager("delay")
        self._cached_config: Optional[DelayConfig] = None
        self._lock = threading.RLock()  # 使用可重入锁保证线程安全

        # 初始加载配置
        self._load_config()


    def set_mode(self, mode: TradingMode) -> None:
        """
        设置交易模式

        Args:
            mode: 交易模式
        """
        if mode not in self.MODE_MAPPING:
            raise ValueError(f"无效的交易模式: {mode}")
        self.mode = self.MODE_MAPPING[mode]

    def get_delay(self, operation: str) -> float:
        """
        获取延迟时间
        
        Args:
            operation: 操作名称

        Returns:
            延迟时间（秒），如果配置不存在则返回0.0
        """
        with self._lock:
            if self._cached_config is None:
                return 0.0

            return self._cached_config.get_delay(self.mode, operation)

    def sleep(self, operation: str) -> None:
        """
        直接执行延迟操作
        
        Args:
            operation: 操作名称
        """
        delay = self.get_delay(operation)
        if delay > 0:
            time.sleep(delay)

    def get_mode_delays(self, mode: TradingMode) -> dict:
        """
        获取指定模式的所有延迟配置
        
        Args:
            mode: 交易模式名称
            
        Returns:
            该模式下所有操作的延迟配置字典
        """
        with self._lock:
            if self._cached_config is None:
                return {}

            return self._cached_config.get_mode_delays(self.MODE_MAPPING[mode])

    def has_operation(self, operation: str, mode: TradingMode = TradingMode.ROLLING) -> bool:
        """
        检查是否存在指定的操作配置
        
        Args:
            operation: 操作名称
            mode: 交易模式，默认为"rolling_mode"
            
        Returns:
            是否存在该操作配置
        """
        with self._lock:
            if self._cached_config is None:
                return False

            if self.mode:
                mode = self.mode
            else:
                mode = self.MODE_MAPPING[mode]
            return self._cached_config.has_operation(mode, operation)

    def get_available_modes(self) -> list:
        """
        获取所有可用的交易模式列表
        
        Returns:
            交易模式名称列表
        """
        with self._lock:
            if self._cached_config is None:
                return []

            return self._cached_config.get_all_modes()

    def get_mode_operations(self, mode: TradingMode) -> list:
        """
        获取指定模式下的所有操作列表

        Args:
            mode: 交易模式名称

        Returns:
            操作名称列表
        """
        with self._lock:
            if self._cached_config is None:
                return []

            return self._cached_config.get_mode_operations(self.MODE_MAPPING[mode])

    def reload_config(self) -> bool:
        """
        重新加载配置（用于配置修改后手动刷新）
        
        Returns:
            是否成功重新加载
        """
        with self._lock:
            return self._load_config()

    def _load_config(self) -> bool:
        """
        加载配置（内部方法，调用时需要持有锁）
        
        Returns:
            是否成功加载
        """
        try:
            self._cached_config = self._config_manager.load_config()
            return True
        except Exception as e:
            print(f"加载延迟配置失败: {e}")
            return False

    def get_config_info(self) -> dict:
        """
        获取配置信息摘要
        
        Returns:
            包含配置统计信息的字典
        """
        with self._lock:
            if self._cached_config is None:
                return {
                    "status": "no_config",
                    "modes": 0,
                    "total_operations": 0
                }

            modes = self._cached_config.get_all_modes()
            total_operations = sum(
                len(self._cached_config.get_mode_operations(mode))
                for mode in modes
            )

            return {
                "status": "loaded",
                "modes": len(modes),
                "mode_names": modes,
                "total_operations": total_operations
            }

    def __str__(self) -> str:
        """字符串表示"""
        info = self.get_config_info()
        return (f"DelayHelper(status={info['status']}, "
                f"modes={info['modes']}, "
                f"operations={info['total_operations']})")

    def __repr__(self) -> str:
        """调试表示"""
        return "DelayHelper()"


# 全局延迟辅助实例
delay_helper = DelayHelper()
