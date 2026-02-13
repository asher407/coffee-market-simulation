# ☕ 咖啡市场大模型多智能体仿真项目 (Coffee Market LLM-MAS Simulation)

## 📌 项目概述 (Project Overview)

本项目是一个基于大语言模型（LLM）和多智能体系统（Multi-Agent System）构建的**微观咖啡市场仿真沙盘**。

- **研究背景**：聚焦中国上海市场（以华东师范大学-环球港商圈为沙盘），研究在复杂的商业环境（品牌调性、物理距离、外卖配送、平台补贴）下，不同人口学特征消费者的咖啡购买决策行为。
- **核心技术栈**：Python, Pandas, DeepSeek API (基于 OpenAI SDK 兼容), 提示词工程 (Prompt Engineering), 合成人口生成 (Synthetic Population Generation)。
- **架构演进备注**：为了贴合真实商业逻辑（连锁品牌门店经理无定价权），**本项目舍弃了“店主 Agent”的动态博弈设计**，将咖啡店铺降级为受外部规则（总部/平台）控制的静态环境实体，全力聚焦于**需求端（顾客 Agent）的微观行为模拟**。

---

## 📂 当前项目结构 (Project Structure)

```text
coffee-market-sim/
├── data/                   # 数据层
│   ├── input/
│   │   ├── shanghai_population.csv    # 仿真顾客池 (人口学与偏好特征)
│   │   └── coffee_brands_library.json # 品牌资料库 (包含品牌画像、活动与菜单价格)
│   └── output/             # 仿真日志与输出
│       └── simulation_results.csv     # LLM决策结果落库
│
├── src/                    # 核心逻辑层
│   ├── agents/
│   │   └── customer.py     # 顾客智能体 (包含人设组装、空间计算、菜单匹配与Prompt生成)
│   │
│   ├── environment/
│   │   └── market.py       # 市场环境引擎 (实体化店铺、运行时间循环、日志记录)
│   │
│   ├── llm/
│   │   └── client.py       # LLM 客户端 (封装 DeepSeek API，强制 JSON 输出)
│   │
│   └── utils/
│       └── population_generator.py    # 顾客生成器 (基于上海实测统计数据的概率分布生成算法)
│
├── .env                    # 环境变量 (存放 DEEPSEEK_API_KEY)
└── PROJECT_STATUS.md       # 本进度文档
```
