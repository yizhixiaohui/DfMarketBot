# -*- coding: utf-8 -*-
"""
配置管理模块
"""
import json
import os
from typing import Dict, Any
from pathlib import Path

from ..core.interfaces import TradingConfig, IConfigManager
from ..core.exceptions import ConfigurationException


class JsonConfigManager(IConfigManager):
    """JSON配置文件管理器"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "config",
                "settings.json"
            )
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> TradingConfig:
        """从JSON文件加载配置"""
        try:
            if not self.config_path.exists():
                # 创建默认配置
                default_config = TradingConfig()
                self.save_config(default_config)
                return default_config
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return TradingConfig(**data)
        except Exception as e:
            raise ConfigurationException(f"加载配置失败: {e}")
    
    def save_config(self, config: TradingConfig) -> None:
        """保存配置到JSON文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config.__dict__, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ConfigurationException(f"保存配置失败: {e}")
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """更新配置"""
        config = self.load_config()
        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)
        self.save_config(config)
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "config",
                "settings.json"
            )
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> TradingConfig:
        """从JSON文件加载配置"""
        try:
            if not self.config_path.exists():
                # 创建默认配置
                default_config = TradingConfig()
                self.save_config(default_config)
                return default_config
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return TradingConfig(**data)
        except Exception as e:
            raise ConfigurationException(f"加载配置失败: {e}")
    
    def save_config(self, config: TradingConfig) -> None:
        """保存配置到JSON文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config.__dict__, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ConfigurationException(f"保存配置失败: {e}")
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """更新配置"""
        config = self.load_config()
        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)
        self.save_config(config)


# 向后兼容的别名
ConfigManager = JsonConfigManager


class ResolutionConfig:
    """分辨率配置"""
    
    BASE_WIDTH = 2560
    BASE_HEIGHT = 1440
    
    # 坐标配置
    COORDINATES = {
        "price_detection": {
            "convertible": [2179/2560, 1078/1440, 2308/2560, 1102/1440],
            "non_convertible": [2179/2560, 1156/1440, 2308/2560, 1178/1440]
        },
        "balance_detection": [1912/2560, 363/1440, 2324/2560, 387/1440],
        "buy_buttons": {
            "convertible_max": [0.9085, 0.7222],
            "convertible_min": [0.8095, 0.7222],
            "non_convertible_max": [2329/2560, 1112/1440],
            "non_convertible_min": [2059/2560, 1112/1440],
            "convertible_buy": [2189/2560, 0.7979],
            "non_convertible_buy": [2186/2560, 1225/1440]
        },
        "rolling_mode": {
            "options": [
                [244/2560, 404/1440],
                [244/2560, 500/1440],
                [244/2560, 591/1440],
                [244/2560, 690/1440]
            ],
            "price_area": [2128/2560, 1133/1440, 2413/2560, 1191/1440],
            "buy_button": [2245/2560, 1165/1440],
            "failure_check": [418/2560, 280/1440, 867/2560, 387/1440]
        }
    }
    
    @classmethod
    def scale_coordinates(cls, target_width: int, target_height: int) -> Dict:
        """根据目标分辨率缩放坐标"""
        scale_x = target_width / cls.BASE_WIDTH
        scale_y = target_height / cls.BASE_HEIGHT
        
        def scale_coord(coord):
            if isinstance(coord, list):
                return [coord[0] * scale_x if i % 2 == 0 else coord[i] * scale_y 
                       for i in range(len(coord))]
            elif isinstance(coord, tuple):
                return (coord[0] * scale_x, coord[1] * scale_y)
            return coord
        
        # 递归缩放所有坐标
        def scale_dict(d):
            result = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    result[k] = scale_dict(v)
                elif isinstance(v, list):
                    if all(isinstance(item, (int, float)) for item in v):
                        result[k] = scale_coord(v)
                    else:
                        result[k] = [scale_coord(item) if isinstance(item, list) else item for item in v]
                else:
                    result[k] = v
            return result
        
        return scale_dict(cls.COORDINATES)