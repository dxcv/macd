#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 20:33:28 2017

@author: liyizheng
"""

import pandas as pd

class inject:
    def __init__(self, minute , day):
        self.day = day
        self.minute = minute
        self.min_boduan = minute.boduan
        self.day_boduan = day.boduan
        self.min_boduan_list = []
        self.min_close = minute.close
        self.day_close = day.close
        self.misplace_point = pd.DataFrame({})



    def mapping(self):
        df_day =self.day_boduan
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
                if df.iloc[j].start_date < day_comfirm_date < df.iloc[j].end_date:
                    flag = False
                j += 1
            bd_type = day_point.bd_type
            if bd_type != df.iloc[j-1].bd_type:
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
        for i in range(min_boduan.shape[0] - 2):
            n1 = min_boduan.iloc[i]
            n3 = min_boduan.iloc[i + 2]
            bd_type = n1.bd_type
            temp = day_boduan[day_boduan.bd_type == bd_type]
            temp = temp[temp.start_date < n1.end_date]
            if temp.empty:
                continue
            A = temp.iloc[-1].comfirm_date
            e = self.minute.comfirm_point_list[i+3]
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


                if temp.iloc[-1].bd_type == "raise" and c <= B2 <= e:
                    misplace_point.append(e)
                    point_type.append("raise_prev")


            if Pb < Pd:
                if temp.iloc[-1].bd_type == "decline" and c <= B1 <= e:

                    misplace_point.append(e)
                    point_type.append("deline_prev")

                if temp.iloc[-1].bd_type == "raise" and a <= B2 <= c:
                    misplace_point.append(e)
                    point_type.append("raise_after")
        df = pd.DataFrame({'miplace_date':misplace_point,'type':point_type})
        self.misplace_point = df

    def run(self):
        self.mapping()
        self.comfirm_num()
        self.misplace()

