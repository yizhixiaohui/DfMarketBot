#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DFMarketBot V2 启动脚本
处理macOS权限问题
"""
import os
import platform
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """主函数"""
    print("=== DFMarketBot V2 启动 ===")

    # 检测操作系统
    current_platform = platform.system()
    print(f"当前平台: {current_platform}")

    if current_platform == "Darwin":
        print("⚠  macOS检测到，跳过键盘监听权限检查")
        print("   在Windows上运行时将正常使用键盘监听")

    try:
        from DFMarketBot import main as app_main

        app_main()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()