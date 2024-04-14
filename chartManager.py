from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties
import pandas as pd

def createPieChartAndGetFileName(data_dict, title_str):
    category_sums = pd.Series(data_dict)
    
    e = []
    for i in range(0, len(data_dict)):
        e.append(0.02)

    font_path = "fonts/Cubic_11_1.010_R.ttf"
    font_prop = FontProperties(fname=font_path, size=14)

    def func(s,d):
        t = int(round(s/100.*sum(d)))
        return f'{s:.1f}%\n({t:,})'

    plt.figure(figsize=(10, 7))
    plt.pie(
    category_sums,
    explode=e,
    labels=category_sums.index,
    autopct=lambda i: func(i,category_sums),
    startangle=90,
    textprops={'fontproperties': font_prop})
    plt.title(title_str, fontproperties=font_prop)
    plt.axis('equal')

    file_name = 'expense_pie_chart.jpg'
    plt.savefig(file_name)
    plt.close()

    return file_name