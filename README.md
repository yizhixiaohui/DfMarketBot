# DFMarketBot

DFMarketBot 是一个专为《三角洲行动》(Delta Force) 设计的抢子弹脚本。基于图像识别技术，通过模拟人工操作实现游戏内交易行的自动化购买功能。

![GitHub stars](https://img.shields.io/github/stars/doveeeee/DfMarketBot?style=social)
![GitHub forks](https://img.shields.io/github/forks/doveeeee/DfMarketBot?style=social)
![GitHub issues](https://img.shields.io/github/issues/doveeeee/DfMarketBot)
![GitHub license](https://img.shields.io/github/license/doveeeee/DfMarketBot)
![Python version](https://img.shields.io/badge/python-3.9+-blue.svg)

> **免责声明**: 本项目仅供学习和研究目的使用。使用本工具可能违反游戏服务条款，请用户自行承担风险。作者不对因使用本工具而导致的任何后果负责。

## 特别说明

### 寻求协作者，而非使用者

> Note: 开发者专用，不提供新手支持
> 
> 这是一个倒子弹脚本。作者因为时间有限，无法独自完成所有功能和维护。
> 
> **开源目的很明确**： 寻找同样懂行的同学一起开发和维护它。如果你也玩这个游戏并且会写代码，欢迎一起来让它变得更强大。
> 
> **文档只包含技术实现和配置说明。** 如果你需要基础的使用指导，这个项目可能不适合你。
> 
> 我需要：
>  - 也玩三角洲行动，知道如何倒子弹。
>  - 会 Python，能看懂代码，能自己 Debug，最好会图像处理相关技术。
>  - 想到什么好点子，愿意直接动手实现（提 PR），而不是光提意见。
> 
> 这里没有：
>  - 手把手教学：怎么搭环境、怎么装 Python 这类问题请自行解决。
>  - 保姆级教程：文档默认你有基础的开发和学习能力。
> 
> 交流群: 399343189

## ✨ 核心特性

- **多模式支持**：支持屯仓和滚仓两种交易策略
- **智能价格识别**：自动识别物品价格并做出购买决策
- **滚仓模式自动售卖**：购买成功后自动售卖子弹
- **自动切换大战场**：切换大战场以防卡顿(目前仅支持滚仓模式)
- **余额检测**：使用哈夫币余额检测购买状态
- **分辨率适配**：自动适配不同屏幕分辨率(1920x1080目前支持不太好)

TODO List:

- [ ] ocr识别优化(高优，1440p存在误识别，1080p几乎无法使用)
- [ ] 双端模式支持
- [ ] 屯仓模式支持切大战场
- [ ] 支持按档位购买，而非固定价格
- [ ] UI支持延迟配置
- [ ] 智能识别售卖比例
- [ ] 长时间卖不出时支持重新上架

## 🚀 快速开始

### 系统要求

- **Python版本**: Python 3.7 或更高版本
- **显示器**: 支持 2560x1440 分辨率(1920x1080目前支持不太好)
- **游戏要求**:
    - 《三角洲行动》需要以无边框模式运行，画面比例为16: 9
    - 不能开启HDR

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/doveeeee/DfMarketBot.git
   cd DfMarketBot
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

| 配置项                           | 说明             | 示例值   | 备注                    |
|-------------------------------|----------------|-------|-----------------------|
| `trading_mode`                | 交易模式：0=屯仓，1=滚仓 | 0     | 核心配置项                 |
| `ideal_price`                 | 理想购买价格         | 550   | 屯仓模式使用                |
| `max_price`                   | 最高接受价格         | 748   | 屯仓模式使用                |
| `hoarding_loop_interval`      | 屯仓模式检查间隔（毫秒）   | 150   | 数值越小检查越频繁             |
| `rolling_loop_interval`       | 滚仓模式检查间隔（毫秒）   | 50    | 数值越小检查越频繁             |
| `item_type`                   | 是否可兑换          | 0     | 影响识别模板选择              |
| `rolling_option`              | 滚仓配置选项索引       | 2     | 对应rolling_options中的配置 |
| `use_balance_calculation`     | 是否使用余额计算       | true  | 智能计算购买数量              |
| `key_mode`                    | 钥匙卡模式          | false | 是否启用钥匙卡模式, 屯仓使用       |
| `auto_sell`                   | 自动卖出           | true  | 是否自动卖出物品              |
| `fast_sell`                   | 快速卖出           | true  | 是否启用快速卖出              |
| `min_sell_price`              | 最低卖出价格         | 0     | 低于此价格不卖出              |
| `second_detect`               | 二次检测           | false | 是否启用二次价格检测            |
| `switch_to_battlefield`       | 切换到战场页面        | true  | 定期切换页面避免卡顿            |
| `switch_to_battlefield_count` | 切换到战场页面的操作次数阈值 | 400   | 执行多少次操作后切换页面          |

### 滚仓模式配置项 (rolling_options)

每个滚仓选项包含以下配置：

| 配置项                   | 说明     | 示例值  | 备注                    |
|-----------------------|--------|------|-----------------------|
| `buy_price`           | 购买价格   | 520  | 目标购买价格                |
| `min_buy_price`       | 最低购买价格 | 300  | 低于此价格必买               |
| `buy_count`           | 购买数量   | 4980 | 单次购买的数量               |
| `fast_sell_threshold` | 快速卖出阈值 | 0    | 触发快速卖出(比最低柱子低一档)的价格阈值 |

## 🎮 使用说明

### 操作热键

- **F8**：开始交易
- **F9**：停止交易

### 交易模式说明

#### 🔄 滚仓模式 (Rolling Mode)

- **适用场景**: 补货期抢子弹
- **工作原理**: 在配装页面自动购买预设配装
- **智能决策**: 根据价格区间和市场波动智能选择购买时机

#### 📦 屯仓模式 (Hoarding Mode)

- **适用场景**: 屯低价子弹可用
- **工作原理**: 在交易页面持续监控目标物品价格
- **触发条件**: 当价格低于设定阈值时自动购买

## 📁 项目结构

```
DeltaForceMarketBot/
├── DFMarketBot.py          # 主程序入口
├── run_v2.py              # 备用启动脚本
├── config/                # 配置文件目录
│   ├── settings.yaml      # 主配置文件
│   ├── settings.json      # JSON格式配置
│   └── delay_config.yaml  # 延迟配置
├── src/                   # 核心源码 (分层架构)
│   ├── core/             # 核心抽象层
│   │   ├── event_bus.py  # 事件总线
│   │   ├── interfaces.py # 接口定义
│   │   └── exceptions.py # 异常定义
│   ├── services/         # 业务逻辑层
│   │   ├── trading_service.py # 交易服务
│   │   ├── trading_modes.py   # 交易模式
│   │   ├── strategy.py        # 交易策略
│   │   └── detector.py        # 检测服务
│   ├── infrastructure/   # 基础设施层
│   │   ├── screen_capture.py  # 屏幕捕获
│   │   ├── ocr_engine.py      # OCR引擎
│   │   └── action_executor.py # 动作执行
│   ├── config/          # 配置管理
│   │   ├── config_manager.py  # 配置管理器
│   │   ├── trading_config.py  # 交易配置
│   │   └── delay_config.py    # 延迟配置
│   ├── ui/              # 用户界面层
│   │   ├── adapter.py   # UI适配器
│   │   └── overlay.py   # 透明覆盖层
│   └── utils/           # 工具类
├── GUI/                 # PyQt5图形界面
│   ├── AppGUI.py       # 主界面
│   ├── AppGUI.ui       # UI设计文件
│   └── RollingConfigUI.py # 滚仓配置界面
├── templates/           # 图像识别模板
│   ├── 1920x1080/      # 1080p模板
│   ├── 2560x1440/      # 1440p模板
│   └── bad_cases/      # 异常情况模板
├── tests/              # 单元测试
└── requirements.txt    # Python依赖
```

## 🧪 测试与开发

### 运行测试

项目采用pytest测试框架，提供全面的单元测试覆盖：

```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_trading_config.py

# 运行特定测试函数
pytest tests/test_trading_config.py::test_trading_config_manager
```

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements.txt

# 安装pre-commit钩子
pre-commit install

# 设置开发环境
python -m venv .venv
.venv\Scripts\activate     # Windows
```

### 代码质量

项目采用现代Python开发最佳实践：

```bash
# 代码格式化 (Black)
black --line-length=120 src/

# 导入排序 (isort)
isort --profile=black --line-length=120 src/

# 代码质量检查 (Pylint)
python run_pylint.py

# 运行所有质量检查
pre-commit run --all-files
```

### UI开发

```bash
# 使用Qt Designer编辑UI
pyqt5-tools.exe designer

# 将.ui文件转换为Python代码
pyuic5 -o GUI/AppGUI.py GUI/AppGUI.ui
```

### 架构设计

项目采用分层架构模式：

- **表示层 (UI Layer)**: PyQt5界面和适配器
- **业务逻辑层 (Service Layer)**: 交易策略和业务规则
- **基础设施层 (Infrastructure Layer)**: OCR、屏幕捕获、动作执行
- **核心层 (Core Layer)**: 事件总线、接口定义、异常处理

## 📋 注意事项

1. **系统要求**：建议使用Windows 10或更高版本
2. **游戏设置**：确保游戏为无边框模式
3. **权限要求**：部分系统需要管理员权限运行
4. **安全提醒**：仅供学习研究使用，请遵守游戏规则

## 🤝 贡献指南

欢迎社区贡献！在提交代码前，请遵循以下流程：

### 提交流程

1. **Fork项目** 并创建功能分支
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **开发和测试**
    - 编写代码并添加相应测试(尽量)
    - 确保所有测试通过: `pytest`
    - 运行代码质量检查: `python run_pylint.py src/`

3. **提交代码**
   ```bash
   git commit -m "feat: add your feature description"
   ```

4. **推送并创建Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### 代码规范

- 遵循 [PEP 8](https://pep8.org/) 编码规范
- 使用 Black 进行代码格式化 (120字符行长度)
- 为新功能编写单元测试
- 添加适当的文档字符串
- 更新相关文档

### 提交信息规范

使用 [Conventional Commits](https://conventionalcommits.org/) 格式(虽然我也没遵守)：

- `feat:` 新功能
- `fix:` 错误修复
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

## 🔗 相关链接

- **项目主页**: [GitHub Repository](https://github.com/doveeeee/DfMarketBot)
- **问题反馈**: [Issues](https://github.com/doveeeee/DfMarketBot/issues)
- **功能请求**: [Feature Requests](https://github.com/doveeeee/DfMarketBot/issues/new?template=feature_request.md)

## 🙏 致谢

- 特别感谢[XiaoGu-G2020](https://github.com/XiaoGu-G2020)
  贡献的[DeltaForceMarketBot](https://github.com/XiaoGu-G2020/DeltaForceMarketBot)，本项目最初由他的代码仓开发而来，

## ⚠️ 免责声明

本项目仅供学习和研究目的使用。使用本工具进行游戏自动化操作可能违反游戏服务条款，请用户：

1. **自行承担风险**: 使用本工具可能导致游戏账号被封禁
2. **遵守法律法规**: 请确保使用行为符合当地法律法规
3. **理性使用**: 建议仅在测试环境或个人学习中使用
4. **责任声明**: **禁止任何形式的商用**，作者不对因使用本工具而导致的任何后果负责
