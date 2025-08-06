# -*- coding: utf-8 -*-
"""
核心接口定义层
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np


class TradingMode(Enum):
    """交易模式枚举"""
    HOARDING = 0  # 屯仓模式 - 交易页面购买
    ROLLING = 1   # 滚仓模式 - 配装页面购买


class ItemType(Enum):
    """物品类型枚举"""
    CONVERTIBLE = 0
    NON_CONVERTIBLE = 1


@dataclass
class TradingConfig:
    """交易配置数据类"""
    ideal_price: int = 0
    key_mode: bool = False
    max_price: int = 0
    loop_interval: int = 50
    item_type: ItemType = ItemType.CONVERTIBLE
    use_balance_calculation: bool = False
    trading_mode: TradingMode = TradingMode.HOARDING
    rolling_option: int = 0  # 滚仓模式下的配装选项
    screen_width: int = 2560
    screen_height: int = 1440
    tesseract_path: str = ""
    log_level: str = "INFO"

    def __post_init__(self):
        """验证配置参数"""
        if self.ideal_price < 0:
            raise ValueError("理想价格不能为负数")
        if self.max_price < 0:
            raise ValueError("最高价格不能为负数")
        if self.loop_interval <= 0:
            raise ValueError("循环间隔必须大于0")
        if self.screen_width <= 0 or self.screen_height <= 0:
            raise ValueError("屏幕分辨率必须大于0")
        
        # 处理整数到枚举的转换
        if isinstance(self.trading_mode, int):
            self.trading_mode = TradingMode(self.trading_mode)
        if isinstance(self.item_type, int):
            self.item_type = ItemType(self.item_type)


@dataclass
class MarketData:
    """市场数据"""
    current_price: int
    balance: Optional[int] = None
    last_balance: Optional[int] = None
    last_buy_quantity: Optional[int] = None
    timestamp: float = 0.0


class IPriceDetector(ABC):
    """价格检测器接口"""
    
    @abstractmethod
    def detect_price(self) -> int:
        """检测当前物品价格"""
        pass
    
    @abstractmethod
    def detect_balance(self) -> Optional[int]:
        """检测当前哈夫币余额"""
        pass


class IActionExecutor(ABC):
    """动作执行器接口"""
    
    @abstractmethod
    def click_position(self, position: Tuple[float, float]) -> None:
        """点击指定位置"""
        pass
    
    @abstractmethod
    def press_key(self, key: str) -> None:
        """按下键盘按键"""
        pass
    
    @abstractmethod
    def move_mouse(self, position: Tuple[float, float]) -> None:
        """移动鼠标到指定位置"""
        pass


class ITradingStrategy(ABC):
    """交易策略接口"""
    
    @abstractmethod
    def should_buy(self, market_data: MarketData) -> bool:
        """判断是否该购买"""
        pass
    
    @abstractmethod
    def should_refresh(self, market_data: MarketData) -> bool:
        """判断是否该刷新"""
        pass
    
    @abstractmethod
    def get_buy_quantity(self, market_data: MarketData) -> int:
        """获取购买数量"""
        pass


class ITradingMode(ABC):
    """交易模式接口"""
    @abstractmethod
    def prepare(self) -> None:
        pass
    
    @abstractmethod
    def execute_cycle(self) -> bool:
        """执行一个交易周期，返回是否继续"""
        pass
    
    @abstractmethod
    def initialize(self, config: TradingConfig) -> None:
        """初始化模式"""
        pass
    
    @abstractmethod
    def get_market_data(self) -> Optional[MarketData]:
        """获取当前市场数据"""
        pass


class ILogger(ABC):
    """日志接口"""
    
    @abstractmethod
    def info(self, message: str) -> None:
        pass
    
    @abstractmethod
    def error(self, message: str) -> None:
        pass
    
    @abstractmethod
    def debug(self, message: str) -> None:
        pass


class IConfigManager(ABC):
    """配置管理器接口"""
    
    @abstractmethod
    def load_config(self) -> TradingConfig:
        """加载配置"""
        pass
    
    @abstractmethod
    def save_config(self, config: TradingConfig) -> None:
        """保存配置"""
        pass
    
    @abstractmethod
    def update_config(self, updates: Dict[str, Any]) -> None:
        """更新配置"""
        pass


class IOCREngine(ABC):
    """OCR引擎接口"""
    
    @abstractmethod
    def image_to_string(self, image: np.ndarray) -> str:
        """将图像转换为字符串"""
        pass
    
    @abstractmethod
    def detect_template(self, image: np.ndarray, template_path: str = None) -> bool:
        """检测模板匹配"""
        pass


class ITradingService(ABC):
    """交易服务接口"""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """初始化交易服务"""
        pass

    @abstractmethod
    def prepare(self) -> None:
        pass
    
    @abstractmethod
    def execute_cycle(self) -> bool:
        """执行一个交易周期"""
        pass
    
    @abstractmethod
    def get_market_data(self) -> Optional[MarketData]:
        """获取当前市场数据"""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """停止交易服务"""
        pass
