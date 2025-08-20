#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试滚仓配置动态加载功能
"""
import os
import sys

import pytest

from src.config.config_manager import TradingConfigManager as ConfigManager
from src.core.interfaces import MarketData
from src.services.strategy import RollingStrategy

# 自动添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def config_manager():
    """Fixture to initialize the ConfigManager"""
    return ConfigManager()


@pytest.fixture
def config(config_manager):
    """Fixture to load the configuration"""
    return config_manager.load_config()


def test_rolling_config_loading(config):
    """测试滚仓配置加载"""
    print("=== 测试滚仓配置动态加载 ===")

    # 验证配置包含滚仓选项
    print("✓ 配置文件加载成功")
    print(f"  - 当前滚仓选项: {config.rolling_option}")
    print(f"  - 可用滚仓选项: {len(config.rolling_options)} 个")

    # 测试每个滚仓选项
    for i, option_config in enumerate(config.rolling_options):
        print(f"\n  选项 {i}: {option_config}")

    # 测试策略类使用配置
    strategy = RollingStrategy(config)

    # 模拟市场数据测试
    MarketData(current_price=1000000)  # 测试价格

    # 测试不同选项
    for i in range(4):
        # 更新配置
        config.rolling_option = i
        strategy.config = config

        if i < len(config.rolling_options):
            option_config = config.rolling_options[i]
            target_price = option_config["buy_price"] * option_config["buy_count"]
            min_price = option_config["min_buy_price"] * option_config["buy_count"]

            print(f"\n选项 {i}:")
            print(f"  目标价格: {target_price}")
            print(f"  最低价格: {min_price}")
            print(f"  购买数量: {option_config['buy_count']}")
            assert target_price > 0
            assert min_price > 0


def test_config_hot_reload(config_manager, config):
    """测试配置热更新"""
    print("\n=== 测试配置热更新 ===")

    # 修改配置
    original_option = config.rolling_option
    new_option = (original_option + 1) % 4

    # 更新配置
    config_manager.update_config({"rolling_option": new_option})

    # 重新加载验证
    updated_config = config_manager.load_config()
    print("✓ 配置热更新成功")
    print(f"  - 原选项: {original_option}")
    print(f"  - 新选项: {updated_config.rolling_option}")

    # 验证选项是否正确更新
    assert updated_config.rolling_option == new_option, "选项更新失败"

    # 恢复原始配置
    config_manager.update_config({"rolling_option": original_option})


def test_custom_rolling_options(config_manager):
    """测试自定义滚仓选项"""
    print("\n=== 测试自定义滚仓选项 ===")

    # 添加新的自定义选项
    custom_options = [
        {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980},
        {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980},
        {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980},
        {"buy_price": 1700, "min_buy_price": 700, "buy_count": 1740},
    ]

    # 更新配置
    config_manager.update_config({"rolling_options": custom_options})

    # 验证更新
    updated_config = config_manager.load_config()
    print("✓ 自定义选项添加成功")
    print(f"  - 可用选项: {len(updated_config.rolling_options)} 个")
    print(f"  - 新选项4: {updated_config.rolling_options[4] if len(updated_config.rolling_options) > 4 else '不存在'}")

    assert len(updated_config.rolling_options) == 4, "自定义选项数量不正确"
    assert updated_config.rolling_options[3] == custom_options[3], "自定义选项内容不正确"


if __name__ == "__main__":
    print("开始测试滚仓配置动态加载功能...")

    tests = [test_rolling_config_loading, test_config_hot_reload, test_custom_rolling_options]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ 测试失败: {e}")

    print("\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")

    if passed == total:
        print("🎉 所有测试通过！滚仓配置动态加载功能正常")
    else:
        print("❌ 部分测试失败")
