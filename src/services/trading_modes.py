# -*- coding: utf-8 -*-
"""
交易模式实现
"""
import time
from typing import Optional

if __name__ == '__main__':
    from src.core.interfaces import ITradingMode, TradingConfig, MarketData, TradingMode, ItemType
    from src.core.exceptions import TradingException
    from src.infrastructure.ocr_engine import TemplateOCREngine
    from src.infrastructure.screen_capture import ScreenCapture
    from src.services.detector import HoardingModeDetector, RollingModeDetector
    from src.services.strategy import StrategyFactory
    from src.services.strategy import RollingStrategy
    from src.infrastructure.action_executor import PyAutoGUIActionExecutor as ActionExecutor
else:
    from ..core.interfaces import ITradingMode, TradingConfig, MarketData, TradingMode, ItemType
    from ..core.exceptions import TradingException
    from ..infrastructure.ocr_engine import TemplateOCREngine
    from ..infrastructure.screen_capture import ScreenCapture
    from ..services.detector import HoardingModeDetector, RollingModeDetector
    from ..services.strategy import StrategyFactory
    from ..services.strategy import RollingStrategy
    from ..infrastructure.action_executor import PyAutoGUIActionExecutor as ActionExecutor

class HoardingTradingMode(ITradingMode):
    """屯仓模式交易实现"""
    
    def __init__(self, price_detector: HoardingModeDetector, action_executor: ActionExecutor):
        self.detector = price_detector
        self.action_executor = action_executor
        self.last_balance = None
        self.current_balance = None
        self.last_buy_quantity = 0
        self.current_market_data = None
        self.config = None
        self.strategy = None
        self.refresh_strategy = None
        self.mouse_position = None

    def initialize(self, config: TradingConfig) -> None:
        """初始化屯仓模式"""
        self.config = config
        factory = StrategyFactory()
        self.strategy = factory.create_strategy(config)
        self.refresh_strategy = factory.create_refresh_strategy(config)

    def prepare(self) -> None:
        self.mouse_position = self.action_executor.get_mouse_position()
        self.current_balance = self._detect_balance()
        self._execute_enter()
        time.sleep(0.05)

    def execute_cycle(self) -> bool:
        """执行一个屯仓交易周期"""
        try:
            # 获取当前价格
            current_price = self.detector.detect_price()

            # 获取当前余额（如果需要）
            if self.config.use_balance_calculation and self.last_buy_quantity != 0:
                self.current_balance = self._detect_balance()

            self.current_market_data = MarketData(
                current_price=current_price,
                balance=self.current_balance,
                last_balance= self.last_balance,
                last_buy_quantity=self.last_buy_quantity,
                timestamp=time.time()
            )

            # 执行交易逻辑
            if self.strategy.should_buy(self.current_market_data):
                print('直接购买')
                # 购买逻辑
                quantity = self.strategy.get_buy_quantity(self.current_market_data)
                self._execute_buy(quantity)
                self.last_buy_quantity = quantity

                if self.config.key_mode:
                    return False  # 钥匙卡模式购买后停止
            elif self.refresh_strategy.should_refresh(self.current_market_data):
                print('刷新购买')
                quantity = self.strategy.get_buy_quantity(self.current_market_data)
                self._execute_buy(quantity)
                self.last_buy_quantity = self.refresh_strategy.get_buy_quantity(self.config)
            elif self.strategy.should_refresh(self.current_market_data):
                print('直接刷新')
                self._execute_refresh()
                self.last_buy_quantity = 0

            # 更新余额
            if self.config.use_balance_calculation:
                self.last_balance = self.current_balance

            return True

        except Exception as e:
            raise TradingException(f"屯仓模式交易失败: {e}")

    def _detect_balance(self):
        self.action_executor.move_mouse(self.detector.coordinates["balance_active"])
        return self.detector.detect_balance()

    def _execute_enter(self) -> None:
        self.action_executor.click_position((self.mouse_position.x, self.mouse_position.y))

    def _execute_buy(self, quantity: int) -> None:
        """执行购买操作"""
        convertible = "" if ItemType(self.config.item_type) == ItemType.CONVERTIBLE else "non_"
        if not self.config.key_mode:
            quantity_pos = "min" if quantity == 31 else "max"
            self.action_executor.click_position(self.detector.coordinates["buy_buttons"][f"{convertible}convertible_{quantity_pos}"])
        self.action_executor.click_position(self.detector.coordinates["buy_buttons"][f"{convertible}convertible_buy"])
        print(f"执行购买: 数量={quantity}")

    def _execute_refresh(self) -> None:
        """执行刷新操作"""
        self.action_executor.press_key('esc')
        self._execute_enter()
        print("执行价格刷新")
    
    def get_market_data(self) -> Optional[MarketData]:
        """获取当前市场数据"""
        return self.current_market_data


