#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试滚仓配置UI功能
"""
import os
import sys

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_rolling_config_ui():
    """测试滚仓配置UI"""
    print("=== 测试滚仓配置UI ===")

    try:
        from PyQt5.QtWidgets import QApplication

        from GUI.RollingConfigUI import RollingConfigUI

        # 测试导入
        print("✓ 成功导入RollingConfigUI")

        # 测试配置管理器
        from src.config.config_manager import TradingConfigManager as ConfigManager

        config_manager = ConfigManager()
        config = config_manager.load_config()

        print(f"✓ 当前配置中的滚仓选项数量: {len(config.rolling_options)}")

        # 显示当前配置
        for i, option in enumerate(config.rolling_options):
            print(
                f"  选项 {i + 1}: 价格={option['buy_price']}, 最低={option['min_buy_price']}, 数量={option['buy_count']}"
            )

        # 测试UI启动（如果用户选择）
        if len(sys.argv) > 1 and sys.argv[1] == "--ui":
            print("\n启动UI界面进行测试...")
            app = QApplication(sys.argv)
            window = RollingConfigUI()
            window.show()
            app.exec_()
        else:
            print("\n使用 --ui 参数启动UI界面进行测试")

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        pytest.fail(f"✗ 测试失败: {e}")


def test_config_integration():
    """测试配置集成"""
    print("\n=== 测试配置集成 ===")

    try:
        from src.config.config_manager import TradingConfigManager

        # 测试配置加载
        config_manager = TradingConfigManager()
        config = config_manager.load_config()

        # 验证rolling_options是数组格式
        assert isinstance(config.rolling_options, list), "rolling_options应该是数组"
        print("✓ rolling_options是数组格式")

        # 验证每个选项的结构
        for i, option in enumerate(config.rolling_options):
            assert isinstance(option, dict), f"选项{i}应该是字典"
            assert "buy_price" in option, f"选项{i}缺少buy_price"
            assert "min_buy_price" in option, f"选项{i}缺少min_buy_price"
            assert "buy_count" in option, f"选项{i}缺少buy_count"
            assert all(isinstance(v, int) for v in option.values()), f"选项{i}的值应该是整数"

        print("✓ 所有选项结构正确")

        # 测试配置更新
        test_options = [
            {"buy_price": 1000, "min_buy_price": 500, "buy_count": 2000},
            {"buy_price": 800, "min_buy_price": 400, "buy_count": 3000},
        ]

        config_manager.update_config({"rolling_options": test_options})

        # 验证更新
        updated_config = config_manager.load_config()
        assert len(updated_config.rolling_options) == 2, "配置更新失败"
        assert updated_config.rolling_options[0]["buy_price"] == 1000, "配置值未更新"

        print("✓ 配置更新功能正常")

        # 恢复原始配置
        config_manager.update_config({"rolling_options": config.rolling_options})

    except Exception as e:
        print(f"✗ 配置集成测试失败: {e}")
        pytest.fail(f"✗ 测试失败: {e}")


if __name__ == "__main__":
    print("开始测试滚仓配置UI功能...")

    tests = [test_rolling_config_ui, test_config_integration]

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
        print("🎉 所有测试通过！滚仓配置UI功能正常")
    else:
        print("❌ 部分测试失败")
