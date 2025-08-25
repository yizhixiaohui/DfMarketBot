# -*- coding: utf-8 -*-
"""
配置管理模块
"""
import os
import time
from typing import Any, Dict, Type

from .delay_config import DelayConfig
from .serializer import ConfigSerializer, JsonSerializer, YamlSerializer

try:
    from src.core.exceptions import ConfigurationException
    from src.core.interfaces import IConfigManager, TConfig, TradingConfig
except ImportError:
    from ..core.exceptions import ConfigurationException
    from ..core.interfaces import IConfigManager, TConfig, TradingConfig


class BaseConfigManager(IConfigManager[TConfig]):
    """基础配置管理器"""

    def __init__(self, config_path: str = None, serializer: ConfigSerializer = None):
        super().__init__(config_path)
        # 获取正确的基目录
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_path = os.path.join(base_dir, "config", "settings.yaml")
        self.config_path = config_path
        # 确保配置目录存在
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        if serializer is None:
            # 默认根据文件后缀选择
            if self.config_path.endswith(".yaml") or self.config_path.endswith(".yml"):
                serializer = YamlSerializer()
            elif self.config_path.endswith(".json"):
                serializer = JsonSerializer()
            else:
                raise ValueError("无法根据文件后缀自动选择序列化器，请传入 serializer 参数")
        self._serializer = serializer
        self._last_modified = 0
        self._cached_config = None

    def load_config(self) -> TConfig:
        raise NotImplementedError("Subclasses must implement this method")

    def save_config(self, config: TConfig):
        raise NotImplementedError("Subclasses must implement this method")

    def reload_config(self) -> TConfig:
        """重新加载配置（支持热更新）"""
        try:
            current_modified = os.path.getmtime(self.config_path) if os.path.exists(self.config_path) else 0
            if current_modified > self._last_modified or self._cached_config is None:
                self._cached_config = self.load_config()
                self._last_modified = current_modified
            return self._cached_config
        except Exception as e:
            print("配置重加载失败:", e)
            # 如果重新加载失败，返回缓存的配置或默认配置
            if self._cached_config is not None:
                return self._cached_config
            return self._create_default_config()

    def update_config(self, updates: Dict[str, Any]) -> TConfig:
        """更新配置"""
        try:
            config_dict = self._config_to_dict(self.load_config())
            self._deep_update(config_dict, updates)
            new_config = self._dict_to_config(config_dict, self._config_class())
            self.save_config(new_config)
            return new_config
        except Exception as e:
            raise ConfigurationException(f"更新配置失败: {e}") from e

    def _config_class(self) -> Type[TConfig]:
        """获取配置类，子类实现"""
        raise NotImplementedError("Subclasses must implement this method")

    def _create_default_config(self) -> TConfig:
        """创建默认配置，子类实现"""
        raise NotImplementedError("Subclasses must implement this method")

    def _deep_update(self, base_dict: Dict, update_dict: Dict) -> None:
        """深度更新字典"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def _load_config(self, config_class: Type[TConfig]) -> TConfig:
        """通用配置加载方法"""
        try:
            if not os.path.exists(self.config_path):
                # 如果配置文件不存在，创建默认配置
                default_config = self._create_default_config()
                self.save_config(default_config)
                return default_config

            data = self._serializer.load(self.config_path)
            return self._dict_to_config(data, config_class)
        except Exception as e:
            # 如果加载失败，返回默认配置
            print(f"警告: 加载配置文件失败，使用默认配置: {e}")
            return self._create_default_config()

    def _save_config(self, config: TConfig) -> None:
        """通用配置保存方法"""
        try:
            config_dict = self._config_to_dict(config)
            self._serializer.save(self.config_path, config_dict)
            self._update_cache(config)
        except Exception as e:
            raise ConfigurationException(f"保存配置失败: {e}") from e

    def _update_cache(self, config: TConfig) -> None:
        """更新缓存"""
        self._cached_config = config
        self._last_modified = time.time()


class TradingConfigManager(BaseConfigManager[TradingConfig]):
    """YAML配置管理器"""

    def load_config(self) -> TradingConfig:
        """加载配置文件"""
        return self._load_config(self._config_class())

    def save_config(self, config: TradingConfig):
        """保存配置到文件"""
        self._save_config(config)

    def _config_class(self) -> Type[TradingConfig]:
        return TradingConfig

    def _create_default_config(self) -> TradingConfig:
        """创建默认配置"""
        return TradingConfig()


class DelayConfigManager(BaseConfigManager[DelayConfig]):
    """延迟配置管理器"""

    def __init__(self, config_path: str = None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_path = os.path.join(base_dir, "config", "delay_config.yaml")
        super().__init__(config_path)

    def load_config(self) -> DelayConfig:
        """加载配置文件"""
        return self._load_config(DelayConfig)

    def save_config(self, config: DelayConfig) -> None:
        """保存配置到YAML文件"""
        self._save_config(config)

    def _config_class(self) -> Type[DelayConfig]:
        return DelayConfig

    def _create_default_config(self) -> DelayConfig:
        """创建基于当前硬编码值的默认配置"""
        return DelayConfig(
            delays={
                "hoarding_mode": {
                    "enter_action": 0.05,  # time.sleep(0.05) in prepare()
                    "balance_detection": 0.0,  # self.action_executor.move_mouse() 无延迟
                    "buy_operation": 0.0,  # 购买操作无额外延迟
                    "refresh_operation": 0.01,  # time.sleep(0.01) in _execute_refresh()
                    "escape_key": 0.0,  # 按ESC键无延迟
                    "re_enter": 0.0,  # 重新进入无延迟
                },
                "rolling_mode": {
                    # 执行完刷新操作(按esc)后的等待时间
                    "after_refresh": 0.01,
                    # 鼠标挪到哈夫币详情页面后，等待检测前的延迟
                    "balance_detection": 0.3,
                    # 初始化完成后延迟的时间（初始化主要会检测一遍现在的哈夫币，用于计算收益）
                    "initialization": 0.4,
                    # 按L进入配装页，点击切换配装之前的延迟
                    "before_option_switch": 0.01,
                    # 点击切换配装之后的延迟，延迟后才会检测价格，以防买到高价
                    "after_option_switch": 0.05,
                    # 价格异常后重试的延迟，异常原因主要是配装时卡顿导致价格迟迟没有出现
                    "price_detection_retry": 0.05,
                    # 点击购买按钮后，检测是否购买成功(也就是是否有弹窗)前的延迟，设置久一点让弹窗动画播完再检测
                    "after_buy": 2.0,
                    # 检测到购买失败(也就是有失败弹窗)后，按下esc退出后的延迟
                    "after_check_purchase_failure": 1.0,
                    # 检测到彻底购买失败(也就是弹窗失败后检测到余额也没变)后，等待退出前的延迟
                    "after_buy_failed": 0.4,
                    # 检测到没有购买失败弹窗(也就是购买成功)后，准备检测余额并执行售卖动作前的延迟，这里
                    "after_buy_success": 1.0,
                    # 售卖流程整体完成后，准备邮件领钱之前的延迟，自动售卖结束时已经有1s间隔了，这里延迟可以不用太高
                    "before_get_mail": 0.3,
                    # 邮件领钱完成后，会按下esc返回进入邮件之前的页面（一般来说是仓库)，等待它完全退出邮件窗口的延迟
                    "after_get_mail": 2.0,
                    # 邮件领完钱后，会回到仓库页面，这里是在仓库页面按下esc后的延迟，用于等待回到配装页面
                    "buy_success_refresh_final": 2.0,
                    # 购买流程全部完成后会检测一次余额，用于计算下次盈利的基础值，这里是检测余额后执行下一步前的延迟
                    "after_get_mail_and_detect_balance": 0.3,
                    # 点击进入仓库页面后的延迟
                    "after_enter_storage": 1.0,
                    # 点击转移全部按钮后的延迟
                    "after_transfer_all": 1.0,
                    # 鼠标挪到待售卖物品后的延迟
                    "after_move_to_sell_item": 0.3,
                    # 鼠标右键点击待售卖物品后的延迟
                    "after_right_click_sell_item": 0.5,
                    # 等待出售窗口出现的延迟
                    "sell_window_wait": 1.0,
                    # 购买窗口出现后，点击出售按钮后的延迟
                    "after_sell_button_click": 0.7,
                    # 解决售卖卡顿出现时的点击间隔(按esc -> delay -> 进入仓库 -> delay)
                    "resolve_sell_stuck": 1.0,
                    # 点击售卖价格输入框后的延迟
                    "after_sell_price_text_click": 0.5,
                    # 全选售卖价格后的延迟
                    "after_select_sell_text_price": 0.5,
                    # 设置售卖价格后的延迟(不管是不是快速售卖，当一切价格设置完成后，准备售卖前的延迟)
                    "after_set_sell_price": 1.0,
                    # 设置售卖价格逻辑整体完成后(也就是最后点击完滑块的步骤)等待的延迟
                    "after_set_sell_price_finish": 1.0,
                    # 检测到售卖数量超出当前可售栏最大值后，按下esc退出售卖后的延迟时间
                    "after_sale_column_full": 1.0,
                    # 鼠标挪到待售卖物品详情后的延迟(用于检测税后价格，计算单价和子弹数量)
                    "after_move_to_sell_detail": 0.3,
                    # 最终成功点击完售卖按钮，成功售卖后的延迟
                    "after_sell_finish": 1.0,
                    # 点击右上角进入邮箱后的延迟
                    "after_mail_button_click": 1.0,
                    # 邮箱界面点击交易行类别邮件后的延迟
                    "after_mail_trade_click": 1.0,
                    # 邮箱界面点击领取全部后的延迟(点完会跳出哈夫币领取的弹框，这里是等待它完全弹出)
                    "after_mail_get_click": 2.0,
                    # 邮箱界面领取完哈夫币，然后再次点击一下退出这个界面，之后的延迟
                    "after_confirm_mail_click": 1.0,
                },
            }
        )
