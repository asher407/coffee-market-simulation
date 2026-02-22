# 🚀 项目运行指南

## 快速开始

### 1️⃣ 环境配置

#### a) 复制 `.env` 文件

```bash
cp .env.example .env
```

#### b) 编辑 `.env` 填入 API Key

```bash
DEEPSEEK_API_KEY=sk-your-real-api-key-here
```

#### c) 安装依赖（如有需要）

```bash
pip install python-dotenv
```

---

### 2️⃣ 生成人口数据

首次运行前，需要生成 1000 名虚拟顾客的数据：

```bash
python -m src.utils.population_generator
```

✅ 输出: `data/input/shanghai_population.csv`

---

### 3️⃣ 运行仿真

#### 🧪 快速测试（5个顾客）

```bash
python main.py --mode test
```

#### 📊 演示运行（20个顾客）

```bash
python main.py --mode demo
```

#### 🎯 完整运行（100个顾客）

```bash
python main.py --mode full
```

#### 🔬 性能基准（200个顾客）

```bash
python main.py --mode benchmark
```

---

### 4️⃣ 营销策略选项

使用 `--strategy` 参数来选择不同的营销规则：

```bash
# 平台常规（无特殊优惠）
python main.py --mode test --strategy default

# 激进补贴（满15元减5元）
python main.py --mode test --strategy aggressive

# 高端推广（满35元减8元）
python main.py --mode test --strategy premium
```

---

### 5️⃣ 指定 API Key（可选）

如果不想使用 `.env` 文件，可以直接在命令行指定：

```bash
python main.py --mode test --api-key sk-your-key-here
```

---

## 📊 输出结果

所有仿真结果保存在 `data/output/` 目录下：

```
simulation_results_test_20260214_120000.csv
simulation_results_full_20260214_120530.csv
...
```

### CSV 列说明

| 列名                | 说明       | 示例         |
| ------------------- | ---------- | ------------ |
| `customer_id`       | 顾客ID     | 1001         |
| `age_group`         | 年龄段     | 25-34        |
| `occupation`        | 职业       | Tech/Finance |
| `income`            | 月收入     | 25000        |
| `preference`        | 咖啡偏好   | Latte        |
| `price_sensitivity` | 价格敏感度 | Low          |
| `decision`          | 购买决策   | Shop_1_Walk  |
| `brand`             | 购买品牌   | Luckin       |
| `method`            | 购买方式   | 自提 或 外卖 |
| `item`              | 购买商品   | 生椰拿铁     |
| `price`             | 支付金额   | 20.8         |
| `reason`            | 决策理由   | 离得近       |

---

## ⚙️ 高级用法

### 配置文件

所有可调参数在 `config.py` 中：

```python
# 修改 LLM 温度（影响决策随机性）
LLM_PARAMS["temperature"] = 0.5

# 修改运费计算规则
DELIVERY_FEE_CONFIG["base_fee"] = 5

# 添加新的营销策略
MARKETING_STRATEGIES["custom"] = {
    "name": "自定义策略",
    ...
}
```

### 地图配置

在 `main.py` 中的 `SimulationConfig.HUASHIDA_MAP` 添加店铺：

```python
"Shop_7": {
    "brand": "Arabica",
    "location": (900, 900),
    "current_queue": 2,
    "description": "新增门店"
}
```

---

## 🐛 故障排除

### 错误：未找到 DEEPSEEK_API_KEY

✅ 解决：

```bash
# 检查 .env 文件是否存在
ls -la .env

# 确保填入了真实的 API Key
cat .env | grep DEEPSEEK_API_KEY
```

### 错误：找不到人口数据文件

✅ 解决：

```bash
# 运行人口数据生成器
python -m src.utils.population_generator
```

### 错误：API 调用失败

✅ 解决：

- 检查网络连接
- 验证 API Key 有效性
- 检查 API 请求额度

---

## 📈 项目结构

```
coffee-market-simulation/
├── main.py                         # ✨ 新增：主程序入口
├── config.py                       # ✨ 新增：全局配置
├── .env                            # ✨ 新增：环境变量
├── .env.example                    # ✨ 新增：配置模板
│
├── data/
│   ├── input/
│   │   ├── shanghai_population.csv
│   │   └── coffee_brands_library.json
│   └── output/
│       └── simulation_results_*.csv
│
├── src/
│   ├── agents/
│   │   └── customer.py
│   ├── environment/
│   │   └── market.py
│   ├── llm/
│   │   └── client.py
│   └── utils/
│       └── population_generator.py
└── README.md
```

---

## 🎯 典型工作流

### 场景 1：快速验证系统

```bash
# 1. 生成人口数据
python -m src.utils.population_generator

# 2. 快速测试（5个顾客，<1分钟）
python main.py --mode test

# 3. 查看输出
cat data/output/simulation_results_test_*.csv | head -20
```

### 场景 2：完整仿真分析

```bash
# 1. 生成人口数据
python -m src.utils.population_generator

# 2. 运行完整仿真（100个顾客，~2分钟）
python main.py --mode full

# 3. A/B 对比分析
python main.py --mode full --strategy aggressive
python main.py --mode full --strategy premium

# 4. 分析结果（后续开发分析模块）
python -m src.analysis.analytics
```

### 场景 3：性能基准测试

```bash
# 运行 200 个顾客仿真
python main.py --mode benchmark

# 记录运行时间和 API 调用次数
```

---

## 💡 下一步计划

- [ ] 开发 `src/analysis/` 模块
  - `analytics.py` - 数据分析和统计
  - `visualizer.py` - 图表可视化

- [ ] 实现测试框架
  - unit tests
  - integration tests

- [ ] 性能优化
  - 异步 API 调用
  - 结果缓存机制
  - 批量请求优化

---

## 📞 问题反馈

如有问题，请检查：

1. Python 版本 >= 3.8
2. 依赖包已安装
3. API Key 有效
4. 网络连接正常

---

**祝你使用愉快！ ☕**
