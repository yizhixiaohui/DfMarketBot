# -*- coding: utf-8 -*-
"""
动作执行器基础设施
"""
import platform
import threading
import time
from typing import Optional, Tuple

import keyboard
import pyautogui
from pyautogui import Point

from ..core.exceptions import ActionExecutionException
from ..core.interfaces import IActionExecutor


class PyAutoGUIActionExecutor(IActionExecutor):
    """基于PyAutoGUI的动作执行器"""

    def __init__(self, debug=False):
        # 设置PyAutoGUI的安全特性
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.05
        self.debug = debug

        # 锁用于线程安全
        self._lock = threading.Lock()

        # 窗口偏移量，用于窗口模式下的坐标转换
        self.window_offset: Optional[Tuple[int, int]] = None

    def set_window_offset(self, x: int, y: int) -> None:
        """设置窗口偏移量，用于窗口模式下的坐标转换"""
        self.window_offset = (x, y)
        if self.debug:
            print(f"设置窗口偏移量: ({x}, {y})")

    def clear_window_offset(self) -> None:
        """清除窗口偏移量，回到全屏模式"""
        self.window_offset = None
        if self.debug:
            print("清除窗口偏移量，回到全屏模式")

    def _convert_coordinates(self, x: float, y: float, reverse=False) -> Tuple[int, int]:
        """将模板坐标转换为基于窗口位置的绝对屏幕坐标"""
        offset_x = self.window_offset[0]
        offset_y = self.window_offset[1]
        if reverse:
            offset_x = -offset_x
            offset_y = -offset_y
        if self.window_offset:
            converted_x = int(x + offset_x)
            converted_y = int(y + offset_y)
            if self.debug:
                print(f"坐标{'反向' if reverse else ''}转换: ({x}, {y}) -> ({converted_x}, {converted_y})")
            return converted_x, converted_y
        return int(x), int(y)

    def click_position(self, position: Tuple[float, float], right_click=False) -> None:
        """点击指定坐标位置"""
        try:
            with self._lock:
                # 应用窗口偏移量进行坐标转换
                x, y = self._convert_coordinates(position[0], position[1])

                # 移动鼠标并点击
                pyautogui.moveTo(x, y)
                if right_click:
                    pyautogui.rightClick()
                else:
                    pyautogui.click()
                if self.debug:
                    print(f"click position ({x}, {y})")

        except Exception as e:
            raise ActionExecutionException(f"点击位置失败: {e}") from e

    def press_key(self, key: str) -> None:
        """按下指定按键"""
        try:
            with self._lock:
                pyautogui.press(key)
                if self.debug:
                    print(f"press key {key}")

        except Exception as e:
            raise ActionExecutionException(f"按键失败: {e}") from e

    def key_down(self, key: str) -> None:
        """按下指定按键"""
        try:
            with self._lock:
                pyautogui.keyDown(key)
                if self.debug:
                    print(f"press key {key}")

        except Exception as e:
            raise ActionExecutionException(f"按键失败: {e}") from e

    def key_up(self, key: str) -> None:
        """按下指定按键"""
        try:
            with self._lock:
                pyautogui.keyUp(key)
                if self.debug:
                    print(f"press key {key}")

        except Exception as e:
            raise ActionExecutionException(f"按键失败: {e}") from e

    def multi_key_press(self, a, b, interval=0.03):
        self.key_down(a)
        time.sleep(interval)
        self.key_down(b)
        time.sleep(interval)
        self.key_up(a)
        time.sleep(interval)
        self.key_up(b)

    def type_text(self, text: str) -> None:
        """输入文本"""
        try:
            with self._lock:
                pyautogui.typewrite(text, interval=0.04)

        except Exception as e:
            raise ActionExecutionException(f"输入文本失败: {e}") from e

    def scroll(self, clicks: int) -> None:
        """滚动鼠标滚轮"""
        try:
            with self._lock:
                pyautogui.scroll(clicks)

        except Exception as e:
            raise ActionExecutionException(f"滚动失败: {e}") from e

    def move_mouse(self, position: Tuple[float, float]) -> None:
        """移动鼠标到指定位置"""
        try:
            with self._lock:
                # 应用窗口偏移量进行坐标转换
                x, y = self._convert_coordinates(position[0], position[1])
                pyautogui.moveTo(x, y)
                if self.debug:
                    print(f"move to ({x}, {y})")
        except Exception as e:
            raise ActionExecutionException(f"移动鼠标失败: {e}") from e

    def get_mouse_position(self) -> Point:
        """获取当前鼠标位置"""
        try:
            pos = pyautogui.position()

            # 如果有窗口偏移量，需要进行反向转换（从屏幕坐标转换回窗口相对坐标）
            if self.window_offset:
                converted_x, converted_y = self._convert_coordinates(pos.x, pos.y, reverse=True)
                pos = Point(x=converted_x, y=converted_y)

            if self.debug:
                print(f"获取鼠标位置: ({pos.x}, {pos.y})")

            return pos

        except Exception as e:
            raise ActionExecutionException(f"获取鼠标位置失败: {e}") from e

    def wait_for_key(self, key: str) -> None:
        """等待按键按下"""
        try:
            # 在macOS上暂时返回True，避免管理员权限问题
            if platform.system() == "Darwin":
                # macOS系统，暂时跳过键盘监听
                time.sleep(1)  # 默认等待1秒
                return
            # Windows系统，使用keyboard库
            keyboard.wait(key)
        except Exception as e:
            raise ActionExecutionException(f"按键失败: {e}") from e


