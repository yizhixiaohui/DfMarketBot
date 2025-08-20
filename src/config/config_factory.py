# -*- coding: utf-8 -*-
"""
配置管理器工厂
提供统一的配置管理器创建接口，屏蔽底层实现细节
"""
from typing import Dict, Type, Optional

try:
    from src.core.interfaces import IConfigManager
    from src.config.config_manager import TradingConfigManager, DelayConfigManager
except ImportError:
    from ..core.interfaces import IConfigManager
    from .config_manager import TradingConfigManager, DelayConfigManager


class ConfigFactory:
    """配置管理器工厂类"""

    CONFIG_MANAGERS: Dict[str, Type[IConfigManager]] = {
        "trading": TradingConfigManager,
        "delay": DelayConfigManager,
    }
    _instances: Dict[str, IConfigManager] = {}

    @classmethod
    def get_config_manager(cls, config_type: str = "trading") -> IConfigManager:
        """
        获取配置管理器实例

        Args:
            config_type: 配置类型，例如 "trading" 或 "delay"

        Returns:
            IConfigManager: 配置管理器接口实例
        """
        if config_type not in cls.CONFIG_MANAGERS:
            raise ValueError(f"Unsupported config type: {config_type}")

        if config_type not in cls._instances:
            manager_class = cls.CONFIG_MANAGERS[config_type]
            cls._instances[config_type] = manager_class()

        return cls._instances[config_type]

    @classmethod
    def create_config_manager(cls, config_type: str = "trading", config_path: Optional[str] = None) -> IConfigManager:
        """
        创建指定格式的配置管理器

        Args:
            config_type: 配置类型
            config_path: 配置文件路径

        Returns:
            IConfigManager: 配置管理器接口实例
        """
        if config_type not in cls.CONFIG_MANAGERS:
            raise ValueError(f"Unsupported config type: {config_type}")

        manager_class = cls.CONFIG_MANAGERS[config_type]
        return manager_class(config_path)


if __name__ == "__main__":
    pass
