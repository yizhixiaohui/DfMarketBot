# -*- coding: utf-8 -*-
"""
延迟配置数据类和管理器
"""
from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass
class DelayConfig:
    """延迟配置数据类"""

    delays: Dict[str, Dict[str, float]]

    def __post_init__(self):
        """验证配置参数"""
        if not isinstance(self.delays, dict):
            raise ValueError("延迟配置必须是字典类型")

        for mode, operations in self.delays.items():
            if not isinstance(mode, str):
                raise ValueError(f"交易模式名称必须是字符串: {mode}")
            if not isinstance(operations, dict):
                raise ValueError(f"操作配置必须是字典类型: {mode}")

            for operation, delay in operations.items():
                if not isinstance(operation, str):
                    raise ValueError(f"操作名称必须是字符串: {mode}.{operation}")
                if not isinstance(delay, (int, float)):
                    raise ValueError(f"延迟参数必须是数字: {mode}.{operation} = {delay}")
                if delay < 0:
                    raise ValueError(f"延迟参数不能为负数: {mode}.{operation} = {delay}")

    def get_delay(self, mode: str, operation: str) -> float:
        """获取指定模式和操作的延迟时间
        
        Args:
            mode: 交易模式（'hoarding_mode' 或 'rolling_mode'）
            operation: 操作名称
        
        Returns:
            延迟时间（秒），如果不存在则返回0.0
        """
        if not isinstance(mode, str) or not isinstance(operation, str):
            return 0.0
        return self.delays.get(mode, {}).get(operation, 0.0)

    def set_delay(self, mode: str, operation: str, delay: float) -> None:
        """设置指定模式和操作的延迟时间
        
        Args:
            mode: 交易模式
            operation: 操作名称
            delay: 延迟时间（秒，支持毫秒级精度）
        
        Raises:
            ValueError: 当延迟时间为负数时
        """
        if not isinstance(mode, str):
            raise ValueError(f"交易模式名称必须是字符串: {mode}")
        if not isinstance(operation, str):
            raise ValueError(f"操作名称必须是字符串: {operation}")
        if not isinstance(delay, (int, float)):
            raise ValueError(f"延迟参数必须是数字: {delay}")
        if delay < 0:
            raise ValueError(f"延迟时间不能为负数: {delay}")

        if mode not in self.delays:
            self.delays[mode] = {}
        self.delays[mode][operation] = float(delay)

    def get_mode_delays(self, mode: str) -> Dict[str, float]:
        """获取指定模式的所有延迟配置
        
        Args:
            mode: 交易模式名称
            
        Returns:
            该模式下所有操作的延迟配置字典副本
        """
        if not isinstance(mode, str):
            return {}
        return self.delays.get(mode, {}).copy()

    def update_mode_delays(self, mode: str, delays: Dict[str, float]) -> None:
        """更新指定模式的延迟配置
        
        Args:
            mode: 交易模式名称
            delays: 要更新的延迟配置字典
            
        Raises:
            ValueError: 当参数类型错误或延迟值无效时
        """
        if not isinstance(mode, str):
            raise ValueError(f"交易模式名称必须是字符串: {mode}")
        if not isinstance(delays, dict):
            raise ValueError(f"延迟配置必须是字典类型: {delays}")

        # 验证所有延迟值
        for operation, delay in delays.items():
            if not isinstance(operation, str):
                raise ValueError(f"操作名称必须是字符串: {operation}")
            if not isinstance(delay, (int, float)):
                raise ValueError(f"延迟参数必须是数字: {mode}.{operation} = {delay}")
            if delay < 0:
                raise ValueError(f"延迟时间不能为负数: {mode}.{operation} = {delay}")

        # 确保模式存在
        if mode not in self.delays:
            self.delays[mode] = {}

        # 更新延迟配置
        for operation, delay in delays.items():
            self.delays[mode][operation] = float(delay)

    def get_all_modes(self) -> list:
        """获取所有可用的交易模式列表"""
        return list(self.delays.keys())

    def get_mode_operations(self, mode: str) -> list:
        """获取指定模式下的所有操作列表"""
        if not isinstance(mode, str):
            return []
        return list(self.delays.get(mode, {}).keys())

    def has_mode(self, mode: str) -> bool:
        """检查是否存在指定的交易模式"""
        return isinstance(mode, str) and mode in self.delays

    def has_operation(self, mode: str, operation: str) -> bool:
        """检查是否存在指定的操作"""
        if not isinstance(mode, str) or not isinstance(operation, str):
            return False
        return mode in self.delays and operation in self.delays[mode]

    def remove_operation(self, mode: str, operation: str) -> bool:
        """移除指定的操作配置
        
        Args:
            mode: 交易模式名称
            operation: 操作名称
            
        Returns:
            是否成功移除（如果操作不存在则返回False）
        """
        if not self.has_operation(mode, operation):
            return False

        del self.delays[mode][operation]
        return True

    def clear_mode(self, mode: str) -> bool:
        """清空指定模式的所有延迟配置
        
        Args:
            mode: 交易模式名称
            
        Returns:
            是否成功清空（如果模式不存在则返回False）
        """
        if not self.has_mode(mode):
            return False

        self.delays[mode].clear()
        return True

    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DelayConfig':
        """从字典创建配置对象"""
        if not isinstance(data, dict):
            raise ValueError("数据必须是字典类型")

        if 'delays' not in data:
            raise ValueError("配置数据中缺少 'delays' 字段")

        return cls(delays=data['delays'])

    def __str__(self) -> str:
        """字符串表示"""
        lines = ["DelayConfig:"]
        for mode, operations in self.delays.items():
            lines.append(f"  {mode}:")
            for operation, delay in operations.items():
                lines.append(f"    {operation}: {delay}s")
        return "\n".join(lines)

    def __repr__(self) -> str:
        """调试表示"""
        return f"DelayConfig(delays={self.delays})"
