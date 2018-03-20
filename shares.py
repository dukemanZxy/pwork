import tushare as ts
import os
import pandas as pd
import configparser
import datetime


# 对比一只股票在选定的时间内是否买盘大于卖盘，返回相差多少手
def screen(code, date, vol):
    data = ts.get_sina_dd(code, date=date, vol=vol)
    if data is None:
        return 0
    else:
        col_sums_buy = data[data.type == '买盘'].volume.sum()
        col_sums_sell = data[data.type == '卖盘'].volume.sum()
        return col_sums_buy - col_sums_sell


# 计算
def calculation(codes, values, ran, date, vol, nums, special_nums):
    for i in range(0, ran):
        # 总股本
        circulation = int(values[i, 5] * 100000000)
        # 买卖盘相差多少股
        num = screen(str(codes[i]), date, int(vol)) * 100
        # 大单买卖盘对应流通股占比
        probability = 0
        if circulation != 0:
            probability = round(num / circulation, 6)
        if abs(probability) >= 1:
            special_nums = special_nums.append({'code': codes[i], 'probability': probability}, ignore_index=True)
            continue
        nums = nums.append({'code': codes[i], 'probability': probability}, ignore_index=True)
    return nums, special_nums


def saveFile(df, date, filename):
    filename_temp = str(date) + filename + '.csv'
    if os.path.exists(filename_temp):
        df.to_csv(filename_temp, mode='a', header=None)
    else:
        df.to_csv(filename_temp)


# 参数date日期格式'2018-02-02',vol 多少手起算
def preferred(date, vol):
    df = ts.get_stock_basics()
    codes = df.index.tolist()
    values = df.values
    # columns = df.columns.tolist()
    # 正常集合
    nums = pd.DataFrame(columns=['code', 'probability'])
    # 波动异常集合
    special_nums = pd.DataFrame(columns=['code', 'probability'])
    ran = len(codes)
    # 计算
    nums, special_nums = calculation(codes, values, ran, date, vol, nums, special_nums)

    # 排序
    nums = nums.sort_values(by='probability', ascending=False)
    special_nums = special_nums.sort_values(by='probability', ascending=False)

    # 保存
    saveFile(nums, date, 'stock')
    saveFile(special_nums, date, 'stockSpecial')


def readInI():
    # preferred('2018-02-02', 500)
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read("db.ini", encoding='utf-8')
    step = int(config.get('current', 'step'))
    vol = int(config.get('current', 'vol'))
    # 今天
    today = datetime.date.today()
    # 前step天
    for i in range(1, step+1):
        stepToday = today + datetime.timedelta(days=-i)
        preferred(stepToday, vol)


readInI()