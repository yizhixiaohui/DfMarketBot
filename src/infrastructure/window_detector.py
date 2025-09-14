# -*- coding: utf-8 -*-
"""
窗口检测器 - 提供底层窗口检测功能
"""
from typing import List, Optional, Tuple

import pyautogui
import win32con
import win32gui

from src.core.exceptions import WindowDetectionException
from src.core.window_models import WindowInfo, WindowState


class WindowDetector:
    """窗口检测器类 - 负责检测和获取目标窗口信息"""

    def __init__(self):
        self._cached_windows: List[WindowInfo] = []

    def find_window_by_title(self, title: str) -> Optional[WindowInfo]:
        """
        根据窗口标题查找窗口

        Args:
            title: 窗口标题（支持部分匹配）

        Returns:
            WindowInfo对象，如果未找到则返回None

        Raises:
            WindowDetectionException: 窗口检测过程中发生错误
        """
        try:
            found_window = None

            def enum_windows_callback(hwnd, lparam):
                nonlocal found_window
                try:
                    window_title = win32gui.GetWindowText(hwnd).strip()
                    if win32gui.IsWindowVisible(hwnd) and window_title == title:
                        window_info = self._get_window_info(hwnd)
                        if window_info:
                            found_window = window_info
                            return False
                except Exception:
                    # 忽略单个窗口的错误，继续枚举其他窗口
                    pass
                return True

            win32gui.EnumWindows(enum_windows_callback, None)
            return found_window

        except Exception as e:
            raise WindowDetectionException(f"查找窗口时发生错误: {e}") from e

    def get_window_rect(self, hwnd: int) -> Tuple[int, int, int, int]:
        """
        获取窗口矩形区域

        Args:
            hwnd: 窗口句柄

        Returns:
            (left, top, right, bottom) 窗口边界坐标

        Raises:
            WindowDetectionException: 获取窗口信息失败
        """
        try:
            return win32gui.GetWindowRect(hwnd)
        except Exception as e:
            raise WindowDetectionException(f"获取窗口矩形失败: {e}") from e

    def get_client_rect(self, hwnd: int) -> Tuple[int, int, int, int]:
        """
        获取窗口客户区矩形（游戏内容区域，不包含标题栏和边框）

        Args:
            hwnd: 窗口句柄

        Returns:
            (left, top, right, bottom) 客户区边界坐标（屏幕坐标系）

        Raises:
            WindowDetectionException: 获取客户区信息失败
        """
        try:
            # 获取客户区矩形（相对于窗口）
            client_rect = win32gui.GetClientRect(hwnd)

            # 将客户区左上角坐标转换为屏幕坐标
            client_left_top = win32gui.ClientToScreen(hwnd, (client_rect[0], client_rect[1]))
            client_right_bottom = win32gui.ClientToScreen(hwnd, (client_rect[2], client_rect[3]))

            return client_left_top[0], client_left_top[1], client_right_bottom[0], client_right_bottom[1]
        except Exception as e:
            raise WindowDetectionException(f"获取客户区矩形失败: {e}") from e

    def is_window_visible(self, hwnd: int) -> bool:
        """
        检查窗口是否可见

        Args:
            hwnd: 窗口句柄

        Returns:
            窗口是否可见
        """
        try:
            return win32gui.IsWindowVisible(hwnd)
        except Exception:
            return False

    def is_window_foreground(self, hwnd: int) -> bool:
        """
        检查窗口是否在前台

        Args:
            hwnd: 窗口句柄

        Returns:
            窗口是否在前台
        """
        try:
            return win32gui.GetForegroundWindow() == hwnd
        except Exception:
            return False

    def bring_window_to_front(self, hwnd: int) -> bool:
        """
        将窗口置于前台

        Args:
            hwnd: 窗口句柄

        Returns:
            操作是否成功
        """
        try:
            # 如果窗口最小化，先恢复
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

            # 将窗口置于前台
            win32gui.SetForegroundWindow(hwnd)

            # 激活窗口
            win32gui.BringWindowToTop(hwnd)

            return True
        except Exception:
            return False

    def is_window_minimized(self, hwnd: int) -> bool:
        """
        检查窗口是否最小化

        Args:
            hwnd: 窗口句柄

        Returns:
            窗口是否最小化
        """
        try:
            return win32gui.IsIconic(hwnd)
        except Exception:
            return False

    def get_window_state(self, window_info: WindowInfo) -> WindowState:
        """
        获取窗口当前状态

        Args:
            window_info: 窗口信息

        Returns:
            窗口状态枚举值
        """
        if not window_info:
            return WindowState.NOT_FOUND

        try:
            # 检查窗口是否仍然存在且可见
            if not self.is_window_visible(window_info.hwnd):
                return WindowState.NOT_FOUND

            # 检查是否最小化
            if self.is_window_minimized(window_info.hwnd):
                return WindowState.MINIMIZED

            # 检查是否在前台（简单的遮挡检测）
            if not self.is_window_foreground(window_info.hwnd):
                return WindowState.OCCLUDED

            return WindowState.DETECTED

        except Exception:
            return WindowState.NOT_FOUND

    def _get_window_info(self, hwnd: int) -> Optional[WindowInfo]:
        """
        获取窗口详细信息（使用客户区域，不包含标题栏和边框）

        Args:
            hwnd: 窗口句柄

        Returns:
            WindowInfo对象，获取失败返回None
        """
        try:
            # 获取窗口标题
            title = win32gui.GetWindowText(hwnd)

            # 获取客户区矩形（游戏内容区域）
            left, top, right, bottom = self.get_client_rect(hwnd)

            # 计算客户区尺寸
            width = right - left
            height = bottom - top

            # 获取窗口状态
            is_visible = self.is_window_visible(hwnd)
            is_foreground = self.is_window_foreground(hwnd)

            return WindowInfo(
                hwnd=hwnd,
                title=title,
                x=left,
                y=top,
                width=width,
                height=height,
                is_visible=is_visible,
                is_foreground=is_foreground,
            )

        except Exception:
            return None

    def refresh_window_info(self, hwnd: int) -> Optional[WindowInfo]:
        """
        刷新指定窗口的信息

        Args:
            hwnd: 窗口句柄

        Returns:
            更新后的WindowInfo对象，失败返回None
        """
        return self._get_window_info(hwnd)

    def find_all_windows_by_title(self, title: str) -> List[WindowInfo]:
        """
        查找所有匹配标题的窗口

        Args:
            title: 窗口标题（支持部分匹配）

        Returns:
            匹配的WindowInfo对象列表
        """
        found_windows = []

        def enum_windows_callback(hwnd, lparam):
            try:
                window_title = win32gui.GetWindowText(hwnd)
                if title in window_title and win32gui.IsWindowVisible(hwnd):
                    window_info = self._get_window_info(hwnd)
                    if window_info:
                        found_windows.append(window_info)
            except Exception:
                # 忽略单个窗口的错误，继续枚举其他窗口
                pass
            return True  # 继续枚举

        try:
            win32gui.EnumWindows(enum_windows_callback, None)
        except Exception as e:
            raise WindowDetectionException(f"枚举窗口时发生错误: {e}") from e

        return found_windows

    def is_window_windowed(self, hwnd: int) -> bool:
        """
        检测窗口是否为真正的窗口模式，通过比较窗口大小和屏幕大小

        Args:
            hwnd: 窗口句柄

        Returns:
            True表示窗口模式，False表示全屏模式
        """
        try:
            # 获取窗口矩形
            window_rect = win32gui.GetWindowRect(hwnd)
            window_width = window_rect[2] - window_rect[0]
            window_height = window_rect[3] - window_rect[1]
            print(window_width, window_height)
            # 获取屏幕尺寸
            screen_width, screen_height = pyautogui.size()
            print(screen_width, screen_height)
            # 如果窗口大小小于屏幕大小，则认为是窗口模式
            is_windowed = (window_width < screen_width) or (window_height < screen_height)

            return is_windowed

        except Exception:
            # 如果检测失败，默认认为是窗口模式
            return True
