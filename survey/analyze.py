import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 1. 设置中文字体与全局样式，防止中文变方块
# Windows 用户默认使用 SimHei（黑体），Mac 用户请改为 'Arial Unicode MS' 或 'PingFang SC'
plt.rcParams['font.sans-serif'] = ['SimHei'] 
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", font='SimHei') 

# 2. 读取之前生成的虚拟问卷数据
file_name = 'ecnu_coffee_full_survey_326.csv'
try:
    df = pd.read_csv(file_name)
    print(f"成功加载数据，共 {len(df)} 条记录。")
except FileNotFoundError:
    print(f"未找到 {file_name}，请确保文件存在。")
    exit()

# ----------------- 图表 1：受访者身份结构分布 (饼图) -----------------
plt.figure(figsize=(8, 6))
identity_counts = df['1.身份'].value_counts()
colors = sns.color_palette('pastel')[0:4]
plt.pie(identity_counts, labels=identity_counts.index, autopct='%1.1f%%', 
        startangle=140, colors=colors, textprops={'fontsize': 12})
plt.title('图 1：华东师大普陀校区咖啡调研样本身份分布', fontsize=15, pad=20)
plt.savefig('chart1_identity_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------- 图表 2：不同身份人群的单杯心理价位 (堆叠柱状图) -----------------
plt.figure(figsize=(10, 6))
# 交叉表计算百分比
price_cross = pd.crosstab(df['1.身份'], df['9.单杯心理价位'], normalize='index') * 100
# 排序：确保图表呈现逻辑清晰
price_order = ['10 元以下（极致性价比）', '10-20 元（主流连锁品牌）', '20-30 元（精品店 / 社交空间）', '30 元以上（高端或特调咖啡）']
price_cross = price_cross.reindex(columns=price_order).fillna(0)

price_cross.plot(kind='bar', stacked=True, figsize=(10, 6), colormap='Set3')
plt.title('图 2：不同身份人群的单杯咖啡心理价位分布', fontsize=15)
plt.xlabel('受访者身份', fontsize=12)
plt.ylabel('占比 (%)', fontsize=12)
plt.xticks(rotation=0)
plt.legend(title='心理价位区间', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('chart2_price_vs_identity.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------- 图表 3：外卖商战/大额红包反应 (环形图) -----------------
plt.figure(figsize=(8, 6))
reaction_counts = df['10.商战/红包反应'].value_counts()
# 画外圈
plt.pie(reaction_counts, labels=reaction_counts.index, autopct='%1.1f%%', 
        startangle=90, colors=sns.color_palette('Set2'), pctdistance=0.85, textprops={'fontsize': 11})
# 画内圈（白色变环形图）
centre_circle = plt.Circle((0,0),0.70,fc='white')
fig = plt.gcf()
fig.gca().add_artist(centre_circle)

plt.title('图 3：消费者对大额外卖商战/跨界红包的消费反应', fontsize=15)
plt.tight_layout()
plt.savefig('chart3_market_war_reaction.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------- 图表 4：咖啡消费决策因素均值对比 (条形图) -----------------
plt.figure(figsize=(10, 6))
factors = ['7.影响因素-价格', '7.影响因素-距离', '7.影响因素-口味', '7.影响因素-空间', '7.影响因素-品牌影响力']
factor_labels = ['价格', '距离', '口味', '空间', '品牌影响力']

# 计算每项的均值
means = df[factors].mean().values

# 画柱状图
sns.barplot(x=factor_labels, y=means, palette='viridis')
plt.title('图 4：咖啡品牌选择核心要素的重视程度 (1-5 分制)', fontsize=15)
plt.ylabel('平均得分', fontsize=12)
plt.ylim(1, 5) # 分数范围是 1 到 5

# 在柱子上添加具体的数值标签
for i, mean_val in enumerate(means):
    plt.text(i, mean_val + 0.05, f'{mean_val:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('chart4_decision_factors.png', dpi=300, bbox_inches='tight')
plt.close()

print("图表生成完毕！已在当前目录保存 4 张高清 PNG 图像。")