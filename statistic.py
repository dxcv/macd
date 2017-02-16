import pandas as pd
import numpy as np
from Trend import *


def returns_sta(boduan):
    rai = boduan[boduan.bd_type == "raise"].returns
    dec = boduan[boduan.bd_type == "decline"].returns

    rai_sta = [rai.mean(), rai.std(), rai.max(), rai.min(), len(rai)]
    dec_sta = [dec.mean(), dec.std(), dec.min(), dec.max(), len(dec)]

    rai_l = len(rai)
    dec_l = len(dec)
    rai = rai.sort_values()[int(0.1 * rai_l):int(0.9 * rai_l)]
    dec = dec.sort_values()[int(0.1 * dec_l):int(0.9 * dec_l)]

    rai_sta_adj = [rai.mean(), rai.std(), rai.max(), rai.min(), len(rai)]
    dec_sta_adj = [dec.mean(), dec.std(), dec.min(), dec.max(), len(dec)]

    return pd.DataFrame({'上涨波段': rai_sta, "下跌波段": dec_sta}, index=['均值', '标准差', '最大值', '最小值', '样本数']).T, pd.DataFrame(
        {'上涨波段': rai_sta_adj, "下跌波段": dec_sta_adj}, index=['均值', '标准差', '最大值', '最小值', '样本数']).T


def continue_sta(boduan):
    rai = boduan[boduan.bd_type == "raise"].afterreturns
    dec = boduan[boduan.bd_type == "decline"].afterreturns

    rai_sta = [rai.mean(), rai.std(), rai.max(), rai.min(), rai[rai < 0.005].shape[
        0], rai[rai < 0.005].shape[0] / (rai.shape[0] + 0.0), len(rai)]
    dec_sta = [dec.mean(),
               dec.std(),
               dec.min(),
               dec.max(),
               dec[dec > -0.005].shape[0],
               dec[dec > -0.005].shape[0] / (dec.shape[0] + 0.0),
               len(dec)]

    rai_l = len(rai)
    dec_l = len(dec)
    rai = rai.sort_values()[int(0.1 * rai_l):int(0.9 * rai_l)]
    dec = dec.sort_values()[int(0.1 * dec_l):int(0.9 * dec_l)]

    rai_sta_adj = [rai.mean(), rai.std(), rai.max(), rai.min(), rai[rai < 0.005].shape[0],
                   rai[rai < 0.005].shape[0] / (rai.shape[0] + 0.0), len(rai)]
    dec_sta_adj = [dec.mean(),
                   dec.std(),
                   dec.min(),
                   dec.max(),
                   dec[dec > -0.005].shape[0],
                   dec[dec > -0.005].shape[0] / (dec.shape[0] + 0.0),
                   len(dec)]

    df1 = pd.DataFrame({'上涨波段延续涨幅': rai_sta, "下跌波段延续涨幅": dec_sta}, index=[
                       '均值', '标准差', '最大值', '最小值', '无延续波段数', '占比', '样本数']).T
    df2 = pd.DataFrame({'上涨波段延续涨幅': rai_sta_adj, "下跌波段延续涨幅": dec_sta_adj}, index=[
        '均值', '标准差', '最大值', '最小值', '无延续波段数', '占比', '样本数']).T
    df1.to_excel("/Users/liyizheng/data/df1.xlsx")
    df2.to_excel("/Users/liyizheng/data/df2.xlsx")
    return df1, df2


def continue_sta_day(boduan):
    rai = boduan[boduan.bd_type == "raise"].aftertime
    dec = boduan[boduan.bd_type == "decline"].aftertime

    rai_sta = [rai.mean(), rai.std(), rai.max(), rai.min(), rai[rai <= 3].shape[
        0], rai[rai <= 3].shape[0] / (rai.shape[0] + 0.0), len(rai)]
    dec_sta = [dec.mean(),
               dec.std(),
               dec.min(),
               dec.max(),
               dec[dec <= 3].shape[0],
               dec[dec <= 3].shape[0] / (dec.shape[0] + 0.0),
               len(dec)]

    rai_l = len(rai)
    dec_l = len(dec)
    rai = rai.sort_values()[int(0.1 * rai_l):int(0.9 * rai_l)]
    dec = dec.sort_values()[int(0.1 * dec_l):int(0.9 * dec_l)]

    rai_sta_adj = [rai.mean(), rai.std(), rai.max(), rai.min(), rai[rai <= 3].shape[0],
                   rai[rai <= 3].shape[0] / (rai.shape[0] + 0.0), len(rai)]
    dec_sta_adj = [dec.mean(),
                   dec.std(),
                   dec.min(),
                   dec.max(),
                   dec[dec <= 3].shape[0],
                   dec[dec <= 3].shape[0] / (dec.shape[0] + 0.0),
                   len(dec)]

    df1 = pd.DataFrame({'上涨波段延续时间': rai_sta, "下跌波段延续时间": dec_sta}, index=[
                       '均值', '标准差', '最大值', '最小值', '无延续波段数', '占比', '样本数']).T
    df2 = pd.DataFrame({'上涨波段延续时间': rai_sta_adj, "下跌波段延续时间": dec_sta_adj}, index=[
        '均值', '标准差', '最大值', '最小值', '无延续波段数', '占比', '样本数']).T
    df1.to_excel("/Users/liyizheng/data/df1_day.xlsx")
    df2.to_excel("/Users/liyizheng/data/df2_day.xlsx")
    return df1, df2


