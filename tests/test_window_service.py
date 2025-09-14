# -*- coding: utf-8 -*-
"""
窗口服务单元测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import time

from src.core.exceptions import (
    WindowDetectionException,
    WindowNotFoundException,
    WindowSizeException
)
from src.core.window_models import WindowInfo, WindowState
from src.services.window_service import WindowService


class TestWindowService:
    """WindowService类的单元测试"""

    def setup_method(self):
        """测试前的设置"""
        self.window_service = WindowService("测试窗口")
        self.mock_window_info = WindowInfo(
            hwnd=12345,
            title="测试窗口",
            x=100,
            y=200,
            width=1920,
            height=1080,
            is_visible=True,
            is_foreground=True
        )

    def test_init_default_values(self):
        """测试初始化默认值"""
        service = WindowService()
        assert service.target_window_title == "三角洲行动"
        assert service.detection_timeout == 15
        assert service.retry_count == 3
        assert service.retry_interval == 5
        assert service.supported_resolutions == [(1920, 1080), (2560, 1440)]
        assert service.current_window is None

    def test_init_custom_title(self):
        """测试自定义窗口标题初始化"""
        service = WindowService("自定义窗口")
        assert service.target_window_title == "自定义窗口"

    def test_detect_game_window_success(self):
        """测试成功检测游戏窗口"""
        # 设置mock
        mock_detector = Mock()
        mock_detector.find_window_by_title.return_value = self.mock_window_info
        mock_detector.get_window_state.return_value = WindowState.DETECTED
        
        # 替换window_detector实例
        self.window_service.window_detector = mock_detector

        # 执行测试
        result = self.window_service.detect_game_window()

        # 验证结果
        assert result is True
        assert self.window_service.current_window == self.mock_window_info
        mock_detector.find_window_by_title.assert_called_once_with("测试窗口")

    def test_detect_game_window_not_found(self):
        """测试窗口未找到"""
        # 设置mock
        mock_detector = Mock()
        mock_detector.find_window_by_title.return_value = None
        
        # 替换window_detector实例
        self.window_service.window_detector = mock_detector

        # 执行测试并验证异常
        with pytest.raises(WindowNotFoundException) as exc_info:
            self.window_service.detect_game_window()
        
        assert "未找到游戏窗口" in str(exc_info.value)
        assert self.window_service.current_window is None

    def test_detect_game_window_invalid_size(self):
        """测试窗口尺寸不支持"""
        # 创建不支持尺寸的窗口信息
        invalid_window = WindowInfo(
            hwnd=12345,
            title="测试窗口",
            x=100,
            y=200,
            width=800,  # 不支持的尺寸
            height=600,
            is_visible=True,
            is_foreground=True
        )

        # 设置mock
        mock_detector = Mock()
        mock_detector.find_window_by_title.return_value = invalid_window
        
        # 替换window_detector实例
        self.window_service.window_detector = mock_detector

        # 执行测试并验证异常
        with pytest.raises(WindowSizeException) as exc_info:
            self.window_service.detect_game_window()
        
        assert "窗口尺寸" in str(exc_info.value)
        assert "不受支持" in str(exc_info.value)

    def test_detect_game_window_minimized_recovery(self):
        """测试最小化窗口的恢复"""
        # 设置mock
        mock_detector = Mock()
        mock_detector.find_window_by_title.return_value = self.mock_window_info
        mock_detector.get_window_state.return_value = WindowState.MINIMIZED
        mock_detector.bring_window_to_front.return_value = True
        mock_detector.refresh_window_info.return_value = self.mock_window_info
        
        # 替换window_detector实例
        self.window_service.window_detector = mock_detector

        # 执行测试
        result = self.window_service.detect_game_window()

        # 验证结果
        assert result is True
        mock_detector.bring_window_to_front.assert_called_once_with(self.mock_window_info.hwnd)
        mock_detector.refresh_window_info.assert_called_once_with(self.mock_window_info.hwnd)

    @patch('src.services.window_service.time.sleep')
    def test_detect_game_window_retry_mechanism(self, mock_sleep):
        """测试重试机制"""
        # 设置mock - 前两次返回None，第三次返回窗口信息
        mock_detector = Mock()
        mock_detector.find_window_by_title.side_effect = [None, None, self.mock_window_info]
        mock_detector.get_window_state.return_value = WindowState.DETECTED
        
        # 替换window_detector实例
        self.window_service.window_detector = mock_detector

        # 设置较短的超时时间以加快测试
        self.window_service.detection_timeout = 1
        self.window_service.retry_interval = 0.1

        # 执行测试
        result = self.window_service.detect_game_window()

        # 验证结果
        assert result is True
        assert mock_detector.find_window_by_title.call_count == 3
        assert mock_sleep.call_count == 2

    def test_get_window_offset_success(self):
        """测试成功获取窗口偏移量"""
        self.window_service.current_window = self.mock_window_info
        
        offset = self.window_service.get_window_offset()
        
        assert offset == (100, 200)

    def test_get_window_offset_no_window(self):
        """测试未检测窗口时获取偏移量"""
        with pytest.raises(WindowDetectionException) as exc_info:
            self.window_service.get_window_offset()
        
        assert "窗口未检测" in str(exc_info.value)

    def test_get_window_size_success(self):
        """测试成功获取窗口尺寸"""
        self.window_service.current_window = self.mock_window_info
        
        size = self.window_service.get_window_size()
        
        assert size == (1920, 1080)

    def test_get_window_size_no_window(self):
        """测试未检测窗口时获取尺寸"""
        with pytest.raises(WindowDetectionException) as exc_info:
            self.window_service.get_window_size()
        
        assert "窗口未检测" in str(exc_info.value)

    def test_is_window_available_true(self):
        """测试窗口可用检查 - 可用"""
        mock_detector = Mock()
        mock_detector.get_window_state.return_value = WindowState.DETECTED
        
        # 替换window_detector实例
        self.window_service.window_detector = mock_detector
        self.window_service.current_window = self.mock_window_info
        
        result = self.window_service.is_window_available()
        
        assert result is True

    def test_is_window_available_false(self):
        """测试窗口可用检查 - 不可用"""
        mock_detector = Mock()
        mock_detector.get_window_state.return_value = WindowState.MINIMIZED
        
        # 替换window_detector实例
        self.window_service.window_detector = mock_detector
        self.window_service.current_window = self.mock_window_info
        
        result = self.window_service.is_window_available()
        
        assert result is False

    def test_is_window_available_no_window(self):
        """测试窗口可用检查 - 无窗口"""
        result = self.window_service.is_window_available()
        
        assert result is False

    def test_refresh_window_info_success(self):
        """测试成功刷新窗口信息"""
        mock_detector = Mock()
        
        updated_window = WindowInfo(
            hwnd=12345,
            title="测试窗口",
            x=150,  # 位置改变
            y=250,
            width=1920,
            height=1080,
            is_visible=True,
            is_foreground=True
        )
        mock_detector.refresh_window_info.return_value = updated_window
        
        # 替换window_detector实例
        self.window_service.window_detector = mock_detector
        self.window_service.current_window = self.mock_window_info
        
        result = self.window_service.refresh_window_info()
        
        assert result is True
        assert self.window_service.current_window == updated_window

    def test_refresh_window_info_window_gone(self):
        """测试刷新窗口信息 - 窗口消失"""
        mock_detector = Mock()
        mock_detector.refresh_window_info.return_value = None
        
        # 替换window_detector实例
        self.window_service.window_detector = mock_detector
        self.window_service.current_window = self.mock_window_info
        
        result = self.window_service.refresh_window_info()
        
        assert result is False
        assert self.window_service.current_window is None

    def test_refresh_window_info_no_window(self):
        """测试刷新窗口信息 - 未检测窗口"""
        with pytest.raises(WindowDetectionException) as exc_info:
            self.window_service.refresh_window_info()
        
        assert "窗口未检测" in str(exc_info.value)

    def test_refresh_window_info_size_changed(self):
        """测试刷新窗口信息 - 尺寸改变为不支持"""
        mock_detector = Mock()
        
        # 尺寸改变为不支持的分辨率
        updated_window = WindowInfo(
            hwnd=12345,
            title="测试窗口",
            x=100,
            y=200,
            width=800,  # 不支持的尺寸
            height=600,
            is_visible=True,
            is_foreground=True
        )
        mock_detector.refresh_window_info.return_value = updated_window
        
        # 替换window_detector实例
        self.window_service.window_detector = mock_detector
        self.window_service.current_window = self.mock_window_info
        
        with pytest.raises(WindowSizeException) as exc_info:
            self.window_service.refresh_window_info()
        
        assert "窗口尺寸已改变" in str(exc_info.value)

    def test_validate_window_size_valid(self):
        """测试验证窗口尺寸 - 有效"""
        self.window_service.current_window = self.mock_window_info
        
        result = self.window_service.validate_window_size()
        
        assert result is True

    def test_validate_window_size_invalid(self):
        """测试验证窗口尺寸 - 无效"""
        invalid_window = WindowInfo(
            hwnd=12345,
            title="测试窗口",
            x=100,
            y=200,
            width=800,  # 不支持的尺寸
            height=600,
            is_visible=True,
            is_foreground=True
        )
        self.window_service.current_window = invalid_window
        
        result = self.window_service.validate_window_size()
        
        assert result is False

    def test_validate_window_size_no_window(self):
        """测试验证窗口尺寸 - 未检测窗口"""
        with pytest.raises(WindowDetectionException) as exc_info:
            self.window_service.validate_window_size()
        
        assert "窗口未检测" in str(exc_info.value)

    def test_get_window_state_success(self):
        """测试获取窗口状态"""
        mock_detector = Mock()
        mock_detector.get_window_state.return_value = WindowState.DETECTED
        
        # 替换window_detector实例
        self.window_service.window_detector = mock_detector
        self.window_service.current_window = self.mock_window_info
        
        state = self.window_service.get_window_state()
        
        assert state == WindowState.DETECTED

    def test_get_window_state_no_window(self):
        """测试获取窗口状态 - 未检测窗口"""
        with pytest.raises(WindowDetectionException) as exc_info:
            self.window_service.get_window_state()
        
        assert "窗口未检测" in str(exc_info.value)

    def test_bring_window_to_front_success(self):
        """测试将窗口置于前台 - 成功"""
        mock_detector = Mock()
        mock_detector.bring_window_to_front.return_value = True
        mock_detector.refresh_window_info.return_value = self.mock_window_info
        
        # 替换window_detector实例
        self.window_service.window_detector = mock_detector
        self.window_service.current_window = self.mock_window_info
        
        result = self.window_service.bring_window_to_front()
        
        assert result is True
        mock_detector.bring_window_to_front.assert_called_once_with(self.mock_window_info.hwnd)

    def test_bring_window_to_front_failure(self):
        """测试将窗口置于前台 - 失败"""
        mock_detector = Mock()
        mock_detector.bring_window_to_front.return_value = False
        
        # 替换window_detector实例
        self.window_service.window_detector = mock_detector
        self.window_service.current_window = self.mock_window_info
        
        result = self.window_service.bring_window_to_front()
        
        assert result is False

    def test_bring_window_to_front_no_window(self):
        """测试将窗口置于前台 - 未检测窗口"""
        with pytest.raises(WindowDetectionException) as exc_info:
            self.window_service.bring_window_to_front()
        
        assert "窗口未检测" in str(exc_info.value)

    def test_get_window_info(self):
        """测试获取窗口信息"""
        self.window_service.current_window = self.mock_window_info
        
        info = self.window_service.get_window_info()
        
        assert info == self.mock_window_info

    def test_get_window_info_no_window(self):
        """测试获取窗口信息 - 无窗口"""
        info = self.window_service.get_window_info()
        
        assert info is None

    def test_set_supported_resolutions_valid(self):
        """测试设置支持的分辨率 - 有效"""
        new_resolutions = [(1920, 1080), (2560, 1440), (3840, 2160)]
        
        self.window_service.set_supported_resolutions(new_resolutions)
        
        assert self.window_service.supported_resolutions == new_resolutions

    def test_set_supported_resolutions_empty(self):
        """测试设置支持的分辨率 - 空列表"""
        with pytest.raises(ValueError) as exc_info:
            self.window_service.set_supported_resolutions([])
        
        assert "支持的分辨率列表不能为空" in str(exc_info.value)

    def test_set_supported_resolutions_invalid(self):
        """测试设置支持的分辨率 - 无效分辨率"""
        with pytest.raises(ValueError) as exc_info:
            self.window_service.set_supported_resolutions([(1920, 1080), (0, 600)])
        
        assert "无效的分辨率" in str(exc_info.value)

    def test_set_detection_config_valid(self):
        """测试设置检测配置 - 有效参数"""
        self.window_service.set_detection_config(timeout=30, retry_count=5, retry_interval=10)
        
        assert self.window_service.detection_timeout == 30
        assert self.window_service.retry_count == 5
        assert self.window_service.retry_interval == 10

    def test_set_detection_config_partial(self):
        """测试设置检测配置 - 部分参数"""
        original_timeout = self.window_service.detection_timeout
        original_interval = self.window_service.retry_interval
        
        self.window_service.set_detection_config(retry_count=10)
        
        assert self.window_service.detection_timeout == original_timeout  # 未改变
        assert self.window_service.retry_count == 10  # 已改变
        assert self.window_service.retry_interval == original_interval  # 未改变

    def test_set_detection_config_invalid_timeout(self):
        """测试设置检测配置 - 无效超时时间"""
        with pytest.raises(ValueError) as exc_info:
            self.window_service.set_detection_config(timeout=0)
        
        assert "检测超时时间必须大于0" in str(exc_info.value)

    def test_set_detection_config_invalid_retry_count(self):
        """测试设置检测配置 - 无效重试次数"""
        with pytest.raises(ValueError) as exc_info:
            self.window_service.set_detection_config(retry_count=-1)
        
        assert "重试次数不能为负数" in str(exc_info.value)

    def test_set_detection_config_invalid_retry_interval(self):
        """测试设置检测配置 - 无效重试间隔"""
        with pytest.raises(ValueError) as exc_info:
            self.window_service.set_detection_config(retry_interval=0)
        
        assert "重试间隔必须大于0" in str(exc_info.value)

    def test_reset(self):
        """测试重置窗口服务状态"""
        self.window_service.current_window = self.mock_window_info
        
        self.window_service.reset()
        
        assert self.window_service.current_window is None

    def test_validate_window_size_private_method(self):
        """测试私有方法 _validate_window_size"""
        # 测试支持的尺寸
        result = self.window_service._validate_window_size(self.mock_window_info)
        assert result is True
        
        # 测试不支持的尺寸
        invalid_window = WindowInfo(
            hwnd=12345,
            title="测试窗口",
            x=100,
            y=200,
            width=800,
            height=600,
            is_visible=True,
            is_foreground=True
        )
        result = self.window_service._validate_window_size(invalid_window)
        assert result is False