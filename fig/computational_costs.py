import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# 数据
x = [0, 4, 7, 10, 13]
y = [0, 250000, 500000, 750000, 1000000, 1250000, 1500000]

# 数据分组
categories = ['share distribution', 'validator public key submission', 'group key submission', 'deposit']
data = [[0, 185536, 194766, 203951, 216161],           # share distribution
        [0, 355322, 378808, 402274, 425741],    # master key submission
        [0, 430549, 662194, 1019513, 1627730],         # group key submission
        [0, 529106, 611041, 692973, 774908]]            # deposit

# 颜色
markers = ['+', ' ', ' / ', '|']

# 创建一个新的图表
plt.figure(figsize=(12,6))

# 绘制条形统计图
bar_width = 0.5
bar_positions = [xi - bar_width / 2 - 0.5 for xi in x[1:]]  # 调整 x 位置，将刻度放在柱形图的中间
for i, category in enumerate(categories):
    plt.bar(bar_positions, data[i][1:], width=bar_width, label=category, color='white', hatch=markers[i], edgecolor="k")
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
plt.yticks(y, fontsize=18)

# 添加图例
plt.legend(fontsize=15)

# 显示图表
plt.show()
