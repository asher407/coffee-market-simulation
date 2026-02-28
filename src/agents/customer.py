import math
import json
import random

BRAND_NAME_MAP = {
    'Luckin': '瑞幸咖啡',
    'Starbucks': '星巴克',
    'Nowwa': 'Nowwa 挪瓦咖啡',
    'Manner': 'Manner Coffee',
    'Tims': 'Tims 天好咖啡',
    'Seesaw': 'Seesaw Coffee',
    'MStand': 'M Stand',
    'Arabica': '%ARABICA',
    'PiYe': '皮爷咖啡',
    'BluebottleC': '蓝瓶咖啡',
    'Yongbo': '永璞咖啡'
}

TOP_N_SHOPS = 3

class Customer:
    def __init__(self, profile_data, location=None):
        self.id = profile_data.get('id', random.randint(1000, 9999))
        self.profile = profile_data
        # 假设地图是以华东师范大学为中心的 2000x2000 区域
        self.location = location if location else (random.randint(500, 1500), random.randint(500, 1500))
        
        self.money = float(profile_data.get('income', 6000)) / 30 
        self.preference = profile_data.get('preference', 'Latte')
        self.sensitivity = profile_data.get('price_sensitivity', 'Medium')
        self.preferred_brand = profile_data.get('brand_preference')
        self.brand_loyalty = float(profile_data.get('brand_loyalty', 0.0) or 0.0)
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self):
        distance_pref = ""
        age = self.profile.get('age_group', '')
        occ = self.profile.get('occupation', '')
        if age == '18-24' or occ == 'Student': 
            distance_pref = "你比较懒，超过800米基本不想走，除非有巨额优惠或特色打卡点。"
        elif occ == 'Retired':
            distance_pref = "你时间充裕，把买咖啡当散步，完全不接受外卖，愿意走远路去环境好的店。"
        else:
            distance_pref = "作为打工人，工作日你倾向于就近购买或外卖，非常看重排队时间。"

        brand_name = BRAND_NAME_MAP.get(self.preferred_brand, self.preferred_brand)
        brand_pref_text = ""
        if brand_name:
            brand_pref_text = f"你对{brand_name}有一定偏好，品牌忠诚度约{self.brand_loyalty}。"

        return self.profile.get('persona_description', '') + f"\n{distance_pref}\n{brand_pref_text}"

    def _get_item_and_price(self, menu):
        """核心新增逻辑：根据顾客偏好，从长菜单中挑选商品"""
        if not menu:
            return "默认咖啡", 20.0
            
        # 遍历菜单，寻找最匹配口味的商品
        for item_name, price in menu.items():
            if self.preference == 'Latte' and ('拿铁' in item_name or '奶' in item_name):
                return item_name, float(price)
            if self.preference == 'Americano' and ('美式' in item_name or '清咖' in item_name):
                return item_name, float(price)
            if self.preference == 'Specialty' and ('特调' in item_name or '创意' in item_name):
                return item_name, float(price)
                
        # 如果没找到完全匹配的，选菜单里的第一个商品兜底
        first_item = list(menu.keys())[0]
        return first_item, float(menu[first_item])

    def _calculate_metrics(self, shop):
        dx = self.location[0] - shop['location'][0]
        dy = self.location[1] - shop['location'][1]
        distance = int(math.sqrt(dx**2 + dy**2))
        walk_time = max(1, int(distance / 80)) # 至少需要1分钟
        return {
            "distance": distance,
            "walk_time": walk_time,
            "delivery_time": 30 + int(distance / 500)
        }

    def _calculate_final_price(self, base_price, distance, platform_rules=None):
        if distance > 3000:
            delivery_fee = 999 
            can_deliver = False
        else:
            can_deliver = True
            delivery_fee = 3 + int(distance / 1000)

        discount_tags = []
        pickup_price = base_price
        delivery_price_before_coupon = base_price
        
        # 平台通用满减（自提和外卖都适用）
        if platform_rules:
            if base_price >= platform_rules.get('coupon_threshold', 999):
                subsidy = platform_rules.get('coupon_amount', 0)
                pickup_price -= subsidy
                delivery_price_before_coupon -= subsidy
                discount_tags.append(f"满减-{subsidy}")
        
        # 外卖专属红包（阶梯式，取最大优惠）
        delivery_coupon = 0
        if platform_rules and platform_rules.get('delivery_coupons_enabled', False):
            if delivery_price_before_coupon >= 30:
                delivery_coupon = 10
                discount_tags.append("外卖满30减10")
            elif delivery_price_before_coupon >= 15:
                delivery_coupon = 5
                discount_tags.append("外卖满15减5")
            elif delivery_price_before_coupon >= 10:
                delivery_coupon = 3
                discount_tags.append("外卖满10减3")
        
        # 免运费活动
        if platform_rules and platform_rules.get('free_delivery_campaign', False):
            delivery_fee = 0
            discount_tags.append("免运费")

        # 最终价格计算
        final_delivery_price = delivery_price_before_coupon - delivery_coupon + delivery_fee
        
        return {
            "pickup_price": round(max(0, pickup_price), 1),
            "delivery_price": round(max(0, final_delivery_price), 1),
            "delivery_fee_real": delivery_fee,
            "delivery_coupon": delivery_coupon,
            "can_deliver": can_deliver,
            "discount_tags": ", ".join(discount_tags)
        }

    def _score_shop(self, shop, metrics, item_price):
        """为门店打分，用于Top-N筛选"""
        score = 0.0
        if self.preferred_brand and shop.get('brand_id') == self.preferred_brand:
            score += 60.0 * self.brand_loyalty
        else:
            score += 5.0 * (1.0 - self.brand_loyalty)

        score += max(0.0, 30.0 - metrics['distance'] / 100.0)
        score += max(0.0, 12.0 - float(shop.get('queue_time', 0)))
        score += max(0.0, 20.0 - float(item_price))
        return round(score, 2)

    def generate_decision_prompt(self, shops, platform_rules=None):
        options_str = ""
        scored_shops = []

        for shop in shops:
            metrics = self._calculate_metrics(shop)
            item_name, item_price = self._get_item_and_price(shop['menu'])
            prices = self._calculate_final_price(item_price, metrics['distance'], platform_rules)
            score = self._score_shop(shop, metrics, item_price)
            scored_shops.append((score, shop, metrics, item_name, item_price, prices))

        scored_shops.sort(key=lambda x: x[0], reverse=True)
        top_shops = scored_shops[:min(TOP_N_SHOPS, len(scored_shops))]

        for score, shop, metrics, item_name, item_price, prices in top_shops:
            promo_text = f"(当前优惠: {prices['discount_tags']})" if prices['discount_tags'] else ""

            if metrics['distance'] <= 2500:
                options_str += (
                    f"【选项 {shop['id']}_Walk】步行去 {shop['brand_name']} ({shop['category']})\n"
                    f"   - 品牌调性: {shop['business_model']}\n"
                    f"   - 常驻活动: {shop['promotions']}\n"
                    f"   - 推荐商品: {item_name} (原价: {item_price}元, 叠加平台优惠后到手估算: {prices['pickup_price']}元)\n"
                    f"   - 物理距离: {metrics['distance']}米 (需步行约 {metrics['walk_time']} 分钟) | 排队: 约 {shop['queue_time']} 分钟\n"
                    f"   - 综合评分: {score}\n\n"
                )

            if prices['can_deliver'] and shop.get('supports_delivery', True):
                coupon_info = f", 已减红包 {prices['delivery_coupon']}元" if prices.get('delivery_coupon', 0) > 0 else ""
                options_str += (
                    f"【选项 {shop['id']}_Delivery】点 {shop['brand_name']} (外卖) {promo_text}\n"
                    f"   - 推荐商品: {item_name} (原价: {item_price}元, 外卖到手总价: {prices['delivery_price']}元, 含运费 {prices['delivery_fee_real']}元{coupon_info})\n"
                    f"   - 预估等待: {metrics['delivery_time']} 分钟\n"
                    f"   - 综合评分: {score}\n\n"
                )

        options_str += "【选项 None】不买了 (原因：都不想喝、嫌贵或太远)\n"

        event_notice = f"!!! 注意：现在是【{platform_rules['event_name']}】活动期间 !!!\n" if platform_rules and platform_rules.get('event_name') else ""

        brand_name = BRAND_NAME_MAP.get(self.preferred_brand, self.preferred_brand)
        brand_pref_notice = ""
        if brand_name:
            brand_pref_notice = f"你对{brand_name}有明显偏好，请优先考虑该品牌。\n"

        user_prompt = (
            f"{event_notice}"
            f"你当前在地图上的坐标是: {self.location}。\n"
            f"系统已根据【品牌偏好/距离/排队/价格】进行初筛，仅展示Top {TOP_N_SHOPS} 个候选。\n"
            f"{brand_pref_notice}"
            f"根据你的位置，你眼前的咖啡消费方案如下：\n\n{options_str}\n"
            f"【决策任务】\n"
            f"请综合考虑你的【消费水平】、【口味偏好】、【步行意愿】以及商家的【品牌调性】做出最符合你人设的选择。\n"
            f"请严格返回 JSON 格式数据，包含以下字段：\n"
            f"{{\n"
            f"  \"decision\": \"选中的选项ID (如 Shop_1_Walk, Shop_2_Delivery 或 None)\",\n"
            f"  \"brand\": \"购买的品牌名称 (如果不买，请填 null)\",\n"
            f"  \"method\": \"购买方式，填 '自提' 或 '外卖' (如果不买，请填 null)\",\n"
            f"  \"item\": \"购买的具体单品名称 (如果不买，请填 null)\",\n"
            f"  \"price\": 最终需要支付的金额数字 (如果不买，请填 0),\n"
            f"  \"reason\": \"你的理由 (请用简体中文，限制在15个字以内，必须符合你的人设)\"\n"
            f"}}"
        )
        return user_prompt