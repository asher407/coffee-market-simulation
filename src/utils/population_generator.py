import numpy as np
import pandas as pd

class ShanghaiCustomerGenerator:
    def __init__(self):
        # 1. 年龄分布 (基于上海统计年鉴2024修正)
        # 核心消费力集中在 25-34 岁 (新上海人/打工人主力)
        self.age_dist = {
            'groups': ['18-24', '25-34', '35-44', '45-54', '55-64', '65+'],
            'probs':  [0.08,    0.30,    0.25,    0.15,    0.10,    0.12] 
        }

        # 2. 职业分布 (映射上海产业结构)
        self.occupations = ['Student', 'White Collar', 'Tech/Finance', 'Freelance', 'Service/Blue', 'Retired']

        # 3. 收入分布 (基于2024上海平均工资 12434元 进行分层)
        # 采用对数正态分布模拟长尾效应 (少数人特别有钱)
        self.income_stats = {
            'Student':      {'mean': 2500,  'sigma': 0.4}, # 生活费
            'White Collar': {'mean': 13000, 'sigma': 0.3}, # 标准打工人
            'Tech/Finance': {'mean': 24000, 'sigma': 0.4}, # 高薪群体
            'Freelance':    {'mean': 11000, 'sigma': 0.8}, # 波动极大
            'Service/Blue': {'mean': 7000,  'sigma': 0.2}, # 基础服务业
            'Retired':      {'mean': 6000,  'sigma': 0.3}  # 退休金
        }

    def _get_occupation_by_age(self, age_group):
        """基于年龄的职业条件概率 P(Occupation|Age)"""
        # 逻辑：年轻人多为学生/初级白领，中年人多为管理/高薪，老年人退休
        if age_group == '18-24':
            return np.random.choice(self.occupations, p=[0.60, 0.20, 0.05, 0.05, 0.10, 0.00])
        elif age_group == '25-34':
            return np.random.choice(self.occupations, p=[0.02, 0.45, 0.25, 0.15, 0.13, 0.00])
        elif age_group == '35-44':
            return np.random.choice(self.occupations, p=[0.00, 0.40, 0.30, 0.15, 0.15, 0.00])
        elif age_group in ['55-64', '65+']:
            # 55岁以上大部分退休或返聘
            p_retire = 0.8 if age_group == '65+' else 0.4
            p_work = (1 - p_retire) / 4
            return np.random.choice(self.occupations, p=[0.00, p_work, p_work, p_work, p_work, p_retire])
        else:
            return np.random.choice(self.occupations, p=[0.00, 0.30, 0.15, 0.20, 0.35, 0.00])

    def _get_income(self, occupation):
        """生成符合对数正态分布的收入"""
        stats = self.income_stats[occupation]
        # Log-Normal生成: mu需要根据mean计算 (mean = exp(mu + sigma^2/2))
        # 简化处理：直接视为正态分布取对数后的还原，或者直接用lognormal函数
        # 这里为了控制方便，使用 np.random.lognormal
        # 需反推 mu: mu = ln(mean) - sigma^2 / 2
        mu = np.log(stats['mean']) - (stats['sigma']**2) / 2
        income = np.random.lognormal(mu, stats['sigma'])
        return int(max(1500, income)) # 兜底最低收入

    def _get_preferences(self, age_group, occupation, income):
        """
        生成消费偏好 (核心逻辑)
        上海市场特征：特调多、对品质有要求、但对价格也敏感
        """
        # 1. 咖啡因需求 (Frequency)
        if occupation in ['Tech/Finance', 'White Collar'] or age_group == '25-34':
            caffeine_need = 'High' # 续命水
        elif occupation == 'Retired':
            caffeine_need = 'Low'
        else:
            caffeine_need = 'Medium'

        # 2. 口味偏好 (Type)
        # 上海特色：拿铁(Latte)是绝对主流，特调(Specialty)占比高
        rand = np.random.random()
        if occupation == 'Student':
            fav_type = 'Specialty' if rand < 0.6 else 'Latte' # 学生喜欢生椰/果咖
        elif occupation in ['Tech/Finance'] and caffeine_need == 'High':
            fav_type = 'Americano' if rand < 0.5 else 'Latte' # 程序员喝冰美式
        elif age_group in ['55-64', '65+']:
            fav_type = 'Americano' if rand < 0.3 else 'Tea' # 老上海喜欢清咖或茶
        else:
            # 大众市场
            fav_type = np.random.choice(['Latte', 'Americano', 'Specialty'], p=[0.5, 0.3, 0.2])

        # 3. 价格敏感度 (Price Sensitivity)
        # 收入越高，敏感度越低。但上海人普遍精明 (Smart Shopper)
        if income > 25000:
            p_sens = 'Low' # 只看品质
        elif income < 8000:
            p_sens = 'High' # 9.9党
        else:
            # 中产阶级，看性价比
            p_sens = 'Medium' 
            
        return fav_type, caffeine_need, p_sens

    def generate_population(self, n=100):
        data = []
        for _ in range(n):
            age_group = np.random.choice(self.age_dist['groups'], p=self.age_dist['probs'])
            occupation = self._get_occupation_by_age(age_group)
            income = self._get_income(occupation)
            fav_type, freq, p_sens = self._get_preferences(age_group, occupation, income)
            
            # 生成 Prompt 描述
            desc = (
                f"你是一名{age_group}岁的{occupation}，生活在上海。"
                f"月收入约{income}元。你对咖啡的需求频率是{freq}。"
                f"你最喜欢的口味是{fav_type}。在价格方面，你的敏感度属于{p_sens}。"
            )
            
            data.append({
                "id": len(data) + 1,
                "age_group": age_group,
                "occupation": occupation,
                "income": income,
                "preference": fav_type,
                "frequency": freq,
                "price_sensitivity": p_sens,
                "persona_description": desc
            })
            
        return pd.DataFrame(data)

if __name__ == "__main__":
    import os
    
    # 1. 实例化生成器
    gen = ShanghaiCustomerGenerator()
    
    # 2. 生成 1000 个顾客 (样本量大一点，统计特征更明显)
    print("正在生成上海顾客仿真数据...")
    df = gen.generate_population(1000)
    
    # 3. 确保 data/input 文件夹存在
    output_dir = "data/input"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"已创建目录: {output_dir}")
    
    # 4. 保存为 CSV
    output_path = f"{output_dir}/shanghai_population.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig') # utf-8-sig 防止中文乱码
    
    print(f"✅ 成功！数据已保存至: {output_path}")
    print("\n--- 数据预览 ---")
    print(df[['occupation', 'income', 'preference', 'price_sensitivity']].head())