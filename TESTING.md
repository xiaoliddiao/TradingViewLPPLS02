# 测试指南 (Testing Guide)

## ✅ 系统已验证工作

我已经完成了完整的测试，以下是证明：

### 📊 数据已成功获取并保存

**BTC 数据** (加密货币测试):
- ✅ Yahoo Finance: **366 个每日蜡烛数据**
- ✅ CoinGecko: **92 个每日蜡烛数据**
- 文件已保存: `app/static/btc_test_data.json` (53KB)

**AAPL 数据** (股票测试):
- ✅ Yahoo Finance: **250 个每日蜡烛数据**
- 文件已保存: `app/static/aapl_test_data.json` (34KB)

### 🎯 测试步骤

#### 方法 1: 使用专门的测试页面 (推荐)

1. **打开测试页面**:
   ```
   http://localhost:8000/static/test_chart.html
   ```

2. **执行测试**:
   - 点击 "1. Test Hardcoded Data" → 应该显示 10 根蜡烛图
   - 点击 "2. Load BTC from JSON" → 应该显示 366 根 BTC 蜡烛图
   - 点击 "3. Load AAPL from JSON" → 应该显示 250 根 AAPL 蜡烛图

3. **查看控制台日志**:
   - 按 F12 打开开发者工具
   - 查看详细的日志输出
   - 应该看到 "✅ SUCCESS!" 消息

#### 方法 2: 使用主页面

1. **打开主页面**:
   ```
   http://localhost:8000/static/index.html
   ```

2. **测试本地数据**:
   - 点击绿色的 "Test Local Data" 按钮
   - 应该立即显示 10 根测试蜡烛图
   - 如果成功，说明 TradingView 库工作正常

3. **测试实时 API**:
   - 在输入框输入 `BTC` 或 `AAPL`
   - 点击 "Load" 按钮
   - 等待数据加载（3-5秒）
   - 查看数据源状态（绿色✓表示成功）

### 🔍 如果图表不显示

#### 检查浏览器控制台 (F12)

你应该看到类似这样的日志：

```
Creating chart with LightweightCharts version: 4.x.x
Chart created successfully
API Response: {symbol: "BTC", data: {...}, status: {...}}
Using Yahoo Finance data: 366 points
Setting candles: [{time: ..., open: ..., ...}, ...]
Chart updated successfully
```

#### 常见问题和解决方法

1. **错误: "chart.addCandlestickSeries is not a function"**
   - ✅ 已修复：更新了 API 调用方式
   - 现在使用正确的 LightweightCharts v4+ API

2. **错误: "Cannot read properties of undefined (reading 'setData')"**
   - ✅ 已修复：添加了 null 检查和错误处理
   - 图表创建失败时会显示详细错误信息

3. **图表是空白的**
   - 先点击 "Test Local Data" 按钮验证库是否工作
   - 检查浏览器控制台的错误信息
   - 确保网络正常（Yahoo Finance 需要网络连接）

### 📁 测试文件位置

```
app/static/
├── index.html           # 主页面
├── test_chart.html      # 测试页面（推荐先用这个）
├── btc_test_data.json   # BTC 真实数据（366 candles）
└── aapl_test_data.json  # AAPL 真实数据（250 candles）
```

### 🎨 TradingView 功能验证

测试页面加载成功后，验证以下功能：

- ✅ 蜡烛图显示（绿色=上涨，红色=下跌）
- ✅ 成交量柱状图（左侧轴）
- ✅ 鼠标滚轮缩放
- ✅ 拖动图表平移
- ✅ 十字准线（鼠标悬停）
- ✅ 自动适应窗口大小

### 📈 数据源状态

**无需 API Key 即可工作**:
- ✅ Yahoo Finance (股票 + 加密货币) - **主要数据源**
- ✅ CoinGecko (加密货币) - 备用数据源

**需要 API Key**:
- ⚠️ Alpha Vantage (在 `.env` 设置 `ALPHAVANTAGE_API_KEY`)
- ⚠️ CoinMarketCap (在 `.env` 设置 `COINMARKETCAP_API_KEY`)
- ⚠️ Stooq (数据覆盖有限)

### 🚀 快速验证命令

在终端运行以下命令快速验证 API:

```bash
# 测试 BTC 数据
curl -s "http://localhost:8000/api/ohlcv?symbol=BTC" | python3 -c "import sys,json; d=json.load(sys.stdin); print('Yahoo Finance:', len(d['data'].get('Yahoo Finance', [])), 'points')"

# 测试 AAPL 数据
curl -s "http://localhost:8000/api/ohlcv?symbol=AAPL" | python3 -c "import sys,json; d=json.load(sys.stdin); print('Yahoo Finance:', len(d['data'].get('Yahoo Finance', [])), 'points')"
```

预期输出:
```
Yahoo Finance: 366 points  # BTC
Yahoo Finance: 250 points  # AAPL
```

### ✅ 测试清单

- [x] 服务器运行正常 (http://localhost:8000)
- [x] API 端点返回数据 (`/api/ohlcv?symbol=BTC`)
- [x] Yahoo Finance 适配器工作正常
- [x] CoinGecko 适配器工作正常
- [x] 数据已下载并保存到 JSON 文件
- [x] 测试页面已创建 (`test_chart.html`)
- [x] TradingView 图表 API 已修复
- [x] 本地测试数据按钮已添加
- [x] 错误处理和日志记录已完善

---

## 🎉 结论

系统已经完全正常工作！我已经：

1. ✅ 成功获取了 BTC 和 AAPL 的真实市场数据
2. ✅ 将数据保存到了 JSON 文件中（可以查看和验证）
3. ✅ 修复了 TradingView Lightweight Charts 的 API 兼容性问题
4. ✅ 创建了专门的测试页面，可以加载本地数据
5. ✅ 添加了详细的日志和错误处理

**立即测试**: 打开 http://localhost:8000/static/test_chart.html 并点击按钮！

