"""
测试导入所有模块
"""

import pytest


class TestModuleImports:
    """模块导入测试类"""

    def test_core_interfaces_import(self):
        """测试核心接口导入"""
        try:
            from src.core.interfaces import MarketData

            assert MarketData is not None
        except ImportError as e:
            pytest.fail(f"核心接口导入失败: {e}")

    def test_config_management_import(self):
        """测试配置管理导入"""
        try:
            from src.config.config_factory import ConfigFactory

            assert ConfigFactory is not None
        except ImportError as e:
            pytest.fail(f"配置管理导入失败: {e}")

    def test_trading_service_import(self):
        """测试交易服务导入"""
        try:
            from src.services.trading_service import TradingService

            assert TradingService is not None
        except ImportError as e:
            pytest.fail(f"交易服务导入失败: {e}")

    def test_detector_import(self):
        """测试检测器导入"""
        try:
            from src.services.detector import (
                HoardingModeDetector,
                PriceDetector,
                RollingModeDetector,
            )

            assert HoardingModeDetector is not None
            assert PriceDetector is not None
            assert RollingModeDetector is not None
        except ImportError as e:
            pytest.fail(f"检测器导入失败: {e}")

    def test_trading_modes_import(self):
        """测试交易模式导入"""
        try:
            from src.services.trading_modes import (
                HoardingTradingMode,
                RollingTradingMode,
                TradingModeFactory,
            )

            assert HoardingTradingMode is not None
            assert RollingTradingMode is not None
            assert TradingModeFactory is not None
        except ImportError as e:
            pytest.fail(f"交易模式导入失败: {e}")

    def test_infrastructure_import(self):
        """测试基础设施导入"""
        try:
            from src.infrastructure.action_executor import ActionExecutorFactory
            from src.infrastructure.ocr_engine import TemplateOCREngine
            from src.infrastructure.screen_capture import ScreenCapture

            assert ActionExecutorFactory is not None
            assert TemplateOCREngine is not None
            assert ScreenCapture is not None
        except ImportError as e:
            pytest.fail(f"基础设施导入失败: {e}")

    def test_ui_adapter_import(self):
        """测试UI适配器导入"""
        try:
            from src.ui.adapter import TradingWorker, UIAdapter

            assert TradingWorker is not None
            assert UIAdapter is not None
        except ImportError as e:
            pytest.fail(f"UI适配器导入失败: {e}")

    def test_event_bus_import(self):
        """测试事件总线导入"""
        try:
            from src.core.event_bus import event_bus

            assert event_bus is not None
        except ImportError as e:
            pytest.fail(f"事件总线导入失败: {e}")

    def test_ui_file_import(self):
        """测试UI文件导入（可选）"""
        try:
            from GUI.AppGUI import Ui_MainWindow

            assert Ui_MainWindow is not None
        except ImportError as e:
            pytest.fail(f"UI文件导入失败: {e}")
