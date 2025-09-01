#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
滚仓配置迁移和验证测试
测试快速售卖阈值配置的迁移、序列化和验证逻辑
"""
import os
import shutil
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.config_manager import TradingConfigManager
from src.config.trading_config import ItemType, TradingConfig, TradingMode


class TestRollingConfigMigration:
    """滚仓配置迁移测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.yaml")

    def teardown_method(self):
        """每个测试方法后的清理"""
        shutil.rmtree(self.temp_dir)

    def test_new_rolling_option_structure_serialization(self):
        """测试新配装选项结构的序列化"""
        # 创建包含快速售卖阈值的配装选项
        rolling_options = [
            {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980, "fast_sell_threshold": 100000},
            {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980, "fast_sell_threshold": 0},
            {"buy_price": 1700, "min_buy_price": 700, "buy_count": 1740, "fast_sell_threshold": 500000},
        ]

        config = TradingConfig(rolling_options=rolling_options)

        # 验证配置创建成功
        assert len(config.rolling_options) == 3
        assert config.rolling_options[0]["fast_sell_threshold"] == 100000
        assert config.rolling_options[1]["fast_sell_threshold"] == 0
        assert config.rolling_options[2]["fast_sell_threshold"] == 500000

        # 测试序列化
        config_dict = config.to_dict()
        assert "rolling_options" in config_dict
        assert len(config_dict["rolling_options"]) == 3
        assert config_dict["rolling_options"][0]["fast_sell_threshold"] == 100000

    def test_new_rolling_option_structure_deserialization(self):
        """测试新配装选项结构的反序列化"""
        config_dict = {
            "trading_mode": 0,
            "item_type": 0,
            "rolling_options": [
                {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980, "fast_sell_threshold": 100000},
                {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980, "fast_sell_threshold": 0},
                {"buy_price": 1700, "min_buy_price": 700, "buy_count": 1740, "fast_sell_threshold": 500000},
            ],
        }

        config = TradingConfig.from_dict(config_dict)

        # 验证反序列化成功
        assert len(config.rolling_options) == 3
        assert config.rolling_options[0]["fast_sell_threshold"] == 100000
        assert config.rolling_options[1]["fast_sell_threshold"] == 0
        assert config.rolling_options[2]["fast_sell_threshold"] == 500000

    def test_backward_compatibility_missing_fast_sell_threshold(self):
        """测试向后兼容性：加载缺少 fast_sell_threshold 的旧配置"""
        # 模拟旧配置格式（没有 fast_sell_threshold 字段）
        legacy_rolling_options = [
            {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980},
            {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980},
            {"buy_price": 1700, "min_buy_price": 700, "buy_count": 1740},
        ]

        config = TradingConfig(rolling_options=legacy_rolling_options)

        # 验证自动添加了默认的 fast_sell_threshold
        assert len(config.rolling_options) == 3
        for option in config.rolling_options:
            assert "fast_sell_threshold" in option
            assert option["fast_sell_threshold"] == 0  # 默认值应该是0

    def test_backward_compatibility_from_dict(self):
        """测试从字典反序列化时的向后兼容性"""
        legacy_config_dict = {
            "trading_mode": 0,
            "item_type": 0,
            "rolling_options": [
                {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980},  # 缺少 fast_sell_threshold
                {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980},  # 缺少 fast_sell_threshold
            ],
        }

        config = TradingConfig.from_dict(legacy_config_dict)

        # 验证自动添加了默认的 fast_sell_threshold
        assert len(config.rolling_options) == 2
        for option in config.rolling_options:
            assert "fast_sell_threshold" in option
            assert option["fast_sell_threshold"] == 0

    def test_default_value_handling_zero_threshold(self):
        """测试默认值处理逻辑：fast_sell_threshold 为 0 时的行为"""
        rolling_options = [
            {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980, "fast_sell_threshold": 0},
            {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980, "fast_sell_threshold": 0},
        ]

        config = TradingConfig(rolling_options=rolling_options)

        # 验证阈值为0的配装选项保持不变（表示总是启用快速售卖）
        assert config.rolling_options[0]["fast_sell_threshold"] == 0
        assert config.rolling_options[1]["fast_sell_threshold"] == 0

    def test_negative_threshold_reset_to_zero(self):
        """测试负数阈值重置为0的逻辑"""
        rolling_options = [
            {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980, "fast_sell_threshold": -100},
            {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980, "fast_sell_threshold": -50},
        ]

        config = TradingConfig(rolling_options=rolling_options)

        # 验证负数阈值被重置为0
        assert config.rolling_options[0]["fast_sell_threshold"] == 0
        assert config.rolling_options[1]["fast_sell_threshold"] == 0

    def test_mixed_configuration_migration(self):
        """测试混合配置的迁移：部分有阈值，部分没有"""
        mixed_rolling_options = [
            {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980, "fast_sell_threshold": 100000},  # 有阈值
            {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980},  # 没有阈值
            {"buy_price": 1700, "min_buy_price": 700, "buy_count": 1740, "fast_sell_threshold": 0},  # 阈值为0
        ]

        config = TradingConfig(rolling_options=mixed_rolling_options)

        # 验证混合配置处理正确
        assert config.rolling_options[0]["fast_sell_threshold"] == 100000  # 保持原值
        assert config.rolling_options[1]["fast_sell_threshold"] == 0  # 自动添加默认值
        assert config.rolling_options[2]["fast_sell_threshold"] == 0  # 保持原值

    def test_config_validation_with_fast_sell_threshold(self):
        """测试包含快速售卖阈值的配置验证"""
        # 测试有效配置
        valid_rolling_options = [
            {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980, "fast_sell_threshold": 100000},
        ]

        config = TradingConfig(rolling_options=valid_rolling_options)
        # 应该不抛出异常
        assert len(config.rolling_options) == 1

        # 测试无效配置：缺少必需字段
        invalid_rolling_options = [
            {"buy_price": 520, "min_buy_price": 300},  # 缺少 buy_count
        ]

        with pytest.raises(ValueError, match="缺少必需字段"):
            TradingConfig(rolling_options=invalid_rolling_options)

    def test_config_validation_negative_values(self):
        """测试配置验证：负数值处理"""
        # 测试负数快速售卖阈值（应该被重置为0，不抛出异常）
        rolling_options_negative_threshold = [
            {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980, "fast_sell_threshold": -100},
        ]

        config = TradingConfig(rolling_options=rolling_options_negative_threshold)
        assert config.rolling_options[0]["fast_sell_threshold"] == 0

        # 测试其他负数值（应该抛出异常）
        rolling_options_negative_price = [
            {"buy_price": -520, "min_buy_price": 300, "buy_count": 4980, "fast_sell_threshold": 100000},
        ]

        with pytest.raises(ValueError, match="购买价格不能为负数"):
            TradingConfig(rolling_options=rolling_options_negative_price)

    def test_file_based_migration_integration(self):
        """测试基于文件的配置迁移集成"""
        manager = TradingConfigManager(self.config_path)

        # 创建旧格式配置并保存
        legacy_config = TradingConfig()
        legacy_config.rolling_options = [
            {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980},  # 缺少 fast_sell_threshold
            {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980},  # 缺少 fast_sell_threshold
        ]

        # 手动保存（模拟旧版本保存的配置）
        manager.save_config(legacy_config)

        # 重新加载配置
        loaded_config = manager.load_config()

        # 验证迁移成功
        assert len(loaded_config.rolling_options) == 2
        for option in loaded_config.rolling_options:
            assert "fast_sell_threshold" in option
            assert option["fast_sell_threshold"] == 0

    def test_default_rolling_options_have_fast_sell_threshold(self):
        """测试默认滚仓选项包含快速售卖阈值"""
        config = TradingConfig()  # 使用默认配置

        # 验证默认配置包含快速售卖阈值
        assert config.rolling_options is not None
        assert len(config.rolling_options) == 4  # 默认有4个选项

        for i, option in enumerate(config.rolling_options):
            assert "fast_sell_threshold" in option, f"默认选项 {i} 应该包含 fast_sell_threshold"
            assert option["fast_sell_threshold"] == 0, f"默认选项 {i} 的 fast_sell_threshold 应该为0"


