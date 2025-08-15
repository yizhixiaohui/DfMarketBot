# -*- coding: utf-8 -*-
"""
事件总线测试用例
测试事件总线和悬浮窗的文本更新功能
"""
import sys
import time
from typing import List

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

# 添加项目根目录到Python路径
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.event_bus import event_bus
from src.ui.overlay import TransparentOverlay


class TestEventBus:
    """事件总线测试类"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.overlay = TransparentOverlay()
        self.received_texts: List[str] = []
        
    def setup_test(self):
        """设置测试环境"""
        self.overlay.show()
        # 连接信号到测试槽
        event_bus.overlay_text_updated.connect(self._on_text_received)
        
    def _on_text_received(self, text: str):
        """接收文本更新的测试槽"""
        self.received_texts.append(text)
        print(f"收到文本更新: {text}")
        
    def test_basic_text_update(self):
        """测试基本文本更新"""
        print("=== 测试基本文本更新 ===")
        test_text = "测试消息"
        event_bus.emit_overlay_text_updated(test_text)
        
        # 等待事件处理
        QTimer.singleShot(100, self.app.quit)
        self.app.exec_()
        
        # 验证结果
        assert test_text in self.received_texts, f"期望收到 '{test_text}'，实际收到: {self.received_texts}"
        assert self.overlay.label.text() == test_text, f"悬浮窗文本应为 '{test_text}'，实际为: {self.overlay.label.text()}"
        print("✅ 基本文本更新测试通过")
        
    def test_multiple_text_updates(self):
        """测试多次文本更新"""
        print("=== 测试多次文本更新 ===")
        test_texts = ["消息1", "消息2", "消息3"]
        
        for text in test_texts:
            event_bus.emit_overlay_text_updated(text)
            
        # 等待事件处理
        QTimer.singleShot(200, self.app.quit)
        self.app.exec_()
        
        # 验证结果
        for text in test_texts:
            assert text in self.received_texts, f"期望收到 '{text}'"
        assert self.overlay.label.text() == test_texts[-1], f"悬浮窗应显示最后一条消息 '{test_texts[-1]}'"
        print("✅ 多次文本更新测试通过")
        
    def test_empty_text(self):
        """测试空文本"""
        print("=== 测试空文本 ===")
        event_bus.emit_overlay_text_updated("")
        
        QTimer.singleShot(100, self.app.quit)
        self.app.exec_()
        
        assert "" in self.received_texts
        print("✅ 空文本测试通过")
        
    def test_long_text(self):
        """测试长文本"""
        print("=== 测试长文本 ===")
        long_text = "这是一个非常长的测试消息，用于测试悬浮窗对长文本的处理能力，确保文本能够正确显示并且不会导致界面异常"
        event_bus.emit_overlay_text_updated(long_text)
        
        QTimer.singleShot(100, self.app.quit)
        self.app.exec_()
        
        assert long_text in self.received_texts
        assert self.overlay.label.text() == long_text
        print("✅ 长文本测试通过")
        
    def test_special_characters(self):
        """测试特殊字符"""
        print("=== 测试特殊字符 ===")
        special_text = "测试消息：价格¥1000，进度100%，时间12:30"
        event_bus.emit_overlay_text_updated(special_text)
        
        QTimer.singleShot(100, self.app.quit)
        self.app.exec_()
        
        assert special_text in self.received_texts
        assert self.overlay.label.text() == special_text
        print("✅ 特殊字符测试通过")
        
    def test_performance(self):
        """测试性能：快速连续发送消息"""
        print("=== 测试性能 ===")
        messages = [f"消息{i}" for i in range(10)]
        
        for msg in messages:
            event_bus.emit_overlay_text_updated(msg)
            
        QTimer.singleShot(300, self.app.quit)
        self.app.exec_()
        
        # 验证所有消息都被接收
        for msg in messages:
            assert msg in self.received_texts
        # 验证最后一条消息显示
        assert self.overlay.label.text() == messages[-1]
        print("✅ 性能测试通过")
        
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始事件总线测试...")
        self.setup_test()
        
        try:
            self.test_basic_text_update()
            self.test_multiple_text_updates()
            self.test_empty_text()
            self.test_long_text()
            self.test_special_characters()
            self.test_performance()
            
            print("\n🎉 所有测试通过！")
            return True
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            return False
            
        finally:
            self.overlay.close()


def main():
    """主测试函数"""
    print("=" * 50)
    print("事件总线测试")
    print("=" * 50)
    
    test = TestEventBus()
    success = test.run_all_tests()
    
    if success:
        print("\n✅ 事件总线功能正常！")
    else:
        print("\n❌ 事件总线存在问题！")
        
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)