# -*- coding: utf-8 -*-
"""
动作执行器窗口偏移功能测试
"""
import unittest
from unittest.mock import patch, MagicMock

from src.infrastructure.action_executor import PyAutoGUIActionExecutor, MockActionExecutor


class TestActionExecutorWindowOffset(unittest.TestCase):
    """测试动作执行器的窗口偏移功能"""

    def setUp(self):
        """测试前准备"""
        self.mock_executor = MockActionExecutor(log_actions=False)
        
    def test_set_window_offset(self):
        """测试设置窗口偏移量"""
        # 设置窗口偏移量
        self.mock_executor.set_window_offset(100, 50)
        
        # 验证偏移量已设置
        self.assertEqual(self.mock_executor.window_offset, (100, 50))
        
    def test_clear_window_offset(self):
        """测试清除窗口偏移量"""
        # 先设置偏移量
        self.mock_executor.set_window_offset(100, 50)
        
        # 清除偏移量
        self.mock_executor.clear_window_offset()
        
        # 验证偏移量已清除
        self.assertIsNone(self.mock_executor.window_offset)
        
    def test_coordinate_conversion_with_offset(self):
        """测试带偏移量的坐标转换"""
        # 设置窗口偏移量
        self.mock_executor.set_window_offset(100, 50)
        
        # 测试坐标转换
        converted = self.mock_executor._convert_coordinates(200, 150)
        
        # 验证转换结果
        self.assertEqual(converted, (300, 200))  # (200+100, 150+50)
        
    def test_coordinate_conversion_without_offset(self):
        """测试无偏移量的坐标转换"""
        # 不设置偏移量
        
        # 测试坐标转换
        converted = self.mock_executor._convert_coordinates(200.5, 150.7)
        
        # 验证转换结果（应该只是转换为整数）
        self.assertEqual(converted, (200, 150))
        
    def test_click_position_with_offset(self):
        """测试带偏移量的点击操作"""
        # 设置窗口偏移量
        self.mock_executor.set_window_offset(100, 50)
        
        # 执行点击操作
        self.mock_executor.click_position((200, 150))
        
        # 验证动作记录
        actions = self.mock_executor.get_actions()
        self.assertEqual(len(actions), 1)
        
        action = actions[0]
        self.assertEqual(action["type"], "click")
        self.assertEqual(action["original_coordinates"], (200, 150))
        self.assertEqual(action["converted_coordinates"], (300, 200))
        
    def test_click_position_without_offset(self):
        """测试无偏移量的点击操作"""
        # 不设置偏移量
        
        # 执行点击操作
        self.mock_executor.click_position((200, 150))
        
        # 验证动作记录
        actions = self.mock_executor.get_actions()
        self.assertEqual(len(actions), 1)
        
        action = actions[0]
        self.assertEqual(action["type"], "click")
        self.assertEqual(action["original_coordinates"], (200, 150))
        self.assertEqual(action["converted_coordinates"], (200, 150))
        
    def test_move_mouse_with_offset(self):
        """测试带偏移量的鼠标移动"""
        # 设置窗口偏移量
        self.mock_executor.set_window_offset(100, 50)
        
        # 执行鼠标移动
        self.mock_executor.move_mouse((200, 150))
        
        # 验证动作记录
        actions = self.mock_executor.get_actions()
        self.assertEqual(len(actions), 1)
        
        action = actions[0]
        self.assertEqual(action["type"], "move")
        self.assertEqual(action["original_position"], (200, 150))
        self.assertEqual(action["converted_position"], (300, 200))
        
    def test_right_click_with_offset(self):
        """测试带偏移量的右键点击"""
        # 设置窗口偏移量
        self.mock_executor.set_window_offset(100, 50)
        
        # 执行右键点击
        self.mock_executor.click_position((200, 150), right_click=True)
        
        # 验证动作记录
        actions = self.mock_executor.get_actions()
        self.assertEqual(len(actions), 1)
        
        action = actions[0]
        self.assertEqual(action["type"], "click")
        self.assertEqual(action["right_click"], True)
        self.assertEqual(action["converted_coordinates"], (300, 200))

    @patch('pyautogui.moveTo')
    @patch('pyautogui.click')
    def test_pyautogui_executor_with_offset(self, mock_click, mock_move_to):
        """测试PyAutoGUI执行器的窗口偏移功能"""
        executor = PyAutoGUIActionExecutor(debug=False)
        
        # 设置窗口偏移量
        executor.set_window_offset(100, 50)
        
        # 执行点击操作
        executor.click_position((200, 150))
        
        # 验证PyAutoGUI调用
        mock_move_to.assert_called_once_with(300, 200)  # 应用了偏移量
        mock_click.assert_called_once()

    @patch('pyautogui.moveTo')
    def test_pyautogui_executor_move_with_offset(self, mock_move_to):
        """测试PyAutoGUI执行器的鼠标移动偏移功能"""
        executor = PyAutoGUIActionExecutor(debug=False)
        
        # 设置窗口偏移量
        executor.set_window_offset(100, 50)
        
        # 执行鼠标移动
        executor.move_mouse((200, 150))
        
        # 验证PyAutoGUI调用
        mock_move_to.assert_called_once_with(300, 200)  # 应用了偏移量


if __name__ == '__main__':
    unittest.main()