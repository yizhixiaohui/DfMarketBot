# -*- coding: utf-8 -*-
"""
UI适配层 - 连接新架构与现有PyQt5 UI
"""
from typing import Dict, Any

from PyQt5.QtCore import QObject, pyqtSignal, QThread, QMutex

from ..config.config_factory import get_config_manager
from ..core.event_bus import event_bus
from ..core.exceptions import TradingException
from ..core.interfaces import IConfigManager, ITradingService, TradingMode, ItemType
from ..services.trading_service import TradingService


class TradingWorker(QThread):
    """交易工作线程"""

    def __init__(self, trading_service: ITradingService, config_manager: IConfigManager):
        super().__init__()
        self.trading_service = trading_service
        self.config_manager = config_manager

        # 线程控制
        self._mutex = QMutex()
        self._running = False
        self._config = None

    def update_config(self, config: Dict[str, Any]) -> None:
        """更新配置"""
        self._mutex.lock()
        try:
            # 保存到配置文件
            self._config = self.config_manager.update_config(config)

        finally:
            self._mutex.unlock()

    def get_current_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        self._mutex.lock()
        try:
            if self._config:
                return self._config.copy()
            else:
                return self.config_manager.load_config().__dict__
        finally:
            self._mutex.unlock()

    def start_trading(self) -> None:
        """开始交易"""
        if not self.isRunning():
            self.start()
            # 通过事件总线发送交易开始事件
            event_bus.emit_trading_started()

    def stop_trading(self) -> None:
        """停止交易"""
        self._mutex.lock()
        self._running = False
        self._mutex.unlock()

        if self.isRunning():
            self.wait()
            # 通过事件总线发送交易停止事件
            event_bus.emit_trading_stopped()

    def run(self) -> None:
        """工作线程主循环"""
        from ..core.event_bus import event_bus
        
        self._mutex.lock()
        self._running = True
        # 获取当前配置
        current_config = self._config or self.config_manager.load_config()
        loop_interval = current_config.loop_interval
        self._mutex.unlock()

        try:
            # 初始化交易服务
            self.trading_service.initialize(current_config)
            self.trading_service.prepare()

            while True:
                self._mutex.lock()
                if not self._running:
                    self._mutex.unlock()
                    break

                self._mutex.unlock()

                try:
                    # 执行交易周期
                    should_continue = self.trading_service.execute_cycle()

                    # 获取最新数据
                    market_data = self.trading_service.get_market_data()

                    # 发送事件更新UI - 使用事件总线
                    if market_data:
                        event_bus.emit_price_updated(market_data.current_price)
                        if market_data.balance is not None:
                            event_bus.emit_balance_updated(market_data.balance)

                    # 更新状态
                    event_bus.emit_status_changed("运行中")

                    # 检查是否应该停止
                    if not should_continue:
                        self.stop_trading()
                        break

                    # 休眠
                    self.msleep(loop_interval)

                except TradingException as e:
                    print(f"循环流执行失败，跳过当前循环流： {e}")
                    # 使用事件总线发送错误事件
                    # event_bus.emit_error_occurred(str(e))
                    # event_bus.emit_status_changed("错误")
                    self.msleep(loop_interval)  # 错误后等待

        except Exception as e:
            print(f"交易服务初始化失败: {e}")
            event_bus.emit_error_occurred(f"交易服务初始化失败: {e}")
            event_bus.emit_status_changed("错误")
        finally:
            event_bus.emit_trading_stopped()