def comfirm_num(day_boduan, min_boduan_list):
    res = []
    for i in range(day_boduan.shape[0]):
        df = min_boduan_list[i]
        if df.empty:
            res.append(1)
            continue
        day_point = day_boduan.ix[i]
        day_comfirm_date = day_point.comfirm_date
        flag = True
        j = 0
        while flag and j < df.shape[0]:
            if df.iloc[j].start_date < day_comfirm_date < df.iloc[j].end_date:
                flag = False
            j += 1
        res.append(j)
    return res


tr = Trend()


def power_value(close, boduan):
    pow_val = []
    for i in range(boduan.shape[0]):
        start_date = boduan.ix[i].start_date
        comfirm_date = boduan.ix[i].comfirm_date
        start_index = list(close.index).index(start_date)
        start_index = start_index - 5 if start_index >= 5 else 0
        start_date = close.index[start_index]
        close_t = close.ix[start_date:comfirm_date]
        pow_val.append(tr.Trend_caculate(close_t, 5))

    boduan['power'] = pow_val
    return boduan


def trade_boduan(close, boduan, ratio):
    cash = 1.0
    stream = []
    p = 0
    raise_date = list(boduan[boduan.bd_type == "raise"].comfirm_date)
    decline_date = list(boduan[boduan.bd_type == "decline"].comfirm_date)
    date_all = list(boduan.comfirm_date)
    for date in close.index:
        if date not in date_all:
            stream.append(p * close.ix[date] + cash)
            continue
        if date in raise_date and cash > 0:
            p += cash / close.ix[date] * (1 - ratio)
            cash = 0

        if date in decline_date and p > 0:
            cash += p * close.ix[date] * (1 - ratio)
            p = 0

        stream.append(p * close.ix[date] + cash)

    df = pd.DataFrame({"strategy": stream,
                       "close": close.iloc[len(close) - len(stream):]})
    df = df / df.ix[0]
    return df


def trade_togather(close, day_boduan, min_boduan, ratio):
    cash = 1.0
    stream = []
    p = 0
    boduan = min_boduan
    raise_date = list(boduan[boduan.bd_type == "raise"].comfirm_date)
    decline_date = list(boduan[boduan.bd_type == "decline"].comfirm_date)
    date_all = list(boduan.comfirm_date)

    for date in close.index:
        if date not in date_all:
            stream.append(p * close.ix[date] + cash)
            continue
        if date in raise_date and cash > 0 and rc(date, day_boduan) == "raise":
            p += cash / close.ix[date] * (1 - ratio)
            cash = 0

        if date in decline_date or rc(date, day_boduan) == "decline" and p > 0:
            cash += p * close.ix[date] * (1 - ratio)
            p = 0

        stream.append(p * close.ix[date] + cash)

    df = pd.DataFrame({"strategy": stream,
                       "close": close.iloc[len(close) - len(stream):]})
    df = df / df.ix[0]
    return df


def rc(date, boduan):
    comfirm_date = boduan.comfirm_date
    bd_type = boduan.bd_type
    if date < comfirm_date[0]:
        return bd_type[1]
    for i in range(boduan.shape[0] - 1):
        if comfirm_date[i] < date < comfirm_date[i + 1]:
            return bd_type[i]
    if date > comfirm_date.iloc[-1]:
        return bd_type.iloc[-1]


def year_returns(Nav):
    grouped = Nav.groupby(lambda x: x.year)
    returns = grouped.apply(lambda x: x.ix[-1] / x.ix[0] - 1)
    return returns


def information_strength(close, boduan):
    information_val = []
    for i in range(boduan.shape[0]):
        temp = boduan.ix[i]
        close_temp = close.ix[temp.start_date:temp.comfirm_date]
        pct_change = close_temp.pct_change()
        sign = np.sign(close_temp.ix[-1] - close_temp.ix[0])
        neg = pct_change[pct_change > 0].shape[0]
        pos = pct_change.shape[0] - neg - 1
        val = (neg - pos + 0.0) / (pct_change.shape[0] - 1) * sign
        information_val.append(val)
    boduan['information_strength'] = information_val
    return boduan


def returns_sta(Nav):
    pass


def macd_mark(boduan, situation):
    mark_val = []
    comfirm_date = boduan.comfirm_date
    for i in range(comfirm_date.shape[0]):
        mark_val.append(mark(comfirm_date[i], situation))
    boduan['mark'] = mark_val
    return boduan


def mark(date, situation):
    if date < situation.iloc[0].startdate:
        return 1 - int(situation.iloc[0].mark)
    for i in range(situation.shape[0]):
        temp = situation.iloc[i]
        if temp.startdate <= date < temp.enddate:
            return int(temp.mark)

    if date > situation.iloc[-1].enddate:
        return int(1 - situation.iloc[-1].mark)


def trade_situation(close, situation, boduan, ratio):
    cash = 1.0
    stream = []
    p = 0
    raise_date = list(boduan[boduan.bd_type == "raise"].comfirm_date)
    decline_date = list(boduan[boduan.bd_type == "decline"].comfirm_date)

    for date in close.index:

        if date in raise_date and cash > 0 and situation.ix[date] == 1:
            p += cash / close.ix[date] * (1 - ratio)
            cash = 0

        if date in decline_date and p > 0 and situation.ix[date] == 1:
            cash += p * close.ix[date] * (1 - ratio)
            p = 0

        stream.append(p * close.ix[date] + cash)

    df = pd.DataFrame({"strategy": stream,
                       "close": close.iloc[len(close) - len(stream):]})
    df = df / df.ix[0]
    return df
