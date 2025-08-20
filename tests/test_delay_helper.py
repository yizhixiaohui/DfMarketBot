# -*- coding: utf-8 -*-
"""
DelayHelper 单元测试
"""
import os
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch

from src.config.delay_config import DelayConfig
from src.config.trading_config import TradingMode
from src.utils.delay_helper import DelayHelper, delay_helper


class TestDelayHelper(unittest.TestCase):
    """DelayHelper 测试类"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_delay_config.yaml")

        # 创建测试用的延迟配置
        self.test_config = DelayConfig(
            delays={
                "hoarding_mode": {"enter_action": 0.05, "refresh_operation": 0.01, "buy_operation": 0.0},
                "rolling_mode": {"balance_detection": 0.3, "buy_operation": 2.0, "sell_preparation": 0.3},
            }
        )

    def tearDown(self):
        """测试后清理"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("src.utils.delay_helper.ConfigFactory")
    def test_init(self, mock_factory):
        """测试DelayHelper初始化"""
        mock_manager = Mock()
        mock_manager.load_config.return_value = self.test_config
        mock_factory.get_config_manager.return_value = mock_manager

        DelayHelper()

        # 验证工厂方法被调用
        mock_factory.get_config_manager.assert_called_once_with("delay")

        # 验证配置被加载
        mock_manager.load_config.assert_called()

    @patch("src.utils.delay_helper.ConfigFactory")
    def test_get_delay(self, mock_factory):
        """测试获取延迟时间"""
        mock_manager = Mock()
        mock_manager.load_config.return_value = self.test_config
        mock_factory.get_config_manager.return_value = mock_manager

        helper = DelayHelper(TradingMode.HOARDING)

        # 测试获取存在的延迟
        delay = helper.get_delay("enter_action")
        self.assertEqual(delay, 0.05)

        # 测试获取不存在的操作
        delay = helper.get_delay("nonexistent")
        self.assertEqual(delay, 0.0)

    @patch("src.utils.delay_helper.ConfigFactory")
    @patch("time.sleep")
    def test_sleep(self, mock_sleep, mock_factory):
        """测试延迟执行"""
        mock_manager = Mock()
        mock_manager.load_config.return_value = self.test_config
        mock_factory.get_config_manager.return_value = mock_manager

        helper = DelayHelper(TradingMode.HOARDING)

        # 测试正常延迟执行
        helper.sleep("enter_action")
        mock_sleep.assert_called_with(0.05)

        # 测试零延迟（不应该调用sleep）
        mock_sleep.reset_mock()
        helper.sleep("buy_operation")
        mock_sleep.assert_not_called()

        # 测试不存在的操作（不应该调用sleep）
        mock_sleep.reset_mock()
        helper.sleep("nonexistent")
        mock_sleep.assert_not_called()

    @patch("src.utils.delay_helper.ConfigFactory")
    def test_get_mode_delays(self, mock_factory):
        """测试获取模式延迟配置"""
        mock_manager = Mock()
        mock_manager.load_config.return_value = self.test_config
        mock_factory.get_config_manager.return_value = mock_manager

        helper = DelayHelper(TradingMode.HOARDING)

        # 测试获取存在的模式
        delays = helper.get_mode_delays(TradingMode.HOARDING)
        expected = {"enter_action": 0.05, "refresh_operation": 0.01, "buy_operation": 0.0}
        self.assertEqual(delays, expected)

    @patch("src.utils.delay_helper.ConfigFactory")
    def test_has_operation(self, mock_factory):
        """测试检查操作是否存在"""
        mock_manager = Mock()
        mock_manager.load_config.return_value = self.test_config
        mock_factory.get_config_manager.return_value = mock_manager

        helper = DelayHelper(TradingMode.HOARDING)

        # 测试存在的操作
        self.assertTrue(helper.has_operation("enter_action"))

        # 测试不存在的操作
        self.assertFalse(helper.has_operation("nonexistent"))

        # 测试不存在的模式
        self.assertFalse(helper.has_operation("enter_action11"))

    @patch("src.utils.delay_helper.ConfigFactory")
    def test_get_available_modes(self, mock_factory):
        """测试获取可用模式列表"""
        mock_manager = Mock()
        mock_manager.load_config.return_value = self.test_config
        mock_factory.get_config_manager.return_value = mock_manager

        helper = DelayHelper(TradingMode.HOARDING)

        modes = helper.get_available_modes()
        self.assertIn("hoarding_mode", modes)
        self.assertIn("rolling_mode", modes)
        self.assertEqual(len(modes), 2)

    @patch("src.utils.delay_helper.ConfigFactory")
    def test_get_mode_operations(self, mock_factory):
        """测试获取模式操作列表"""
        mock_manager = Mock()
        mock_manager.load_config.return_value = self.test_config
        mock_factory.get_config_manager.return_value = mock_manager

        helper = DelayHelper(TradingMode.HOARDING)

        # 测试存在的模式
        operations = helper.get_mode_operations(TradingMode.HOARDING)
        expected = ["enter_action", "refresh_operation", "buy_operation"]
        self.assertEqual(sorted(operations), sorted(expected))

    @patch("src.utils.delay_helper.ConfigFactory")
    def test_reload_config(self, mock_factory):
        """测试重新加载配置"""
        mock_manager = Mock()
        mock_manager.load_config.return_value = self.test_config
        mock_factory.get_config_manager.return_value = mock_manager

        helper = DelayHelper()

        # 重置mock以清除初始化时的调用
        mock_manager.load_config.reset_mock()

        # 测试重新加载
        result = helper.reload_config()
        self.assertTrue(result)
        mock_manager.load_config.assert_called_once()

    @patch("src.utils.delay_helper.ConfigFactory")
    def test_reload_config_failure(self, mock_factory):
        """测试重新加载失败的情况"""
        mock_manager = Mock()
        mock_manager.load_config.side_effect = Exception("加载失败")
        mock_factory.get_config_manager.return_value = mock_manager

        helper = DelayHelper()

        # 测试重新加载失败
        result = helper.reload_config()
        self.assertFalse(result)

    @patch("src.utils.delay_helper.ConfigFactory")
    def test_get_config_info(self, mock_factory):
        """测试获取配置信息"""
        mock_manager = Mock()
        mock_manager.load_config.return_value = self.test_config
        mock_factory.get_config_manager.return_value = mock_manager

        helper = DelayHelper()

        info = helper.get_config_info()

        self.assertEqual(info["status"], "loaded")
        self.assertEqual(info["modes"], 2)
        self.assertIn("hoarding_mode", info["mode_names"])
        self.assertIn("rolling_mode", info["mode_names"])
        self.assertEqual(info["total_operations"], 6)  # 3 + 3 operations

    @patch("src.utils.delay_helper.ConfigFactory")
    def test_get_config_info_no_config(self, mock_factory):
        """测试无配置时的信息获取"""
        mock_manager = Mock()
        mock_manager.load_config.return_value = None
        mock_factory.get_config_manager.return_value = mock_manager

        helper = DelayHelper()

        info = helper.get_config_info()

        self.assertEqual(info["status"], "no_config")
        self.assertEqual(info["modes"], 0)
        self.assertEqual(info["total_operations"], 0)

    @patch("src.utils.delay_helper.ConfigFactory")
    def test_thread_safety(self, mock_factory):
        """测试线程安全性"""
        mock_manager = Mock()
        mock_manager.load_config.return_value = self.test_config
        mock_factory.get_config_manager.return_value = mock_manager

        helper = DelayHelper(TradingMode.HOARDING)
        results = []
        errors = []

        # 使用事件来同步线程启动，避免竞争条件
        start_event = threading.Event()

        def worker():
            try:
                # 等待所有线程准备就绪
                start_event.wait()
                for _ in range(10):  # 减少循环次数以避免长时间运行
                    delay = helper.get_delay("enter_action")
                    results.append(delay)
                    # 不调用实际的sleep，只测试get_delay的线程安全性
            except Exception as e:
                errors.append(e)

        # 创建多个线程并发访问
        threads = [threading.Thread(target=worker) for _ in range(3)]  # 减少线程数

        for thread in threads:
            thread.start()

        # 启动所有线程
        start_event.set()

        # 等待所有线程完成，设置超时避免死锁
        for thread in threads:
            thread.join(timeout=5.0)  # 5秒超时
            if thread.is_alive():
                # 如果线程仍然活着，说明可能死锁了
                self.fail("Thread did not complete within timeout - possible deadlock")

        # 验证没有错误发生
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")

        # 验证结果正确
        expected_results = 30  # 3 threads * 10 iterations
        self.assertEqual(len(results), expected_results)
        self.assertTrue(all(delay == 0.05 for delay in results))

    @patch("src.utils.delay_helper.ConfigFactory")
    def test_str_and_repr(self, mock_factory):
        """测试字符串表示方法"""
        mock_manager = Mock()
        mock_manager.load_config.return_value = self.test_config
        mock_factory.get_config_manager.return_value = mock_manager

        helper = DelayHelper(TradingMode.HOARDING)

        # 测试 __str__
        str_repr = str(helper)
        self.assertIn("DelayHelper", str_repr)
        self.assertIn("status=loaded", str_repr)
        self.assertIn("modes=2", str_repr)
        self.assertIn("operations=6", str_repr)

        # 测试 __repr__
        repr_str = repr(helper)
        self.assertIn("DelayHelper", repr_str)


class TestGlobalDelayHelper(unittest.TestCase):
    """全局DelayHelper实例和便捷函数测试"""

    def test_global_instance_exists(self):
        """测试全局实例存在"""
        self.assertIsInstance(delay_helper, DelayHelper)


class TestDelayHelperErrorHandling(unittest.TestCase):
    """DelayHelper错误处理测试"""

    @patch("src.utils.delay_helper.ConfigFactory")
    def test_config_manager_exception(self, mock_factory):
        """测试配置管理器异常处理"""
        mock_manager = Mock()
        mock_manager.load_config.side_effect = Exception("配置加载失败")
        mock_factory.get_config_manager.return_value = mock_manager

        helper = DelayHelper(TradingMode.HOARDING)

        # 即使配置加载失败，也应该能正常工作
        delay = helper.get_delay("enter_action")
        self.assertEqual(delay, 0.0)

        # 获取配置信息应该显示无配置状态
        info = helper.get_config_info()
        self.assertEqual(info["status"], "no_config")


if __name__ == "__main__":
    unittest.main()