class UIAdapter:
    """UI适配器 - 连接PyQt5 UI与新架构"""

    def __init__(self, ui_instance, overlay):
        self.ui = ui_instance
        self.config_manager = get_config_manager()
        self.overlay_ui = overlay
        self.trading_service = TradingService()
        self.worker = None

        # 初始化UI
        self._setup_ui()
        self._connect_signals()
        self._load_initial_config()

    def _setup_ui(self) -> None:
        """设置UI初始状态"""
        # 设置模式选项
        if hasattr(self.ui, 'comboBox_mode'):
            self.ui.comboBox_mode.clear()
            self.ui.comboBox_mode.addItems(["屯仓模式", "滚仓模式"])

        # 设置滚仓模式选项
        if hasattr(self.ui, 'comboBox_mode1_option'):
            self.ui.comboBox_mode1_option.clear()
            self.ui.comboBox_mode1_option.addItems([
                "配装选项1", "配装选项2", "配装选项3", "配装选项4"
            ])

    def _connect_signals(self) -> None:
        """连接信号"""
        # 连接UI控件信号
        if hasattr(self.ui, 'comboBox_mode'):
            self.ui.comboBox_mode.currentIndexChanged.connect(self._on_mode_changed)

        if hasattr(self.ui, 'comboBox_mode1_option'):
            self.ui.comboBox_mode1_option.currentIndexChanged.connect(self._on_rolling_option_changed)

        # 连接数值输入信号
        for widget_name in ['textEdit_ideal_price', 'textEdit_unacceptable_price', 'textEdit_loop_gap']:
            if hasattr(self.ui, widget_name):
                widget = getattr(self.ui, widget_name)
                widget.textChanged.connect(self._on_config_changed)

        # 连接复选框信号
        for widget_name in ['is_convertiable', 'is_key_mode', 'is_half_coin_mode']:
            if hasattr(self.ui, widget_name):
                widget = getattr(self.ui, widget_name)
                widget.stateChanged.connect(self._on_config_changed)

    def _load_initial_config(self) -> None:
        """加载初始配置"""
        try:
            config = self.config_manager.load_config()
            self._update_ui_from_config(config.__dict__)
        except Exception as e:
            print(f"加载初始配置失败: {e}")

    def _update_ui_from_config(self, config: Dict[str, Any]) -> None:
        """根据配置更新UI"""
        # 更新模式选择
        if hasattr(self.ui, 'comboBox_mode'):
            mode_index = config.get('trading_mode', TradingMode.HOARDING).value
            self.ui.comboBox_mode.setCurrentIndex(mode_index)

        # 更新滚仓模式选项
        if hasattr(self.ui, 'comboBox_mode1_option'):
            rolling_option = config.get('rolling_option', 0)
            self.ui.comboBox_mode1_option.setCurrentIndex(rolling_option)

        # 更新数值输入
        if hasattr(self.ui, 'textEdit_ideal_price'):
            self.ui.textEdit_ideal_price.setPlainText(str(config.get('ideal_price', 0)))

        if hasattr(self.ui, 'textEdit_unacceptable_price'):
            self.ui.textEdit_unacceptable_price.setPlainText(str(config.get('max_price', 0)))

        if hasattr(self.ui, 'textEdit_loop_gap'):
            self.ui.textEdit_loop_gap.setPlainText(str(int(config.get('loop_interval', 50))))

        # 更新复选框
        if hasattr(self.ui, 'is_convertiable'):
            self.ui.is_convertiable.setChecked(config.get('item_type', ItemType.CONVERTIBLE) == ItemType.CONVERTIBLE)

        if hasattr(self.ui, 'is_key_mode'):
            self.ui.is_key_mode.setChecked(config.get('key_mode', False))

        if hasattr(self.ui, 'is_half_coin_mode'):
            self.ui.is_half_coin_mode.setChecked(config.get('use_balance_calculation', False))

        # 更新UI可见性
        self._update_ui_visibility()

    def _update_ui_visibility(self) -> None:
        """更新UI控件的可见性"""
        current_mode = 0
        if hasattr(self.ui, 'comboBox_mode'):
            current_mode = self.ui.comboBox_mode.currentIndex()

        # 滚仓模式选项的可见性
        if hasattr(self.ui, 'label_mode1_option') and hasattr(self.ui, 'comboBox_mode1_option'):
            is_rolling = (current_mode == 1)
            self.ui.label_mode1_option.setVisible(is_rolling)
            self.ui.comboBox_mode1_option.setVisible(is_rolling)

    def _on_mode_changed(self, index: int) -> None:
        """模式改变处理"""
        self._update_ui_visibility()
        self._on_config_changed()

    def _on_rolling_option_changed(self, index: int) -> None:
        """滚仓选项改变处理"""
        self._on_config_changed()

    def _on_config_changed(self) -> None:
        """配置改变处理"""
        config = self._get_config_from_ui()
        if self.worker:
            self.worker.update_config(config)

    def _get_config_from_ui(self) -> Dict[str, Any]:
        """从UI获取配置"""
        config = {}

        # 模式
        if hasattr(self.ui, 'comboBox_mode'):
            config['trading_mode'] = self.ui.comboBox_mode.currentIndex()

        # 滚仓选项
        if hasattr(self.ui, 'comboBox_mode1_option'):
            config['rolling_option'] = self.ui.comboBox_mode1_option.currentIndex()

        # 数值参数
        try:
            if hasattr(self.ui, 'textEdit_ideal_price'):
                text = self.ui.textEdit_ideal_price.toPlainText().replace(',', '')
                config['ideal_price'] = int(text) if text else 0

            if hasattr(self.ui, 'textEdit_unacceptable_price'):
                text = self.ui.textEdit_unacceptable_price.toPlainText().replace(',', '')
                config['max_price'] = int(text) if text else 0

            if hasattr(self.ui, 'textEdit_loop_gap'):
                text = self.ui.textEdit_loop_gap.toPlainText().replace(',', '')
                config['loop_interval'] = int(text) if text else 50
        except ValueError:
            pass

        # 物品类型
        item_type = 1  # 默认不可兑换
        if hasattr(self.ui, 'is_convertiable') and self.ui.is_convertiable.isChecked():
            item_type = 0

        config['item_type'] = item_type

        # 钥匙卡模式
        if hasattr(self.ui, 'is_key_mode'):
            config['key_mode'] = self.ui.is_key_mode.isChecked()

        # 其他选项
        if hasattr(self.ui, 'is_half_coin_mode'):
            config['use_balance_calculation'] = self.ui.is_half_coin_mode.isChecked()

        return config

    def start_trading(self) -> None:
        """开始交易"""
        if self.worker is None:
            self.worker = TradingWorker(self.trading_service, self.config_manager)
            self._connect_worker_signals()

        if not self.worker.isRunning():
            config = self._get_config_from_ui()
            self.worker.update_config(config)
            self.worker.start_trading()

    def stop_trading(self) -> None:
        """停止交易"""
        if self.worker and self.worker.isRunning():
            self.worker.stop_trading()

    def _connect_worker_signals(self) -> None:
        """连接工作线程信号"""

        # 连接事件总线信号
        event_bus.status_changed.connect(self._on_status_changed)
        event_bus.error_occurred.connect(self._on_error_occurred)
        event_bus.price_updated.connect(self._on_price_updated)
        event_bus.balance_updated.connect(self._on_balance_updated)
        
        event_bus.trading_started.connect(self._on_trading_started)
        event_bus.trading_stopped.connect(self._on_trading_stopped)

    def _on_status_changed(self, status: str) -> None:
        """状态改变处理"""
        if hasattr(self.ui, 'label_status'):
            self.ui.label_status.setText(f"状态: {status}")

    def _on_error_occurred(self, error: str) -> None:
        """错误处理"""
        print(f"交易错误: {error}")
        if hasattr(self.ui, 'label_status'):
            self.ui.label_status.setText(f"错误: {error}")

    def _on_price_updated(self, price: int) -> None:
        """价格更新处理"""
        if hasattr(self.ui, 'label_current_price'):
            self.ui.label_current_price.setText(f"当前价格: {price}")

    def _on_balance_updated(self, balance: int) -> None:
        """余额更新处理"""
        if hasattr(self.ui, 'label_balance'):
            self.ui.label_balance.setText(f"哈夫币余额: {balance}")

    def _on_trading_started(self) -> None:
        """交易开始处理"""
        if hasattr(self.ui, 'label_status'):
            self.ui.label_status.setText("状态: 运行中")

    def _on_trading_stopped(self) -> None:
        """交易停止处理"""
        if hasattr(self.ui, 'label_status'):
            self.ui.label_status.setText("状态: 已停止")

    def cleanup(self) -> None:
        """清理资源"""

        # 断开事件总线连接
        try:
            event_bus.status_changed.disconnect(self._on_status_changed)
            event_bus.error_occurred.disconnect(self._on_error_occurred)
            event_bus.price_updated.disconnect(self._on_price_updated)
            event_bus.balance_updated.disconnect(self._on_balance_updated)
        except:
            pass
            
        if self.worker:
            self.worker.stop_trading()
            self.worker = None
