#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DFMarketBot V2 启动脚本
处理macOS权限问题
"""
import json
import sys
import os
import platform

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
        from DFMarketBotV2 import main as app_main
        app_main()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # main()
    import requests
    body = '{"model":"DeepSeek-R1","messages":[{"role":"user","content":"北京天气怎么样？"}],"tools":[{"type":"function","function":{"name":"get_current_weather","description":"获取当前天气信息","parameters":{"type":"object","properties":{"location":{"type":"string","description":"城市名称，例如：北京"},"unit":{"type":"string","enum":["celsius","fahrenheit"],"description":"温度单位，默认为摄氏度"}},"required":["location"]}}}],"temperature":0.6,"stream":true,"max_tokens":600}'
    res = json.loads(body)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-4d5fd5e8-9155-42a5-84db-38eb504df510",
    }
    resp = requests.post('http://api.haihub.cn/v1/chat/completions', headers=headers, data=body)
    print(resp.text)