# -*- coding: utf-8 -*-
"""
动作执行器基础设施
"""
import time
import pyautogui
import keyboard
from typing import Tuple, Optional
import threading

from pyautogui import Point

from ..core.interfaces import IActionExecutor
from ..core.exceptions import ActionExecutionException


class PyAutoGUIActionExecutor(IActionExecutor):
    """基于PyAutoGUI的动作执行器"""
    
    def __init__(self):
        # 设置PyAutoGUI的安全特性
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01
        
        # 锁用于线程安全
        self._lock = threading.Lock()
    
    def click_position(self, coordinates: Tuple[float, float]) -> None:
        """点击指定坐标位置"""
        try:
            with self._lock:
                x, y = coordinates
                # 确保坐标是整数
                x, y = int(x), int(y)
                
                # 移动鼠标并点击
                pyautogui.moveTo(x, y)
                pyautogui.click()
                
        except Exception as e:
            raise ActionExecutionException(f"点击位置失败: {e}")
    
    def press_key(self, key: str) -> None:
        """按下指定按键"""
        try:
            with self._lock:
                pyautogui.press(key)
                
        except Exception as e:
            raise ActionExecutionException(f"按键失败: {e}")
    
    def type_text(self, text: str) -> None:
        """输入文本"""
        try:
            with self._lock:
                pyautogui.typewrite(text, interval=0.01)
                
        except Exception as e:
            raise ActionExecutionException(f"输入文本失败: {e}")
    
    def scroll(self, clicks: int) -> None:
        """滚动鼠标滚轮"""
        try:
            with self._lock:
                pyautogui.scroll(clicks)
                
        except Exception as e:
            raise ActionExecutionException(f"滚动失败: {e}")
    
    def move_mouse(self, position: Tuple[float, float]) -> None:
        """移动鼠标到指定位置"""
        try:
            with self._lock:
                x, y = int(position[0]), int(position[1])
                pyautogui.moveTo(x, y, duration=0.1)
        except Exception as e:
            raise ActionExecutionException(f"移动鼠标失败: {e}")
    
    def get_mouse_position(self) -> Point:
        """获取当前鼠标位置"""
        try:
            return pyautogui.position()
        except Exception as e:
            raise ActionExecutionException(f"获取鼠标位置失败: {e}")
    
    def wait_for_key(self, key: str):
        """等待按键按下"""
        try:
            # 在macOS上暂时返回True，避免管理员权限问题
            import platform
            if platform.system() == "Darwin":
                # macOS系统，暂时跳过键盘监听
                import time
                time.sleep(1)  # 默认等待1秒
                return True
            else:
                # Windows系统，使用keyboard库
                keyboard.wait(key)
        except Exception as e:
            raise ActionExecutionException(f"按键失败: {e}")


class MockActionExecutor(IActionExecutor):
    """动作执行器的模拟实现，用于测试"""
    
    def __init__(self, log_actions: bool = True):
        self.log_actions = log_actions
        self.actions = []
    
    def click_position(self, coordinates: Tuple[float, float]) -> None:
        """模拟点击位置"""
        action = {"type": "click", "coordinates": coordinates}
        self.actions.append(action)
        if self.log_actions:
            print(f"模拟点击: {coordinates}")
    
    def press_key(self, key: str) -> None:
        """模拟按键"""
        action = {"type": "key", "key": key}
        self.actions.append(action)
        if self.log_actions:
            print(f"模拟按键: {key}")
    
    def type_text(self, text: str) -> None:
        """模拟输入文本"""
        action = {"type": "type", "text": text}
        self.actions.append(action)
        if self.log_actions:
            print(f"模拟输入: {text}")
    
    def scroll(self, clicks: int) -> None:
        """模拟滚动"""
        action = {"type": "scroll", "clicks": clicks}
        self.actions.append(action)
        if self.log_actions:
            print(f"模拟滚动: {clicks}")
    
    def move_mouse(self, position: Tuple[float, float]) -> None:
        """模拟移动鼠标"""
        action = {"type": "move", "position": position}
        self.actions.append(action)
        if self.log_actions:
            print(f"模拟移动鼠标: {position}")
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """获取模拟鼠标位置"""
        return (100, 100)  # 返回固定位置
    
    def wait_for_key(self, key: str, timeout: Optional[float] = None) -> bool:
        """模拟等待按键"""
        return True  # 总是返回成功
    
    def get_actions(self) -> list:
        """获取执行过的动作列表"""
        return self.actions.copy()
    
    def clear_actions(self) -> None:
        """清空动作记录"""
        self.actions.clear()


class ActionExecutorFactory:
    """动作执行器工厂"""
    
    @staticmethod
    def create_executor(executor_type: str = "pyautogui", **kwargs):
        """创建动作执行器"""
        if executor_type == "pyautogui":
            return PyAutoGUIActionExecutor()
        elif executor_type == "mock":
            return MockActionExecutor(**kwargs)
        else:
            raise ValueError(f"不支持的动作执行器类型: {executor_type}")