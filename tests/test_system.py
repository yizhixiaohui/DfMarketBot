#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统完整性测试脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """测试所有模块导入"""
    print("=== 测试模块导入 ===")
    
    try:
        from DFMarketBot import main
        print("✓ DFMarketBot.py 导入成功")
    except Exception as e:
        print(f"✗ DFMarketBot.py 导入失败: {e}")
        return False
    
    try:
        from src.core.interfaces import ITradingService, ITradingMode, IPriceDetector
        print("✓ 核心接口导入成功")
    except Exception as e:
        print(f"✗ 核心接口导入失败: {e}")
        return False
    
    try:
        from src.services.trading_service import TradingService
        print("✓ 交易服务导入成功")
    except Exception as e:
        print(f"✗ 交易服务导入失败: {e}")
        return False
    
    try:
        from src.infrastructure.ocr_engine import TemplateOCREngine
        print("✓ OCR引擎导入成功")
    except Exception as e:
        print(f"✗ OCR引擎导入失败: {e}")
        return False
    
    try:
        from src.infrastructure.action_executor import ActionExecutorFactory
        print("✓ 动作执行器导入成功")
    except Exception as e:
        print(f"✗ 动作执行器导入失败: {e}")
        return False
    
    return True

def test_ocr_engine():
    """测试OCR引擎"""
    print("\n=== 测试OCR引擎 ===")
    
    try:
        from src.infrastructure.ocr_engine import TemplateOCREngine
        
        # 创建OCR引擎实例
        ocr = TemplateOCREngine()
        print("✓ OCR引擎创建成功")
        
        # 检查模板加载
        if hasattr(ocr, '_templates') and ocr._templates:
            print(f"✓ 模板加载成功，共{len(ocr._templates)}组模板")
        else:
            print("✗ 模板加载失败")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ OCR引擎测试失败: {e}")
        return False

def test_trading_service():
    """测试交易服务"""
    print("\n=== 测试交易服务 ===")
    
    try:
        from src.services.trading_service import TradingService
        
        # 创建交易服务实例
        service = TradingService()
        print("✓ 交易服务创建成功")
        
        # 测试初始化
        try:
            service.initialize()
            print("✓ 交易服务初始化成功")
        except Exception as e:
            print(f"⚠ 交易服务初始化警告: {e}（可能在非Windows环境）")
        
        return True
        
    except Exception as e:
        print(f"✗ 交易服务测试失败: {e}")
        return False

def test_configuration():
    """测试配置文件"""
    print("\n=== 测试配置文件 ===")
    
    try:
        from src.config.config_manager import YamlConfigManager
        
        # 创建配置管理器
        config_manager = YamlConfigManager()
        config = config_manager.load_config()
        
        print("✓ 配置文件加载成功")
        print(f"  - 交易模式: {getattr(config, 'trading_mode', '未设置')}")
        print(f"  - 理想价格: {getattr(config, 'ideal_price', '未设置')}")
        print(f"  - 最大价格: {getattr(config, 'max_price', '未设置')}")
        
        return True
        
    except Exception as e:
        print(f"✗ 配置文件测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始系统完整性测试...")
    
    tests = [
        test_imports,
        test_ocr_engine,
        test_configuration,
        test_trading_service,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！系统完整性验证成功")
        return True
    else:
        print("❌ 部分测试失败，请检查错误信息")
        return False

if __name__ == "__main__":
    main()