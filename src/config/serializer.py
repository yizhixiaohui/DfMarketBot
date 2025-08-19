import json
from abc import ABC, abstractmethod
from typing import Any, Dict

import yaml


class ConfigSerializer(ABC):
    """配置序列化器抽象基类"""

    @abstractmethod
    def load(self, file_path: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def save(self, file_path: str, data: Dict[str, Any]):
        pass


class YamlSerializer(ConfigSerializer):
    """YAML 序列化器"""

    def load(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def save(self, file_path: str, data: Dict[str, Any]):
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


class JsonSerializer(ConfigSerializer):
    """JSON 序列化器"""

    def load(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, file_path: str, data: Dict[str, Any]):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
