# -*- coding: utf-8 -*-
"""
配置管理模块
"""
import os
import time
from typing import Any, Dict, Type

from .delay_config import DelayConfig
from .serializer import ConfigSerializer, YamlSerializer, JsonSerializer

try:
    from src.core.exceptions import ConfigurationException
    from src.core.interfaces import IConfigManager, TConfig, TradingConfig
except ImportError:
    from ..core.exceptions import ConfigurationException
    from ..core.interfaces import IConfigManager, TConfig, TradingConfig


class BaseConfigManager(IConfigManager[TConfig]):
    """基础配置管理器"""

    def __init__(self, config_path: str = None, serializer: ConfigSerializer = None):
        super().__init__(config_path)
        # 获取正确的基目录
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_path = os.path.join(base_dir, "config", "settings.yaml")
        self.config_path = config_path
        # 确保配置目录存在
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        if serializer is None:
            # 默认根据文件后缀选择
            if self.config_path.endswith(".yaml") or self.config_path.endswith(".yml"):
                serializer = YamlSerializer()
            elif self.config_path.endswith(".json"):
                serializer = JsonSerializer()
            else:
                raise ValueError("无法根据文件后缀自动选择序列化器，请传入 serializer 参数")
        self._serializer = serializer
        self._last_modified = 0
        self._cached_config = None

    def load_config(self) -> TConfig:
        raise NotImplementedError("Subclasses must implement this method")

    def save_config(self, config: TConfig):
        raise NotImplementedError("Subclasses must implement this method")

    def reload_config(self) -> TConfig:
        """重新加载配置（支持热更新）"""
        try:
            current_modified = os.path.getmtime(self.config_path) if os.path.exists(self.config_path) else 0
            if current_modified > self._last_modified or self._cached_config is None:
                self._cached_config = self.load_config()
                self._last_modified = current_modified
            return self._cached_config
        except Exception as e:
            print("配置重加载失败:", e)
            # 如果重新加载失败，返回缓存的配置或默认配置
            if self._cached_config is not None:
                return self._cached_config
            return self._create_default_config()

    def update_config(self, updates: Dict[str, Any]) -> TConfig:
        """更新配置"""
        try:
            config_dict = self._config_to_dict(self.load_config())
            self._deep_update(config_dict, updates)
            new_config = self._dict_to_config(config_dict, self._config_class())
            self.save_config(new_config)
            return new_config
        except Exception as e:
            raise ConfigurationException(f"更新配置失败: {e}") from e

    def _config_class(self) -> Type[TConfig]:
        """获取配置类，子类实现"""
        raise NotImplementedError("Subclasses must implement this method")

    def _create_default_config(self) -> TConfig:
        """创建默认配置，子类实现"""
        raise NotImplementedError("Subclasses must implement this method")

    def _deep_update(self, base_dict: Dict, update_dict: Dict) -> None:
        """深度更新字典"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def _load_config(self, config_class: Type[TConfig]) -> TConfig:
        """通用配置加载方法"""
        try:
            if not os.path.exists(self.config_path):
                # 如果配置文件不存在，创建默认配置
                default_config = self._create_default_config()
                self.save_config(default_config)
                return default_config

            data = self._serializer.load(self.config_path)
            return self._dict_to_config(data, config_class)
        except Exception as e:
            # 如果加载失败，返回默认配置
            print(f"警告: 加载配置文件失败，使用默认配置: {e}")
            return self._create_default_config()

    def _save_config(self, config: TConfig) -> None:
        """通用配置保存方法"""
        try:
            config_dict = self._config_to_dict(config)
            self._serializer.save(self.config_path, config_dict)
            self._update_cache(config)
        except Exception as e:
            raise ConfigurationException(f"保存配置失败: {e}") from e

    def _update_cache(self, config: TConfig) -> None:
        """更新缓存"""
        self._cached_config = config
        self._last_modified = time.time()


class TradingConfigManager(BaseConfigManager[TradingConfig]):
    """YAML配置管理器"""

    def load_config(self) -> TradingConfig:
        """加载配置文件"""
        return self._load_config(self._config_class())

    def save_config(self, config: TradingConfig):
        """保存配置到文件"""
        self._save_config(config)

    def _config_class(self) -> Type[TradingConfig]:
        return TradingConfig

    def _create_default_config(self) -> TradingConfig:
        """创建默认配置"""
        return TradingConfig()


class DelayConfigManager(BaseConfigManager[DelayConfig]):
    """延迟配置管理器"""

    def __init__(self, config_path: str = None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_path = os.path.join(base_dir, "config", "timing_config.yaml")
        super().__init__(config_path)

    def load_config(self) -> DelayConfig:
        """加载配置文件"""
        return self._load_config(DelayConfig)

    def save_config(self, config: DelayConfig) -> None:
        """保存配置到YAML文件"""
        self._save_config(config)

    def _config_class(self) -> Type[DelayConfig]:
        return DelayConfig

    def _create_default_config(self) -> DelayConfig:
        """创建基于当前硬编码值的默认配置"""
        return DelayConfig(delays={
            "hoarding_mode": {
                "enter_action": 0.05,  # time.sleep(0.05) in prepare()
                "balance_detection": 0.0,  # self.action_executor.move_mouse() 无延迟
                "buy_operation": 0.0,  # 购买操作无额外延迟
                "refresh_operation": 0.01,  # time.sleep(0.01) in _execute_refresh()
                "escape_key": 0.0,  # 按ESC键无延迟
                "re_enter": 0.0  # 重新进入无延迟
            },
            "rolling_mode": {
                "balance_detection": 0.3,  # time.sleep(0.3) in _detect_balance()
                "initialization": 0.4,  # time.sleep(0.4) in prepare()
                "enter_action": 0.01,  # time.sleep(0.01) after _execute_enter()
                "option_switch": 0.05,  # time.sleep(0.05) after _switch_to_option()
                "price_detection_retry": 0.05,  # time.sleep(0.05) in price detection retry
                "buy_operation": 2.0,  # time.sleep(2) after _execute_buy()
                "purchase_check": 1.0,  # time.sleep(1) after purchase failure check
                "balance_update": 1.0,  # time.sleep(1) after balance detection
                "sell_preparation": 0.3,  # time.sleep(0.3) before sell operations
                "mail_operations": 2.0,  # time.sleep(2) in _execute_get_mail_half_coin()
                "refresh_final": 2.0,  # time.sleep(2) after final refresh
                "statistics_update": 0.4,  # time.sleep(0.4) in statistics update
                "storage_entry": 1.0,  # time.sleep(1) after entering storage
                "item_transfer": 1.0,  # time.sleep(1) after transfer all
                "sell_interface_wait": 0.7,  # time.sleep(0.7) after sell button click
                "sell_retry": 1.0,  # time.sleep(1) in sell retry logic
                "item_hover": 0.3,  # time.sleep(0.3) after mouse move to item
                "right_click_wait": 0.5,  # time.sleep(0.5) after right click
                "sell_window_wait": 1.0,  # time.sleep(1) waiting for sell window
                "price_setting": 1.0,  # time.sleep(1) after price setting operations
                "price_input": 0.5,  # time.sleep(0.5) for price input operations
                "sell_detail_hover": 0.3,  # time.sleep(0.3) after hovering sell detail
                "transaction_confirm": 1.0,  # time.sleep(1) after final sell confirmation
                "mail_button_click": 1.0  # time.sleep(1) after mail button operations
            }
        })
