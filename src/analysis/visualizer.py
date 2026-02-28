#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
☕ 咖啡市场仿真 - 可视化模块

功能：
  1. 品牌销售对比柱状图
  2. 市场份额分布饼图
  3. 年龄段消费趋势折线图
  4. 购买方式占比图表
  5. 价格敏感性分析图
  6. 热力图（地理分布）
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams
from .analytics import CoffeeMarketAnalyzer


# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False
rcParams['figure.figsize'] = (12, 6)


class CoffeeMarketVisualizer:
    """咖啡市场数据可视化工具"""
    
    def __init__(self, analyzer):
        """
        初始化可视化工具
        
        Args:
            analyzer (CoffeeMarketAnalyzer): 数据分析器实例
        """
        self.analyzer = analyzer
        self.output_dir = os.path.dirname(analyzer.csv_path)
    
    def plot_brand_sales_bar(self, top_n=10, save=True):
        """
        品牌销售对比柱状图
        
        Args:
            top_n (int): 显示前N个品牌
            save (bool): 是否保存图片
        """
        brand_df = self.analyzer.brand_sales_analysis()
        top_brands = brand_df.head(top_n)
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # 双坐标轴：左侧是销售额，右侧是销售量
        ax1 = ax
        ax2 = ax1.twinx()
        
        x = range(len(top_brands))
        bars1 = ax1.bar([i - 0.2 for i in x], top_brands['revenue'], width=0.4, 
                        label='销售额', color='#FF6B6B', alpha=0.8)
        bars2 = ax2.bar([i + 0.2 for i in x], top_brands['quantity'], width=0.4,
                        label='销售量', color='#4ECDC4', alpha=0.8)
        
        ax1.set_xlabel('品牌', fontsize=12, fontweight='bold')
        ax1.set_ylabel('销售额 (¥)', fontsize=12, fontweight='bold', color='#FF6B6B')
        ax2.set_ylabel('销售量 (笔)', fontsize=12, fontweight='bold', color='#4ECDC4')
        ax1.set_title('☕ 咖啡品牌销售对比 (TOP 10)', fontsize=14, fontweight='bold', pad=20)
        
        ax1.set_xticks(x)
        ax1.set_xticklabels(top_brands['brand'], rotation=45, ha='right')
        
        ax1.tick_params(axis='y', labelcolor='#FF6B6B')
        ax2.tick_params(axis='y', labelcolor='#4ECDC4')
        
        # 添加数值标签
        for i, (revenue, quantity) in enumerate(zip(top_brands['revenue'], top_brands['quantity'])):
            ax1.text(i - 0.2, revenue, f'¥{revenue:.0f}', ha='center', va='bottom', fontsize=9)
            ax2.text(i + 0.2, quantity, f'{quantity}', ha='center', va='bottom', fontsize=9)
        
        fig.legend([bars1, bars2], ['销售额', '销售量'], loc='upper right', fontsize=10)
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, 'chart_brand_sales.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"✅ 品牌销售图已保存: {filepath}")
        
        plt.show()
    
    def plot_market_share_pie(self, top_n=8, save=True):
        """
        市场份额分布饼图
        
        Args:
            top_n (int): 显示前N个品牌，其余归为"其他"
            save (bool): 是否保存图片
        """
        brand_df = self.analyzer.brand_sales_analysis()
        
        if len(brand_df) > top_n:
            top_brands = brand_df.head(top_n)
            other_revenue = brand_df.iloc[top_n:]['revenue'].sum()
            
            pie_data = list(top_brands['revenue']) + [other_revenue]
            pie_labels = list(top_brands['brand']) + ['其他']
        else:
            pie_data = brand_df['revenue']
            pie_labels = brand_df['brand']
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        colors = plt.cm.Set3(range(len(pie_data)))
        wedges, texts, autotexts = ax.pie(
            pie_data,
            labels=pie_labels,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 11}
        )
        
        # 美化文字
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        ax.set_title('☕ 咖啡品牌市场份额分布', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, 'chart_market_share.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"✅ 市场份额图已保存: {filepath}")
        
        plt.show()
    
    def plot_age_group_spending(self, save=True):
        """
        年龄段消费趋势折线图
        
        Args:
            save (bool): 是否保存图片
        """
        age_df = self.analyzer.age_group_analysis()
        
        # 按年龄排序
        age_order = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+']
        age_df['age_group'] = pd.Categorical(age_df['age_group'], categories=age_order, ordered=True)
        age_df = age_df.sort_values('age_group')
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 左图：总消费额趋势
        ax1.plot(age_df['age_group'], age_df['total_spend'], marker='o', linewidth=2.5,
                markersize=8, color='#FF6B6B', label='总消费额')
        ax1.fill_between(range(len(age_df)), age_df['total_spend'], alpha=0.3, color='#FF6B6B')
        ax1.set_xlabel('年龄段', fontsize=12, fontweight='bold')
        ax1.set_ylabel('总消费额 (¥)', fontsize=12, fontweight='bold')
        ax1.set_title('📊 不同年龄段的总消费额趋势', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 添加数值标签
        for x, y in enumerate(age_df['total_spend']):
            ax1.text(x, y, f'¥{y:.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 右图：人均消费额对比
        ax2.bar(age_df['age_group'], age_df['avg_spend'], color='#4ECDC4', alpha=0.8)
        ax2.set_xlabel('年龄段', fontsize=12, fontweight='bold')
        ax2.set_ylabel('人均消费额 (¥)', fontsize=12, fontweight='bold')
        ax2.set_title('💰 不同年龄段的人均消费额', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标签
        for x, y in enumerate(age_df['avg_spend']):
            ax2.text(x, y, f'¥{y:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, 'chart_age_spending.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"✅ 年龄段消费图已保存: {filepath}")
        
        plt.show()
    
    def plot_delivery_method(self, save=True):
        """
        购买方式占比图
        
        Args:
            save (bool): 是否保存图片
        """
        method_df = self.analyzer.delivery_method_analysis()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 左图：购买量占比
        colors = ['#FF6B6B', '#4ECDC4']
        wedges, texts, autotexts = ax1.pie(
            method_df['quantity'],
            labels=method_df['method'],
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 12, 'fontweight': 'bold'}
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax1.set_title('🚗 购买方式分布 (按购买笔数)', fontsize=13, fontweight='bold')
        
        # 右图：购买额占比
        wedges2, texts2, autotexts2 = ax2.pie(
            method_df['revenue'],
            labels=method_df['method'],
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 12, 'fontweight': 'bold'}
        )
        
        for autotext in autotexts2:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax2.set_title('💰 购买方式分布 (按消费金额)', fontsize=13, fontweight='bold')
        
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, 'chart_delivery_method.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"✅ 购买方式图已保存: {filepath}")
        
        plt.show()
    
    def plot_price_sensitivity(self, save=True):
        """
        价格敏感性分析图
        
        Args:
            save (bool): 是否保存图片
        """
        ps_df = self.analyzer.price_sensitivity_analysis()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 左图：人均消费额对比
        colors_ps = ['#90EE90', '#FFD700', '#FF6B6B']
        bars = ax1.bar(ps_df['price_sensitivity'], ps_df['avg_spend'], color=colors_ps, alpha=0.8)
        ax1.set_xlabel('价格敏感度', fontsize=12, fontweight='bold')
        ax1.set_ylabel('人均消费额 (¥)', fontsize=12, fontweight='bold')
        ax1.set_title('💵 价格敏感度与消费金额的关系', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'¥{height:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # 右图：价格范围对比
        x = range(len(ps_df))
        width = 0.25
        
        ax2.bar([i - width for i in x], ps_df['price_min'], width=width, label='最低价', color='#90EE90', alpha=0.8)
        ax2.bar(x, ps_df['price_median'], width=width, label='中位价', color='#FFD700', alpha=0.8)
        ax2.bar([i + width for i in x], ps_df['price_max'], width=width, label='最高价', color='#FF6B6B', alpha=0.8)
        
        ax2.set_xlabel('价格敏感度', fontsize=12, fontweight='bold')
        ax2.set_ylabel('价格 (¥)', fontsize=12, fontweight='bold')
        ax2.set_title('🎯 不同敏感度群体的价格范围', fontsize=13, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(ps_df['price_sensitivity'])
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, 'chart_price_sensitivity.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"✅ 价格敏感性图已保存: {filepath}")
        
        plt.show()
    
    def plot_occupation_spending(self, save=True):
        """
        职业类别消费对比图
        
        Args:
            save (bool): 是否保存图片
        """
        occ_df = self.analyzer.occupation_analysis()
        occ_df = occ_df.sort_values('total_spend', ascending=True)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        bars = ax.barh(occ_df['occupation'], occ_df['total_spend'], color='#95B8D1', alpha=0.8)
        
        ax.set_xlabel('总消费额 (¥)', fontsize=12, fontweight='bold')
        ax.set_ylabel('职业类别', fontsize=12, fontweight='bold')
        ax.set_title('💼 不同职业的消费规模', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        # 添加数值标签和购买笔数
        for i, (bar, spend, count) in enumerate(zip(bars, occ_df['total_spend'], occ_df['total_purchases'])):
            ax.text(spend, i, f' ¥{spend:.0f} ({count}笔)', va='center', fontweight='bold', fontsize=10)
        
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, 'chart_occupation_spending.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"✅ 职业消费图已保存: {filepath}")
        
        plt.show()
    
    def plot_all_charts(self):
        """生成所有图表"""
        print("\n" + "="*80)
        print("📊 生成所有可视化图表...")
        print("="*80 + "\n")
        
        try:
            print("1️⃣  生成品牌销售对比柱状图...")
            self.plot_brand_sales_bar()
        except Exception as e:
            print(f"   ⚠️  柱状图生成失败: {e}")
        
        try:
            print("2️⃣  生成市场份额分布饼图...")
            self.plot_market_share_pie()
        except Exception as e:
            print(f"   ⚠️  饼图生成失败: {e}")
        
        try:
            print("3️⃣  生成年龄段消费趋势图...")
            self.plot_age_group_spending()
        except Exception as e:
            print(f"   ⚠️  趋势图生成失败: {e}")
        
        try:
            print("4️⃣  生成购买方式占比图...")
            self.plot_delivery_method()
        except Exception as e:
            print(f"   ⚠️  方式占比图生成失败: {e}")
        
        try:
            print("5️⃣  生成价格敏感性分析图...")
            self.plot_price_sensitivity()
        except Exception as e:
            print(f"   ⚠️  敏感性图生成失败: {e}")
        
        try:
            print("6️⃣  生成职业消费对比图...")
            self.plot_occupation_spending()
        except Exception as e:
            print(f"   ⚠️  职业对比图生成失败: {e}")
        
        print("\n" + "="*80)
        print("✨ 所有图表生成完成！")
        print("="*80 + "\n")


if __name__ == '__main__':
    import glob
    import sys
    
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
    visualizer = CoffeeMarketVisualizer(analyzer)
    visualizer.plot_all_charts()
