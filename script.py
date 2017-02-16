# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 00:12:50 2017

@author: lyzheng
"""

import pandas as pd
import numpy as np


def fluctutate_interval(self, distance):
    if distance.empty:
        return []
    else:
        max_gap = 0
        for j in distance.index:
            for k in distance.index:
                if np.abs(distance[j] - distance[k]) >= max_gap:
                    max_gap = np.abs(distance[j] - distance[k])

        Tao = []
        for y in distance.index:
            for x in distance.index:
                if x < y and np.abs(distance[x] - distance[y]) == max_gap:
                    Tao.append([x, y])

        x_bound = max(distance.index)
        choose_pair = []
        for pair in Tao:
            if pair[0] < x_bound:
                x_bound = pair[0]
                choose_pair = pair
        if choose_pair[0] == distance.index[0]:
            left_interval = pd.Series([])
        else:
            left_interval = distance.ix[distance.index[0]:choose_pair[0]]
        if choose_pair[1] == distance.index[-1]:
            right_interval = pd.Series([])
        else:
            right_interval = distance.ix[choose_pair[1]:]
        result = list()
        result.append(choose_pair)
        result.extend(self.fluctutate_interval(left_interval))
        result.extend(self.fluctutate_interval(right_interval))
        return result


def mapping(df_day, df_min):
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
            print i


        else:
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

        mapping_table.append(mapping_df)
        mapping_num.append(mapping_df.shape[0])
    return mapping_num, mapping_table


def restrict(min_boduan, day_boduan, min_close, day_close):
    min_boduan_list = []
    zuji = []
    zuji_success = []
    zuji_boduan = []
    tupo = []
    tupo_success = []
    tupo_boduan = []
    for i in range(day_boduan.shape[0]-1):
        start_date = day_boduan.iloc[i].start_date
        comfirm_date = day_boduan.iloc[i + 1].comfirm_date
        mapping_df = min_boduan[(min_boduan.start_date >= start_date)&(min_boduan.comfirm_date <= comfirm_date)]
        if not mapping_df.empty:
            a = mapping_df.index[0]
            b = mapping_df.index[-1]
        if min_boduan.ix[a].bd_type != day_boduan.iloc[i].bd_type:
            mapping_df = min_boduan.ix[a - 1:b]
        min_boduan_list.append(mapping_df)
        if day_boduan.iloc[i].bd_type == "raise":
            flag=True
            j = 0

            while flag and j < mapping_df.shape[0] - 2:
                if mapping_df.iloc[j + 2].end_price < mapping_df.iloc[j].end_price:
                    if j + 3 < mapping_df.shape[0]:
                        zuji.append(mapping_df.iloc[j + 3].comfirm_date)
                        zuji_boduan.append(i)
                        premax = day_close.ix[day_boduan.iloc[i].comfirm_date:mapping_df.iloc[j + 3].comfirm_date].max()
                        nowmax = day_close.ix[mapping_df.iloc[j + 3].comfirm_date:day_boduan.iloc[i + 1].comfirm_date].max()
                        if nowmax > premax:
                            zuji_success.append(0)
                        else:
                            zuji_success.append(1)
                            flag = False
                j += 2

            flag = True
            j=0

            while flag and j < mapping_df.shape[0] - 4:
                avalue = mapping_df.iloc[j + 3].end_price
                five = mapping_df.iloc[j + 4]
                five_price = min_close.ix[five.comfirm_date:day_boduan.iloc[i+1].comfirm_date]
                c = five_price[five_price < avalue]

                if not c.empty:
                    tupo.append(c.index[0])
                    tupo_boduan.append(i)
                    premax = day_close.ix[day_boduan.iloc[i].comfirm_date:c.index[0]].max()
                    nowmax = day_close.ix[c.index[0]:day_boduan.iloc[i + 1].comfirm_date].max()
                    if nowmax > premax:
                        tupo_success.append(0)
                    else:
                        tupo_success.append(1)
                        flag = False
                j += 2



        if day_boduan.iloc[i].bd_type == "decline":
            flag = True
            j = 0
            while flag and j < mapping_df.shape[0] - 2:
                if mapping_df.iloc[j + 2].end_price > mapping_df.iloc[j].end_price:
                    if j + 3 < mapping_df.shape[0]:
                        zuji_boduan.append(i)
                        zuji.append(mapping_df.iloc[j + 3].comfirm_date)
                        premin = day_close.ix[day_boduan.iloc[i].comfirm_date:mapping_df.iloc[j + 3].comfirm_date].min()
                        nowmin = day_close.ix[mapping_df.iloc[j + 3].comfirm_date:day_boduan.iloc[i + 1].comfirm_date].min()
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
                five_price = min_close.ix[five.comfirm_date:day_boduan.iloc[i+1].comfirm_date]
                c = five_price[five_price > avalue]

                if not c.empty:
                    tupo.append(c.index[0])
                    tupo_boduan.append(i)
                    premax = day_close.ix[day_boduan.iloc[i].comfirm_date:c.index[0]].min()
                    nowmax = day_close.ix[c.index[0]:day_boduan.iloc[i + 1].comfirm_date].min()
                    if nowmax < premax:
                        tupo_success.append(0)
                    else:
                        tupo_success.append(1)
                        flag = False
                j += 2

    zuji_situation = pd.DataFrame({'zuji_date':zuji,'zuji_boduan':zuji_boduan,'zuji_success':zuji_success})
    tupo_situation = pd.DataFrame({'tupo_date': tupo, 'tupo_boduan': tupo_boduan, 'tupo_success': tupo_success})
    return zuji_situation,tupo_situation,min_boduan_list














