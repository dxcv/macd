#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 20:33:28 2017

@author: liyizheng
"""

import pandas as pd


class inject:

    def __init__(self, minute, day):
        self.day = day
        self.minute = minute
        self.min_boduan = minute.boduan
        self.day_boduan = day.boduan
        self.min_boduan_list = []
        self.min_close = minute.close
        self.day_close = day.close
        self.misplace_point = pd.DataFrame({})
        self.zuji_situation = pd.DataFrame({})
        self.tupo_situation = pd.DataFrame({})
        self.zujiplustupo = pd.DataFrame({})

    def mapping(self):
        df_day = self.day_boduan
        df_min = self.min_boduan
        mapping_num = []
        mapping_table = []
        for i in range(len(df_day)):

            start = df_day.ix[i].start_date
            end = df_day.ix[i].end_date
            mapping_df = df_min[
                (df_min.start_date >= start) & (
                    df_min.end_date <= end)]

            if not mapping_df.empty:
                a = mapping_df.index[0]
                b = mapping_df.index[-1]

            else:
                mapping_table.append(mapping_df)
                mapping_num.append(1)
                continue

            if df_min.ix[b].bd_type == df_day.ix[i].bd_type and df_min.ix[
                    a].bd_type != df_day.ix[i].bd_type:
                mapping_df = df_min.ix[a - 1:b]
            if df_min.ix[a].bd_type == df_day.ix[i].bd_type and df_min.ix[
                    b].bd_type != df_day.ix[i].bd_type:
                mapping_df = df_min.ix[a:b + 1]
            if df_min.ix[a].bd_type != df_day.ix[i].bd_type and df_min.ix[
                    b].bd_type != df_day.ix[i].bd_type:
                mapping_df = df_min.ix[a - 1:b + 1]

            if df_day.ix[i].bd_type == "decline":
                for j in list(mapping_df.index[:-2]):
                    if j not in mapping_df.index:
                        continue
                    bd = mapping_df.ix[j]
                    if bd.bd_type == "decline":
                        if bd.end_price > mapping_df.end_price.ix[:j].min():
                            bdp2 = mapping_df.ix[j + 2]
                            mapping_df = mapping_df.drop(j)
                            mapping_df = mapping_df.drop(j + 1)
                            mapping_df = mapping_df.drop(j + 2)
                            mapping_df.ix[j] = {
                                'start_point': bd.start_point,
                                'end_point': bdp2.end_point,
                                'start_date': bd.start_date,
                                'end_date': bdp2.end_date,
                                'start_price': bd.start_price,
                                'end_price': bdp2.end_price,
                                'comfirmpoint': bd.comfirmpoint,
                                'prevtime': bd.prevtime,
                                'aftertime': bdp2.end_point - bd.comfirmpoint,
                                'timedelta': bdp2.end_point - bd.start_point,
                                'bd_type': 'decline',
                                'comfirm_date': bd.comfirm_date,
                                'comfirm_price': bd.comfirm_price,
                                'returns': bdp2.end_price / bd.start_price - 1,
                                'prevreturns': bd.comfirm_price / bd.start_price - 1,
                                'afterreturns': bdp2.end_price / bd.comfirm_price - 1,
                                'continue_ratio': (
                                    bd.comfirm_price / bd.start_price - 1) / (
                                    bdp2.end_price / bd.comfirm_price - 1)}

                            mapping_df = mapping_df.sort_index()

            elif df_day.ix[i].bd_type == "raise":
                for j in list(mapping_df.index[:-2]):
                    if j not in mapping_df.index:
                        continue
                    bd = mapping_df.ix[j]
                    if bd.bd_type == "raise":
                        if bd.end_price < mapping_df.end_price.ix[:j].max():
                            bdp2 = mapping_df.ix[j + 2]
                            mapping_df = mapping_df.drop(j)
                            mapping_df = mapping_df.drop(j + 1)
                            mapping_df = mapping_df.drop(j + 2)
                            mapping_df.ix[j] = {
                                'start_point': bd.start_point,
                                'end_point': bdp2.end_point,
                                'start_date': bd.start_date,
                                'end_date': bdp2.end_date,
                                'start_price': bd.start_price,
                                'end_price': bdp2.end_price,
                                'comfirmpoint': bd.comfirmpoint,
                                'prevtime': bd.prevtime,
                                'aftertime': bdp2.end_point - bd.comfirmpoint,
                                'timedelta': bdp2.end_point - bd.start_point,
                                'bd_type': 'raise',
                                'comfirm_date': bd.comfirm_date,
                                'comfirm_price': bd.comfirm_price,
                                'returns': bdp2.end_price / bd.start_price - 1,
                                'prevreturns': bd.comfirm_price / bd.start_price - 1,
                                'afterreturns': bdp2.end_price / bd.comfirm_price - 1,
                                'continue_ratio': (
                                    bd.comfirm_price / bd.start_price - 1) / (
                                    bdp2.end_price / bd.comfirm_price - 1)}

                            mapping_df = mapping_df.sort_index()

            mapping_table.append(mapping_df)
            mapping_num.append(mapping_df.shape[0])
        df_day['total_num'] = mapping_num
        self.day_boduan = df_day
        a = self.day
        a.boduan = df_day
        self.day = a
        self.min_boduan_list = mapping_table

    def comfirm_num(self):
        day_boduan = self.day_boduan
        min_boduan_list = self.min_boduan_list
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
                if df.iloc[j].start_date < day_comfirm_date < df.iloc[
                        j].end_date:
                    flag = False
                j += 1
            bd_type = day_point.bd_type
            if bd_type != df.iloc[j - 1].bd_type:
                j -= 1
            res.append(j)

        day_boduan['comfirm_num'] = res
        self.day_boduan = day_boduan
        a = self.day
        a.boduan = day_boduan
        self.day = a

    def misplace(self):
        min_boduan = self.min_boduan
        day_boduan = self.day_boduan
        min_close = self.min_close
        day_close = self.day_close
        misplace_point = []
        point_type = []
        day_comfirm = []
        misplace_success = []
        for i in range(min_boduan.shape[0] - 2):
            n1 = min_boduan.iloc[i]
            n3 = min_boduan.iloc[i + 2]
            bd_type = n1.bd_type
            temp = day_boduan[day_boduan.bd_type == bd_type]
            temp = temp[temp.start_date < n1.end_date]
            if temp.empty:
                continue

            if temp.index[-1] >= day_boduan.shape[0] - 1:
                break
            A = temp.iloc[-1].comfirm_date
            e = self.minute.comfirm_point_list[i + 3]
            a = n1.start_date
            c = n3.start_date
            b = n1.end_date
            d = n3.end_date
            Pb = min_close.ix[b]
            Pd = min_close.ix[d]
            Ae = day_close.ix[A:e]
            if Ae.empty:
                continue
            B1 = Ae.idxmin()
            B2 = Ae.idxmax()
            if Pb > Pd:
                if temp.iloc[-1].bd_type == "decline" and a <= B1 <= c:
                    misplace_point.append(e)
                    point_type.append("deline_after")
                    day_comfirm.append(
                        day_boduan.iloc[temp.index[-1] + 1].comfirm_date)
                    premin = min_close.ix[A:e].min()
                    nowmin = min_close.ix[e:day_boduan.iloc[
                        temp.index[-1] + 1].comfirm_date].min()
                    if nowmin < premin:
                        misplace_success.append(1)
                    else:
                        misplace_success.append(0)

                if temp.iloc[-1].bd_type == "raise" and c <= B2 <= e:
                    misplace_point.append(e)
                    point_type.append("raise_prev")
                    day_comfirm.append(
                        day_boduan.iloc[temp.index[-1] + 1].comfirm_date)
                    premax = min_close.ix[A:e].max()
                    nowmax = min_close.ix[e:day_boduan.iloc[
                        temp.index[-1] + 1].comfirm_date].max()
                    if nowmax > premax:
                        misplace_success.append(1)
                    else:
                        misplace_success.append(0)

            if Pb < Pd:
                if temp.iloc[-1].bd_type == "decline" and c <= B1 <= e:

                    misplace_point.append(e)
                    point_type.append("deline_prev")
                    day_comfirm.append(
                        day_boduan.iloc[temp.index[-1] + 1].comfirm_date)
                    premin = min_close.ix[A:e].min()
                    nowmin = min_close.ix[e:day_boduan.iloc[
                        temp.index[-1] + 1].comfirm_date].min()
                    if nowmin < premin:
                        misplace_success.append(1)
                    else:
                        misplace_success.append(0)

                if temp.iloc[-1].bd_type == "raise" and a <= B2 <= c:
                    misplace_point.append(e)
                    point_type.append("raise_after")
                    day_comfirm.append(
                        day_boduan.iloc[temp.index[-1] + 1].comfirm_date)
                    premax = min_close.ix[A:e].max()
                    nowmax = min_close.ix[e:day_boduan.iloc[
                        temp.index[-1] + 1].comfirm_date].max()
                    if nowmax > premax:
                        misplace_success.append(1)
                    else:
                        misplace_success.append(0)
        df = pd.DataFrame({'miplace_date': misplace_point,
                           'type': point_type,
                           'day_comfirm': day_comfirm,
                           'misplace_success': misplace_success})
        self.misplace_point = df

    def restrict(self):
        min_boduan = self.min_boduan
        day_boduan = self.day_boduan
        min_close = self.min_close
        day_close = self.day_close
        min_boduan_list = []
        zuji = []
        zuji_success = []
        zuji_boduan = []
        zuji_day = []
        tupo = []
        tupo_success = []
        tupo_boduan = []
        tupo_day = []
        zt = []
        zt_boduan = []
        zt_day = []
        zt_success = []
        for i in range(day_boduan.shape[0] - 1):
            start_date = day_boduan.iloc[i].start_date
            comfirm_date = day_boduan.iloc[i + 1].comfirm_date
            mapping_df = min_boduan[
                (min_boduan.start_date >= start_date) & (
                    min_boduan.comfirm_date <= comfirm_date)]
            if not mapping_df.empty:
                a = mapping_df.index[0]
                b = mapping_df.index[-1]
            if min_boduan.ix[a].bd_type != day_boduan.iloc[i].bd_type:
                mapping_df = min_boduan.ix[a - 1:b]
            min_boduan_list.append(mapping_df)
            if day_boduan.iloc[i].bd_type == "raise":
                flag = True
                j = 0

                while flag and j < mapping_df.shape[0] - 2:
                    if mapping_df.iloc[
                            j + 2].end_price < mapping_df.iloc[j].end_price:
                        if j + 3 < mapping_df.shape[0]:
                            zuji.append(mapping_df.iloc[j + 3].comfirm_date)
                            zuji_boduan.append(i)
                            zuji_day.append(
                                day_boduan.iloc[
                                    i + 1].comfirm_date)
                            premax = day_close.ix[
                                day_boduan.iloc[i].comfirm_date:mapping_df.iloc[
                                    j + 3].comfirm_date].max()
                            nowmax = day_close.ix[
                                mapping_df.iloc[
                                    j +
                                    3].comfirm_date:day_boduan.iloc[
                                    i +
                                    1].comfirm_date].max()
                            if nowmax > premax:
                                zuji_success.append(0)
                            else:
                                zuji_success.append(1)
                                flag = False
                    j += 2

                flag = True
                j = 0

                while flag and j < mapping_df.shape[0] - 4:
                    avalue = mapping_df.iloc[j + 3].end_price
                    five = mapping_df.iloc[j + 4]
                    five_price = min_close.ix[
                        five.comfirm_date:day_boduan.iloc[
                            i + 1].comfirm_date]
                    c = five_price[five_price < avalue]

                    if not c.empty:
                        tupo.append(c.index[0])
                        tupo_boduan.append(i)
                        tupo_day.append(day_boduan.iloc[i + 1].comfirm_date)
                        premax = day_close.ix[
                            day_boduan.iloc[i].comfirm_date:c.index[0]].max()
                        nowmax = day_close.ix[
                            c.index[0]:day_boduan.iloc[
                                i + 1].comfirm_date].max()
                        if nowmax > premax:
                            tupo_success.append(0)
                        else:
                            tupo_success.append(1)
                            flag = False
                    j += 2

                flag = True
                j = 0

                while flag and j < mapping_df.shape[0] - 3:
                    a = mapping_df.iloc[j].end_price
                    b = mapping_df.iloc[j + 1].end_price
                    c = mapping_df.iloc[j + 2].end_price
                    append = False
                    if a > c:
                        d = mapping_df.iloc[j + 3]
                        if d.comfirm_price < b:
                            zt.append(d.comfirm_date)
                            zt_boduan.append(i)
                            zt_day.append(day_boduan.iloc[i + 1].comfirm_date)
                            append = True
                        else:
                            d_price = min_close.ix[
                                d.comfirm_date:day_boduan.iloc[
                                    i + 1].comfirm_date]
                            d_price = d_price[d_price < b]
                            if not d_price.empty:
                                zt.append(d_price.index[0])
                                zt_boduan.append(i)
                                zt_day.append(
                                    day_boduan.iloc[
                                        i + 1].comfirm_date)
                                append = True

                        if append:
                            premax = day_close.ix[day_boduan.iloc[
                                i].comfirm_date:zt[-1]].max()
                            nowmax = day_close.ix[
                                zt[-1]:day_boduan.iloc[i + 1].comfirm_date].max()
                            if premax >= nowmax:
                                zt_success.append(1)
                                flag = False
                            else:
                                zt_success.append(0)
                    j += 2

            if day_boduan.iloc[i].bd_type == "decline":
                flag = True
                j = 0
                while flag and j < mapping_df.shape[0] - 2:
                    if mapping_df.iloc[
                            j + 2].end_price > mapping_df.iloc[j].end_price:
                        if j + 3 < mapping_df.shape[0]:
                            zuji_boduan.append(i)
                            zuji.append(mapping_df.iloc[j + 3].comfirm_date)
                            zuji_day.append(
                                day_boduan.iloc[
                                    i + 1].comfirm_date)
                            premin = day_close.ix[
                                day_boduan.iloc[i].comfirm_date:mapping_df.iloc[
                                    j + 3].comfirm_date].min()
                            nowmin = day_close.ix[
                                mapping_df.iloc[
                                    j +
                                    3].comfirm_date:day_boduan.iloc[
                                    i +
                                    1].comfirm_date].min()
                            if nowmin < premin:
                                zuji_success.append(0)
                            else:
                                zuji_success.append(1)
                                flag = False
                    j += 2

                flag = True
                j = 0

                while flag and j < mapping_df.shape[0] - 4:
                    avalue = mapping_df.iloc[j + 3].end_price
                    five = mapping_df.iloc[j + 4]
                    five_price = min_close.ix[
                        five.comfirm_date:day_boduan.iloc[
                            i + 1].comfirm_date]
                    c = five_price[five_price > avalue]

                    if not c.empty:
                        tupo.append(c.index[0])
                        tupo_boduan.append(i)
                        tupo_day.append(day_boduan.iloc[i + 1].comfirm_date)
                        premax = day_close.ix[
                            day_boduan.iloc[i].comfirm_date:c.index[0]].min()
                        nowmax = day_close.ix[
                            c.index[0]:day_boduan.iloc[
                                i + 1].comfirm_date].min()
                        if nowmax < premax:
                            tupo_success.append(0)
                        else:
                            tupo_success.append(1)
                            flag = False
                    j += 2

                while flag and j < mapping_df.shape[0] - 3:
                    a = mapping_df.iloc[j].end_price
                    b = mapping_df.iloc[j + 1].end_price
                    c = mapping_df.iloc[j + 2].end_price
                    append = False
                    if a < c:
                        d = mapping_df.iloc[j + 3]
                        if d.comfirm_price > b:
                            zt.append(d.comfirm_date)
                            zt_boduan.append(i)
                            zt_day.append(day_boduan.iloc[i + 1].comfirm_date)
                            append = True
                        else:
                            d_price = min_close.ix[
                                d.comfirm_date:day_boduan.iloc[
                                    i + 1].comfirm_date]
                            d_price = d_price[d_price > b]
                            if not d_price.empty:
                                zt.append(d_price.index[0])
                                zt_boduan.append(i)
                                zt_day.append(
                                    day_boduan.iloc[
                                        i + 1].comfirm_date)
                                append = True

                        if append:
                            premin = day_close.ix[day_boduan.iloc[
                                i].comfirm_date:zt[-1]].min()
                            nowmin = day_close.ix[
                                zt[-1]:day_boduan.iloc[i + 1].comfirm_date].min()
                            if premin <= nowmin:
                                zt_success.append(1)
                                flag = False
                            else:
                                zt_success.append(0)

                    j += 2

        zuji_situation = pd.DataFrame({'zuji_date': zuji,
                                       'day_comfirm': zuji_day,
                                       'zuji_boduan': zuji_boduan,
                                       'zuji_success': zuji_success})
        tupo_situation = pd.DataFrame({'tupo_date': tupo,
                                       'day_comfirm': tupo_day,
                                       'tupo_boduan': tupo_boduan,
                                       'tupo_success': tupo_success})
        zt_situation = pd.DataFrame({'zt_date': zt,
                                     'day_comfirm': zt_day,
                                     'zt_boduan': zt_boduan,
                                     'zt_success': zt_success})
        self.zuji_situation = zuji_situation
        self.tupo_situation = tupo_situation
        self.zujiplustupo = zt_situation

    def run(self):
        self.mapping()
        self.comfirm_num()
        self.misplace()
        self.restrict()
