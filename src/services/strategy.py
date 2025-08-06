# -*- coding: utf-8 -*-
"""
交易策略服务
"""
from typing import Dict, Any

from ..core.interfaces import ITradingStrategy, TradingConfig, MarketData, ItemType, TradingMode


class HoardingStrategy(ITradingStrategy):
    """屯仓模式交易策略"""
    def __init__(self, config):
        self.config = config

    @staticmethod
    def _need_calc_unit_price(market_data: MarketData) -> bool:
        return (market_data.balance is not None
                and market_data.last_balance is not None
                and 0 < market_data.last_balance != market_data.balance > 0
                and market_data.last_buy_quantity > 0)

    @staticmethod
    def _calc_unit_price(market_data: MarketData) -> float:
        if market_data.last_buy_quantity == 0:
            return 0
        return (market_data.last_balance - market_data.balance) / market_data.last_buy_quantity
    
    def should_buy(self, market_data: MarketData) -> bool:
        """判断是否该购买"""
        if self._need_calc_unit_price(market_data):
            # 计算单价
            unit_price = self._calc_unit_price(market_data)
            if unit_price > 100:
                return unit_price <= self.config.max_price
            print(f"单价计算异常({unit_price})，直接看市场底价")
        print('current_price:', market_data.current_price, 'max_price:', self.config.max_price)
        return market_data.current_price <= int(self.config.max_price)
    
    def should_refresh(self, market_data: MarketData) -> bool:
        """判断是否该刷新"""
        return market_data.current_price > self.config.max_price
    
    def get_buy_quantity(self, market_data: MarketData) -> int:
        """获取购买数量"""
        if self.config.key_mode:
            return 1
        if self._need_calc_unit_price(market_data):
            # 计算单价
            unit_price = self._calc_unit_price(market_data)
            print('计算上次购买单价:', unit_price)
            if self.config.ideal_price < unit_price <= self.config.max_price:
                return 31
            if unit_price <= self.config.ideal_price:
                return 200
            return 0
        if market_data.current_price > self.config.max_price:
            return 0
        if self.config.ideal_price < market_data.current_price <= self.config.max_price:
            return 31
        return 200  # 默认购买200发


class RefreshOnlyStrategy(ITradingStrategy):
    """仅刷新策略（用于价格高于理想值时）"""
    
    def __init__(self, config):
        self.last_balance = None
        self.last_buy_quantity = 0
        self.config = config
    
    def should_buy(self, market_data: MarketData) -> bool:
        return False
    
    def should_refresh(self, market_data: MarketData) -> bool:
        print('理想价格:', self.config.ideal_price)
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
    
    # 配装选项配置
    ROLLING_OPTIONS = {
        0: {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980},
        1: {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980},
        2: {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980},
        3: {"buy_price": 1700, "min_buy_price": 700, "buy_count": 1740}
    }
    
    def should_buy(self, market_data: MarketData) -> bool:
        """判断是否该购买"""
        if self.config.trading_mode != TradingMode.ROLLING:
            return False
            
        option_config = self.ROLLING_OPTIONS.get(self.config.rolling_option)
        if not option_config:
            return False
            
        target_price = option_config["buy_price"] * option_config["buy_count"]
        min_price = option_config["min_buy_price"] * option_config["buy_count"]
        
        return min_price < market_data.current_price <= target_price
    
    def should_refresh(self, market_data: MarketData) -> bool:
        """判断是否该刷新"""
        if self.config.trading_mode != TradingMode.ROLLING:
            return False
            
        option_config = self.ROLLING_OPTIONS.get(self.config.rolling_option)
        if not option_config:
            return False

        target_price = option_config["buy_price"] * option_config["buy_count"]
        return market_data.current_price > target_price
    
    def get_buy_quantity(self, market_data: MarketData) -> int:
        """获取购买数量"""
        if self.config.trading_mode != TradingMode.ROLLING:
            return 0
            
        option_config = self.ROLLING_OPTIONS.get(self.config.rolling_option)
        return option_config["buy_count"] if option_config else 0
    
    def get_option_config(self, option_index: int) -> Dict[str, Any]:
        """获取配装选项配置"""
        return self.ROLLING_OPTIONS.get(option_index, {})


class StrategyFactory:
    """策略工厂"""
    
    @staticmethod
    def create_strategy(config: TradingConfig) -> ITradingStrategy:
        """根据配置创建策略"""
        if config.trading_mode == TradingMode.ROLLING:
            return RollingStrategy(config)
        else:
            return HoardingStrategy(config)
    
    @staticmethod
    def create_refresh_strategy(config: TradingConfig) -> ITradingStrategy:
        """创建刷新策略"""
        return RefreshOnlyStrategy(config)