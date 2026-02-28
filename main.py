#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
☕ 咖啡市场 LLM 多智能体仿真系统 - 主程序入口

项目说明：
  基于 DeepSeek LLM 和多智能体系统的微观咖啡市场仿真沙盘。
  研究上海华东师范大学-环球港商圈消费者的咖啡购买决策行为。

使用方式：
  python main.py --mode test      # 测试运行 (5个顾客)
  python main.py --mode full      # 完整运行 (100个顾客)
  python main.py --mode benchmark # 性能基准测试
"""

import os
import sys
import argparse
import time
import json
from datetime import datetime
from dotenv import load_dotenv

# 修复 Windows 编码问题
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.environment.market import CoffeeMarket
from src.utils.population_generator import ShanghaiCustomerGenerator


# ============================================================================
# 🔧 配置管理
# ============================================================================

class SimulationConfig:
    """仿真参数配置"""
    
    # 基础路径
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    DATA_INPUT_DIR = os.path.join(PROJECT_ROOT, "data/input")
    DATA_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data/output")
    
    # 数据文件
    POPULATION_CSV = os.path.join(DATA_INPUT_DIR, "shanghai_population.csv")
    BRAND_LIBRARY_JSON = os.path.join(DATA_INPUT_DIR, "coffee_brands_library.json")
    
    # 模拟规模参数 (根据模式动态设置)
    SIMULATION_MODES = {
        "test": {
            "sample_size": 5,
            "description": "快速测试运行 (5个顾客)"
        },
        "demo": {
            "sample_size": 20,
            "description": "演示运行 (20个顾客)"
        },
        "half": {
            "sample_size": 50,
            "description": "半量运行 (50个顾客)"
        },
        "mass": {
            "sample_size": 1000,
            "description": "大规模运行 (1000个顾客)"
        },
        "full": {
            "sample_size": 100,
            "description": "完整运行 (100个顾客)"
        },
        "benchmark": {
            "sample_size": 200,
            "description": "性能基准测试 (200个顾客)"
        }
    }
    
    # 华东师范大学-环球港虚拟商圈地图配置
    # 坐标系：以校门为原点 (1000, 1000)，单位为米
    HUASHIDA_MAP = {
        # 一期：核心4家店
        "Shop_1": {
            "brand": "Luckin",
            "location": (1000, 1050),
            "current_queue": 15,
            "description": "校门口瑞幸 - 人气旺、排队久"
        },
        "Shop_2": {
            "brand": "Nowwa",
            "location": (1000, 1200),
            "current_queue": 3,
            "description": "枣阳路挪瓦 - 周边社区、外卖主力"
        },
        "Shop_3": {
            "brand": "Manner",
            "location": (1000, 1800),
            "current_queue": 8,
            "description": "环球港 Manner - 精品小店、自带杯文化"
        },
        "Shop_4": {
            "brand": "MStand",
            "location": (1050, 1850),
            "current_queue": 5,
            "description": "环球港 M Stand - 高颜值打卡店"
        },
        # 可选：二期扩展店铺
        "Shop_5": {
            "brand": "Starbucks",
            "location": (900, 1600),
            "current_queue": 10,
            "description": "环球港星巴克 - 全球连锁品牌"
        },
        "Shop_6": {
            "brand": "Seesaw",
            "location": (1100, 1700),
            "current_queue": 4,
            "description": "创意体验 Seesaw - 精品咖啡馆"
        },
        # 三期：全品牌覆盖
        "Shop_7": {
            "brand": "Tims",
            "location": (950, 1500),
            "current_queue": 3,
            "description": "Tims 天好咖啡 - 咖啡+暖食便捷餐饮"
        },
        "Shop_8": {
            "brand": "Arabica",
            "location": (1150, 1600),
            "current_queue": 2,
            "description": "%ARABICA - 高端精品咖啡馆"
        },
        "Shop_9": {
            "brand": "Yongbo",
            "location": (900, 1700),
            "current_queue": 4,
            "description": "永璞咖啡 - 新锐创意品牌"
        },
        "Shop_10": {
            "brand": "PiYe",
            "location": (1200, 1500),
            "current_queue": 5,
            "description": "皮爷咖啡 - 社交打卡新宠"
        },
        "Shop_11": {
            "brand": "BluebottleC",
            "location": (1000, 1400),
            "current_queue": 3,
            "description": "蓝瓶咖啡 - 国际精品咖啡连锁"
        },
        # 四期：同品牌多店分布（贴近真实商圈密度）
        "Shop_12": {
            "brand": "Luckin",
            "location": (980, 1120),
            "current_queue": 12,
            "description": "瑞幸咖啡 - 二店（教学楼侧门）"
        },
        "Shop_13": {
            "brand": "Nowwa",
            "location": (1030, 1300),
            "current_queue": 2,
            "description": "Nowwa 挪瓦 - 二店（社区外卖点）"
        },
        "Shop_14": {
            "brand": "Manner",
            "location": (1020, 1750),
            "current_queue": 6,
            "description": "Manner - 二店（商场内店）"
        },
        "Shop_15": {
            "brand": "Starbucks",
            "location": (880, 1550),
            "current_queue": 9,
            "description": "星巴克 - 二店（北广场）"
        },
        "Shop_16": {
            "brand": "Tims",
            "location": (960, 1450),
            "current_queue": 4,
            "description": "Tims 天好咖啡 - 二店（写字楼入口）"
        }
    }
    
    # 平台规则（可模拟不同营销策略）
    PLATFORM_RULES_DEFAULT = {
        "event_name": "外卖福利：免运费+阶梯红包（满10减3/满15减5/满30减10）",
        "free_delivery_campaign": True,      # 全平台免运费
        "delivery_coupons_enabled": True,    # 启用外卖红包
        "coupon_threshold": 999,             # 通用满减门槛（暂不启用）
        "coupon_amount": 0                   # 通用满减金额（暂不启用）
    }
    
    PLATFORM_RULES_AGGRESSIVE = {
        "event_name": "瑞幸补贴：满15元减5元",
        "free_delivery_campaign": False,
        "coupon_threshold": 15,
        "coupon_amount": 5
    }
    
    PLATFORM_RULES_PREMIUM = {
        "event_name": "高端品牌周：精品咖啡优惠",
        "free_delivery_campaign": False,
        "coupon_threshold": 35,
        "coupon_amount": 8
    }
    
    @classmethod
    def get_simulation_config(cls, mode="test"):
        """获取指定模式的仿真配置"""
        if mode not in cls.SIMULATION_MODES:
            raise ValueError(f"未知的仿真模式: {mode}。可选值: {list(cls.SIMULATION_MODES.keys())}")
        return cls.SIMULATION_MODES[mode]


# ============================================================================
# 📊 主程序
# ============================================================================

class SimulationRunner:
    """仿真运行器 - 协调整个模拟流程"""
    
    def __init__(self, api_key=None, mode="test"):
        """初始化仿真运行器"""
        self.mode = mode
        self.config = SimulationConfig.get_simulation_config(mode)
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.market = None
        self.start_time = None
        self.end_time = None
        
    def validate_environment(self):
        """检查环境依赖"""
        print("🔍 检查环境依赖...")
        
        # 检查 API Key
        if not self.api_key:
            print("❌ 错误：未找到 DEEPSEEK_API_KEY")
            print("   请设置环境变量或在 .env 文件中配置")
            return False
        
        # 检查数据文件
        if not os.path.exists(SimulationConfig.POPULATION_CSV):
            print(f"❌ 错误：缺少人口数据文件: {SimulationConfig.POPULATION_CSV}")
            print("   请先运行: python -m src.utils.population_generator")
            return False
        
        if not os.path.exists(SimulationConfig.BRAND_LIBRARY_JSON):
            print(f"❌ 错误：缺少品牌库文件: {SimulationConfig.BRAND_LIBRARY_JSON}")
            return False
        
        # 创建输出目录
        os.makedirs(SimulationConfig.DATA_OUTPUT_DIR, exist_ok=True)
        
        print("✅ 环境检查通过\n")
        return True
    
    def initialize_market(self, platform_rules=None):
        """初始化市场环境"""
        print("🌍 初始化市场环境...")
        
        try:
            self.market = CoffeeMarket(
                population_csv=SimulationConfig.POPULATION_CSV,
                brand_library_json=SimulationConfig.BRAND_LIBRARY_JSON,
                map_config=SimulationConfig.HUASHIDA_MAP,
                api_key=self.api_key
            )
            print("✅ 市场初始化成功\n")
            return True
        except Exception as e:
            print(f"❌ 市场初始化失败: {e}\n")
            return False
    
    def run(self, platform_rules=None, output_filename=None):
        """执行仿真"""
        print("=" * 70)
        print(f"☕ 开始仿真 - 模式: {self.mode.upper()} ({self.config['description']})")
        print("=" * 70)
        print()
        
        # 1. 环境检查
        if not self.validate_environment():
            return False
        
        # 2. 市场初始化
        if not self.initialize_market(platform_rules):
            return False
        
        # 3. 运行仿真
        self.start_time = time.time()
        print(f"⏳ 模拟规模: {self.config['sample_size']} 名顾客")
        print(f"🗺️  地图范围: {len(SimulationConfig.HUASHIDA_MAP)} 家咖啡店")
        print()
        
        try:
            self.market.run_simulation(
                sample_size=self.config['sample_size'],
                platform_rules=platform_rules or SimulationConfig.PLATFORM_RULES_DEFAULT
            )
        except Exception as e:
            print(f"❌ 仿真运行出错: {e}")
            return False
        
        self.end_time = time.time()
        
        # 4. 导出结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_filename:
            if not output_filename.lower().endswith(".csv"):
                output_filename += ".csv"
        else:
            output_filename = f"simulation_results_{self.mode}_{timestamp}.csv"
        
        try:
            self.market.export_results(output_filename)
        except Exception as e:
            print(f"❌ 结果导出失败: {e}")
            return False
        
        # 5. 打印统计
        self._print_summary(timestamp)
        
        return True
    
    def _print_summary(self, timestamp):
        """打印仿真总结"""
        elapsed_time = self.end_time - self.start_time
        sample_size = self.config['sample_size']
        time_per_customer = elapsed_time / sample_size if sample_size > 0 else 0
        
        print("\n" + "=" * 70)
        print("📈 仿真完成统计")
        print("=" * 70)
        print(f"⏱️  总耗时: {elapsed_time:.2f} 秒")
        print(f"👥 处理顾客数: {sample_size} 人")
        print(f"⚡ 平均耗时/人: {time_per_customer:.2f} 秒")
        print(f"📊 结果文件: data/output/simulation_results_{self.mode}_{timestamp}.csv")
        print("=" * 70)
        print()


# ============================================================================
# 🚀 命令行入口
# ============================================================================

def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="☕ 咖啡市场 LLM 多智能体仿真系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例子:
  python main.py --mode test          # 快速测试 (5个顾客)
  python main.py --mode full          # 完整运行 (100个顾客)
    python main.py --mode benchmark     # 性能测试 (200个顾客)
    python main.py --mode mass          # 大规模运行 (1000个顾客)
    python main.py --mode test --api-key sk-xxx  # 指定 API Key
    python main.py --mode mass --output data/output/simulation_results_1000.csv
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=list(SimulationConfig.SIMULATION_MODES.keys()),
        default="test",
        help="仿真模式 (默认: test)"
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="DeepSeek API Key (默认从环境变量读取)"
    )
    
    parser.add_argument(
        "--strategy",
        choices=["default", "aggressive", "premium"],
        default="default",
        help="平台营销策略 (默认: default)"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="结果输出文件名 (可包含路径，默认自动生成)"
    )
    
    return parser


def get_platform_rules(strategy):
    """获取相应策略的平台规则"""
    if strategy == "aggressive":
        return SimulationConfig.PLATFORM_RULES_AGGRESSIVE
    elif strategy == "premium":
        return SimulationConfig.PLATFORM_RULES_PREMIUM
    else:
        return SimulationConfig.PLATFORM_RULES_DEFAULT


def main():
    """主程序入口"""
    # 1. 加载环境变量 (.env 文件)
    load_dotenv()
    
    # 2. 解析命令行参数
    parser = create_parser()
    args = parser.parse_args()
    
    # 3. 创建运行器
    runner = SimulationRunner(
        api_key=args.api_key,
        mode=args.mode
    )
    
    # 4. 获取平台规则
    platform_rules = get_platform_rules(args.strategy)
    
    # 5. 执行仿真
    success = runner.run(platform_rules=platform_rules, output_filename=args.output)
    
    # 6. 返回退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
