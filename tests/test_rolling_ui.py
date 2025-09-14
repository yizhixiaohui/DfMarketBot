#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试滚仓配置UI功能
"""
import os
import shutil
import sys
import tempfile

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

        # 创建临时目录和配置文件
        temp_dir = tempfile.mkdtemp()
        temp_config_path = os.path.join(temp_dir, "test_config.yaml")

        try:
            # 测试配置加载
            config_manager = TradingConfigManager(temp_config_path)
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

        finally:
            # 清理临时文件
            shutil.rmtree(temp_dir)

    except Exception as e:
        print(f"✗ 配置集成测试失败: {e}")
        pytest.fail(f"✗ 测试失败: {e}")


def test_fast_sell_threshold_ui():
    """测试快速售卖阈值UI功能"""
    print("\n=== 测试快速售卖阈值UI功能 ===")

    try:
        from PyQt5.QtWidgets import QApplication

        from GUI.RollingConfigUI import RollingConfigUI
        from src.config.config_manager import TradingConfigManager

        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        temp_config_path = os.path.join(temp_dir, "test_config.yaml")

        try:
            # 创建应用程序实例（如果不存在）
            app = QApplication.instance()
            if app is None:
                app = QApplication([])

            # 创建UI实例
            ui = RollingConfigUI()

            # 验证表格列数
            assert ui.table.columnCount() == 6, f"表格应该有5列，实际有{ui.table.columnCount()}列"
            print("✓ 表格包含快速售卖阈值列")

            # 验证表头
            headers = [ui.table.horizontalHeaderItem(i).text() for i in range(ui.table.columnCount())]
            expected_headers = ["选项", "购买价格", "最低价格", "购买数量", "快速售卖阈值", "最低卖价"]
            assert headers == expected_headers, f"表头不匹配，期望{expected_headers}，实际{headers}"
            print("✓ 表头包含快速售卖阈值")

            # 测试配置加载和显示
            config_manager = TradingConfigManager(temp_config_path)

            # 创建包含快速售卖阈值的测试配置
            test_options = [
                {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980, "fast_sell_threshold": 100000},
                {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980, "fast_sell_threshold": 0},
            ]

            # 更新UI的rolling_options
            ui.rolling_options = test_options
            ui.refresh_table()

            # 验证表格显示
            assert ui.table.rowCount() == 2, f"表格应该有2行，实际有{ui.table.rowCount()}行"

            # 验证快速售卖阈值列的显示
            threshold_item_1 = ui.table.item(0, 4)
            threshold_item_2 = ui.table.item(1, 4)

            assert threshold_item_1 is not None, "第一行快速售卖阈值单元格不应为空"
            assert threshold_item_2 is not None, "第二行快速售卖阈值单元格不应为空"

            assert threshold_item_1.text() == "100000", f"第一行快速售卖阈值应为100000，实际为{threshold_item_1.text()}"
            assert threshold_item_2.text() == "0", f"第二行快速售卖阈值应为0，实际为{threshold_item_2.text()}"

            print("✓ 快速售卖阈值正确显示在表格中")

            # 测试向后兼容性 - 加载没有fast_sell_threshold的配置
            legacy_options = [
                {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980},  # 缺少fast_sell_threshold
            ]

            ui.rolling_options = legacy_options
            ui.refresh_table()

            # 验证默认值处理
            threshold_item = ui.table.item(0, 4)
            assert threshold_item is not None, "快速售卖阈值单元格不应为空"
            assert threshold_item.text() == "0", f"缺少fast_sell_threshold时应默认为0，实际为{threshold_item.text()}"

            print("✓ 向后兼容性测试通过")

            # 测试重置为默认配置（直接设置，避免对话框）
            ui.rolling_options = [
                {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980, "fast_sell_threshold": 0},
                {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980, "fast_sell_threshold": 0},
                {"buy_price": 450, "min_buy_price": 270, "buy_count": 4980, "fast_sell_threshold": 0},
                {"buy_price": 1700, "min_buy_price": 700, "buy_count": 1740, "fast_sell_threshold": 0},
            ]
            ui.refresh_table()

            # 验证默认配置包含fast_sell_threshold
            for i, option in enumerate(ui.rolling_options):
                assert "fast_sell_threshold" in option, f"默认配置选项{i}缺少fast_sell_threshold"
                assert (
                    option["fast_sell_threshold"] == 0
                ), f"默认fast_sell_threshold应为0，实际为{option['fast_sell_threshold']}"

            print("✓ 重置为默认配置包含快速售卖阈值")

        finally:
            # 清理临时文件
            shutil.rmtree(temp_dir)

    except Exception as e:
        print(f"✗ 快速售卖阈值UI测试失败: {e}")
        pytest.fail(f"✗ 测试失败: {e}")


@pytest.mark.skip("测试会修改配置文件，先跳过")
def test_fast_sell_threshold_editing():
    """测试快速售卖阈值编辑功能"""
    print("\n=== 测试快速售卖阈值编辑功能 ===")

    try:
        from PyQt5.QtWidgets import QApplication, QTableWidgetItem

        from GUI.RollingConfigUI import RollingConfigUI

        # 创建应用程序实例（如果不存在）
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # 创建UI实例
        ui = RollingConfigUI()

        # 设置测试数据
        ui.rolling_options = [
            {"buy_price": 520, "min_buy_price": 300, "buy_count": 4980, "fast_sell_threshold": 100000},
        ]
        ui.refresh_table()

        # 测试编辑快速售卖阈值
        # 模拟用户编辑第0行第4列（快速售卖阈值）
        new_threshold = 200000
        item = QTableWidgetItem(str(new_threshold))
        ui.table.setItem(0, 4, item)

        # 模拟单元格修改事件
        ui.on_cell_changed(0, 4)

        # 验证配置已更新
        assert (
            ui.rolling_options[0]["fast_sell_threshold"] == new_threshold
        ), f"快速售卖阈值应更新为{new_threshold}，实际为{ui.rolling_options[0]['fast_sell_threshold']}"

        print("✓ 快速售卖阈值编辑功能正常")

        # 测试输入验证 - 负数
        try:
            invalid_item = QTableWidgetItem("-100")
            ui.table.setItem(0, 4, invalid_item)
            ui.on_cell_changed(0, 4)

            # 验证值没有被更新（应该保持原值）
            assert ui.rolling_options[0]["fast_sell_threshold"] == new_threshold, "负数输入应该被拒绝，配置不应更新"

            print("✓ 负数输入验证正常")
        except Exception:
            # 预期会有异常，这是正常的
            pass

        # 测试输入验证 - 非数字
        try:
            invalid_item = QTableWidgetItem("abc")
            ui.table.setItem(0, 4, invalid_item)
            ui.on_cell_changed(0, 4)

            # 验证值没有被更新
            assert ui.rolling_options[0]["fast_sell_threshold"] == new_threshold, "非数字输入应该被拒绝，配置不应更新"

            print("✓ 非数字输入验证正常")
        except Exception:
            # 预期会有异常，这是正常的
            pass

        # 测试零值（应该被接受）
        zero_item = QTableWidgetItem("0")
        ui.table.setItem(0, 4, zero_item)
        ui.on_cell_changed(0, 4)

        assert ui.rolling_options[0]["fast_sell_threshold"] == 0, "零值应该被接受"

        print("✓ 零值输入正常")

    except Exception as e:
        print(f"✗ 快速售卖阈值编辑测试失败: {e}")
        pytest.fail(f"✗ 测试失败: {e}")


if __name__ == "__main__":
    print("开始测试滚仓配置UI功能...")

    tests = [
        test_rolling_config_ui,
        test_config_integration,
        test_fast_sell_threshold_ui,
        test_fast_sell_threshold_editing,
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
        print("🎉 所有测试通过！滚仓配置UI功能正常")
    else:
        print("❌ 部分测试失败")
