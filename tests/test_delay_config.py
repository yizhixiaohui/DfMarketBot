# -*- coding: utf-8 -*-
"""
延迟配置测试模块
"""
import os
import tempfile
import unittest
from unittest.mock import patch

from src.config.config_manager import DelayConfigManager
from src.config.delay_config import DelayConfig


class TestDelayConfig(unittest.TestCase):
    """DelayConfig数据类测试"""

    def setUp(self):
        """测试前准备"""
        self.valid_delays = {
            "hoarding_mode": {
                "enter_action": 0.05,
                "balance_detection": 0.0,
                "buy_operation": 0.0
            },
            "rolling_mode": {
                "balance_detection": 0.3,
                "initialization": 0.4,
                "buy_operation": 2.0
            }
        }
        self.config = DelayConfig(delays=self.valid_delays)

    def test_init_valid_config(self):
        """测试有效配置初始化"""
        config = DelayConfig(delays=self.valid_delays)
        self.assertEqual(config.delays, self.valid_delays)

    def test_init_invalid_delays_type(self):
        """测试无效的delays类型"""
        with self.assertRaises(ValueError) as context:
            DelayConfig(delays="invalid")
        self.assertIn("延迟配置必须是字典类型", str(context.exception))

    def test_init_invalid_mode_type(self):
        """测试无效的模式名称类型"""
        invalid_delays = {123: {"operation": 0.1}}
        with self.assertRaises(ValueError) as context:
            DelayConfig(delays=invalid_delays)
        self.assertIn("交易模式名称必须是字符串", str(context.exception))

    def test_init_invalid_operations_type(self):
        """测试无效的操作配置类型"""
        invalid_delays = {"mode": "invalid"}
        with self.assertRaises(ValueError) as context:
            DelayConfig(delays=invalid_delays)
        self.assertIn("操作配置必须是字典类型", str(context.exception))

    def test_init_invalid_operation_name_type(self):
        """测试无效的操作名称类型"""
        invalid_delays = {"mode": {123: 0.1}}
        with self.assertRaises(ValueError) as context:
            DelayConfig(delays=invalid_delays)
        self.assertIn("操作名称必须是字符串", str(context.exception))

    def test_init_invalid_delay_type(self):
        """测试无效的延迟值类型"""
        invalid_delays = {"mode": {"operation": "invalid"}}
        with self.assertRaises(ValueError) as context:
            DelayConfig(delays=invalid_delays)
        self.assertIn("延迟参数必须是数字", str(context.exception))

    def test_init_negative_delay(self):
        """测试负数延迟值"""
        invalid_delays = {"mode": {"operation": -0.1}}
        with self.assertRaises(ValueError) as context:
            DelayConfig(delays=invalid_delays)
        self.assertIn("延迟参数不能为负数", str(context.exception))

    def test_get_delay_existing(self):
        """测试获取存在的延迟"""
        delay = self.config.get_delay("hoarding_mode", "enter_action")
        self.assertEqual(delay, 0.05)

    def test_get_delay_nonexistent_mode(self):
        """测试获取不存在的模式"""
        delay = self.config.get_delay("nonexistent_mode", "operation")
        self.assertEqual(delay, 0.0)

    def test_get_delay_nonexistent_operation(self):
        """测试获取不存在的操作"""
        delay = self.config.get_delay("hoarding_mode", "nonexistent_operation")
        self.assertEqual(delay, 0.0)

    def test_get_delay_invalid_types(self):
        """测试无效参数类型"""
        delay = self.config.get_delay(123, "operation")
        self.assertEqual(delay, 0.0)
        delay = self.config.get_delay("mode", 123)
        self.assertEqual(delay, 0.0)

    def test_set_delay_new_mode(self):
        """测试设置新模式的延迟"""
        self.config.set_delay("new_mode", "new_operation", 0.5)
        self.assertEqual(self.config.get_delay("new_mode", "new_operation"), 0.5)

    def test_set_delay_existing_operation(self):
        """测试更新现有操作的延迟"""
        self.config.set_delay("hoarding_mode", "enter_action", 0.1)
        self.assertEqual(self.config.get_delay("hoarding_mode", "enter_action"), 0.1)

    def test_set_delay_invalid_mode_type(self):
        """测试设置延迟时无效的模式类型"""
        with self.assertRaises(ValueError) as context:
            self.config.set_delay(123, "operation", 0.1)
        self.assertIn("交易模式名称必须是字符串", str(context.exception))

    def test_set_delay_invalid_operation_type(self):
        """测试设置延迟时无效的操作类型"""
        with self.assertRaises(ValueError) as context:
            self.config.set_delay("mode", 123, 0.1)
        self.assertIn("操作名称必须是字符串", str(context.exception))

    def test_set_delay_invalid_delay_type(self):
        """测试设置延迟时无效的延迟类型"""
        with self.assertRaises(ValueError) as context:
            self.config.set_delay("mode", "operation", "invalid")
        self.assertIn("延迟参数必须是数字", str(context.exception))

    def test_set_delay_negative_value(self):
        """测试设置负数延迟"""
        with self.assertRaises(ValueError) as context:
            self.config.set_delay("mode", "operation", -0.1)
        self.assertIn("延迟时间不能为负数", str(context.exception))

    def test_get_mode_delays(self):
        """测试获取模式延迟配置"""
        mode_delays = self.config.get_mode_delays("hoarding_mode")
        expected = {
            "enter_action": 0.05,
            "balance_detection": 0.0,
            "buy_operation": 0.0
        }
        self.assertEqual(mode_delays, expected)

    def test_get_mode_delays_nonexistent(self):
        """测试获取不存在模式的延迟配置"""
        mode_delays = self.config.get_mode_delays("nonexistent_mode")
        self.assertEqual(mode_delays, {})

    def test_get_mode_delays_invalid_type(self):
        """测试获取模式延迟配置时无效类型"""
        mode_delays = self.config.get_mode_delays(123)
        self.assertEqual(mode_delays, {})

    def test_update_mode_delays(self):
        """测试更新模式延迟配置"""
        updates = {"enter_action": 0.1, "new_operation": 0.2}
        self.config.update_mode_delays("hoarding_mode", updates)

        self.assertEqual(self.config.get_delay("hoarding_mode", "enter_action"), 0.1)
        self.assertEqual(self.config.get_delay("hoarding_mode", "new_operation"), 0.2)
        # 确保其他操作未受影响
        self.assertEqual(self.config.get_delay("hoarding_mode", "balance_detection"), 0.0)

    def test_update_mode_delays_invalid_mode_type(self):
        """测试更新模式延迟配置时无效模式类型"""
        with self.assertRaises(ValueError) as context:
            self.config.update_mode_delays(123, {"operation": 0.1})
        self.assertIn("交易模式名称必须是字符串", str(context.exception))

    def test_update_mode_delays_invalid_delays_type(self):
        """测试更新模式延迟配置时无效延迟类型"""
        with self.assertRaises(ValueError) as context:
            self.config.update_mode_delays("mode", "invalid")
        self.assertIn("延迟配置必须是字典类型", str(context.exception))

    def test_update_mode_delays_invalid_operation_name(self):
        """测试更新模式延迟配置时无效操作名称"""
        with self.assertRaises(ValueError) as context:
            self.config.update_mode_delays("mode", {123: 0.1})
        self.assertIn("操作名称必须是字符串", str(context.exception))

    def test_update_mode_delays_invalid_delay_value(self):
        """测试更新模式延迟配置时无效延迟值"""
        with self.assertRaises(ValueError) as context:
            self.config.update_mode_delays("mode", {"operation": "invalid"})
        self.assertIn("延迟参数必须是数字", str(context.exception))

    def test_update_mode_delays_negative_value(self):
        """测试更新模式延迟配置时负数延迟值"""
        with self.assertRaises(ValueError) as context:
            self.config.update_mode_delays("mode", {"operation": -0.1})
        self.assertIn("延迟时间不能为负数", str(context.exception))

    def test_get_all_modes(self):
        """测试获取所有模式"""
        modes = self.config.get_all_modes()
        self.assertEqual(set(modes), {"hoarding_mode", "rolling_mode"})

    def test_get_mode_operations(self):
        """测试获取模式操作列表"""
        operations = self.config.get_mode_operations("hoarding_mode")
        expected = ["enter_action", "balance_detection", "buy_operation"]
        self.assertEqual(set(operations), set(expected))

    def test_get_mode_operations_nonexistent(self):
        """测试获取不存在模式的操作列表"""
        operations = self.config.get_mode_operations("nonexistent_mode")
        self.assertEqual(operations, [])

    def test_get_mode_operations_invalid_type(self):
        """测试获取模式操作列表时无效类型"""
        operations = self.config.get_mode_operations(123)
        self.assertEqual(operations, [])

    def test_has_mode(self):
        """测试检查模式是否存在"""
        self.assertTrue(self.config.has_mode("hoarding_mode"))
        self.assertFalse(self.config.has_mode("nonexistent_mode"))
        self.assertFalse(self.config.has_mode(123))

    def test_has_operation(self):
        """测试检查操作是否存在"""
        self.assertTrue(self.config.has_operation("hoarding_mode", "enter_action"))
        self.assertFalse(self.config.has_operation("hoarding_mode", "nonexistent_operation"))
        self.assertFalse(self.config.has_operation("nonexistent_mode", "operation"))
        self.assertFalse(self.config.has_operation(123, "operation"))
        self.assertFalse(self.config.has_operation("mode", 123))

    def test_remove_operation(self):
        """测试移除操作"""
        self.assertTrue(self.config.remove_operation("hoarding_mode", "enter_action"))
        self.assertFalse(self.config.has_operation("hoarding_mode", "enter_action"))

        # 尝试移除不存在的操作
        self.assertFalse(self.config.remove_operation("hoarding_mode", "nonexistent_operation"))

    def test_clear_mode(self):
        """测试清空模式"""
        self.assertTrue(self.config.clear_mode("hoarding_mode"))
        self.assertEqual(self.config.get_mode_operations("hoarding_mode"), [])

        # 尝试清空不存在的模式
        self.assertFalse(self.config.clear_mode("nonexistent_mode"))

    def test_to_dict(self):
        """测试转换为字典"""
        result = self.config.to_dict()
        self.assertEqual(result["delays"], self.valid_delays)

    def test_from_dict(self):
        """测试从字典创建配置"""
        data = {"delays": self.valid_delays}
        config = DelayConfig.from_dict(data)
        self.assertEqual(config.delays, self.valid_delays)

    def test_from_dict_invalid_type(self):
        """测试从无效类型创建配置"""
        with self.assertRaises(ValueError) as context:
            DelayConfig.from_dict("invalid")
        self.assertIn("数据必须是字典类型", str(context.exception))

    def test_from_dict_missing_delays(self):
        """测试从缺少delays字段的字典创建配置"""
        with self.assertRaises(ValueError) as context:
            DelayConfig.from_dict({"other": "data"})
        self.assertIn("配置数据中缺少 'delays' 字段", str(context.exception))

    def test_str_representation(self):
        """测试字符串表示"""
        str_repr = str(self.config)
        self.assertIn("DelayConfig:", str_repr)
        self.assertIn("hoarding_mode:", str_repr)
        self.assertIn("rolling_mode:", str_repr)
        self.assertIn("enter_action: 0.05s", str_repr)

    def test_repr_representation(self):
        """测试调试表示"""
        repr_str = repr(self.config)
        self.assertIn("DelayConfig(delays=", repr_str)


