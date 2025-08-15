# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个用于腾讯三角洲行动游戏内交易行的自动化市场工具，通过图像识别和模拟鼠标键盘操作实现自动购买功能。

## 架构版本

### V1 版本 (传统架构)
- **主程序**: `DFMarketBot.py`
- **特点**: 单体架构，功能耦合
- **状态**: 保留兼容性，不再维护新功能

### V2 版本 (新架构)
- **主程序**: `DFMarketBotV2.py`
- **特点**: 分层架构，高内聚低耦合
- **状态**: 推荐使用，持续维护

## V2 新架构详解

### 1. 分层架构设计

```
src/
├── core/           # 核心抽象层
│   ├── interfaces.py    # 接口定义
│   └── exceptions.py    # 异常体系
├── config/         # 配置管理层
│   └── config_manager.py      # JSON配置管理
├── services/       # 业务逻辑层
│   ├── detector.py      # 价格检测服务
│   ├── strategy.py      # 交易策略
│   ├── trading_modes.py # 交易模式实现
│   └── trading_service.py # 交易服务整合
├── infrastructure/ # 基础设施层
│   ├── screen_capture.py   # 屏幕捕获
│   ├── ocr_engine.py      # OCR引擎
│   └── action_executor.py # 动作执行器
└── ui/             # UI适配层
    └── adapter.py        # PyQt5适配器
```

### 2. 核心特性

#### 可扩展性
- 通过接口实现松耦合
- 策略模式支持多种交易逻辑
- 工厂模式创建组件实例
- 钥匙卡模式独立配置

#### 可维护性
- 单一职责原则
- 依赖注入降低耦合
- 统一的异常处理
- 毫秒级循环间隔控制

#### 可测试性
- 接口隔离便于单元测试
- Mock实现支持离线测试
- 配置驱动的测试环境

### 3. 交易模式

#### 屯仓模式 (TradingMode.HOARDING)
- **场景**: 交易页面批量购买
- **策略**: 价格触发 + 数量控制
- **特点**: 支持钥匙卡特殊处理（独立配置）

#### 滚仓模式 (TradingMode.ROLLING)
- **场景**: 配装页面自动购买
- **策略**: 预设价格区间 + 选项选择
- **特点**: 4个预设配装选项

## 运行命令

### V1 版本 (兼容)
```bash
# 安装依赖
pip install -r requirements.txt

# 运行旧版本
python DFMarketBot.py
```

### V2 版本 (推荐)
```bash
# 运行新版本
python DFMarketBot.py

# 开发调试
python -m src.services.trading_service  # 测试交易服务
```

## 配置管理

### V2 配置结构 (config/settings.json)
```json
{
  "trading_mode": 0,
  "rolling_option": 0,
  "ideal_price": 1000,
  "max_price": 2000,
  "loop_interval": 50,
  "item_type": 0,
  "key_mode": false,
  "use_balance_calculation": false,
  "screen_width": 2560,
  "screen_height": 1440,
  "tesseract_path": "",
  "log_level": "INFO"
}
```

### 配置热更新
- 运行时修改配置立即生效
- 线程安全的配置同步
- JSON格式易于编辑

## 开发指南

### 1. 添加新功能

#### 新交易模式
1. 在 `core/interfaces.py` 定义接口
2. 在 `services/trading_modes.py` 实现模式
3. 在 `services/strategy.py` 添加策略
4. 更新UI适配器

#### 新检测器
1. 实现 `IPriceDetector` 接口
2. 注册到服务工厂
3. 更新坐标配置

### 2. 测试策略

#### 单元测试
```python
# 使用Mock对象测试
from src.infrastructure.action_executor import MockActionExecutor
from src.infrastructure.ocr_engine import MockOCREngine
```

#### 集成测试
```python
# 使用配置文件测试不同场景
python DFMarketBotV2.py --config test_config.json
```

### 3. 性能优化

#### 分辨率适配
- 自动缩放坐标系统
- 支持2560x1440基准
- 动态计算其他分辨率

#### 资源管理
- 线程安全的单例模式
- 及时释放系统资源
- 优雅的错误恢复

## 故障排除

### 常见问题

#### OCR识别失败
- 检查Tesseract安装
- 验证配置文件路径
- 确认游戏分辨率

#### 屏幕捕获问题
- 确保游戏窗口在前台
- 检查系统权限
- 验证坐标配置

#### 热键冲突
- 修改全局热键设置
- 检查游戏快捷键
- 使用配置文件自定义

## 文件结构 (V2)

```
DFMarketBot/
├── DFMarketBotV2.py          # V2主程序入口
├── config/
│   └── settings.json         # 配置文件
├── src/                      # V2源代码
│   ├── core/
│   ├── config/
│   ├── services/
│   ├── infrastructure/
│   └── ui/
├── DFMarketBot.py            # V1主程序 (兼容)
├── backend/                  # V1代码 (兼容)
├── GUI/                      # UI文件 (共享)
├── README_V2.md              # V2使用文档
└── requirements.txt          # 依赖列表
```

## 迁移说明

### 从V1到V2
1. **零配置迁移**: 自动读取现有配置
2. **UI兼容**: 使用相同界面文件
3. **功能兼容**: 所有功能保持不变
4. **数据兼容**: 配置文件格式兼容

### 并行运行
- V1和V2可以并存
- 共享UI配置文件
- 独立运行互不干扰

## 开发注意事项

1. **架构原则**: 优先使用V2架构开发新功能
2. **向后兼容**: 保持V1版本功能稳定
3. **测试覆盖**: 为新功能添加单元测试
4. **文档更新**: 同步更新相关文档
5. **性能监控**: 关注内存和CPU使用情况
6. **修改流程**: 对用户提出的问题和修改建议，先评估合理性，与用户讨论确认后再执行修改
