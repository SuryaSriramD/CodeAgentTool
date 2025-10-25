# 修改后的完整代码：添加折线连接柱状图中间点，并设置纵坐标起始点为200

# 导入必要的库
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# 使用提供的数据创建 DataFrame
data = {
    'Language': ['Python', 'Java', 'Go', 'C++', 'JavaScript', 'C', 'C#', 'PHP', 'Ruby'],
    'Merged': [446.871, 281.141, 461.708, 440.707, 345.513, 455.566, 228.146, 266.448, 369.800],
    'Closed': [324.825, 327.672, 430.286, 366.592, 309.266, 352.729, 218.493, 246.081, 315.719]
}
df_languages = pd.DataFrame(data)

# 融合数据以便于绘图
df_languages_melted = pd.melt(df_languages, id_vars='Language', value_vars=['Merged', 'Closed'], var_name='Category', value_name='Execution Time')

# 使用不同的花纹来区分 Merged 和 Closed
patterns = {'Merged': 'x', 'Closed': 'o'}
palette = {"Merged": "lightblue", "Closed": "orange"}


# 创建柱状图，并为每个柱子应用不同的花纹
plt.figure(figsize=(12, 8))
# bars = sns.barplot(x='Language', y='Execution Time', hue='Category', data=df_languages_melted)
bars = sns.barplot(x='Language', y='Execution Time', hue='Category', data=df_languages_melted, palette=palette)

# 记录每个柱子的中间点位置
points = {category: [] for category in patterns.keys()}

# 为每个柱子应用相应的花纹，并记录中间点位置
for bar, (lang, cat, time) in zip(bars.patches, df_languages_melted.itertuples(index=False)):
    bar.set_hatch(patterns[cat])
    points[cat].append((bar.get_x() + bar.get_width() / 2, time))

# # 连接中间点
# for cat, pts in points.items():
#     plt.plot([p[0] for p in pts], [p[1] for p in pts], marker='o')

# 设置 y 轴起始点为 200
plt.ylim(200, None)

# 添加图表标题和轴标签
plt.title('Average Execution Time with Patterns for Different Programming Languages')
plt.xlabel('Programming Language')
plt.ylabel('Execution Time (seconds)')
# plt.xticks(rotation=45)

# 添加图例
plt.legend(title='Category')

# 显示图表并保存为 PDF 文件

plt.savefig('executiontime.pdf')

