# -*- coding: utf-8 -*-
"""
配置管理器工厂
提供统一的配置管理器创建接口，屏蔽底层实现细节
"""
from typing import Optional

from .config_manager import JsonConfigManager, YamlConfigManager
from ..core.interfaces import IConfigManager


class ConfigFactory:
    """配置管理器工厂类"""

    _config_manager: Optional[IConfigManager] = None
    _config_format: str = "yaml"  # 默认使用YAML格式

    @classmethod
    def set_config_format(cls, format_type: str) -> None:
        """
        设置配置格式
        
        Args:
            format_type: 配置格式，支持 "json" 或 "yaml"
        """
        if format_type.lower() not in ["json", "yaml"]:
            raise ValueError("配置格式必须是 'json' 或 'yaml'")
        cls._config_format = format_type.lower()
        cls._config_manager = None  # 重置配置管理器

    @classmethod
    def get_config_manager(cls) -> IConfigManager:
        """
        获取配置管理器实例
        
        Returns:
            IConfigManager: 配置管理器接口实例
        """
        if cls._config_manager is None:
            if cls._config_format == "json":
                cls._config_manager = JsonConfigManager()
            else:
                cls._config_manager = YamlConfigManager()
        return cls._config_manager

    @classmethod
    def create_config_manager(cls, format_type: str = "yaml", config_path: str = None) -> IConfigManager:
        """
        创建指定格式的配置管理器
        
        Args:
            format_type: 配置格式，支持 "json" 或 "yaml"
            config_path: 配置文件路径
            
        Returns:
            IConfigManager: 配置管理器接口实例
        """
        if format_type.lower() == "json":
            return JsonConfigManager(config_path)
        else:
            return YamlConfigManager(config_path)


# 全局配置管理器实例
_config_manager: Optional[IConfigManager] = None


def get_config_manager() -> IConfigManager:
    """
    获取全局配置管理器实例
    
    Returns:
        IConfigManager: 配置管理器接口实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigFactory.get_config_manager()
    return _config_manager


def set_config_manager(manager: IConfigManager) -> None:
    """
    设置全局配置管理器实例
    
    Args:
        manager: 配置管理器实例
    """
    global _config_manager
    _config_manager = manager
