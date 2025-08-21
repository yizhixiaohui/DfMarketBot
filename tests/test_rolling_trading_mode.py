#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
滚仓交易模式测试
测试滚仓交易模式的快速售卖阈值逻辑
"""
import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.trading_config import TradingConfig
from src.services.trading_modes import RollingTradingMode


class TestRollingTradingMode(unittest.TestCase):
    """滚仓交易模式测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建模拟的依赖对象
        self.mock_detector = Mock()
        self.mock_action_executor = Mock()

        # 创建滚仓交易模式实例
        self.trading_mode = RollingTradingMode(self.mock_detector, self.mock_action_executor)

        # 创建测试配置
        self.test_config = TradingConfig()
        self.test_config.rolling_option = 0
        self.test_config.rolling_options = [
            {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980, "fast_sell_threshold": 100000},
            {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980, "fast_sell_threshold": 0},
            {"buy_price": 1700, "min_buy_price": 700, "buy_count": 1740, "fast_sell_threshold": 500000},
        ]

        # 初始化交易模式
        self.trading_mode.initialize(self.test_config)

    def test_get_current_fast_sell_threshold_valid_option(self):
        """测试 _get_current_fast_sell_threshold 方法返回正确的阈值 - 有效选项"""
        # 测试第一个配装选项
        self.trading_mode.config.rolling_option = 0
        threshold = self.trading_mode._get_fast_sell_threshold()
        self.assertEqual(threshold, 100000, "应该返回第一个配装的快速售卖阈值")

        # 测试第二个配装选项（阈值为0）
        self.trading_mode.config.rolling_option = 1
        threshold = self.trading_mode._get_fast_sell_threshold()
        self.assertEqual(threshold, 0, "应该返回第二个配装的快速售卖阈值0")

        # 测试第三个配装选项
        self.trading_mode.config.rolling_option = 2
        threshold = self.trading_mode._get_fast_sell_threshold()
        self.assertEqual(threshold, 500000, "应该返回第三个配装的快速售卖阈值")

    def test_get_current_fast_sell_threshold_invalid_option_index(self):
        """测试 _get_current_fast_sell_threshold 方法 - 无效选项索引"""
        # 测试负数索引
        self.trading_mode.config.rolling_option = -1
        threshold = self.trading_mode._get_fast_sell_threshold()
        self.assertEqual(threshold, 0, "无效索引应该返回默认值0")

        # 测试超出范围的索引
        self.trading_mode.config.rolling_option = 10
        threshold = self.trading_mode._get_fast_sell_threshold()
        self.assertEqual(threshold, 0, "超出范围的索引应该返回默认值0")

    def test_get_current_fast_sell_threshold_empty_options(self):
        """测试 _get_current_fast_sell_threshold 方法 - 空配装选项"""
        # 测试空配装选项列表
        self.trading_mode.option_configs = []
        threshold = self.trading_mode._get_fast_sell_threshold()
        self.assertEqual(threshold, 0, "空配装选项应该返回默认值0")

        # 测试None配装选项
        self.trading_mode.option_configs = None
        threshold = self.trading_mode._get_fast_sell_threshold()
        self.assertEqual(threshold, 0, "None配装选项应该返回默认值0")

    def test_get_current_fast_sell_threshold_missing_field(self):
        """测试 _get_current_fast_sell_threshold 方法 - 缺少快速售卖阈值字段"""
        # 创建缺少 fast_sell_threshold 字段的配装选项
        self.trading_mode.option_configs = [
            {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980}  # 缺少 fast_sell_threshold
        ]
        self.trading_mode.config.rolling_option = 0

        threshold = self.trading_mode._get_fast_sell_threshold()
        self.assertEqual(threshold, 0, "缺少快速售卖阈值字段应该返回默认值0")

    @patch("src.services.trading_modes.delay_helper")
    def test_set_sell_price_with_fast_sell_enabled_above_threshold(self, mock_delay_helper):
        """测试快速售卖逻辑 - 启用快速售卖且超过阈值"""
        # 设置模拟返回值
        self.mock_detector.coordinates = {
            "rolling_mode": {
                "sell_num_left": (100, 200),
                "sell_num_right": (300, 200),
                "sell_price_text": (150, 250),
                "min_sell_price_button": (200, 300),
            }
        }
        self.mock_detector.detect_min_sell_price.return_value = 150000
        self.mock_detector.detect_second_min_sell_price.return_value = 160000
        self.mock_detector.detect_min_sell_price_count.return_value = 200000  # 超过阈值100000

        # 设置当前配装为第一个（阈值100000）
        self.trading_mode.config.rolling_option = 0

        # 调用 _set_sell_price 方法，启用快速售卖
        result = self.trading_mode._set_sell_price(0.5, 0, fast_sell=True)

        # 验证快速售卖逻辑被触发
        self.mock_action_executor.click_position.assert_any_call(
            self.mock_detector.coordinates["rolling_mode"]["sell_price_text"]
        )
        self.mock_action_executor.multi_key_press.assert_called_with("ctrl", "a")
        self.mock_action_executor.type_text.assert_called()

        # 验证返回的最低售卖价格
        expected_price = 150000 - (160000 - 150000)  # 140000
        self.assertEqual(result, expected_price, "应该返回计算后的快速售卖价格")

    @patch("src.services.trading_modes.delay_helper")
    def test_set_sell_price_with_fast_sell_enabled_below_threshold(self, mock_delay_helper):
        """测试快速售卖逻辑 - 启用快速售卖但未超过阈值"""
        # 设置模拟返回值
        self.mock_detector.coordinates = {
            "rolling_mode": {
                "sell_num_left": (100, 200),
                "sell_num_right": (300, 200),
                "sell_price_text": (150, 250),
                "min_sell_price_button": (200, 300),
            }
        }
        self.mock_detector.detect_min_sell_price.return_value = 150000
        self.mock_detector.detect_second_min_sell_price.return_value = 160000
        self.mock_detector.detect_min_sell_price_count.return_value = 50000  # 低于阈值100000

        # 设置当前配装为第一个（阈值100000）
        self.trading_mode.config.rolling_option = 0

        # 调用 _set_sell_price 方法，启用快速售卖
        result = self.trading_mode._set_sell_price(0.5, 0, fast_sell=True)

        # 验证使用正常售卖逻辑（点击最低价格按钮）
        self.mock_action_executor.click_position.assert_any_call(
            self.mock_detector.coordinates["rolling_mode"]["min_sell_price_button"]
        )

        # 验证没有触发快速售卖的文本输入
        self.mock_action_executor.type_text.assert_not_called()

        # 验证返回的最低售卖价格
        self.assertEqual(result, 150000, "应该返回检测到的最低售卖价格")

    @patch("src.services.trading_modes.delay_helper")
    def test_set_sell_price_with_threshold_zero_always_fast_sell(self, mock_delay_helper):
        """测试阈值为0时总是启用快速售卖的边界条件"""
        # 设置模拟返回值
        self.mock_detector.coordinates = {
            "rolling_mode": {
                "sell_num_left": (100, 200),
                "sell_num_right": (300, 200),
                "sell_price_text": (150, 250),
                "min_sell_price_button": (200, 300),
            }
        }
        self.mock_detector.detect_min_sell_price.return_value = 150000
        self.mock_detector.detect_second_min_sell_price.return_value = 160000
        self.mock_detector.detect_min_sell_price_count.return_value = 1  # 任意小值

        # 设置当前配装为第二个（阈值为0）
        self.trading_mode.config.rolling_option = 1

        # 调用 _set_sell_price 方法，启用快速售卖
        result = self.trading_mode._set_sell_price(0.5, 0, fast_sell=True)

        # 验证快速售卖逻辑被触发（因为阈值为0）
        self.mock_action_executor.click_position.assert_any_call(
            self.mock_detector.coordinates["rolling_mode"]["sell_price_text"]
        )
        self.mock_action_executor.multi_key_press.assert_called_with("ctrl", "a")
        self.mock_action_executor.type_text.assert_called()

        # 验证返回的最低售卖价格
        expected_price = 150000 - (160000 - 150000)  # 140000
        self.assertEqual(result, expected_price, "阈值为0时应该总是启用快速售卖")

    @patch("src.services.trading_modes.delay_helper")
    def test_set_sell_price_with_fast_sell_disabled(self, mock_delay_helper):
        """测试快速售卖功能被禁用时的逻辑"""
        # 设置模拟返回值
        self.mock_detector.coordinates = {
            "rolling_mode": {
                "sell_num_left": (100, 200),
                "sell_num_right": (300, 200),
                "sell_price_text": (150, 250),
                "min_sell_price_button": (200, 300),
            }
        }
        self.mock_detector.detect_min_sell_price.return_value = 150000
        self.mock_detector.detect_second_min_sell_price.return_value = 160000
        self.mock_detector.detect_min_sell_price_count.return_value = 200000  # 超过阈值

        # 设置当前配装为第一个（阈值100000）
        self.trading_mode.config.rolling_option = 0

        # 调用 _set_sell_price 方法，禁用快速售卖
        result = self.trading_mode._set_sell_price(0.5, 0, fast_sell=False)

        # 验证使用正常售卖逻辑（点击最低价格按钮）
        self.mock_action_executor.click_position.assert_any_call(
            self.mock_detector.coordinates["rolling_mode"]["min_sell_price_button"]
        )

        # 验证没有触发快速售卖的文本输入
        self.mock_action_executor.type_text.assert_not_called()

        # 验证返回的最低售卖价格
        self.assertEqual(result, 150000, "禁用快速售卖时应该返回检测到的最低售卖价格")

    @patch("src.services.trading_modes.delay_helper")
    def test_set_sell_price_with_zero_min_price(self, mock_delay_helper):
        """测试最低售卖价格为0时的边界条件"""
        # 设置模拟返回值
        self.mock_detector.coordinates = {
            "rolling_mode": {
                "sell_num_left": (100, 200),
                "sell_num_right": (300, 200),
                "sell_price_text": (150, 250),
                "min_sell_price_button": (200, 300),
            }
        }
        self.mock_detector.detect_min_sell_price.return_value = 0  # 最低价格为0
        self.mock_detector.detect_second_min_sell_price.return_value = 10000
        self.mock_detector.detect_min_sell_price_count.return_value = 200000

        # 设置当前配装为第一个（阈值100000）
        self.trading_mode.config.rolling_option = 0

        # 调用 _set_sell_price 方法，启用快速售卖
        result = self.trading_mode._set_sell_price(0.5, 0, fast_sell=True)

        # 验证当最低价格为0时，不触发快速售卖逻辑
        self.mock_action_executor.click_position.assert_any_call(
            self.mock_detector.coordinates["rolling_mode"]["min_sell_price_button"]
        )

        # 验证没有触发快速售卖的文本输入
        self.mock_action_executor.type_text.assert_not_called()

        # 验证返回的最低售卖价格
        self.assertEqual(result, 0, "最低价格为0时应该返回0")

    def test_integration_fast_sell_threshold_usage(self):
        """集成测试：验证快速售卖阈值在完整流程中的使用"""
        # 创建包含不同阈值的配装选项
        test_options = [
            {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980, "fast_sell_threshold": 100000},
            {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980, "fast_sell_threshold": 0},
            {"buy_price": 1700, "min_buy_price": 700, "buy_count": 1740, "fast_sell_threshold": 500000},
        ]

        self.trading_mode.option_configs = test_options

        # 测试切换不同配装时获取正确的阈值
        for i, expected_threshold in enumerate([100000, 0, 500000]):
            self.trading_mode.config.rolling_option = i
            actual_threshold = self.trading_mode._get_fast_sell_threshold()
            self.assertEqual(actual_threshold, expected_threshold, f"配装 {i} 应该返回阈值 {expected_threshold}")

    def test_backward_compatibility_missing_threshold(self):
        """测试向后兼容性：处理缺少快速售卖阈值的旧配置"""
        # 创建缺少 fast_sell_threshold 的旧格式配装选项
        legacy_options = [
            {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980},  # 缺少 fast_sell_threshold
            {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980},  # 缺少 fast_sell_threshold
        ]

        self.trading_mode.option_configs = legacy_options

        # 测试第一个配装选项
        self.trading_mode.config.rolling_option = 0
        threshold = self.trading_mode._get_fast_sell_threshold()
        self.assertEqual(threshold, 0, "缺少快速售卖阈值字段应该返回默认值0")

        # 测试第二个配装选项
        self.trading_mode.config.rolling_option = 1
        threshold = self.trading_mode._get_fast_sell_threshold()
        self.assertEqual(threshold, 0, "缺少快速售卖阈值字段应该返回默认值0")


if __name__ == "__main__":
    print("开始测试滚仓交易模式...")

    # 运行测试
    unittest.main(verbosity=2)
