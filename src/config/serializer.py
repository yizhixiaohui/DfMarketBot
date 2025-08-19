import json
from abc import ABC, abstractmethod
from typing import Any, Dict

from ruamel.yaml import YAML


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

    def __init__(self):
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(sequence=4, offset=2)

    def load(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8") as f:
            return self.yaml.load(f) or {}

    def save(self, file_path: str, data: Dict[str, Any]):
        old_data = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                old_data = self.yaml.load(f) or {}
        except FileNotFoundError:
            old_data = {}

        # 逐层更新，而不是覆盖掉整个 dict，这样能尽量保持注释位置
        if isinstance(old_data, dict):
            old_data.update(data)
            new_data = old_data
        else:
            new_data = data

        with open(file_path, "w", encoding="utf-8") as f:
            self.yaml.dump(new_data, f)


class JsonSerializer(ConfigSerializer):
    """JSON 序列化器"""

    def load(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, file_path: str, data: Dict[str, Any]):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