class MockActionExecutor(IActionExecutor):
    """动作执行器的模拟实现，用于测试"""

    def __init__(self, log_actions: bool = True):
        self.log_actions = log_actions
        self.actions = []
        # 窗口偏移量，用于窗口模式下的坐标转换
        self.window_offset: Optional[Tuple[int, int]] = None

    def set_window_offset(self, x: int, y: int) -> None:
        """设置窗口偏移量，用于窗口模式下的坐标转换"""
        self.window_offset = (x, y)
        if self.log_actions:
            print(f"模拟设置窗口偏移量: ({x}, {y})")

    def clear_window_offset(self) -> None:
        """清除窗口偏移量，回到全屏模式"""
        self.window_offset = None
        if self.log_actions:
            print("模拟清除窗口偏移量，回到全屏模式")

    def _convert_coordinates(self, x: float, y: float) -> Tuple[int, int]:
        """将模板坐标转换为基于窗口位置的绝对屏幕坐标"""
        if self.window_offset:
            converted_x = int(x + self.window_offset[0])
            converted_y = int(y + self.window_offset[1])
            if self.log_actions:
                print(f"模拟坐标转换: ({x}, {y}) -> ({converted_x}, {converted_y})")
            return converted_x, converted_y
        return int(x), int(y)

    def click_position(self, position: Tuple[float, float], right_click=False) -> None:
        """模拟点击位置"""
        # 应用窗口偏移量进行坐标转换
        converted_pos = self._convert_coordinates(position[0], position[1])
        action = {
            "type": "click",
            "original_coordinates": position,
            "converted_coordinates": converted_pos,
            "right_click": right_click,
        }
        self.actions.append(action)
        if self.log_actions:
            print(f"模拟点击: {position} -> {converted_pos}")

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
        # 应用窗口偏移量进行坐标转换
        converted_pos = self._convert_coordinates(position[0], position[1])
        action = {"type": "move", "original_position": position, "converted_position": converted_pos}
        self.actions.append(action)
        if self.log_actions:
            print(f"模拟移动鼠标: {position} -> {converted_pos}")

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
        if executor_type == "mock":
            return MockActionExecutor(**kwargs)
        raise ValueError(f"不支持的动作执行器类型: {executor_type}")