def test_run_all_migration_tests():
    """运行所有迁移测试"""
    print("=== 开始滚仓配置迁移测试 ===")

    test_class = TestRollingConfigMigration()
    test_methods = [
        test_class.test_new_rolling_option_structure_serialization,
        test_class.test_new_rolling_option_structure_deserialization,
        test_class.test_backward_compatibility_missing_fast_sell_threshold,
        test_class.test_backward_compatibility_from_dict,
        test_class.test_default_value_handling_zero_threshold,
        test_class.test_negative_threshold_reset_to_zero,
        test_class.test_mixed_configuration_migration,
        test_class.test_config_validation_with_fast_sell_threshold,
        test_class.test_config_validation_negative_values,
        test_class.test_file_based_migration_integration,
        test_class.test_default_rolling_options_have_fast_sell_threshold,
    ]

    passed = 0
    total = len(test_methods)

    for test_method in test_methods:
        try:
            test_class.setup_method()
            test_method()
            test_class.teardown_method()
            print(f"✓ {test_method.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {test_method.__name__}: {e}")
            test_class.teardown_method()

    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")

    if passed == total:
        print("🎉 所有配置迁移测试通过！")
    else:
        print("❌ 部分测试失败")


if __name__ == "__main__":
    test_run_all_migration_tests()
