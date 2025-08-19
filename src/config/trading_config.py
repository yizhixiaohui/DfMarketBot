from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict


class TradingMode(Enum):
    """交易模式枚举"""

    ROLLING = 0  # 滚仓模式 - 配装页面购买
    HOARDING = 1  # 屯仓模式 - 交易页面购买


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
    rolling_loop_interval: int = 50
    hoarding_loop_interval: int = 150
    item_type: ItemType = ItemType.CONVERTIBLE
    use_balance_calculation: bool = False
    trading_mode: TradingMode = TradingMode.HOARDING
    rolling_option: int = 0  # 滚仓模式下的配装选项
    rolling_options: list = None  # 滚仓选项配置数组
    screen_width: int = 2560
    screen_height: int = 1440
    auto_sell: bool = True
    fast_sell: bool = True
    fast_sell_threshold: int = 200000
    log_level: str = "INFO"

    def __post_init__(self):
        """验证配置参数"""
        if self.ideal_price < 0:
            raise ValueError("理想价格不能为负数")
        if self.max_price < 0:
            raise ValueError("最高价格不能为负数")
        if self.rolling_loop_interval <= 0:
            raise ValueError("循环间隔必须大于0")
        if self.hoarding_loop_interval <= 0:
            raise ValueError("循环间隔必须大于0")
        if self.screen_width <= 0 or self.screen_height <= 0:
            raise ValueError("屏幕分辨率必须大于0")

        # 处理整数到枚举的转换
        if isinstance(self.trading_mode, int):
            self.trading_mode = TradingMode(self.trading_mode)
        if isinstance(self.item_type, int):
            self.item_type = ItemType(self.item_type)

        # 设置默认滚仓选项配置
        if self.rolling_options is None:
            self.rolling_options = [
                {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980},
                {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980},
                {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980},
                {"buy_price": 1700, "min_buy_price": 700, "buy_count": 1740},
            ]

    def to_dict(self):
        """序列化为 dict，枚举转 value"""
        config_dict = asdict(self)
        config_dict["trading_mode"] = config_dict["trading_mode"].value
        config_dict["item_type"] = config_dict["item_type"].value
        return config_dict

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "TradingConfig":
        """从 dict 反序列化，支持枚举"""
        # 处理枚举类型
        if "trading_mode" in config_dict and not isinstance(config_dict["trading_mode"], TradingMode):
            config_dict["trading_mode"] = TradingMode(config_dict["trading_mode"])
        if "item_type" in config_dict and not isinstance(config_dict["item_type"], ItemType):
            config_dict["item_type"] = ItemType(config_dict["item_type"])
        return cls(**config_dict)