class RollingTradingMode(ITradingMode):
    """滚仓模式交易实现"""
    
    def __init__(self, rolling_detector: RollingModeDetector, action_executor: ActionExecutor):
        self.detector = rolling_detector
        self.action_executor = action_executor
        self.strategy_factory = StrategyFactory()
        self.current_market_data = None
        self.option_configs = RollingStrategy.ROLLING_OPTIONS
        self.config = None
    
    def initialize(self, config) -> None:
        """初始化滚仓模式"""
        self.config = config

    def prepare(self) -> None:
        pass
    
    def execute_cycle(self) -> bool:
        """执行一个滚仓交易周期"""
        try:
            self._execute_enter()
            # 切换到指定配装选项
            self._switch_to_option(self.config.rolling_option)
            time.sleep(0.1)
            # 检测价格
            current_price = self.detector.detect_price()

            # 存储市场数据
            self.current_market_data = MarketData(
                current_price=current_price,
                balance=None,  # 滚仓模式不检测余额
                timestamp=time.time()
            )

            # 获取配装配置
            option_config = self.option_configs.get(self.config.rolling_option)
            if not option_config:
                return False
            
            target_price = option_config["buy_price"] * option_config["buy_count"]
            min_price = option_config["min_buy_price"] * option_config["buy_count"]
            
            print(f"滚仓模式: 单价={option_config['buy_price']}, "
                  f"数量={option_config['buy_count']}, "
                  f"总价={target_price}, 最低价={min_price}, "
                  f"当前价={current_price}")
            
            # 执行交易决策
            if min_price < current_price <= target_price:
                # 购买
                self._execute_buy()

                # 检查购买是否成功
                time.sleep(2)
                if self.detector.check_purchase_failure():
                    print("购买失败，继续购买")
                    self._execute_refresh()
                    time.sleep(1)
                    return True
                else:
                    print("购买完毕，手动检查购买是否成功")
                    return False  # 购买成功后停止

            # 刷新
            self._execute_refresh()
            
            return True
            
        except Exception as e:
            raise TradingException(f"滚仓模式交易失败: {e}")

    def _execute_enter(self):
        self.action_executor.press_key('l')

    def _switch_to_option(self, option_index: int) -> None:
        """切换到指定配装选项"""
        coordinates = self.detector.coordinates["rolling_mode"]["options"]
        if 0 <= option_index < len(coordinates):
            self.action_executor.click_position(coordinates[option_index])
    
    def _execute_buy(self) -> None:
        """执行购买操作"""
        coordinates = self.detector.coordinates["rolling_mode"]["buy_button"]
        self.action_executor.click_position(coordinates)
    
    def _execute_refresh(self) -> None:
        """执行刷新操作"""
        print('execute refresh')
        self.action_executor.press_key('esc')

    def _execute_auto_sell(self):
        self.action_executor.click_position(self.detector.coordinates["rolling_mode"]["enter_storage"])
        time.sleep(1)
        self.action_executor.click_position(self.detector.coordinates["rolling_mode"]["transfer_all"])
        time.sleep(1)
        pos = self.detector.detect_sellable_item()
        while True:
            self.action_executor.move_mouse(pos)
            time.sleep(0.3)
            self.action_executor.multi_key_press('alt', 'd')
            time.sleep(1)
            self.action_executor.click_position(self.detector.coordinates["rolling_mode"]["sell_button"])
            time.sleep(1)
            if "交易行未满" != "交易行未满":
                break
            self.action_executor.click_position(self.detector.coordinates["rolling_mode"]["sell_return_button"])
            time.sleep(1)


    def get_market_data(self) -> Optional[MarketData]:
        """获取当前市场数据"""
        return self.current_market_data


class TradingModeFactory:
    """交易模式工厂"""
    
    @staticmethod
    def create_mode(config: TradingConfig,
                    ocr_engine: TemplateOCREngine,
                    screen_capture: ScreenCapture,
                    action_executor: ActionExecutor) -> ITradingMode:
        """根据类型创建交易模式"""
        if config.trading_mode == TradingMode.HOARDING:
            price_detector = HoardingModeDetector(screen_capture, ocr_engine, ItemType(config.item_type) == ItemType.CONVERTIBLE)
            mode = HoardingTradingMode(price_detector, action_executor)
        elif config.trading_mode == TradingMode.ROLLING:
            price_detector = RollingModeDetector(screen_capture, ocr_engine)
            mode = RollingTradingMode(price_detector, action_executor)
        else:
            raise ValueError(f"不支持的交易模式: {config.trading_mode}")
        return mode


if __name__ == '__main__':
    sc = ScreenCapture()
    ocr = TemplateOCREngine()
    detector = RollingModeDetector(sc, ocr)
    executor = ActionExecutor()
    mode = RollingTradingMode(detector, executor)
    mode._execute_auto_sell()
