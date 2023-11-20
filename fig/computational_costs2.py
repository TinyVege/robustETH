import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# 数据
x = [0, 4, 7, 10, 13]
y = [0, 150000, 300000, 450000, 600000, 750000, 900000, 1050000, 1200000]

# 数据分组
categories = ['normal exit', 'slash exit', 'lagging trig exit']
data = [[0, 200810, 230335, 259861, 289388],           # normal exit
        [0, 816052, 858625, 901186, 943124],    # slash exit 			
        [0, 193175, 193175, 193175, 193175]]         # lagging trig exit

# 形状
markers = ['/', ' ', '|']

# 创建一个新的图表
plt.figure(figsize=(12,6))

# 绘制条形统计图，利用 fillstyle 参数设置形状填充
bar_width = 0.7
bar_positions = [xi - bar_width / 2 - 0.35 for xi in x[1:]]  # 调整 x 位置，不包括0的位置
for i, category in enumerate(categories):
    plt.bar(bar_positions, data[i][1:], width=bar_width, label=category, color='white', hatch=markers[i],edgecolor="k",)
    bar_positions = [xi + bar_width for xi in bar_positions]  # 更新下一个柱的位置


def formatnum(x, pos):
    return '%.0fK' % (x/1e3)

formatter = FuncFormatter(formatnum)
plt.gca().yaxis.set_major_formatter(formatter)

# 添加标题和标签
plt.xlabel('Number of Participants',fontsize=18)
plt.ylabel('Gas Required',fontsize=18)

# 添加横轴刻度
plt.xticks(x[1:], [str(xi) for xi in x[1:]],fontsize=18)

# 手动设置 y 轴刻度标签
plt.yticks(y,fontsize=18)

# 添加图例
plt.legend(fontsize=15)

# 显示图表
plt.show()
