#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
☕ 咖啡市场仿真 - 数据分析模块

功能：
  1. 品牌销售分析 (销售量、销售额、市场份额)
  2. 消费者分层分析 (按年龄、职业、收入、偏好)
  3. 购买方式分析 (外卖vs自提占比)
  4. 价格敏感性分析
  5. 购买理由分析
"""

import os
import sys
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path


class CoffeeMarketAnalyzer:
    """咖啡市场数据分析器"""
    
    def __init__(self, csv_path):
        """
        初始化分析器
        
        Args:
            csv_path (str): 仿真结果 CSV 文件路径
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"结果文件不存在: {csv_path}")
        
        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path, encoding='utf-8')
        self.total_customers = len(self.df)
        self.total_sales = self.df['price'].sum()
        
        print(f"✅ 已加载仿真数据: {self.total_customers} 名顾客, 总销售额: ¥{self.total_sales:.2f}")
    
    # ========================================================================
    # 🏪 品牌销售分析
    # ========================================================================
    
    def brand_sales_analysis(self):
        """
        品牌销售统计分析
        
        Returns:
            dict: 包含销售量、销售额、市场份额等信息
        """
        brand_stats = {
            'brand': [],
            'quantity': [],
            'revenue': [],
            'avg_price': [],
            'market_share': []
        }
        
        for brand in self.df['brand'].unique():
            brand_data = self.df[self.df['brand'] == brand]
            quantity = len(brand_data)
            revenue = brand_data['price'].sum()
            avg_price = revenue / quantity if quantity > 0 else 0
            market_share = (revenue / self.total_sales * 100) if self.total_sales > 0 else 0
            
            brand_stats['brand'].append(brand)
            brand_stats['quantity'].append(quantity)
            brand_stats['revenue'].append(revenue)
            brand_stats['avg_price'].append(avg_price)
            brand_stats['market_share'].append(market_share)
        
        result_df = pd.DataFrame(brand_stats)
        result_df = result_df.sort_values('revenue', ascending=False)
        result_df['quantity_share'] = (result_df['quantity'] / self.total_customers * 100).round(2)
        
        return result_df
    
    # ========================================================================
    # 👥 消费者分层分析
    # ========================================================================
    
    def age_group_analysis(self):
        """按年龄段分析购买行为"""
        age_stats = []
        
        for age_group in self.df['age_group'].unique():
            group_data = self.df[self.df['age_group'] == age_group]
            
            # 购买量和金额
            purchases = len(group_data)
            total_spend = group_data['price'].sum()
            avg_spend = total_spend / purchases if purchases > 0 else 0
            
            # 偏好品牌（TOP 3）
            top_brands = group_data['brand'].value_counts().head(3)
            
            # 购买方式占比
            delivery_ratio = (group_data['method'] == '外卖').sum() / purchases * 100 if purchases > 0 else 0
            
            # 价格敏感度分布
            price_sensitivity = group_data['price_sensitivity'].value_counts().to_dict()
            
            top_brands_str = ', '.join([f"{b}({c})" for b, c in zip(top_brands.index, top_brands.values)])
            
            age_stats.append({
                'age_group': age_group,
                'total_customers': len(group_data['customer_id'].unique()),
                'total_purchases': purchases,
                'total_spend': round(total_spend, 2),
                'avg_spend': round(avg_spend, 2),
                'top_brands': top_brands_str,
                'delivery_ratio': round(delivery_ratio, 2),
                'price_sensitivity_dist': price_sensitivity
            })
        
        result_df = pd.DataFrame(age_stats).sort_values('total_spend', ascending=False)
        return result_df
    
    def occupation_analysis(self):
        """按职业分析购买行为"""
        occ_stats = []
        
        for occupation in self.df['occupation'].unique():
            occ_data = self.df[self.df['occupation'] == occupation]
            
            purchases = len(occ_data)
            total_spend = occ_data['price'].sum()
            avg_spend = total_spend / purchases if purchases > 0 else 0
            
            # 偏好品牌
            top_brands = occ_data['brand'].value_counts().head(3)
            
            # 购买方式占比
            delivery_ratio = (occ_data['method'] == '外卖').sum() / purchases * 100 if purchases > 0 else 0
            
            top_brands_str = ', '.join([f"{b}({c})" for b, c in zip(top_brands.index, top_brands.values)])
            
            occ_stats.append({
                'occupation': occupation,
                'total_customers': len(occ_data['customer_id'].unique()),
                'total_purchases': purchases,
                'total_spend': round(total_spend, 2),
                'avg_spend': round(avg_spend, 2),
                'top_brands': top_brands_str,
                'delivery_ratio': round(delivery_ratio, 2)
            })
        
        result_df = pd.DataFrame(occ_stats).sort_values('total_spend', ascending=False)
        return result_df
    
    def income_segment_analysis(self):
        """按收入分层分析购买行为"""
        # 按收入分段
        self.df['income_segment'] = pd.cut(
            self.df['income'],
            bins=[0, 8000, 15000, 25000, 100000],
            labels=['低收入(0-8K)', '中低收入(8-15K)', '中高收入(15-25K)', '高收入(25K+)']
        )
        
        income_stats = []
        
        for segment in ['低收入(0-8K)', '中低收入(8-15K)', '中高收入(15-25K)', '高收入(25K+)']:
            seg_data = self.df[self.df['income_segment'] == segment]
            
            if len(seg_data) == 0:
                continue
            
            purchases = len(seg_data)
            total_spend = seg_data['price'].sum()
            avg_spend = total_spend / purchases if purchases > 0 else 0
            
            # 偏好品牌
            top_brands = seg_data['brand'].value_counts().head(3)
            
            # 购买方式占比
            delivery_ratio = (seg_data['method'] == '外卖').sum() / purchases * 100 if purchases > 0 else 0
            
            # 平均收入
            avg_income = seg_data['income'].mean()
            
            top_brands_str = ', '.join([f"{b}({c})" for b, c in zip(top_brands.index, top_brands.values)])
            
            income_stats.append({
                'income_segment': segment,
                'avg_income': round(avg_income, 2),
                'total_customers': len(seg_data['customer_id'].unique()),
                'total_purchases': purchases,
                'total_spend': round(total_spend, 2),
                'avg_spend': round(avg_spend, 2),
                'top_brands': top_brands_str,
                'delivery_ratio': round(delivery_ratio, 2)
            })
        
        result_df = pd.DataFrame(income_stats)
        
        # 清理临时列
        self.df.drop('income_segment', axis=1, inplace=True)
        
        return result_df
    
    def preference_analysis(self):
        """按咖啡偏好分析购买行为"""
        pref_stats = []
        
        for preference in self.df['preference'].unique():
            pref_data = self.df[self.df['preference'] == preference]
            
            purchases = len(pref_data)
            total_spend = pref_data['price'].sum()
            avg_spend = total_spend / purchases if purchases > 0 else 0
            
            # 实际购买品牌
            top_brands = pref_data['brand'].value_counts().head(3)
            
            # 购买方式占比
            delivery_ratio = (pref_data['method'] == '外卖').sum() / purchases * 100 if purchases > 0 else 0
            
            top_brands_str = ', '.join([f"{b}({c})" for b, c in zip(top_brands.index, top_brands.values)])
            
            pref_stats.append({
                'preference': preference,
                'total_purchases': purchases,
                'total_spend': round(total_spend, 2),
                'avg_spend': round(avg_spend, 2),
                'top_brands': top_brands_str,
                'delivery_ratio': round(delivery_ratio, 2)
            })
        
        result_df = pd.DataFrame(pref_stats).sort_values('total_spend', ascending=False)
        return result_df
    
    # ========================================================================
    # 🚗 购买方式分析
    # ========================================================================
    
    def delivery_method_analysis(self):
        """外卖 vs 自提 购买方式分析"""
        method_counts = self.df['method'].value_counts()
        method_revenue = self.df.groupby('method')['price'].sum()
        method_avg_price = self.df.groupby('method')['price'].mean()
        
        method_stats = {
            'method': [],
            'quantity': [],
            'quantity_ratio': [],
            'revenue': [],
            'revenue_ratio': [],
            'avg_price': []
        }
        
        for method in method_counts.index:
            quantity = method_counts[method]
            revenue = method_revenue[method]
            
            method_stats['method'].append(method)
            method_stats['quantity'].append(quantity)
            method_stats['quantity_ratio'].append(round(quantity / self.total_customers * 100, 2))
            method_stats['revenue'].append(round(revenue, 2))
            method_stats['revenue_ratio'].append(round(revenue / self.total_sales * 100, 2))
            method_stats['avg_price'].append(round(method_avg_price[method], 2))
        
        result_df = pd.DataFrame(method_stats)
        return result_df
    
    def delivery_method_by_group(self):
        """各人群的购买方式偏好"""
        method_by_age = []
        
        for age_group in sorted(self.df['age_group'].unique()):
            age_data = self.df[self.df['age_group'] == age_group]
            
            total = len(age_data)
            delivery = (age_data['method'] == '外卖').sum()
            pickup = (age_data['method'] == '自提').sum()
            
            method_by_age.append({
                'age_group': age_group,
                'delivery_count': delivery,
                'delivery_ratio': round(delivery / total * 100, 2),
                'pickup_count': pickup,
                'pickup_ratio': round(pickup / total * 100, 2)
            })
        
        result_df = pd.DataFrame(method_by_age)
        return result_df
    
    # ========================================================================
    # 💰 价格敏感性分析
    # ========================================================================
    
    def price_sensitivity_analysis(self):
        """价格敏感度与消费行为的关系"""
        ps_stats = []
        
        for sensitivity in self.df['price_sensitivity'].unique():
            ps_data = self.df[self.df['price_sensitivity'] == sensitivity]
            
            purchases = len(ps_data)
            total_spend = ps_data['price'].sum()
            avg_spend = total_spend / purchases if purchases > 0 else 0
            
            # 购买方式占比
            delivery_ratio = (ps_data['method'] == '外卖').sum() / purchases * 100 if purchases > 0 else 0
            
            # 价格分布
            price_min = ps_data['price'].min()
            price_max = ps_data['price'].max()
            price_median = ps_data['price'].median()
            
            ps_stats.append({
                'price_sensitivity': sensitivity,
                'total_purchases': purchases,
                'total_spend': round(total_spend, 2),
                'avg_spend': round(avg_spend, 2),
                'price_min': round(price_min, 2),
                'price_max': round(price_max, 2),
                'price_median': round(price_median, 2),
                'delivery_ratio': round(delivery_ratio, 2)
            })
        
        result_df = pd.DataFrame(ps_stats)
        # 按敏感度排序
        sensitivity_order = {'Low': 1, 'Medium': 2, 'High': 3}
        result_df['order'] = result_df['price_sensitivity'].map(sensitivity_order)
        result_df = result_df.sort_values('order').drop('order', axis=1)
        
        return result_df
    
    # ========================================================================
    # 📋 决策理由分析
    # ========================================================================
    
    def reason_analysis(self):
        """购买决策理由分析"""
        # 提取关键词
        reasons = self.df['reason'].str.split('，|、', expand=True).stack().reset_index(drop=True)
        reason_counts = reasons.value_counts().head(15)
        
        reason_stats = {
            'reason': [],
            'count': [],
            'percentage': []
        }
        
        for reason, count in reason_counts.items():
            reason = reason.strip()
            reason_stats['reason'].append(reason)
            reason_stats['count'].append(count)
            reason_stats['percentage'].append(round(count / len(self.df) * 100, 2))
        
        result_df = pd.DataFrame(reason_stats)
        return result_df
    
    # ========================================================================
    # 📊 综合报告生成
    # ========================================================================
    
    def generate_comprehensive_report(self, output_dir=None):
        """
        生成综合分析报告
        
        Args:
            output_dir (str): 输出目录，默认为 data/output
        """
        if output_dir is None:
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(self.csv_path))),
                'output'
            )
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 时间戳
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("\n" + "="*80)
        print("📊 生成分析报告...")
        print("="*80)
        
        # 1. 品牌销售分析
        print("\n🏪 品牌销售分析...")
        brand_df = self.brand_sales_analysis()
        brand_file = os.path.join(output_dir, f"analysis_brand_sales_{timestamp}.csv")
        brand_df.to_csv(brand_file, index=False, encoding='utf-8')
        print(f"   ✅ 已保存: {brand_file}")
        print(brand_df.to_string(index=False))
        
        # 2. 年龄段分析
        print("\n👤 年龄段分析...")
        age_df = self.age_group_analysis()
        age_file = os.path.join(output_dir, f"analysis_age_group_{timestamp}.csv")
        age_df.to_csv(age_file, index=False, encoding='utf-8')
        print(f"   ✅ 已保存: {age_file}")
        print(age_df[['age_group', 'total_purchases', 'total_spend', 'avg_spend', 'delivery_ratio']].to_string(index=False))
        
        # 3. 职业分析
        print("\n💼 职业分析...")
        occ_df = self.occupation_analysis()
        occ_file = os.path.join(output_dir, f"analysis_occupation_{timestamp}.csv")
        occ_df.to_csv(occ_file, index=False, encoding='utf-8')
        print(f"   ✅ 已保存: {occ_file}")
        print(occ_df[['occupation', 'total_purchases', 'total_spend', 'avg_spend', 'delivery_ratio']].to_string(index=False))
        
        # 4. 收入分层分析
        print("\n💰 收入分层分析...")
        income_df = self.income_segment_analysis()
        income_file = os.path.join(output_dir, f"analysis_income_segment_{timestamp}.csv")
        income_df.to_csv(income_file, index=False, encoding='utf-8')
        print(f"   ✅ 已保存: {income_file}")
        print(income_df[['income_segment', 'total_purchases', 'total_spend', 'avg_spend', 'delivery_ratio']].to_string(index=False))
        
        # 5. 咖啡偏好分析
        print("\n☕ 咖啡偏好分析...")
        pref_df = self.preference_analysis()
        pref_file = os.path.join(output_dir, f"analysis_preference_{timestamp}.csv")
        pref_df.to_csv(pref_file, index=False, encoding='utf-8')
        print(f"   ✅ 已保存: {pref_file}")
        print(pref_df.to_string(index=False))
        
        # 6. 购买方式分析
        print("\n🚗 购买方式分析...")
        method_df = self.delivery_method_analysis()
        method_file = os.path.join(output_dir, f"analysis_delivery_method_{timestamp}.csv")
        method_df.to_csv(method_file, index=False, encoding='utf-8')
        print(f"   ✅ 已保存: {method_file}")
        print(method_df.to_string(index=False))
        
        # 7. 购买方式分群分析
        print("\n🚗 各年龄段购买方式占比...")
        method_group_df = self.delivery_method_by_group()
        method_group_file = os.path.join(output_dir, f"analysis_delivery_by_age_{timestamp}.csv")
        method_group_df.to_csv(method_group_file, index=False, encoding='utf-8')
        print(f"   ✅ 已保存: {method_group_file}")
        print(method_group_df.to_string(index=False))
        
        # 8. 价格敏感性分析
        print("\n💵 价格敏感性分析...")
        ps_df = self.price_sensitivity_analysis()
        ps_file = os.path.join(output_dir, f"analysis_price_sensitivity_{timestamp}.csv")
        ps_df.to_csv(ps_file, index=False, encoding='utf-8')
        print(f"   ✅ 已保存: {ps_file}")
        print(ps_df.to_string(index=False))
        
        # 9. 决策理由分析
        print("\n📋 购买决策理由TOP 15...")
        reason_df = self.reason_analysis()
        reason_file = os.path.join(output_dir, f"analysis_reasons_{timestamp}.csv")
        reason_df.to_csv(reason_file, index=False, encoding='utf-8')
        print(f"   ✅ 已保存: {reason_file}")
        print(reason_df.to_string(index=False))
        
        # 10. 综合统计摘要
        print("\n📈 综合统计摘要...")
        summary_stats = {
            '指标': [
                '总顾客数',
                '总购买笔数',
                '总销售额',
                '平均单笔金额',
                '外卖占比',
                '自提占比',
                '品牌数量',
                '最热门品牌',
                '最热门品牌销售额',
            ],
            '数值': [
                self.total_customers,
                len(self.df),
                f"¥{self.total_sales:.2f}",
                f"¥{self.df['price'].mean():.2f}",
                f"{(self.df['method'] == '外卖').sum() / len(self.df) * 100:.2f}%",
                f"{(self.df['method'] == '自提').sum() / len(self.df) * 100:.2f}%",
                self.df['brand'].nunique(),
                brand_df.iloc[0]['brand'],
                f"¥{brand_df.iloc[0]['revenue']:.2f}",
            ]
        }
        summary_df = pd.DataFrame(summary_stats)
        summary_file = os.path.join(output_dir, f"analysis_summary_{timestamp}.csv")
        summary_df.to_csv(summary_file, index=False, encoding='utf-8')
        print(f"   ✅ 已保存: {summary_file}")
        print(summary_df.to_string(index=False))
        
        print("\n" + "="*80)
        print(f"✨ 所有分析报告已保存到: {output_dir}")
        print("="*80 + "\n")
        
        return {
            'brand': brand_df,
            'age_group': age_df,
            'occupation': occ_df,
            'income_segment': income_df,
            'preference': pref_df,
            'delivery_method': method_df,
            'delivery_by_age': method_group_df,
            'price_sensitivity': ps_df,
            'reasons': reason_df,
            'summary': summary_df
        }


if __name__ == '__main__':
    # 示例：分析最新的仿真结果
    import glob
    
    # 自动查找最新的仿真结果文件
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'data', 'output'
    )
    csv_files = glob.glob(os.path.join(output_dir, 'simulation_results_*.csv'))
    
    if not csv_files:
        print("❌ 未找到仿真结果文件，请先运行: python main.py --mode test")
        sys.exit(1)
    
    latest_csv = max(csv_files, key=os.path.getctime)
    print(f"📊 分析最新结果: {latest_csv}")
    
    analyzer = CoffeeMarketAnalyzer(latest_csv)
    analyzer.generate_comprehensive_report()
