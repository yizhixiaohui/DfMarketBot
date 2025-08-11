# -*- coding: utf-8 -*-
"""
交易服务 - 核心业务逻辑整合
"""
from typing import Optional, Dict, Any

from ..core.exceptions import TradingException
from ..core.interfaces import ITradingService, TradingConfig, MarketData
from ..infrastructure.action_executor import ActionExecutorFactory
from ..infrastructure.ocr_engine import TemplateOCREngine
from ..infrastructure.screen_capture import ScreenCapture
from ..services.trading_modes import TradingModeFactory


class TradingService(ITradingService):
    """交易服务实现"""

    def __init__(self):
        # 初始化基础设施
        self.screen_capture = ScreenCapture()
        self.ocr_engine = TemplateOCREngine()
        self.action_executor = ActionExecutorFactory.create_executor("pyautogui")

        # 初始化交易模式
        self.current_mode = None
        self.current_config = None

    def initialize(self, config: TradingConfig) -> None:
        """初始化交易服务"""
        try:
            # 检查基础设施是否可用
            self._check_infrastructure()
            # 转换配置

            self._switch_mode(config)

            # 更新当前配置
            self.current_config = config
            print("交易服务初始化成功")

        except Exception as e:
            raise TradingException(f"交易服务初始化失败: {e}")

    def prepare(self) -> None:
        try:
            self.current_mode.prepare()
        except Exception as e:
            raise TradingException(f"交易服务准备失败: {e}")

    def execute_cycle(self) -> bool:
        """执行一个交易周期"""
        try:
            # 执行交易周期
            return self.current_mode.execute_cycle()

        except Exception as e:
            raise TradingException(f"交易周期执行失败: {e}")

    def get_market_data(self) -> Optional[MarketData]:
        """获取当前市场数据"""
        if self.current_mode is not None:
            return self.current_mode.get_market_data()
        return None

    def stop(self) -> None:
        """停止交易服务"""
        self.current_mode = None
        self.current_config = None

    def _check_infrastructure(self) -> None:
        """检查基础设施是否可用"""
        # 检查屏幕捕获
        try:
            test_image = self.screen_capture.capture_region([0, 0, 256, 1440])
            if test_image is None or test_image.size == 0:
                raise TradingException("屏幕捕获失败")
        except Exception as e:
            raise TradingException(f"屏幕捕获不可用: {e}")

        # 检查OCR引擎
        try:
            test_image = self.screen_capture.capture_region([0, 0, 256, 144])
            self.ocr_engine.image_to_string(test_image)
        except Exception as e:
            raise TradingException(f"OCR引擎不可用: {e}")

        # 检查动作执行器
        try:
            self.action_executor.get_mouse_position()
        except Exception as e:
            raise TradingException(f"动作执行器不可用: {e}")

    def _switch_mode(self, config: TradingConfig) -> None:
        """切换交易模式"""
        try:
            # 创建新的交易模式
            new_mode = TradingModeFactory.create_mode(
                config,
                self.ocr_engine,
                self.screen_capture,
                self.action_executor
            )

            # 初始化新模式
            new_mode.initialize(config)

            # 更新当前模式
            self.current_mode = new_mode

            print(f"切换到模式: {config.trading_mode}")

        except Exception as e:
            raise TradingException(f"切换交易模式失败: {e}")
