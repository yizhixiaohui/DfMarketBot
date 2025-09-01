#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器测试
测试新的统一配置管理器架构
"""
import os
import shutil
import sys
import tempfile

from src.config.trading_config import ItemType, TradingConfig, TradingMode

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.config_manager import TradingConfigManager


def test_trading_config_manager():
    """测试YAML配置管理器"""
    print("=== 测试trading配置管理器 ===")

    temp_dir = tempfile.mkdtemp()
    config_path = os.path.join(temp_dir, "test.yaml")

    try:
        # 创建管理器
        manager = TradingConfigManager(config_path)

        # 测试加载默认配置
        config = manager.load_config()
        assert isinstance(config, TradingConfig), "应该返回TradingConfig实例"
        assert config.trading_mode == TradingMode.HOARDING, "默认模式应该是HOARDING"
        assert len(config.rolling_options) == 4, "应该有4个默认滚仓选项"
        print("✓ 默认配置加载成功")

        # 测试保存配置
        config.ideal_price = 1000
        config.max_price = 2000
        manager.save_config(config)

        # 验证文件存在
        assert os.path.exists(config_path), "配置文件应该被创建"

        # 重新加载验证
        new_manager = TradingConfigManager(config_path)
        new_config = new_manager.load_config()
        assert new_config.ideal_price == 1000, "保存的值应该被正确加载"
        assert new_config.max_price == 2000, "保存的值应该被正确加载"
        print("✓ 配置保存和重新加载成功")

        # 测试更新配置
        manager.update_config({"ideal_price": 1500, "hoarding_loop_interval": 100})
        updated_config = manager.load_config()
        assert updated_config.ideal_price == 1500, "更新应该生效"
        assert updated_config.hoarding_loop_interval == 100, "更新应该生效"
        print("✓ 配置更新成功")

        # 测试YAML格式
        with open(config_path, "r", encoding="utf-8") as f:
            yaml_content = f.read()
        assert "ideal_price: 1500" in yaml_content, "YAML应该包含更新的值"
        assert "hoarding_loop_interval: 100" in yaml_content, "YAML应该包含更新的值"
        print("✓ YAML格式正确")

    finally:
        shutil.rmtree(temp_dir)


def test_rolling_options_config():
    """测试滚仓选项配置"""
    print("\n=== 测试滚仓选项配置 ===")

    temp_dir = tempfile.mkdtemp()
    config_path = os.path.join(temp_dir, "test.yaml")

    try:
        manager = TradingConfigManager(config_path)

        # 测试自定义滚仓选项
        custom_options = [
            {"buy_price": 1000, "min_buy_price": 500, "buy_count": 1000},
            {"buy_price": 2000, "min_buy_price": 1000, "buy_count": 2000},
            {"buy_price": 3000, "min_buy_price": 1500, "buy_count": 3000},
        ]

        manager.update_config({"rolling_options": custom_options})

        # 验证加载
        config = manager.load_config()
        assert len(config.rolling_options) == 3, "应该有3个自定义选项"
        assert config.rolling_options[0]["buy_price"] == 1000, "第一个选项价格应该是1000"
        assert config.rolling_options[2]["buy_count"] == 3000, "第三个选项数量应该是3000"
        print("✓ 自定义滚仓选项配置成功")

    finally:
        shutil.rmtree(temp_dir)


def test_enum_serialization():
    """测试枚举类型序列化"""
    print("\n=== 测试枚举类型序列化 ===")

    temp_dir = tempfile.mkdtemp()

    try:
        # 测试YAML
        yaml_path = os.path.join(temp_dir, "enum_test.yaml")
        manager = TradingConfigManager(yaml_path)

        config = manager.load_config()
        config.trading_mode = TradingMode.ROLLING
        config.item_type = ItemType.NON_CONVERTIBLE
        manager.save_config(config)

        # 重新加载验证
        reloaded = manager.load_config()
        assert reloaded.trading_mode == TradingMode.ROLLING, "YAML应该正确序列化枚举"
        assert reloaded.item_type == ItemType.NON_CONVERTIBLE, "YAML应该正确序列化枚举"
        print("✓ YAML枚举序列化成功")

    finally:
        shutil.rmtree(temp_dir)


def test_base_config_manager():
    """测试基础配置管理器"""
    print("\n=== 测试基础配置管理器 ===")

    temp_dir = tempfile.mkdtemp()

    try:
        # 测试BaseConfigManager不能直接实例化
        base_path = os.path.join(temp_dir, "base.json")

        # 测试子类功能
        trading_manager = TradingConfigManager(base_path)
        assert hasattr(trading_manager, "load_config"), "应该有load_config方法"
        assert hasattr(trading_manager, "save_config"), "应该有save_config方法"
        assert hasattr(trading_manager, "update_config"), "应该有update_config方法"
        print("✓ 基础配置管理器功能正确")

    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("开始测试配置管理器...")

    tests = [
        test_trading_config_manager,
        test_rolling_options_config,
        test_enum_serialization,
        test_base_config_manager,
    ]

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
        print("🎉 所有配置管理器测试通过！")
    else:
        print("❌ 部分测试失败")
