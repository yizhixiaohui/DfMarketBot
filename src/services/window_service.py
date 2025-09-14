# -*- coding: utf-8 -*-
"""
窗口服务 - 管理窗口状态和业务逻辑
"""
import time
from typing import List, Optional, Tuple

try:
    from ..core.exceptions import WindowDetectionException, WindowNotFoundException, WindowSizeException
    from ..core.window_models import WindowInfo, WindowState
    from ..infrastructure.window_detector import WindowDetector
except ImportError:
    from src.core.exceptions import WindowDetectionException, WindowNotFoundException, WindowSizeException
    from src.core.window_models import WindowInfo, WindowState
    from src.infrastructure.window_detector import WindowDetector


class WindowService:
    """窗口服务类 - 管理窗口状态和提供窗口相关业务逻辑"""

    def __init__(self, target_window_title: str = "三角洲行动"):
        """
        初始化窗口服务

        Args:
            target_window_title: 目标窗口标题
        """
        self.target_window_title = target_window_title
        self.window_detector = WindowDetector()
        self.current_window: Optional[WindowInfo] = None

        # 配置参数
        self.detection_timeout = 15  # 检测超时时间（秒）
        self.retry_count = 3  # 重试次数
        self.retry_interval = 5  # 重试间隔（秒）

        # 支持的分辨率
        self.supported_resolutions = [(1920, 1080), (2560, 1440)]

    def detect_game_window(self) -> bool:
        """
        检测游戏窗口

        Returns:
            检测是否成功

        Raises:
            WindowNotFoundException: 窗口未找到
            WindowSizeException: 窗口尺寸不支持
            WindowDetectionException: 检测过程中发生其他错误
        """
        start_time = time.time()
        retry_attempts = 0

        while retry_attempts < self.retry_count:
            try:
                # 查找目标窗口
                window_info = self.window_detector.find_window_by_title(self.target_window_title)

                if window_info:
                    # 验证窗口尺寸
                    if not self._validate_window_size(window_info):
                        raise WindowSizeException(
                            f"窗口尺寸 {window_info.width}x{window_info.height} 不受支持。"
                            f"支持的分辨率: {self.supported_resolutions}"
                        )

                    # 检查窗口状态
                    window_state = self.window_detector.get_window_state(window_info)
                    if window_state == WindowState.MINIMIZED:
                        # 尝试恢复窗口
                        if self.window_detector.bring_window_to_front(window_info.hwnd):
                            # 重新获取窗口信息
                            window_info = self.window_detector.refresh_window_info(window_info.hwnd)

                    self.current_window = window_info
                    print(
                        f"成功检测到游戏窗口: {window_info.title} "
                        f"位置: ({window_info.x}, {window_info.y}) "
                        f"尺寸: {window_info.width}x{window_info.height}"
                    )
                    return True

                # 检查是否超时
                if time.time() - start_time > self.detection_timeout:
                    break

                # 等待重试
                retry_attempts += 1
                if retry_attempts < self.retry_count:
                    print(f"未找到游戏窗口，{self.retry_interval}秒后重试... ({retry_attempts}/{self.retry_count})")
                    time.sleep(self.retry_interval)

            except (WindowSizeException, WindowDetectionException):
                # 这些异常直接抛出，不重试
                raise
            except Exception as e:
                retry_attempts += 1
                if retry_attempts >= self.retry_count:
                    raise WindowDetectionException(f"窗口检测失败: {e}") from e
                print(f"检测出错，{self.retry_interval}秒后重试: {e}")
                time.sleep(self.retry_interval)

        # 所有重试都失败
        raise WindowNotFoundException(f"未找到游戏窗口 '{self.target_window_title}'。" "请确保游戏已启动并且窗口可见。")

    def get_window_offset(self) -> Tuple[int, int]:
        """
        获取窗口偏移量

        Returns:
            (x, y) 窗口左上角坐标

        Raises:
            WindowDetectionException: 窗口未检测或无效
        """
        if not self.current_window:
            raise WindowDetectionException("窗口未检测，请先调用 detect_game_window()")

        return self.current_window.x, self.current_window.y

    def get_window_size(self) -> Tuple[int, int]:
        """
        获取窗口尺寸

        Returns:
            (width, height) 窗口尺寸

        Raises:
            WindowDetectionException: 窗口未检测或无效
        """
        if not self.current_window:
            raise WindowDetectionException("窗口未检测，请先调用 detect_game_window()")

        return self.current_window.width, self.current_window.height

    def is_window_available(self) -> bool:
        """
        检查窗口是否可用

        Returns:
            窗口是否可用
        """
        if not self.current_window:
            return False

        try:
            # 检查窗口状态
            window_state = self.window_detector.get_window_state(self.current_window)
            return window_state == WindowState.DETECTED
        except Exception:
            return False

    def refresh_window_info(self) -> bool:
        """
        刷新窗口信息

        Returns:
            刷新是否成功

        Raises:
            WindowDetectionException: 窗口未检测
        """
        if not self.current_window:
            raise WindowDetectionException("窗口未检测，请先调用 detect_game_window()")

        try:
            # 刷新窗口信息
            updated_window = self.window_detector.refresh_window_info(self.current_window.hwnd)

            if not updated_window:
                # 窗口不再存在
                self.current_window = None
                return False

            # 验证窗口尺寸是否仍然支持
            if not self._validate_window_size(updated_window):
                raise WindowSizeException(
                    f"窗口尺寸已改变为不支持的 {updated_window.width}x{updated_window.height}。"
                    f"支持的分辨率: {self.supported_resolutions}"
                )

            self.current_window = updated_window
            return True

        except WindowSizeException:
            # 尺寸异常直接抛出
            raise
        except Exception as e:
            raise WindowDetectionException(f"刷新窗口信息失败: {e}") from e

    def validate_window_size(self) -> bool:
        """
        验证当前窗口尺寸

        Returns:
            尺寸是否有效

        Raises:
            WindowDetectionException: 窗口未检测
        """
        if not self.current_window:
            raise WindowDetectionException("窗口未检测，请先调用 detect_game_window()")

        return self._validate_window_size(self.current_window)

    def get_window_state(self) -> WindowState:
        """
        获取当前窗口状态

        Returns:
            窗口状态枚举值

        Raises:
            WindowDetectionException: 窗口未检测
        """
        if not self.current_window:
            raise WindowDetectionException("窗口未检测，请先调用 detect_game_window()")

        try:
            return self.window_detector.get_window_state(self.current_window)
        except Exception as e:
            raise WindowDetectionException(f"获取窗口状态失败: {e}") from e

    def bring_window_to_front(self) -> bool:
        """
        将窗口置于前台

        Returns:
            操作是否成功

        Raises:
            WindowDetectionException: 窗口未检测
        """
        if not self.current_window:
            raise WindowDetectionException("窗口未检测，请先调用 detect_game_window()")

        try:
            success = self.window_detector.bring_window_to_front(self.current_window.hwnd)
            if success:
                # 刷新窗口信息
                self.refresh_window_info()
            return success
        except Exception as e:
            raise WindowDetectionException(f"将窗口置于前台失败: {e}") from e

    def get_window_info(self) -> Optional[WindowInfo]:
        """
        获取当前窗口信息

        Returns:
            窗口信息对象，未检测时返回None
        """
        return self.current_window

    def set_supported_resolutions(self, resolutions: List[Tuple[int, int]]) -> None:
        """
        设置支持的分辨率列表

        Args:
            resolutions: 支持的分辨率列表 [(width, height), ...]
        """
        if not resolutions:
            raise ValueError("支持的分辨率列表不能为空")

        for width, height in resolutions:
            if width <= 0 or height <= 0:
                raise ValueError(f"无效的分辨率: {width}x{height}")

        self.supported_resolutions = resolutions

    def set_detection_config(self, timeout: int = None, retry_count: int = None, retry_interval: int = None) -> None:
        """
        设置检测配置参数

        Args:
            timeout: 检测超时时间（秒）
            retry_count: 重试次数
            retry_interval: 重试间隔（秒）
        """
        if timeout is not None:
            if timeout <= 0:
                raise ValueError("检测超时时间必须大于0")
            self.detection_timeout = timeout

        if retry_count is not None:
            if retry_count < 0:
                raise ValueError("重试次数不能为负数")
            self.retry_count = retry_count

        if retry_interval is not None:
            if retry_interval <= 0:
                raise ValueError("重试间隔必须大于0")
            self.retry_interval = retry_interval

    def _validate_window_size(self, window_info: WindowInfo) -> bool:
        """
        验证窗口尺寸是否支持

        Args:
            window_info: 窗口信息

        Returns:
            尺寸是否支持
        """
        window_size = (window_info.width, window_info.height)
        return window_size in self.supported_resolutions

    def is_game_windowed(self) -> bool:
        """
        检测游戏是否为真正的窗口模式（有边框）

        Returns:
            True表示游戏运行在有边框的窗口模式，False表示全屏或无边框

        Raises:
            WindowDetectionException: 窗口未检测或检测失败
        """
        if not self.current_window:
            raise WindowDetectionException("窗口未检测，请先调用 detect_game_window()")

        try:
            return self.window_detector.is_window_windowed(self.current_window.hwnd)
        except Exception as e:
            raise WindowDetectionException(f"检测窗口模式失败: {e}") from e

    def reset(self) -> None:
        """
        重置窗口服务状态
        """
        self.current_window = None


if __name__ == "__main__":
    ws = WindowService()
    ws.detect_game_window()
    res = ws.is_game_windowed()
    print(res)
