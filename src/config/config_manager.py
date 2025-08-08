# -*- coding: utf-8 -*-
"""
配置管理模块
"""
import json
import os
from pathlib import Path
from typing import Dict, Any

import yaml

if __name__ == '__main__':
    from src.core.interfaces import TradingConfig, IConfigManager
    from src.core.exceptions import ConfigurationException
else:
    from ..core.interfaces import TradingConfig, IConfigManager
    from ..core.exceptions import ConfigurationException


class BaseConfigManager(IConfigManager):
    """基础配置管理器"""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "config",
                "settings.yaml"
            )
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> TradingConfig:
        raise NotImplementedError("not implemented")

    def save_config(self, config: TradingConfig):
        raise NotImplementedError("not implemented")

    def _load_config(self, loader, **load_params):
        try:
            if not self.config_path.exists():
                # 创建默认配置
                default_config = TradingConfig()
                self.save_config(default_config)
                return default_config

            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = loader.load(f, **load_params)

            return self._dict_to_config(data)
        except json.JSONDecodeError as e:
            raise ConfigurationException(f"JSON配置文件格式错误: {e}")
        except Exception as e:
            raise ConfigurationException(f"加载配置失败: {e}")

    def _save_config(self, config: TradingConfig, dumper, **dump_params) -> None:
        try:
            config_dict = self._config_to_dict(config)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                dumper.dump(config_dict, f, **dump_params)
        except Exception as e:
            raise ConfigurationException(f"保存配置失败: {e}")

    def update_config(self, updates: Dict[str, Any]) -> None:
        """更新配置"""
        try:
            config_dict = self._config_to_dict(self.load_config())
            config_dict.update(updates)
            new_config = self._dict_to_config(config_dict)
            self.save_config(new_config)

        except Exception as e:
            raise ConfigurationException(f"更新配置失败: {e}")


class YamlConfigManager(BaseConfigManager):
    """YAML配置管理器"""

    def __init__(self, config_path: str = None):
        super().__init__(config_path)

    def load_config(self) -> TradingConfig:
        """加载配置文件"""
        return self._load_config(yaml, Loader=yaml.SafeLoader)

    def save_config(self, config: TradingConfig):
        """保存配置到文件"""
        self._save_config(config, yaml, default_flow_style=False, allow_unicode=True, sort_keys=False)


class JsonConfigManager(BaseConfigManager):
    """JSON配置文件管理器"""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "config",
                "settings.json"
            )
        super().__init__(config_path)

    def load_config(self) -> TradingConfig:
        """加载配置文件"""
        return self._load_config(json)

    def save_config(self, config: TradingConfig) -> None:
        """保存配置到JSON文件"""
        self._save_config(config, json, indent=2, ensure_ascii=False)