class TestDelayConfigManager(unittest.TestCase):
    """DelayConfigManager测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_delay_config.yaml")
        self.manager = DelayConfigManager(self.config_path)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        os.rmdir(self.temp_dir)

    def test_create_default_config(self):
        """测试创建默认配置"""
        config = self.manager._create_default_config()
        self.assertIsInstance(config, DelayConfig)
        self.assertTrue(config.has_mode("hoarding_mode"))
        self.assertTrue(config.has_mode("rolling_mode"))
        self.assertTrue(config.has_operation("hoarding_mode", "enter_action"))
        self.assertTrue(config.has_operation("rolling_mode", "balance_detection"))

    def test_load_config_creates_default_when_missing(self):
        """测试配置文件不存在时创建默认配置"""
        config = self.manager.load_config()
        self.assertIsInstance(config, DelayConfig)
        self.assertTrue(os.path.exists(self.config_path))

    def test_save_and_load_config(self):
        """测试保存和加载配置"""
        original_config = DelayConfig(delays={
            "test_mode": {"test_operation": 0.123}
        })

        self.manager.save_config(original_config)
        loaded_config = self.manager.load_config()

        self.assertEqual(loaded_config.get_delay("test_mode", "test_operation"), 0.123)

    def test_update_config(self):
        """测试更新配置"""
        # 先创建一个配置
        original_config = self.manager.load_config()

        # 更新配置
        updates = {
            "delays": {
                "hoarding_mode": {"enter_action": 0.123}
            }
        }
        updated_config = self.manager.update_config(updates)

        self.assertEqual(updated_config.get_delay("hoarding_mode", "enter_action"), 0.123)

    def test_reload_config(self):
        """测试重新加载配置"""
        # 创建初始配置
        config = self.manager.load_config()

        # 重新加载应该返回相同的配置
        reloaded_config = self.manager.reload_config()
        self.assertEqual(config.delays, reloaded_config.delays)

    @patch('builtins.open', side_effect=IOError("File access error"))
    def test_load_config_error_handling(self, mock_file):
        """测试加载配置时的错误处理"""
        # 当文件访问出错时，应该返回默认配置
        config = self.manager.load_config()
        self.assertIsInstance(config, DelayConfig)

    def test_config_class(self):
        """测试配置类方法"""
        config_class = self.manager._config_class()
        self.assertEqual(config_class, DelayConfig)


if __name__ == '__main__':
    unittest.main()
