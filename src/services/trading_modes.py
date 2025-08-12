# -*- coding: utf-8 -*-
"""
交易模式实现
"""
import datetime
import time
from typing import Optional, Dict, Tuple

if __name__ == '__main__':
    from src.core.interfaces import ITradingMode, TradingConfig, MarketData, TradingMode, ItemType
    from src.core.exceptions import TradingException
    from src.infrastructure.ocr_engine import TemplateOCREngine
    from src.infrastructure.screen_capture import ScreenCapture
    from src.services.detector import HoardingModeDetector, RollingModeDetector
    from src.services.strategy import StrategyFactory
    from src.infrastructure.action_executor import PyAutoGUIActionExecutor as ActionExecutor
else:
    from ..core.interfaces import ITradingMode, TradingConfig, MarketData, TradingMode, ItemType
    from ..core.exceptions import TradingException
    from ..infrastructure.ocr_engine import TemplateOCREngine
    from ..infrastructure.screen_capture import ScreenCapture
    from ..services.detector import HoardingModeDetector, RollingModeDetector
    from ..services.strategy import StrategyFactory
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
                last_balance=self.last_balance,
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
            self.action_executor.click_position(
                self.detector.coordinates["buy_buttons"][f"{convertible}convertible_{quantity_pos}"])
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
        self.option_configs = None
        self.config = None
        self.last_balance = None
        self.profit = 0
        # 已出售总数
        self.count = 0

    def initialize(self, config) -> None:
        """初始化滚仓模式"""
        self.config = config
        self.option_configs = config.rolling_options

    def prepare(self) -> None:
        self.last_balance = self._detect_balance()
        print('初始化成功，当前余额:', self.last_balance)
        self.append_to_sell_log(f"初始化成功，当前余额: {self.last_balance}")
        time.sleep(0.4)

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
            if self.config.rolling_option >= len(self.option_configs):
                return False
            option_config = self.option_configs[self.config.rolling_option]
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
                    self._execute_refresh()
                    time.sleep(1)
                    cur_balance = self._detect_balance()
                    if cur_balance == self.last_balance:
                        print("购买失败！")
                        time.sleep(0.4)
                        return True
                    print('部分购买失败，执行售卖')
                else:
                    print("购买成功！")
                    cur_balance = self._detect_balance()
                cost = self.last_balance - cur_balance
                self.profit -= cost
                self.append_to_sell_log(f"购买成功, 花费: {cost}, 当前盈利: {self.profit}")
                self._execute_auto_sell(cost)
                # 自动售卖结束时已经有1s间隔了，这里延迟可以不用太高
                time.sleep(0.3)
                self._execute_get_mail_half_coin()
                time.sleep(2)
                self._execute_refresh()
                time.sleep(1)
                self.last_balance = cur_balance
            else:
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

    def _execute_auto_sell(self, cost=0):
        """执行自动售卖流程"""
        self._enter_storage_and_transfer()
        sell_results = self._execute_sell_cycles(cost)
        self._log_final_sell_results(sell_results, cost)

    def _enter_storage_and_transfer(self):
        """进入仓库并转移物品"""
        self.action_executor.click_position(self.detector.coordinates["rolling_mode"]["enter_storage"])
        time.sleep(1)
        self.action_executor.click_position(self.detector.coordinates["rolling_mode"]["transfer_all"])
        time.sleep(1)

    def _execute_sell_cycles(self, cost: float) -> Dict[str, any]:
        """执行售卖循环"""
        sell_time = 0
        idx = 0
        sell_ratios = [0.33, 0.5, 1.0]
        total_profit = 0
        total_count = 0
        cycle_results = []

        while sell_time < len(sell_ratios):
            result = self._execute_single_sell_cycle(idx, sell_ratios[sell_time])
            if not result["success"]:
                break

            total_profit += result["revenue"]
            total_count += result["count"]
            cycle_results.append(result)
            idx += 1
            sell_time += 1

        return {
            "total_profit": total_profit,
            "total_count": total_count,
            "cycles": cycle_results
        }

    def _execute_single_sell_cycle(self, cycle_index: int, sell_ratio: float) -> Dict[str, any]:
        """执行单个售卖循环"""
        try:
            # 检测可售卖物品
            item_pos = self.detector.detect_sellable_item()
            if item_pos[0] == 0 and item_pos[1] == 0:
                return {"success": False, "message": "无可售卖物品"}

            # 执行售卖操作
            sell_info = self._perform_sell_operation(item_pos, sell_ratio, cycle_index)

            # 更新统计数据
            self.profit += sell_info["revenue"]
            self.count += sell_info["count"]

            return {
                "success": True,
                "revenue": sell_info["revenue"],
                "count": sell_info["count"],
                "price": sell_info["price"]
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _perform_sell_operation(self, item_pos: Tuple[int, int], sell_ratio: float, cycle_index: int) -> Dict[str, any]:
        """执行单个售卖操作"""
        sell_pos = (
            item_pos[0] + self.detector.coordinates["rolling_mode"]["item_sell_offset"][0],
            item_pos[1] + self.detector.coordinates["rolling_mode"]["item_sell_offset"][1],
        )

        # 进入售卖界面并处理可能的卡顿
        self._enter_sell_interface_with_retry(item_pos, sell_pos)

        # 设置售卖价格
        self._set_sell_price(sell_ratio, cycle_index)

        # 获取售卖信息并确认
        return self._confirm_sell_transaction()

    def _enter_sell_interface_with_retry(self, item_pos: Tuple[int, int], sell_pos: Tuple[int, int]):
        """进入售卖界面，带重试机制"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self._click_sell_item(item_pos, sell_pos)
                if self._wait_for_sell_window():
                    return

                # 处理卡顿
                print(f'出售按钮没有按动，尝试解除卡顿 (尝试 {attempt + 1}/{max_retries})')
                self._resolve_sell_stuck()

            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(1)

    def _click_sell_item(self, item_pos: Tuple[int, int], sell_pos: Tuple[int, int]):
        """点击售卖物品"""
        self.action_executor.move_mouse(item_pos)
        time.sleep(0.3)
        self.action_executor.click_position(item_pos, right_click=True)
        time.sleep(0.5)
        self.action_executor.click_position(sell_pos)

    def _wait_for_sell_window(self) -> bool:
        """等待售卖窗口出现"""
        time.sleep(1)
        return self.detector.check_sell_window()

    def _resolve_sell_stuck(self):
        """解决售卖卡顿"""
        self.action_executor.press_key('esc')
        time.sleep(1)
        self.action_executor.click_position(self.detector.coordinates["rolling_mode"]["enter_storage"])
        time.sleep(1)

    def _set_sell_price(self, sell_ratio: float, cycle_index: int):
        """设置售卖价格"""
        min_sell_pos = self.detector.coordinates["rolling_mode"]["sell_num_left"]
        sell_num_slice_length = self.detector.coordinates["rolling_mode"]["sell_num_right"][0] - min_sell_pos[0]

        sell_x = min_sell_pos[0] + sell_num_slice_length * sell_ratio
        sell_y = min_sell_pos[1]

        self.action_executor.click_position(self.detector.coordinates["rolling_mode"]["min_sell_price_button"])
        time.sleep(1)
        self.action_executor.click_position((sell_x, sell_y))
        time.sleep(1)

    def _confirm_sell_transaction(self) -> Dict[str, any]:
        """确认售卖交易"""
        # 检测售卖数量
        cur_num, max_num = self.detector.detect_sell_num()
        if cur_num > max_num:
            self.action_executor.press_key('esc')
            time.sleep(1)
            raise ValueError("售卖数量超出限制")

        # 获取售卖信息
        min_sell_price = self.detector.detect_min_sell_price()
        expected_revenue = self.detector.detect_expected_revenue()

        self.action_executor.move_mouse(self.detector.coordinates["rolling_mode"]["sell_detail_button"])
        time.sleep(0.3)

        total_sell_price = self.detector.detect_total_sell_price_area()
        count = int(total_sell_price / min_sell_price) if min_sell_price > 0 else 0

        # 确认售卖
        self.action_executor.click_position(self.detector.coordinates["rolling_mode"]["final_sell_button"])
        time.sleep(1)

        # 记录售卖日志
        self.append_to_sell_log(
            f"出售成功, 单价: {min_sell_price}, 数量: {count}, 总价: {total_sell_price}, "
            f"预期收入: {expected_revenue}")

        return {
            "revenue": expected_revenue,
            "count": count,
            "price": min_sell_price
        }

    def _log_final_sell_results(self, sell_results: Dict[str, any], cost: float):
        """记录最终售卖结果"""
        total_profit = sell_results.get("total_profit", 0)
        total_count = sell_results.get("total_count", 0)
        cur_profit = total_profit

        self.append_to_sell_log(
            f"本轮售卖完成, 本轮盈利: {cur_profit - cost}, 本轮售卖: {total_count}个, "
            f"当前总盈利: {self.profit}, 当前售卖总量: {self.count}")

    def _execute_get_mail_half_coin(self):
        self.action_executor.click_position(self.detector.coordinates["rolling_mode"]["mail_button"])
        time.sleep(1)
        self.action_executor.click_position(self.detector.coordinates["rolling_mode"]["mail_trade_button"])
        time.sleep(1)
        self.action_executor.click_position(self.detector.coordinates["rolling_mode"]["mail_get_button"])
        time.sleep(1)
        self.action_executor.click_position(self.detector.coordinates["rolling_mode"]["mail_get_button"])
        time.sleep(1)
        self.action_executor.press_key('esc')

    def get_market_data(self) -> Optional[MarketData]:
        """获取当前市场数据"""
        return self.current_market_data

    def _detect_balance(self):
        self.action_executor.move_mouse(self.detector.coordinates["balance_active"])
        time.sleep(0.3)
        return self.detector.detect_balance()

    def append_to_sell_log(self, content, path='sell.log'):
        """
        追加内容到当前目录下的sell.log文件中

        参数:
            content (str): 要追加写入的内容

        返回:
            bool: 成功返回True，失败返回False
        """
        try:
            with open(path, 'a', encoding='utf-8') as f:
                current_time = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
                f.write(f"{current_time} {content}\n")  # 自动添加换行符
            return True
        except Exception as e:
            print(f"写入sell.log文件失败: {e}")
            return False


class TradingModeFactory:
    """交易模式工厂"""

    @staticmethod
    def create_mode(config: TradingConfig,
                    ocr_engine: TemplateOCREngine,
                    screen_capture: ScreenCapture,
                    action_executor: ActionExecutor) -> ITradingMode:
        """根据类型创建交易模式"""
        if config.trading_mode == TradingMode.HOARDING:
            price_detector = HoardingModeDetector(screen_capture, ocr_engine,
                                                  ItemType(config.item_type) == ItemType.CONVERTIBLE)
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
