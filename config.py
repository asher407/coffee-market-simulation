# -*- coding: utf-8 -*-
"""
⚙️ 全局配置文件

包含仿真的各种可调参数：
  - 地图配置（店铺位置、排队时间）
  - LLM 参数（温度、token 限制）
  - 营销规则（优惠、补贴策略）
  - 输出配置（日志、结果格式）
"""

import os
from datetime import datetime

# ============================================================================
# 📍 地理位置配置
# ============================================================================

# 虚拟地图范围（单位：米）
MAP_WIDTH = 2000
MAP_HEIGHT = 2000

# 华东师范大学参考坐标
HUASHIDA_CENTER = (1000, 1000)

# 步行速度（米/分钟）- 用于计算步行时间
WALK_SPEED = 80

# ============================================================================
# 🤖 LLM 配置
# ============================================================================

# DeepSeek API 配置
DEEPSEEK_CONFIG = {
    "model": "deepseek-chat",
    "base_url": "https://api.deepseek.com",
    "timeout": 30,
    "max_retries": 3
}

# 模型参数
LLM_PARAMS = {
    "temperature": 0.7,        # 0.7 给予适度随机性，符合真实消费者非绝对理性
    "max_tokens": 200,         # 决策结果很短
    "response_format": "json"   # 强制 JSON 输出
}

# ============================================================================
# 🛍️ 消费者决策配置
# ============================================================================

# 消费者参数
CUSTOMER_PARAMS = {
    "min_location": 500,
    "max_location": 1500,
    "daily_budget": None,  # 不限制，根据月收入计算
}

# 距离决策规则（单位：米）
DISTANCE_RULES = {
    "student_max_walk": 800,          # 学生最大步行距离
    "office_worker_max_walk": 1000,   # 上班族最大步行距离
    "retired_max_walk": 2000,         # 退休人士不限距离（有时间）
    "delivery_max_distance": 3000     # 最大外卖配送距离
}

# 价格敏感度映射
PRICE_SENSITIVITY = {
    "High": 0.8,     # 高敏感 - 价格提升20%可能放弃购买
    "Medium": 0.5,   # 中等敏感
    "Low": 0.2       # 低敏感 - 基本不看价格
}

# ============================================================================
# 💰 平台营销规则
# ============================================================================

# 运费计算规则
DELIVERY_FEE_CONFIG = {
    "base_fee": 3,              # 基础配送费
    "distance_per_yuan": 1000,  # 每1000米增加1元
    "max_distance": 3000,       # 最大配送距离
    "override_fee": 999         # 超出范围的虚拟费用（表示无法配送）
}

# 预置的营销策略集合
MARKETING_STRATEGIES = {
    "default": {
        "name": "平台常规",
        "description": "无特殊优惠",
        "free_delivery": False,
        "coupon_threshold": 999,
        "coupon_amount": 0,
        "event_name": "日常购物"
    },
    "aggressive": {
        "name": "激进补贴",
        "description": "低价策略 - 激发消费需求",
        "free_delivery": False,
        "coupon_threshold": 15,
        "coupon_amount": 5,
        "event_name": "瑞幸补贴：满15元减5元"
    },
    "premium": {
        "name": "高端推广",
        "description": "精品品牌优惠",
        "free_delivery": False,
        "coupon_threshold": 35,
        "coupon_amount": 8,
        "event_name": "高端品牌周：精品优惠"
    },
    "free_delivery": {
        "name": "免运费活动",
        "description": "所有外卖单免运费",
        "free_delivery": True,
        "coupon_threshold": 999,
        "coupon_amount": 0,
        "event_name": "开学季：外卖全平台免运费"
    },
    "double_bonus": {
        "name": "双重优惠",
        "description": "免运费 + 满减",
        "free_delivery": True,
        "coupon_threshold": 25,
        "coupon_amount": 5,
        "event_name": "双重优惠：免运费+满25减5"
    }
}

# ============================================================================
# 📊 输出与日志配置
# ============================================================================

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/simulation.log"
}

# 输出文件配置
OUTPUT_CONFIG = {
    "base_dir": "data/output",
    "csv_separator": ",",
    "encoding": "utf-8-sig",  # utf-8-sig 防止中文乱码（Excel 兼容）
    "include_columns": [
        "customer_id", "age_group", "occupation", "income",
        "preference", "price_sensitivity", "decision",
        "brand", "method", "item", "price", "reason"
    ]
}

# 结果分析配置
ANALYSIS_CONFIG = {
    "enable_brand_share": True,      # 品牌市场份额分析
    "enable_demographic": True,       # 人口学分层分析
    "enable_price_analysis": True,    # 价格分析
    "enable_visualization": True      # 可视化图表
}

# ============================================================================
# 🔬 实验配置
# ============================================================================

# A/B 测试配置
AB_TEST_CONFIG = {
    "enable": False,
    "control_strategy": "default",
    "treatment_strategy": "aggressive",
    "sample_ratio": 0.5,  # 50% 对照组，50% 实验组
}

# 多轮模拟配置（模拟多日积累效应）
MULTI_DAY_CONFIG = {
    "enable": False,
    "days": 7,
    "vary_rules": True,  # 每天变化营销规则
}

# ============================================================================
# 🏆 性能和缓存配置
# ============================================================================

# 缓存配置
CACHE_CONFIG = {
    "enable": False,
    "type": "sqlite",  # "memory" 或 "sqlite"
    "path": "cache/decisions.db",
    "ttl_hours": 24  # 缓存过期时间（小时）
}

# 并发配置
ASYNC_CONFIG = {
    "enable": False,
    "max_workers": 5,  # 最多同时调用 API 的线程数
    "rate_limit": 10   # 请求/秒
}

# ============================================================================
# 🎯 快捷配置组
# ============================================================================

# 快速模式 - 快速测试（不调用 API）
QUICK_MODE_CONFIG = {
    "enable": False,
    "use_mock_llm": True,  # 使用模拟 LLM 而非真实 API
}

# 当前活跃配置
ACTIVE_CONFIG = {
    "logging": LOGGING_CONFIG,
    "output": OUTPUT_CONFIG,
    "marketing": MARKETING_STRATEGIES["default"],
    "analysis": ANALYSIS_CONFIG,
}


# ============================================================================
# 🔧 配置加载和验证
# ============================================================================

def load_config(strategy="default", mode="test"):
    """根据策略和模式加载配置"""
    config = {
        "strategy": strategy,
        "mode": mode,
        "marketing": MARKETING_STRATEGIES.get(strategy, MARKETING_STRATEGIES["default"]),
        "llm": LLM_PARAMS,
        "deepseek": DEEPSEEK_CONFIG,
    }
    return config


def get_output_dir():
    """获取输出目录"""
    output_dir = OUTPUT_CONFIG["base_dir"]
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def get_log_dir():
    """获取日志目录"""
    log_dir = os.path.dirname(LOGGING_CONFIG["file"])
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


if __name__ == "__main__":
    # 打印当前配置
    print("📋 当前配置状态：")
    print(f"  LLM 温度: {LLM_PARAMS['temperature']}")
    print(f"  Max Tokens: {LLM_PARAMS['max_tokens']}")
    print(f"  营销策略: {MARKETING_STRATEGIES['default']['name']}")
    print(f"  输出目录: {OUTPUT_CONFIG['base_dir']}")
    print(f"  日志级别: {LOGGING_CONFIG['level']}")
