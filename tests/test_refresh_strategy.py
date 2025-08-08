#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试RefreshOnlyStrategy的余额计算逻辑
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.strategy import RefreshOnlyStrategy
from src.core.interfaces import TradingConfig, MarketData, ItemType

def test_refresh_strategy():
    """测试RefreshOnlyStrategy的余额计算逻辑"""
    print("=== 测试RefreshOnlyStrategy余额计算逻辑 ===")
    
    # 创建策略实例
    strategy = RefreshOnlyStrategy()
    
    # 创建配置
    config = TradingConfig(
        ideal_price=1000,
        max_price=2000,
        item_type=ItemType.CONVERTIBLE
    )
    
    # 测试场景1: 真实单价低于理想价格
    print("\n--- 测试场景1: 真实单价低于理想价格 ---")
    strategy.update_balance_info(balance=10000, buy_quantity=31)
    market_data = MarketData(
        current_price=1200,
        balance=6900  # 10000 - (1000 * 31) = 6900，真实单价=1000
    )
    quantity = strategy.get_buy_quantity(config, market_data)
    print(f"余额: 10000 -> 6900, 购买数量: 31")
    print(f"真实单价: {(10000-6900)/31:.2f}, 理想价格: {config.ideal_price}")
    print(f"预期购买数量: 200, 实际: {quantity}")
    assert quantity == 200, f"期望200，实际{quantity}"
    
    # 测试场景2: 真实单价高于理想价格但低于最高价格
    print("\n--- 测试场景2: 真实单价高于理想价格但低于最高价格 ---")
    strategy.update_balance_info(balance=10000, buy_quantity=31)
    market_data = MarketData(
        current_price=1500,
        balance=6513  # 10000 - (1127 * 31) = 6513，真实单价=1127
    )
    quantity = strategy.get_buy_quantity(config, market_data)
    print(f"余额: 10000 -> 6513, 购买数量: 31")
    print(f"真实单价: {(10000-6513)/31:.2f}, 理想价格: {config.ideal_price}, 最高价格: {config.max_price}")
    print(f"预期购买数量: 31, 实际: {quantity}")
    assert quantity == 31, f"期望31，实际{quantity}"
    
    # 测试场景3: 真实单价高于最高价格
    print("\n--- 测试场景3: 真实单价高于最高价格 ---")
    strategy.update_balance_info(balance=10000, buy_quantity=31)
    market_data = MarketData(
        current_price=2500,
        balance=3790  # 10000 - (2003 * 31) = 3790，真实单价=2003
    )
    quantity = strategy.get_buy_quantity(config, market_data)
    print(f"余额: 10000 -> 3790, 购买数量: 31")
    print(f"真实单价: {(10000-3790)/31:.2f}, 最高价格: {config.max_price}")
    print(f"预期购买数量: 0, 实际: {quantity}")
    assert quantity == 0, f"期望0，实际{quantity}"
    
    # 测试场景4: 首次运行（无余额信息）
    print("\n--- 测试场景4: 首次运行（无余额信息） ---")
    strategy = RefreshOnlyStrategy()  # 重置策略
    market_data = MarketData(current_price=1200, balance=None)
    quantity = strategy.get_buy_quantity(config, market_data)
    print(f"无余额信息时的默认购买数量: {quantity}")
    assert quantity == 31, f"期望31，实际{quantity}"
    
    print("\n✅ 所有测试通过！RefreshOnlyStrategy余额计算逻辑正确")

if __name__ == "__main__":
    test_refresh_strategy()