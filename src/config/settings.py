# -*- coding: utf-8 -*-
"""
配置管理模块
"""
import json
import os
from typing import Dict, Any
from pathlib import Path

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


class ResolutionConfig:
    """分辨率配置"""

    BASE_WIDTH = 2560
    BASE_HEIGHT = 1440

    # 坐标配置
    COORDINATES = {
        "price_detection": {
            "convertible": [2179 / 2560, 1078 / 1440, 2308 / 2560, 1102 / 1440],
            "non_convertible": [2179 / 2560, 1156 / 1440, 2308 / 2560, 1178 / 1440]
        },
        "balance_active": [2200 / 2560, 70 / 1440],
        "balance_detection": [1912 / 2560, 363 / 1440, 2324 / 2560, 387 / 1440],
        "buy_buttons": {
            "convertible_max": [0.9085, 0.7222],
            "convertible_min": [0.8095, 0.7222],
            "non_convertible_max": [2329 / 2560, 1112 / 1440],
            "non_convertible_min": [2059 / 2560, 1112 / 1440],
            "convertible_buy": [2189 / 2560, 0.7979],
            "non_convertible_buy": [2186 / 2560, 1225 / 1440]
        },
        "rolling_mode": {
            "options": [
                [244 / 2560, 404 / 1440],
                [244 / 2560, 500 / 1440],
                [244 / 2560, 591 / 1440],
                [244 / 2560, 690 / 1440]
            ],
            "price_area": [2128 / 2560, 1133 / 1440, 2413 / 2560, 1191 / 1440],
            "buy_button": [2245 / 2560, 1165 / 1440],
            "failure_check": [418 / 2560, 280 / 1440, 867 / 2560, 387 / 1440],

            "item_range": [84 / 2560, 84 / 1440],
            # 仓库前10行为等待售卖区域
            "wait_sell_item_area": [1651 / 2560, 177 / 1440, 2416 / 2560, 1028 / 1440],
            "enter_storage": [427 / 2560, 76 / 1440],
            "transfer_all": [390 / 2560, 1403 / 1440],
            "sell_button": [1877 / 2560, 939 / 1440],
            "sell_return_button": [1280 / 2560, 1258 / 1440]
        }
    }

    @classmethod
    def restore_coordinates(cls, target_width: int = 2560, target_height: int = 1440) -> Dict:
        """将比例坐标还原为目标分辨率下的绝对像素坐标

        Args:
            target_width: 目标宽度（像素）
            target_height: 目标高度（像素）

        Returns:
            包含绝对像素坐标的配置字典
        """

        def restore_coord(coord):
            if isinstance(coord, list):
                return [int(coord[i] * (target_width if i % 2 == 0 else target_height))
                        for i in range(len(coord))]
            elif isinstance(coord, tuple):
                return tuple(int(coord[i] * (target_width if i % 2 == 0 else target_height))
                             for i in range(len(coord)))
            return coord

        # 递归处理所有坐标
        def restore_dict(d):
            result = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    result[k] = restore_dict(v)
                elif isinstance(v, list):
                    if all(isinstance(item, (int, float)) for item in v):
                        result[k] = restore_coord(v)
                    else:
                        result[k] = [restore_coord(item) if isinstance(item, (list, tuple)) else item
                                     for item in v]
                else:
                    result[k] = v
            return result

        return restore_dict(cls.COORDINATES)


if __name__ == '__main__':
    res = ResolutionConfig.restore_coordinates(2560, 1440)
    print(ResolutionConfig.COORDINATES)
    print(res)
