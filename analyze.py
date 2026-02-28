#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
☕ 咖啡市场仿真 - 数据分析入口

这是一个统一的分析脚本，可以：
1. 对最新的仿真结果进行全面数据分析
2. 生成多维度的统计报告
3. 创建各类可视化图表

使用方式：
  python analyze.py                  # 分析最新的仿真结果
  python analyze.py --file <path>    # 分析指定的结果文件
  python analyze.py --charts         # 仅生成图表
  python analyze.py --report         # 仅生成报告
"""

import os
import sys
import argparse
import glob
from datetime import datetime
from pathlib import Path

# 修复 Windows 编码问题
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根路径到 sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.analysis.analytics import CoffeeMarketAnalyzer
from src.analysis.visualizer import CoffeeMarketVisualizer


def find_latest_result():
    """查找最新的仿真结果文件"""
    output_dir = os.path.join(project_root, 'data', 'output')
    
    if not os.path.exists(output_dir):
        return None
    
    csv_files = glob.glob(os.path.join(output_dir, 'simulation_results_*.csv'))
    
    if not csv_files:
        return None
    
    # 按修改时间排序，返回最新的
    latest_csv = max(csv_files, key=os.path.getctime)
    return latest_csv


def main():
    parser = argparse.ArgumentParser(
        description='☕ 咖啡市场仿真数据分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python analyze.py                  # 分析最新结果，生成报告和图表
  python analyze.py --file data/output/simulation_results_test_*.csv  # 分析指定文件
  python analyze.py --report         # 仅生成统计报告
  python analyze.py --charts         # 仅生成可视化图表
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        help='指定要分析的 CSV 文件路径',
        default=None
    )
    
    parser.add_argument(
        '--report', '-r',
        action='store_true',
        help='仅生成统计报告'
    )
    
    parser.add_argument(
        '--charts', '-c',
        action='store_true',
        help='仅生成可视化图表'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='指定输出目录',
        default=None
    )
    
    args = parser.parse_args()
    
    # 确定要分析的文件
    if args.file:
        csv_path = args.file
    else:
        csv_path = find_latest_result()
    
    if not csv_path or not os.path.exists(csv_path):
        print("❌ 错误: 未找到仿真结果文件")
        print("\n可能的原因:")
        print("  1. 还没有运行过仿真")
        print("  2. 仿真结果文件已被删除")
        print("\n请先运行仿真:")
        print("  python main.py --mode test")
        sys.exit(1)
    
    print(f"\n{'='*80}")
    print(f"📊 数据分析系统 - 分析咖啡市场仿真结果")
    print(f"{'='*80}")
    print(f"📁 分析文件: {csv_path}")
    print(f"⏰ 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 创建分析器
    try:
        analyzer = CoffeeMarketAnalyzer(csv_path)
    except Exception as e:
        print(f"❌ 分析器初始化失败: {e}")
        sys.exit(1)
    
    # 确定输出目录
    output_dir = args.output or os.path.dirname(csv_path)
    
    # 决定执行的操作
    generate_report = args.report or (not args.charts)  # 默认生成报告
    generate_charts = args.charts or (not args.report)  # 默认生成图表
    
    try:
        # 生成报告
        if generate_report:
            print(f"\n{'='*80}")
            print("📋 第一步: 生成统计分析报告")
            print(f"{'='*80}")
            analyzer.generate_comprehensive_report(output_dir)
        
        # 生成图表
        if generate_charts:
            try:
                import matplotlib
                print(f"\n{'='*80}")
                print("📊 第二步: 生成可视化图表")
                print(f"{'='*80}")
                visualizer = CoffeeMarketVisualizer(analyzer)
                visualizer.plot_all_charts()
            except ImportError:
                print("\n⚠️  未安装 matplotlib，跳过图表生成")
                print("   如需生成图表，请运行: pip install matplotlib")
        
    except Exception as e:
        print(f"\n❌ 分析过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print(f"\n{'='*80}")
    print("✨ 分析完成！所有报告和图表已生成")
    print(f"   输出目录: {output_dir}")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
