# 测试文件夹规范

## 目录结构

```
tests/
├── README.md              # 测试规范说明
├── test_*.py             # 单元测试文件
├── integration/          # 集成测试
├── fixtures/             # 测试数据
└── mocks/               # Mock对象
```

## 命名规范

1. **单元测试文件**: `test_<模块名>.py`
    - 例如: `test_config.py`, `test_strategy.py`

2. **集成测试文件**: `test_integration_<功能名>.py`
    - 例如: `test_integration_trading.py`

3. **测试数据文件**: `test_<类型>_data.json/yaml`
    - 例如: `test_config_data.yaml`

## 测试文件模板

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试描述
"""
import sys
import os
import tempfile
import shutil

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入被测试的模块
from src.module import ClassName


def test_function_name():
    """测试函数描述"""
    print("=== 测试函数描述 ===")
    
    # 使用临时目录避免污染项目
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 测试代码
        assert True, "测试失败描述"
        print("✓ 测试通过")
        return True
        
    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("开始测试...")
    
    tests = [
        test_function_name,
        # 添加更多测试函数
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ 测试失败: {e}")
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print("❌ 部分测试失败")
```

## 运行测试

### 运行所有测试

```bash
python -m pytest tests/
```

### 运行特定测试

```bash
python tests/test_config.py
python tests/test_yaml_config.py
```

### 运行集成测试

```bash
python tests/integration/test_integration_trading.py
```

## 测试数据管理

1. **临时文件**: 使用 `tempfile` 模块创建临时文件和目录
2. **测试数据**: 放在 `tests/fixtures/` 目录下
3. **Mock数据**: 放在 `tests/mocks/` 目录下

## 最佳实践

1. **独立性**: 每个测试应该独立运行，不依赖其他测试
2. **可重复**: 测试结果应该可重复，不受外部环境影响
3. **清理**: 测试完成后清理所有临时文件
4. **断言**: 使用明确的断言来验证预期结果
5. **文档**: 为每个测试函数添加清晰的文档字符串

## 当前测试文件

- `test_config.py`: JSON配置管理器测试
- `test_yaml_config.py`: YAML配置管理器测试
- `test_rolling_config.py`: 滚仓配置动态加载测试
- `test_rolling_ui.py`: 滚仓配置UI测试
- `test_system.py`: 系统集成测试
- `test_import.py`: 模块导入测试