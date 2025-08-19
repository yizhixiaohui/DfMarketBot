# -*- coding: utf-8 -*-
"""
交易策略服务
"""
from typing import Any, Dict

from ..config.trading_config import TradingMode
from ..core.event_bus import event_bus
from ..core.interfaces import ITradingStrategy, MarketData, TradingConfig


class HoardingStrategy(ITradingStrategy):
    """屯仓模式交易策略"""

    def __init__(self, config: TradingConfig):
        self.config = config

    def _need_calc_unit_price(self, market_data: MarketData) -> bool:
        return self.config.use_balance_calculation and (
            market_data.last_balance is not None
            and market_data.balance is not None
            and 0 < market_data.last_balance != market_data.balance > 0
            and market_data.last_buy_quantity > 0
        )

    @staticmethod
    def _calc_unit_price(market_data: MarketData) -> float:
        if market_data.last_buy_quantity == 0:
            return 0
        return (market_data.last_balance - market_data.balance) / market_data.last_buy_quantity

    def should_buy(self, market_data: MarketData) -> bool:
        """判断是否该购买"""
        if market_data.last_buy_quantity != 0 and market_data.last_balance == market_data.balance:
            print("上次购买失败，直接看市场底价")
            event_bus.emit_overlay_text_updated("上次购买失败，直接看市场底价")
        if self._need_calc_unit_price(market_data):
            # 计算单价
            unit_price = self._calc_unit_price(market_data)
            if unit_price > 100:
                event_bus.emit_overlay_text_updated(f"上次购买单价: {unit_price}")
                return unit_price <= self.config.max_price
            print(f"单价计算异常({unit_price})，直接看市场底价")
            event_bus.emit_overlay_text_updated(f"单价计算异常({unit_price})，直接看市场底价")
        print("current_price:", market_data.current_price, "max_price:", self.config.max_price)
        return market_data.current_price <= int(self.config.max_price)

    def should_refresh(self, market_data: MarketData) -> bool:
        """判断是否该刷新"""
        return market_data.current_price > self.config.max_price

    def get_buy_quantity(self, market_data: MarketData) -> int:
        """获取购买数量"""
        # 默认购买200发
        buy_quantity = 200
        if self.config.key_mode:
            buy_quantity = 1
        elif self._need_calc_unit_price(market_data):
            # 计算单价
            unit_price = self._calc_unit_price(market_data)
            if unit_price >= 50:
                print("计算上次购买单价:", unit_price)
                event_bus.emit_overlay_text_updated(f"上次购买单价: {unit_price}")
                if self.config.ideal_price < unit_price <= self.config.max_price:
                    buy_quantity = 31
                elif unit_price <= self.config.ideal_price:
                    buy_quantity = 200
                else:
                    buy_quantity = 0
                return buy_quantity
            print(f"单价计算异常({unit_price})，直接看市场底价")
        elif (
            self.config.use_balance_calculation
            and self.config.ideal_price < market_data.current_price <= self.config.max_price
        ):
            buy_quantity = 31
        elif market_data.current_price > self.config.max_price:
            buy_quantity = 0
        return buy_quantity


class RefreshOnlyStrategy(ITradingStrategy):
    """仅刷新策略（用于价格高于理想值时）"""

    def __init__(self, config):
        self.last_balance = None
        self.last_buy_quantity = 0
        self.config = config

    def should_buy(self, market_data: MarketData) -> bool:
        return False

    def should_refresh(self, market_data: MarketData) -> bool:
        print("理想价格:", self.config.ideal_price)
        return self.config.max_price >= market_data.current_price > self.config.ideal_price

    def get_buy_quantity(self, market_data: MarketData) -> int:
        return 31

    def update_balance_info(self, balance: float, buy_quantity: int) -> None:
        """更新余额和购买数量信息"""
        self.last_balance = balance
        self.last_buy_quantity = buy_quantity


class RollingStrategy(ITradingStrategy):
    """滚仓模式交易策略"""

    def __init__(self, config: TradingConfig):
        self.config = config

    def should_buy(self, market_data: MarketData) -> bool:
        """判断是否该购买"""
        if self.config.trading_mode != TradingMode.ROLLING:
            return False

        if self.config.rolling_option >= len(self.config.rolling_options):
            return False
        option_config = self.config.rolling_options[self.config.rolling_option]

        target_price = option_config["buy_price"] * option_config["buy_count"]
        min_price = option_config["min_buy_price"] * option_config["buy_count"]

        return min_price < market_data.current_price <= target_price

    def should_refresh(self, market_data: MarketData) -> bool:
        """判断是否该刷新"""
        if self.config.trading_mode != TradingMode.ROLLING:
            return False

        if self.config.rolling_option >= len(self.config.rolling_options):
            return False
        option_config = self.config.rolling_options[self.config.rolling_option]

        target_price = option_config["buy_price"] * option_config["buy_count"]
        return market_data.current_price > target_price

    def get_buy_quantity(self, market_data: MarketData) -> int:
        """获取购买数量"""
        if self.config.trading_mode != TradingMode.ROLLING:
            return 0

        if self.config.rolling_option >= len(self.config.rolling_options):
            return 0
        option_config = self.config.rolling_options[self.config.rolling_option]
        return option_config["buy_count"]

    def get_option_config(self, option_index: int) -> Dict[str, Any]:
        """获取配装选项配置"""
        if option_index >= len(self.config.rolling_options):
            return {}
        return self.config.rolling_options[option_index]


class StrategyFactory:
    """策略工厂"""

    @staticmethod
    def create_strategy(config: TradingConfig) -> ITradingStrategy:
        """根据配置创建策略"""
        if config.trading_mode == TradingMode.ROLLING:
            return RollingStrategy(config)
        return HoardingStrategy(config)

    @staticmethod
    def create_refresh_strategy(config: TradingConfig) -> ITradingStrategy:
        """创建刷新策略"""
        return RefreshOnlyStrategy(config)
