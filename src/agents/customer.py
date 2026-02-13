import math
import json
import random

class Customer:
    def __init__(self, profile_data, location=None):
        self.id = profile_data.get('id', random.randint(1000, 9999))
        self.profile = profile_data
        # 假设地图是以华东师范大学为中心的 2000x2000 区域
        self.location = location if location else (random.randint(500, 1500), random.randint(500, 1500))
        
        self.money = float(profile_data.get('income', 6000)) / 30 
        self.preference = profile_data.get('preference', 'Latte')
        self.sensitivity = profile_data.get('price_sensitivity', 'Medium')
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

        return self.profile.get('persona_description', '') + f"\n{distance_pref}"

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
        if platform_rules:
            if platform_rules.get('free_delivery_campaign', False):
                delivery_fee = 0
                discount_tags.append("免运费")
            if base_price >= platform_rules.get('coupon_threshold', 999):
                subsidy = platform_rules.get('coupon_amount', 0)
                base_price -= subsidy
                discount_tags.append(f"满减-{subsidy}")

        return {
            "pickup_price": round(max(0, base_price), 1),
            "delivery_price": round(max(0, base_price + delivery_fee), 1),
            "delivery_fee_real": delivery_fee,
            "can_deliver": can_deliver,
            "discount_tags": ", ".join(discount_tags)
        }

    def generate_decision_prompt(self, shops, platform_rules=None):
        options_str = ""
        
        for shop in shops:
            metrics = self._calculate_metrics(shop)
            # 根据偏好挑选商品
            item_name, item_price = self._get_item_and_price(shop['menu'])
            # 计算最终价格
            prices = self._calculate_final_price(item_price, metrics['distance'], platform_rules)
            promo_text = f"(当前优惠: {prices['discount_tags']})" if prices['discount_tags'] else ""

            # 选项 A: 步行自提
            if metrics['distance'] <= 2500:
                options_str += (
                    f"【选项 {shop['id']}_Walk】步行去 {shop['brand_name']} ({shop['category']})\n"
                    f"   - 品牌调性: {shop['business_model']}\n"
                    f"   - 常驻活动: {shop['promotions']}\n"
                    f"   - 推荐商品: {item_name} (原价: {item_price}元, 叠加平台优惠后到手估算: {prices['pickup_price']}元)\n"
                    f"   - 物理距离: {metrics['distance']}米 (需步行约 {metrics['walk_time']} 分钟) | 排队: 约 {shop['queue_time']} 分钟\n\n"
                )

            # 选项 B: 外卖配送
            if prices['can_deliver'] and shop.get('supports_delivery', True):
                options_str += (
                    f"【选项 {shop['id']}_Delivery】点 {shop['brand_name']} (外卖) {promo_text}\n"
                    f"   - 推荐商品: {item_name} (原价: {item_price}元, 外卖到手总价: {prices['delivery_price']}元, 含运费 {prices['delivery_fee_real']}元)\n"
                    f"   - 预估等待: {metrics['delivery_time']} 分钟\n\n"
                )

        options_str += "【选项 None】不买了 (原因：都不想喝、嫌贵或太远)\n"

        event_notice = f"!!! 注意：现在是【{platform_rules['event_name']}】活动期间 !!!\n" if platform_rules and platform_rules.get('event_name') else ""

        user_prompt = (
            f"{event_notice}"
            f"你当前在地图上的坐标是: {self.location}。\n"
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