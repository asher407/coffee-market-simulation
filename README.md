# ☕ 咖啡市场大模型多智能体仿真项目 (Coffee Market LLM-MAS Simulation)

## 📌 项目概述 (Project Overview)

本项目是一个基于大语言模型（LLM）和多智能体系统（Multi-Agent System）构建的**微观咖啡市场仿真沙盘**。

- **研究背景**：聚焦中国上海市场（以华东师范大学-环球港商圈为沙盘），研究在复杂的商业环境（品牌调性、物理距离、外卖配送、平台补贴）下，不同人口学特征消费者的咖啡购买决策行为。
- **核心技术栈**：Python, Pandas, DeepSeek API (基于 OpenAI SDK 兼容), 提示词工程 (Prompt Engineering), 合成人口生成 (Synthetic Population Generation)。
- **架构演进备注**：为了贴合真实商业逻辑（连锁品牌门店经理无定价权），**本项目舍弃了“店主 Agent”的动态博弈设计**，将咖啡店铺降级为受外部规则（总部/平台）控制的静态环境实体，全力聚焦于**需求端（顾客 Agent）的微观行为模拟**。

---

## 📂 项目结构 (Project Structure)

```text
coffee-market-simulation/
├── data/                              # 数据层
│   ├── input/
│   │   ├── shanghai_population.csv    # 仿真顾客池（1000人，含品牌偏好）
│   │   └── coffee_brands_library.json # 品牌资料库（11个品牌，含菜单价格）
│   └── output/                        # 仿真结果与分析报告
│       ├── simulation_results_*.csv   # LLM决策日志
│       └── analysis_*.csv             # 数据分析报告
│
├── src/                               # 核心业务逻辑
│   ├── agents/
│   │   └── customer.py                # 顾客智能体（品牌偏好、Top-N筛选、决策提示生成）
│   ├── environment/
│   │   └── market.py                  # 市场环境引擎（店铺管理、仿真循环）
│   ├── llm/
│   │   └── client.py                  # LLM客户端（DeepSeek API封装）
│   ├── utils/
│   │   └── population_generator.py    # 人口生成器（基于真实统计分布）
│   └── analysis/
│       ├── analytics.py               # 数据分析引擎
│       └── visualizer.py              # 可视化工具
│
├── main.py                            # 主程序入口
├── analyze.py                         # 数据分析入口
├── .env                               # 环境变量（API密钥）
├── .gitignore                         # Git忽略文件
└── README.md                          # 项目文档
```

---

## 📊 数据分析模块 (Data Analytics Module) ✨ NEW

本项目已集成全面的数据分析功能，可自动生成仿真结果的多维度分析报告和可视化图表。

### 🎯 核心分析功能

| 分析类别           | 功能说明                               | 输出          |
| ------------------ | -------------------------------------- | ------------- |
| **品牌销售分析**   | 销售量、销售额、平均单价、市场份额     | CSV + 柱状图  |
| **消费者分层**     | 按年龄、职业、收入、偏好分类分析       | 4 份 CSV 报告 |
| **购买方式分析**   | 外卖 vs 自提占比、各人群的购买方式偏好 | 2 份 CSV 报告 |
| **价格敏感性分析** | 价格敏感度与消费金额的关系             | CSV + 图表    |
| **决策理由分析**   | TOP 15 购买决策理由排名                | CSV 报告      |

### ⚡ 快速使用

**一键生成分析报告和图表：**

```bash
# 运行仿真
python main.py --mode full

# 分析结果，自动生成 10 个 CSV 报告 + 6 个 PNG 图表
python analyze.py
```

**输出文件示例：**

- `analysis_brand_sales_20260222_213148.csv` - 品牌销售统计
- `analysis_age_group_20260222_213148.csv` - 年龄段分析
- `analysis_occupation_20260222_213148.csv` - 职业分析
- `analysis_income_segment_20260222_213148.csv` - 收入分层
- `analysis_delivery_method_20260222_213148.csv` - 购买方式
- `analysis_price_sensitivity_20260222_213148.csv` - 价格敏感性
- `analysis_reasons_20260222_213148.csv` - 决策理由
- `chart_brand_sales.png` - 品牌销售对比图
- `chart_market_share.png` - 市场份额饼图
- `chart_age_spending.png` - 年龄段消费趋势

---

## ⚙️ 快速开始 (Quick Start)

### 1. 环境配置

```bash
# 安装依赖
pip install pandas openai python-dotenv numpy matplotlib seaborn

# 配置API密钥
echo "DEEPSEEK_API_KEY=your_api_key_here" > .env
```

### 2. 生成仿真人口数据

```bash
python -m src.utils.population_generator
```

### 3. 运行仿真

```bash
# 快速测试（5人）
python main.py --mode test

# 演示运行（20人）
python main.py --mode demo

# 半量运行（50人）
python main.py --mode half

# 大规模运行（1000人）
python main.py --mode mass
```

### 4. 分析结果

```bash
# 自动分析最新仿真结果
python analyze.py
```

---

## 🎯 核心特性

- ✅ **品牌偏好系统**：市场份额驱动的品牌忠诚度模型（瑞幸45%、星巴克14%等）
- ✅ **Top-N筛选**：基于品牌偏好+距离+价格+排队的综合评分，筛选Top3候选店
- ✅ **外卖激励**：阶梯红包（满10减3/满15减5/满30减10）+ 免运费
- ✅ **多店铺支持**：16家门店覆盖11个品牌，模拟真实商圈密度
- ✅ **人群细分**：按年龄、职业、收入、价格敏感度生成1000人合成人口
- ✅ **全面分析**：10+维度数据分析报告 + 6类可视化图表

---

## 📊 项目成果

**最新仿真结果（50人测试）：**

- 品牌分布：瑞幸31.25% | Manner 14.58% | Nowwa 14.58% | 星巴克12.5%
- 外卖比例：60%（免运费+红包激励下）
- 平均客单价：22.4元

```

```
