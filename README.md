# AmethystFlame_BN

币安期货网格交易策略机器人

## 项目简介

AmethystFlame_BN 是一个专为币安期货市场设计的智能网格交易策略机器人。该项目采用WebSocket实时数据流和动态网格策略，能够自动执行买入、卖出和止盈操作。

## 主要特性

- 🚀 **实时交易**: 基于WebSocket的实时价格监控
- 📊 **智能网格**: 动态调整网格间距和交易数量
- 🔒 **风险控制**: 内置持仓阈值和止损机制
- 🔄 **自动重连**: 网络断线自动重连机制
- 📝 **详细日志**: 完整的交易记录和错误日志
- ⚡ **高性能**: 异步处理，低延迟执行

## 技术架构

- **编程语言**: Python 3.8+
- **交易接口**: CCXT库 + 币安API
- **实时数据**: WebSocket连接
- **并发处理**: asyncio异步编程
- **配置管理**: 环境变量 + python-dotenv

## 快速开始

### 1. 环境要求

- Python 3.8 或更高版本
- 币安期货账户和API密钥
- 稳定的网络连接

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境

创建 `.env` 文件：

```bash
API_KEY=your_binance_api_key_here
API_SECRET=your_binance_secret_key_here
```

### 4. 运行策略

```bash
python AmethystFlame_BN.py
```

## 配置说明

主要配置参数在 `AmethystFlame_BN.py` 文件中：

```python
COIN_NAME = "ASTER"          # 交易币种
CONTRACT_TYPE = "USDT"       # 合约类型
GRID_SPACING = 0.005         # 网格间距 (0.5%)
INITIAL_QUANTITY = 10        # 初始交易数量
LEVERAGE = 20                # 杠杆倍数
POSITION_THRESHOLD = 600     # 锁仓阈值
POSITION_LIMIT = 200         # 持仓数量阈值
```

## VPS部署

详细的VPS部署指南请参考 `VPS_DEPLOYMENT_GUIDE_NEW.md` 文件。

## 风险提示

⚠️ **重要提醒**:
- 本项目仅供学习和研究使用
- 数字货币交易存在高风险，可能导致资金损失
- 请在充分了解风险的前提下使用
- 建议先在测试环境中验证策略效果
- 使用前请设置合理的风险控制参数

## 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。

## 免责声明

本软件按"原样"提供，不提供任何明示或暗示的保证。作者不对使用本软件造成的任何损失承担责任。用户应自行承担使用风险。