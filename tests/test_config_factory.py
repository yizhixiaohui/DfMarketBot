#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试配置管理器工厂功能
"""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.config_factory import ConfigFactory
from src.core.interfaces import IConfigManager


def test_config_factory_creation():
    """测试配置工厂创建不同格式的管理器"""
    print("=== 测试配置工厂创建功能 ===")

    temp_dir = tempfile.mkdtemp()

    try:
        # 测试YAML格式
        yaml_manager = ConfigFactory.create_config_manager("yaml", os.path.join(temp_dir, "test.yaml"))
        assert isinstance(yaml_manager, IConfigManager), "YAML管理器应该实现IConfigManager接口"
        print("✓ YAML配置管理器创建成功")

        # 测试JSON格式
        json_manager = ConfigFactory.create_config_manager("json", os.path.join(temp_dir, "test.json"))
        assert isinstance(json_manager, IConfigManager), "JSON管理器应该实现IConfigManager接口"
        print("✓ JSON配置管理器创建成功")

    finally:
        shutil.rmtree(temp_dir)


def test_global_config_manager():
    """测试全局配置管理器"""
    print("\n=== 测试全局配置管理器 ===")

    # 获取默认管理器
    manager1 = ConfigFactory.get_config_manager()
    manager2 = ConfigFactory.get_config_manager()

    # 验证是同一个实例
    assert manager1 is manager2, "应该返回同一个实例"
    assert isinstance(manager1, IConfigManager), "应该实现IConfigManager接口"

    print("✓ 全局配置管理器单例模式正确")


def test_config_format_switching():
    """测试配置格式切换"""
    print("\n=== 测试配置格式切换 ===")

    # 切换到JSON格式
    ConfigFactory.set_config_format("json")
    json_manager = ConfigFactory.get_config_manager()

    # 切换到YAML格式
    ConfigFactory.set_config_format("yaml")
    yaml_manager = ConfigFactory.get_config_manager()

    # 验证是不同的实例
    assert json_manager is not yaml_manager, "切换格式后应该返回不同实例"

    print("✓ 配置格式切换功能正确")


def test_interface_compliance():
    """测试接口合规性"""
    print("\n=== 测试接口合规性 ===")

    manager = ConfigFactory.get_config_manager()

    # 验证所有必要的方法都存在
    assert hasattr(manager, "load_config"), "应该实现load_config方法"
    assert hasattr(manager, "save_config"), "应该实现save_config方法"
    assert hasattr(manager, "update_config"), "应该实现update_config方法"

    # 测试基本功能
    config = manager.load_config()
    assert config is not None, "应该能加载配置"

    print("✓ 接口合规性测试通过")


if __name__ == "__main__":
    print("开始测试配置管理器工厂功能...")

    tests = [
        test_config_factory_creation,
        test_global_config_manager,
        test_config_format_switching,
        test_interface_compliance,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ 测试失败: {e}")

    print("\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")

    if passed == total:
        print("🎉 所有配置工厂测试通过！")
    else:
        print("❌ 部分测试失败")
