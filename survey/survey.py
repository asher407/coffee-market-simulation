import pandas as pd
import random

def generate_full_survey(n=326):
    data = []
    
    # 开放性建议预设池 (对应最后一道建议题)
    suggestions_pool = [
        "无", "", "挺好的", 
        "希望早八能早点开门，有时候赶早课买不到。", 
        "枣阳路外卖送不进来太难受了，希望能多点校内经营点。",
        "千问的活动希望能多搞，学生党真的很需要优惠！",
        "环球港的店人太多没法自习，希望能多一些安静的独立咖啡馆。",
        "乳糖不耐受，强烈呼吁校内机子加燕麦奶选项。"
    ]

    for i in range(n):
        # Q1. 身份 (强化校外人员和学生比例) [cite: 3, 4, 5, 6, 7]
        identity = random.choices(
            ['本科生', '研究生（硕士/博士）', '教职工', '校外人员'], 
            weights=[0.40, 0.25, 0.05, 0.30]
        )[0]

        # Q2. 频率 (排除“几乎不喝”) [cite: 8, 9, 10, 11, 12]
        if identity == '校外人员':
            freq = random.choices(['1-2 次', '3-5 次', '每天 1 次及以上'], weights=[0.4, 0.4, 0.2])[0]
        else:
            freq = random.choices(['1-2 次', '3-5 次', '每天 1 次及以上'], weights=[0.5, 0.3, 0.2])[0]

        # Q3. 目的/场景 (多选题，随机组合) [cite: 13, 14, 15, 16, 17]
        purposes = ['课间/办公提神', '线下社交/组会讨论', '图书馆/自习室长时间陪伴', '搭配餐食（早餐或下午茶）']
        if identity == '本科生':
            purpose = "、".join(random.sample(purposes, k=random.randint(1, 3)))
        else:
            purpose = "、".join(random.sample(purposes, k=random.randint(1, 2)))

        # Q4. 消费形式 [cite: 18, 19, 20, 21]
        if identity == '校外人员':
            form = random.choices(['堂食（在店内停留使用空间）', '线下自取（点单后步行至店取走）', '外卖配送（送至校门口或宿舍楼）'], weights=[0.6, 0.3, 0.1])[0]
        else:
            form = random.choices(['堂食（在店内停留使用空间）', '线下自取（点单后步行至店取走）', '外卖配送（送至校门口或宿舍楼）'], weights=[0.2, 0.5, 0.3])[0]

        # Q5. 咖啡来源 [cite: 22, 23, 24, 25, 26]
        if identity == '校外人员':
            source = random.choices(['校内经营点（食堂、教学楼内咖啡柜台 / 自动机等）', '校园周边沿街店铺（如枣阳路等步行可达区域）', '附近商圈连锁品牌（如环球港、近铁等）', '仅通过外卖平台跨区域点单（配送距离较远）'], weights=[0.05, 0.35, 0.5, 0.1])[0]
        else:
            source = random.choices(['校内经营点（食堂、教学楼内咖啡柜台 / 自动机等）', '校园周边沿街店铺（如枣阳路等步行可达区域）', '附近商圈连锁品牌（如环球港、近铁等）', '仅通过外卖平台跨区域点单（配送距离较远）'], weights=[0.3, 0.4, 0.2, 0.1])[0]

        # Q6. 每月支出 [cite: 27, 28, 29, 30, 31]
        if identity == '教职工' or identity == '校外人员':
            expense = random.choices(['100 元以下', '100-300 元', '300-500 元', '500 元以上'], weights=[0.1, 0.3, 0.4, 0.2])[0]
        else:
            expense = random.choices(['100 元以下', '100-300 元', '300-500 元', '500 元以上'], weights=[0.3, 0.5, 0.15, 0.05])[0]

        # Q7. 影响因素打分 (1-5分) [cite: 32, 33, 34, 35, 36, 37]
        if identity in ['本科生', '研究生（硕士/博士）']:
            score_price = random.randint(4, 5)   # 学生对价格敏感
            score_dist = random.randint(4, 5)    # 对距离敏感
            score_taste = random.randint(2, 4)
            score_space = random.randint(3, 5)
            score_brand = random.randint(1, 3)
        else:
            score_price = random.randint(2, 4)
            score_dist = random.randint(3, 5)
            score_taste = random.randint(4, 5)   # 校外人员对口味/品牌更看重
            score_space = random.randint(4, 5)
            score_brand = random.randint(3, 5)

        # Q8. 联名活动 [cite: 38, 39, 40, 41, 42]
        collab = random.choices(
            ['只要有我喜欢的 IP，一定会去购买', '会增加好感，但最终仍取决于价格和口味', '仅在有实用赠品（杯垫、贴纸、提袋）时考虑', '基本不关注联名信息，只看产品本身'],
            weights=[0.15, 0.4, 0.25, 0.2]
        )[0]

        # Q9. 心理价位 [cite: 43, 44, 45, 46, 47]
        if identity == '本科生':
            price_limit = random.choices(['10 元以下（极致性价比）', '10-20 元（主流连锁品牌）', '20-30 元（精品店 / 社交空间）', '30 元以上（高端或特调咖啡）'], weights=[0.3, 0.6, 0.1, 0.0])[0]
        else:
            price_limit = random.choices(['10 元以下（极致性价比）', '10-20 元（主流连锁品牌）', '20-30 元（精品店 / 社交空间）', '30 元以上（高端或特调咖啡）'], weights=[0.1, 0.4, 0.4, 0.1])[0]

        # Q10. 商战反应 [cite: 48, 49, 50, 51, 52]
        reaction = random.choices(
            ['极大刺激了消费，会因为领到大额券而特意下单', '有一定影响，领券后会倾向于选择该平台的店铺', '影响很小，只在本来就想喝的时候顺便寻找优惠', '无影响，依然根据个人口味偏好下单'],
            weights=[0.35, 0.45, 0.15, 0.05]
        )[0]

        # Q11. 外卖限制反应 [cite: 53, 54, 55, 56, 57]
        delivery_limit = random.choices(
            ['步行去校门口取餐点自提（为了特定品牌或更低价格）', '支付更高费用选择能送达校内楼栋的特殊配送', '直接购买校内步行最近的咖啡品牌 / 自动机', '放弃本次购买'],
            weights=[0.4, 0.1, 0.3, 0.2]
        )[0]

        # Q12. 学习/工作场所硬件条件 [cite: 58, 59, 60, 61, 62, 63]
        workspace = random.choices(
            ['充足的电源插座', '室内安静程度（背景音乐音量适中）', '桌面高度与椅子舒适度（适合长时间码字）', '室内采光与通风情况', '不在咖啡店学习或工作'],
            weights=[0.3, 0.2, 0.2, 0.1, 0.2]
        )[0]

        # Q13. 营业时间期望 [cite: 64, 65, 66, 67, 68]
        hours = random.choices(
            ['早晨 7:30 前开始营业（满足早八课提神需求）', '晚上 22:00 后继续营业（满足熬夜科研 / 赶 due 需求）', '周末及节假日保持全天候营业', '现有的常规营业时间（如 9:00-21:00）已足够'],
            weights=[0.3, 0.3, 0.1, 0.3]
        )[0]

        # Q14. 促销吸引力 [cite: 69, 70, 71, 72, 73]
        promo = random.choices(
            ['持续的 “开业前三天买一送一”', '针对本校师生持有效证件（学生证 / 教工证）长期打折', '加入该校区专属社群，定期领取大额优惠券', '提供针对校内师生的 “外卖免配送费” 活动'],
            weights=[0.15, 0.45, 0.2, 0.2]
        )[0]

        # Q15. 健康/代餐需求 [cite: 74, 75, 76, 77, 78]
        health = random.choices(
            ['必须有相关选项，且经常购买', '偶尔会尝试，但不是刚需', '基本不关注，只喝常规款咖啡', '完全不需要'],
            weights=[0.15, 0.45, 0.3, 0.1]
        )[0]

        # 开放题建议 (按较小概率生成实质性建议) [cite: 79]
        if random.random() > 0.8:
            suggestion = random.choice(suggestions_pool[3:])
        else:
            suggestion = random.choice(suggestions_pool[:3])

        data.append([
            i+1, identity, freq, purpose, form, source, expense, 
            score_price, score_dist, score_taste, score_space, score_brand,
            collab, price_limit, reaction, delivery_limit, workspace, hours, promo, health, suggestion
        ])

    columns = [
        '序号', '1.身份', '2.饮用频率', '3.主要目的/场景', '4.消费形式', '5.最常购买来源', '6.每月支出',
        '7.影响因素-价格', '7.影响因素-距离', '7.影响因素-口味', '7.影响因素-空间', '7.影响因素-品牌影响力',
        '8.联名活动影响', '9.单杯心理价位', '10.商战/红包反应', '11.外卖无法送入反应', '12.看重的硬性条件',
        '13.期望的营业时间', '14.最吸引的促销方式', '15.健康/代餐需求', '16.其他建议'
    ]
    
    return pd.DataFrame(data, columns=columns)

# 执行生成并导出 CSV
if __name__ == "__main__":
    df_full = generate_full_survey(326)
    df_full.to_csv('ecnu_coffee_full_survey_326.csv', index=False, encoding='utf-8-sig')
    print("成功生成 326 份完整虚拟调研数据，已保存至 ecnu_coffee_full_survey_326.csv！")