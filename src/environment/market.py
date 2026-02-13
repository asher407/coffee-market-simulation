import pandas as pd
import json
import time
import os
from src.agents.customer import Customer
from src.llm.client import DeepSeekClient

class CoffeeMarket:
    def __init__(self, population_csv, brand_library_json, map_config, api_key=None):
        print("🌍 正在初始化咖啡市场 (华东师范大学-环球港 虚拟商圈)...")
        
        # 1. 加载顾客数据
        self.population_df = pd.read_csv(population_csv)
        self.customers = []
        for _, row in self.population_df.iterrows():
            self.customers.append(Customer(profile_data=row.to_dict()))
        print(f"👥 成功加载 {len(self.customers)} 名虚拟顾客数据。")
        
        # 2. 实体化店铺 (将 JSON 模板映射到地图上)
        self.shops = self._load_shops(brand_library_json, map_config)
        print(f"🏪 成功在地图上开出 {len(self.shops)} 家咖啡门店。")
        
        # 3. 接入大模型客户端
        self.llm_client = DeepSeekClient(api_key=api_key)
        self.simulation_logs = []

    def _load_shops(self, library_path, map_config):
        """读取品牌库并根据地图配置生成实体店"""
        with open(library_path, 'r', encoding='utf-8') as f:
            brand_library = json.load(f)
            
        actual_shops = []
        for shop_id, setup in map_config.items():
            brand_id = setup['brand']
            brand_info = brand_library.get(brand_id)
            if not brand_info:
                print(f"⚠️ 警告：品牌库中找不到品牌 {brand_id}")
                continue
                
            shop_instance = {
                "id": shop_id,
                "brand_name": brand_info['brand_name'],
                "category": brand_info['category'],
                "business_model": brand_info['business_model'],
                "promotions": brand_info['promotions'],
                "menu": brand_info['menu'],
                "supports_delivery": brand_info['supports_delivery'],
                # 实体特有的动态物理属性
                "location": setup['location'],
                "queue_time": setup['current_queue']
            }
            actual_shops.append(shop_instance)
        return actual_shops

    def run_simulation(self, sample_size=10, platform_rules=None):
            print(f"\n⏳ 开始模拟，随机抽取 {sample_size} 名顾客进行决策测试...")
            
            import random
            test_customers = random.sample(self.customers, min(sample_size, len(self.customers)))
            
            for i, customer in enumerate(test_customers):
                print(f"[{i+1}/{sample_size}] 顾客 ID:{customer.id} | 职业:{customer.profile.get('occupation')} | 月收:{customer.profile.get('income')} | 偏好:{customer.preference}")
                
                sys_prompt = customer.system_prompt
                user_prompt = customer.generate_decision_prompt(self.shops, platform_rules)
                
                decision_data = self.llm_client.get_decision(sys_prompt, user_prompt)
                
                # ========= 更新打印语句，直观展示购买细节 =========
                brand = decision_data.get('brand')
                if brand:
                    print(f"   👉 决策: 选择了【{brand}】的【{decision_data.get('item')}】")
                    print(f"   👉 方式: {decision_data.get('method')} | 花费: {decision_data.get('price')}元")
                else:
                    print(f"   👉 决策: 放弃购买 (None)")
                print(f"   👉 理由: {decision_data.get('reason')}\n")
                
                # ========= 更新日志字典，增加我们要求的四个新字段 =========
                log_entry = {
                    "customer_id": customer.id,
                    "age_group": customer.profile.get('age_group'),
                    "occupation": customer.profile.get('occupation'),
                    "income": customer.profile.get('income'),
                    "preference": customer.profile.get('preference'),
                    "price_sensitivity": customer.profile.get('price_sensitivity'),
                    "decision": decision_data.get('decision'),
                    "brand": decision_data.get('brand'),         # 新增
                    "method": decision_data.get('method'),       # 新增
                    "item": decision_data.get('item'),           # 新增
                    "price": decision_data.get('price'),         # 新增
                    "reason": decision_data.get('reason')
                }
                self.simulation_logs.append(log_entry)
                
                time.sleep(0.5) 
                
            print("✅ 模拟循环结束！")

    def export_results(self, output_filename="simulation_results.csv"):
        if not self.simulation_logs:
            return
            
        df_results = pd.DataFrame(self.simulation_logs)
        output_dir = "data/output"
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, output_filename)
        df_results.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"\n📊 完整决策结果已保存至: {filepath}")
        
        print("\n--- 🏆 最终销售统计 ---")
        print(df_results['decision'].value_counts())


# --- 运行入口 ---
if __name__ == "__main__":
    # ⚠️ 换成你的真实 DeepSeek API KEY ⚠️
    API_KEY = "sk-d6389f6e995543959b1c313cf2ffd778" 
    
    # 🗺️ 华东师范大学-环球港 虚拟商圈地图配置
    # 假设校门坐标为 (1000, 1000)
    HUASHIDA_MAP = {
        # 校门口的瑞幸，排队人多 (距离极近)
        "Shop_1": {"brand": "Luckin", "location": (1000, 1050), "current_queue": 15},
        # 枣阳路的挪瓦，做周边社区外卖 (距离近)
        "Shop_2": {"brand": "Nowwa",  "location": (1000, 1200), "current_queue": 3},
        # 环球港的 Manner，距离较远 (约800米)
        "Shop_3": {"brand": "Manner", "location": (1000, 1800), "current_queue": 8},
        # 环球港的 M Stand，距离远，主打堂食打卡
        "Shop_4": {"brand": "MStand", "location": (1050, 1850), "current_queue": 5}
    }
    
    TODAY_RULES = {
        "event_name": "开学季：外卖全平台免运费",
        "free_delivery_campaign": True
    }
    
    # 初始化市场
    market = CoffeeMarket(
        population_csv="data/input/shanghai_population.csv", 
        brand_library_json="data/input/coffee_brands_library.json",
        map_config=HUASHIDA_MAP,
        api_key=API_KEY
    )
    
    # 抽取 5 名顾客进行测试，跑通后再调大数值
    market.run_simulation(sample_size=5, platform_rules=TODAY_RULES)
    market.export_results("test_huashida_run.csv")