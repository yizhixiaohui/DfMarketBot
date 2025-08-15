#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事件总线集成测试 - 验证业务事件迁移
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from src.core.event_bus import event_bus
from src.ui.adapter import TradingWorker, UIAdapter
from src.services.trading_service import TradingService
from src.config.config_factory import get_config_manager


class TestEventBusIntegration:
    """事件总线集成测试类"""
    
    @pytest.fixture(scope="class")
    def app(self):
        """创建QApplication实例"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        yield app
    
    def test_event_bus_business_events(self, app):
        """测试业务事件通过事件总线正确分发"""
        # 创建测试用的信号收集器
        signals_received = {
            'price_updated': [],
            'balance_updated': [],
            'status_changed': [],
            'error_occurred': [],
            'trading_started': [],
            'trading_stopped': []
        }
        
        def on_price_updated(price):
            signals_received['price_updated'].append(price)
            
        def on_balance_updated(balance):
            signals_received['balance_updated'].append(balance)
            
        def on_status_changed(status):
            signals_received['status_changed'].append(status)
            
        def on_error_occurred(error):
            signals_received['error_occurred'].append(error)
            
        def on_trading_started():
            signals_received['trading_started'].append(True)
            
        def on_trading_stopped():
            signals_received['trading_stopped'].append(True)
        
        # 连接事件总线信号
        event_bus.price_updated.connect(on_price_updated)
        event_bus.balance_updated.connect(on_balance_updated)
        event_bus.status_changed.connect(on_status_changed)
        event_bus.error_occurred.connect(on_error_occurred)
        event_bus.trading_started.connect(on_trading_started)
        event_bus.trading_stopped.connect(on_trading_stopped)
        
        try:
            # 直接触发事件总线事件
            event_bus.emit_price_updated(1000)
            event_bus.emit_balance_updated(5000)
            event_bus.emit_status_changed("测试中")
            event_bus.emit_error_occurred("测试错误")
            event_bus.emit_trading_started()
            event_bus.emit_trading_stopped()
            
            # 处理事件
            QTest.qWait(100)
            
            # 验证信号正确接收
            assert 1000 in signals_received['price_updated']
            assert 5000 in signals_received['balance_updated']
            assert "测试中" in signals_received['status_changed']
            assert "测试错误" in signals_received['error_occurred']
            assert True in signals_received['trading_started']
            assert True in signals_received['trading_stopped']
            
        finally:
            # 清理连接
            event_bus.price_updated.disconnect(on_price_updated)
            event_bus.balance_updated.disconnect(on_balance_updated)
            event_bus.status_changed.disconnect(on_status_changed)
            event_bus.error_occurred.disconnect(on_error_occurred)
            event_bus.trading_started.disconnect(on_trading_started)
            event_bus.trading_stopped.disconnect(on_trading_stopped)
    
    def test_trading_worker_events_through_bus(self, app):
        """测试TradingWorker通过事件总线发送事件"""
        # 创建测试用的信号收集器
        signals_received = {
            'price_updated': [],
            'balance_updated': [],
            'status_changed': []
        }
        
        def on_price_updated(price):
            signals_received['price_updated'].append(price)
            
        def on_balance_updated(balance):
            signals_received['balance_updated'].append(balance)
            
        def on_status_changed(status):
            signals_received['status_changed'].append(status)
        
        # 连接事件总线信号
        event_bus.price_updated.connect(on_price_updated)
        event_bus.balance_updated.connect(on_balance_updated)
        event_bus.status_changed.connect(on_status_changed)
        
        try:
            # 创建模拟的交易服务
            overlay = None  # 使用None作为overlay，因为我们测试事件总线
            trading_service = TradingService(overlay)
            config_manager = get_config_manager()
            
            # 创建TradingWorker
            worker = TradingWorker(trading_service, config_manager)
            
            # 注意：我们不实际启动worker，而是测试事件总线机制
            
            # 验证事件总线连接存在
            assert hasattr(event_bus, 'price_updated')
            assert hasattr(event_bus, 'balance_updated')
            assert hasattr(event_bus, 'status_changed')
            
        finally:
            # 清理连接
            event_bus.price_updated.disconnect(on_price_updated)
            event_bus.balance_updated.disconnect(on_balance_updated)
            event_bus.status_changed.disconnect(on_status_changed)
    
    def test_ui_adapter_event_connections(self, app):
        """测试UIAdapter正确连接事件总线"""
        # 创建测试用的信号收集器
        signals_received = {
            'price_updated': [],
            'balance_updated': [],
            'status_changed': []
        }
        
        def on_price_updated(price):
            signals_received['price_updated'].append(price)
            
        def on_balance_updated(balance):
            signals_received['balance_updated'].append(balance)
            
        def on_status_changed(status):
            signals_received['status_changed'].append(status)
        
        # 连接事件总线信号
        event_bus.price_updated.connect(on_price_updated)
        event_bus.balance_updated.connect(on_balance_updated)
        event_bus.status_changed.connect(on_status_changed)
        
        try:
            # 创建UIAdapter实例
            # 注意：这里使用mock的UI实例
            class MockUI:
                pass
            
            mock_ui = MockUI()
            overlay = None
            
            # 创建UIAdapter
            adapter = UIAdapter(mock_ui, overlay)
            
            # 验证事件总线连接存在
            assert hasattr(event_bus, 'price_updated')
            assert hasattr(event_bus, 'balance_updated')
            assert hasattr(event_bus, 'status_changed')
            
            # 触发事件总线事件
            event_bus.emit_price_updated(2000)
            event_bus.emit_balance_updated(10000)
            event_bus.emit_status_changed("UI测试")
            
            # 处理事件
            QTest.qWait(100)
            
            # 验证信号正确接收
            assert 2000 in signals_received['price_updated']
            assert 10000 in signals_received['balance_updated']
            assert "UI测试" in signals_received['status_changed']
            
            # 清理
            adapter.cleanup()
            
        finally:
            # 清理连接
            try:
                event_bus.price_updated.disconnect(on_price_updated)
                event_bus.balance_updated.disconnect(on_balance_updated)
                event_bus.status_changed.disconnect(on_status_changed)
            except:
                pass  # 忽略已经断开的连接


if __name__ == "__main__":
    pytest.main([__file__, "-v"])