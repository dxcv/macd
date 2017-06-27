# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 14:13:27 2017

@author: lh
"""

# -*- coding: utf-8 -*-
from macd_split import *
import datetime


def get_yesterday():
    today = datetime.date.today()
    oneday = datetime.timedelta(days=0)
    yesterday = today - oneday
    return yesterday


def get_data(code, field, perid, start, end):
    dat = w.wsd(
        code,
        ",".join(field),
        start,
        end,
        "PriceAdj=F;Period=%s" %
        perid)
    strtime = map(
        lambda x: x.strftime("%Y-%m-%d") + " 15:00",
        dat.Times)

    df = pd.DataFrame(
        np.array(
            dat.Data).T, index=map(
            lambda x: datetime.datetime.strptime(
                x, "%Y-%m-%d %H:%M"), strtime), columns=field)
    return df


def get_min_data(code, field, period, start, end):
    dat = w.wsi(
        code,
        ",".join(field),
        start,
        end,
        "BarSize=%d;PriceAdj=F" %
        period)
    strtime = map(
        lambda x: x.strftime("%Y-%m-%d %X"),
        dat.Times)

    df = pd.DataFrame(
        np.array(
            dat.Data).T, index=map(
            lambda x: datetime.datetime.strptime(
                x, "%Y-%m-%d %X"), strtime), columns=field)
    return df


def now_situation(mindata_path, num):
    stockindex = dict()
    stockindex['szzz'] = u'上证综指'
    stockindex['szcz'] = u'深证成指'
    stockindex['hs300'] = u'沪深300'
    stockindex['zz500'] = u'中证500'
    stockindex['cybz'] = u'创业板指'
    stockindex['zxbz'] = u'中小板指'

    index_code = dict()
    index_code['szzz'] = '000001.SH'
    index_code['szcz'] = '399001.SZ'
    index_code['hs300'] = '000300.SH'
    index_code['zz500'] = '000905.SH'
    index_code['cybz'] = '399006.SZ'
    index_code['zxbz'] = '399005.SZ'

    change = dict()
    change['raise'] = u'上涨'
    change['decline'] = u'下跌'
    for index in stockindex.keys():
        fname = mindata_path + "\\" + index + ".xlsx"
        nowtime = get_yesterday().strftime('%Y-%m-%d') + " 15:01:00"
        # lasttime = w.tdaysoffset(-num, nowtime).Data[0][0].strftime("%Y-%m-%d %X")

        priceseries = pd.read_excel(fname)
        priceseries['time'] = priceseries['time'].map(
            lambda x: datetime.datetime.strptime(
                str(x), "%Y-%m-%d %H:%M:%S"))
        priceseries = priceseries.set_index('time')
        lasttime = priceseries.index[-1]
        newdata = get_min_data(index_code[index], ["close"], 30, lasttime, nowtime)
        min_close = pd.concat([priceseries.close, newdata[1:].close])
        # min_close = min_close[-num * 8:]
        day_close = get_data(index_code[index], ["close"], "D", min_close.index[0], min_close.index[-1]).close
        min_close.index = map(lambda x: str(x), min_close.index)
        day_close.index = map(lambda x: str(x), day_close.index)
        minute = MACD_split(min_close)
        day = MACD_split(day_close)
        minute.run()
        day.run()
        min_boduan = minute.boduan
        day_boduan = day.boduan
        last_boduan = day_boduan.iloc[-1]
        latest_comfirm = day.comfirm_point_list[-1]
        begin_date = last_boduan.end_date
        bd_type = last_boduan.bd_type
        now_bdtype = "raise" if bd_type == "decline" else "decline"
        now_min_boduan = min_boduan[min_boduan.start_date > begin_date]
        if not now_min_boduan.empty:
            if now_min_boduan.iloc[0].bd_type != now_bdtype:
                loc = now_min_boduan.index[0]
                now_min_boduan = min_boduan[loc - 1:]
            j = 0
            flag = True
            while flag and j < now_min_boduan.shape[0]:
                duan = now_min_boduan.iloc[j]
                if duan.start_date < latest_comfirm < duan.end_date:
                    flag = False
                j += 1
            if flag:
                j += 1
            length = now_min_boduan.shape[0] + 1
        else:
            j = 1
            length = 1
        print u"目前%s正处于%s的第%d段," % (stockindex[index], change[now_bdtype], length) + \
              u"该段%s开始于%s," % (change[now_bdtype], begin_date) + u"其在%s确认该段%s," % (latest_comfirm, change[now_bdtype]) + \
              u"%s确认时位于第%s段." % (change[now_bdtype], j)


def get_industry_situation(swdata_path, num):
    sw_data = pd.read_excel(swdata_path)
    sw_name = dict()
    sw_name[u'801010.SI'] = u'农林牧渔'
    sw_name[u'801020.SI'] = u'采掘'
    sw_name[u'801030.SI'] = u'化工'
    sw_name[u'801040.SI'] = u'钢铁'
    sw_name[u'801080.SI'] = u'电子'
    sw_name[u'801110.SI'] = u'家用电器'
    sw_name[u'801120.SI'] = u'食品饮料'
    sw_name[u'801130.SI'] = u'纺织服装'
    sw_name[u'801140.SI'] = u'轻工制造'
    sw_name[u'801150.SI'] = u'医药生物'
    sw_name[u'801160.SI'] = u'公用事业'
    sw_name[u'801170.SI'] = u'交通运输'
    sw_name[u'801180.SI'] = u'房地产'
    sw_name[u'801200.SI'] = u'商业贸易'
    sw_name[u'801210.SI'] = u'休闲服务'
    sw_name[u'801230.SI'] = u'综合'
    sw_name[u'801710.SI'] = u'建筑材料'
    sw_name[u'801120.SI'] = u'建筑装饰'
    sw_name[u'801730.SI'] = u'电气设备'
    sw_name[u'801740.SI'] = u'国防军工'
    sw_name[u'801750.SI'] = u'计算机'
    sw_name[u'801760.SI'] = u'传媒'
    sw_name[u'801770.SI'] = u'通信'
    sw_name[u'801780.SI'] = u'银行'
    sw_name[u'801790.SI'] = u'非银金融'
    sw_name[u'801880.SI'] = u'汽车'
    sw_name[u'801890.SI'] = u'机械设备'

    change = dict()
    change['raise'] = u'上涨'
    change['decline'] = u'下跌'

    for industry in sw_data.columns:
        priceseries = sw_data[industry]
        nowtime = get_yesterday().strftime('%Y-%m-%d') + " 15:01:00"
        lasttime = w.tdaysoffset(-num, nowtime).Data[0][0].strftime("%Y-%m-%d %X")
        newdata = get_min_data(industry, ["close"], 30, lasttime, nowtime)
        min_close = pd.concat([priceseries, newdata[1:].close])
        min_close = min_close[-num * 8:]
        day_close = get_data(industry, ["close"], "D", min_close.index[0], min_close.index[-1]).close
        minute = MACD_split(min_close)
        day = MACD_split(day_close)
        minute.run()
        day.run()
        min_boduan = minute.boduan
        day_boduan = day.boduan
        last_boduan = day_boduan.iloc[-1]
        latest_comfirm = str(day.comfirm_point_list[-1])
        begin_date = str(last_boduan.end_date)
        bd_type = last_boduan.bd_type
        now_bdtype = "raise" if bd_type == "decline" else "decline"
        now_min_boduan = min_boduan[min_boduan.start_date > begin_date]
        if not now_min_boduan.empty:
            if now_min_boduan.iloc[0].bd_type != now_bdtype:
                loc = now_min_boduan.index[0]
                now_min_boduan = min_boduan[loc - 1:]
            j = 0
            flag = True
            while flag:
                duan = now_min_boduan.iloc[j]
                if duan.start_date < latest_comfirm < duan.end_date:
                    flag = False
                j += 1
                length = now_min_boduan.shape[0] + 1
        else:
            j = 1
            length = 1

        print u"目前%s正处于%s的第%d段," % (sw_name[industry], change[now_bdtype], length) + \
              u"该段%s开始于%s," % (change[now_bdtype], begin_date) + u"其在%s确认该段%s," % (latest_comfirm, change[now_bdtype]) + \
              u"%s确认时位于第%s段." % (change[now_bdtype], j)


now_situation('D:\indexdata', 300)
# get_industry_situation('D:\indexdata\sw30.xlsx', 300)

