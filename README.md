# DFMarketBot

DFMarketBot 是一个基于图像识别技术的自动化交易工具，通过模拟人工操作实现游戏内交易行的自动化购买功能。

## 🎯 核心功能

- **智能价格识别**：自动识别物品价格并做出购买决策
- **多模式支持**：支持屯仓和滚仓两种交易策略
- **分辨率适配**：自动适配不同屏幕分辨率
- **实时配置**：支持运行时配置修改，无需重启程序
- **热键控制**：通过快捷键快速启停自动化流程

## 🚀 快速开始

### 环境要求

- Python 3.7 或更高版本
- Windows 操作系统（推荐）
- 游戏窗口需要在前台运行

### 安装步骤

1. **克隆项目**
   ```bash
   git clone [项目地址]
   cd DFMarketBot
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动程序**
   ```bash
   python DFMarketBot.py
   ```

## ⚙️ 配置指南

配置文件位于 `config/settings.yaml`，首次运行会自动创建默认配置。

### 基础配置项

| 配置项                      | 说明             | 示例值  |
|--------------------------|----------------|------|
| `trading_mode`           | 交易模式：0=屯仓，1=滚仓 | 0    |
| `ideal_price`            | 理想购买价格         | 1000 |
| `max_price`              | 最高接受价格         | 2000 |
| `hoarding_loop_interval` | 屯仓模式检查间隔（毫秒）   | 150  |
| `rolling_loop_interval`  | 滚仓模式检查间隔（毫秒）   | 50   |
| `screen_width`           | 屏幕宽度           | 2560 |
| `screen_height`          | 屏幕高度           | 1440 |

### 配置示例

```yaml
trading_mode: 0
ideal_price: 568
max_price: 628
hoarding_loop_interval: 500
rolling_loop_interval: 50
screen_width: 2560
screen_height: 1440
log_level: INFO
key_mode: false
use_balance_calculation: true
```

## 🎮 使用说明

### 操作热键

- **F8**：开始自动化交易
- **F9**：停止自动化交易

### 交易模式说明

#### 滚仓模式（模式0）
- 在配装页面自动购买预设配装
- 根据价格区间智能选择
- 适合快速周转和利润最大化

#### 屯仓模式（模式1）
- 在交易页面持续监控物品价格
- 当价格低于设定值时自动购买
- 适合大量囤积低价物品

## 🔧 故障排除

### 常见问题及解决方案

| 问题现象   | 可能原因          | 解决方案              |
|--------|---------------|-------------------|
| 程序无法启动 | Python环境未配置   | 确认Python 3.7+已安装  |
| 识别失败   | 分辨率不匹配、开启了HDR | 检查配置中的屏幕分辨率并关闭HDR |
| 无响应    | 游戏窗口未激活       | 确保游戏窗口在前台         |
| 权限错误   | 系统权限不足        | 以管理员身份运行程序        |

## 📁 项目结构

```
DFMarketBot/
├── DFMarketBot.py          # 主程序入口
├── config/
│   └── settings.yaml       # YAML配置文件
├── src/                    # 核心源码
│   ├── core/              # 核心功能模块
│   ├── services/          # 业务逻辑
│   ├── infrastructure/    # 基础设施
│   └── ui/                # 用户界面
├── GUI/                   # 图形界面
├── templates/             # 图像模板
├── tests/                 # 测试文件
└── requirements.txt       # 依赖列表
```

## 🧪 测试指南

### 运行测试

项目已配置pytest测试框架：

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_trading_config.py

# 运行特定测试函数
pytest tests/test_trading_config.py::test_trading_config_manager

# 显示详细输出
pytest -v
```

## 🛠️ 开发指南

### 代码规范

项目遵循Python最佳实践：
- 使用pylint进行代码质量检查
- 遵循PEP 8编码规范

### 代码检查

```bash
# 检查所有代码
python run_pylint.py

# 格式化代码
black --line-length=120 src/
isort --profile=black --line-length=120 src/
```

### 添加新测试

在 `tests/` 目录下创建新的测试文件，使用pytest框架：

```python
def test_new_feature():
    """测试新功能"""
    assert True  # 你的测试逻辑
```

## 📋 注意事项

1. **系统要求**：建议使用Windows 10或更高版本
2. **游戏设置**：确保游戏为窗口化或无边框模式
3. **权限要求**：部分系统需要管理员权限运行
4. **安全提醒**：仅供学习研究使用，请遵守游戏规则

## 🤝 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目。在贡献代码前，请确保：

1. 代码通过pylint检查
2. 为新功能添加测试用例
3. 更新相关文档
4. 确保所有测试通过

## 📄 许可证

本项目采用MIT许可证，详见 [LICENSE](LICENSE) 文件。