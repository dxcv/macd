from WindPy import w

w.start()


def get_day_situation(min_boduan, day_boduan, mapping_table):
    start = day_boduan.start_date.iloc[0]
    end = day_boduan.end_date.iloc[-1]
    days = w.tdays(start, end).Data[0]
    days = map(lambda x: str(x).split(' ')[0], days)
    df = pd.DataFrame(columns=['future_day_situation', 'now_day_situation', 'future_day_start', 'future_day_end',
                               'now_day_start', 'future_minute_situation', 'now_minute_situation',
                               'future_min_start', 'future_min_end', 'now_min_start',
                               'future_min_duannum', 'now_min_duannum'],
                      index=days)

    for i in range(1, day_boduan.shape[0]):
        duan = day_boduan.iloc[i]
        start_date = str(duan.start_date)
        end_date = str(duan.end_date)
        comfirm_date = str(duan.comfirm_date)
        prev_start_date = day_boduan.iloc[i - 1].start_date
        situation = duan.bd_type
        situation_inverse = 'raise' if situation == 'decline' else 'decline'
        df['future_day_situation'].ix[start_date:end_date] = situation
        df['now_day_situation'].ix[start_date:comfirm_date] = situation_inverse
        df['now_day_situation'].ix[comfirm_date:end_date] = situation
        df['future_day_start'].ix[start_date:end_date] = start_date
        df['future_day_end'].ix[start_date:end_date] = end_date
        df['now_day_start'].ix[start_date:comfirm_date] = prev_start_date
        df['now_day_start'].ix[comfirm_date:end_date] = start_date
        table = mapping_table[i]
        prev_table = mapping_table[i - 1]
        if len(table.shape) == 1:
            num = 1
        else:
            num = table.shape[0]
        for j in range(num):
            if len(table.shape) == 1:
                min_start_date = str(table.start_date)
                min_end_date = str(table.end_date)
                min_comfirm_date = str(table.comfirm_date)
            else:
                min_duan = table.iloc[j]
                min_start_date = str(min_duan.start_date)
                min_end_date = str(min_duan.end_date)
                min_comfirm_date = str(min_duan.comfirm_date)

            df['future_min_duannum'].ix[min_start_date:min_comfirm_date] = j
            df['future_min_duannum'].ix[min_comfirm_date:min_end_date] = j + 1
            df['now_min_duannum'].ix[start_date:comfirm_date].ix[min_start_date:min_comfirm_date] = \
                prev_table.shape[0] + j
            df['now_min_duannum'].ix[start_date:comfirm_date].ix[min_comfirm_date:min_end_date] = \
                prev_table.shape[0] + j + 1
            df['now_min_duannum'].ix[comfirm_date:end_date].ix[min_start_date:min_comfirm_date] = j
            df['now_min_duannum'].ix[comfirm_date:end_date].ix[min_comfirm_date:min_end_date] = j + 1

    for i in range(1, min_boduan.shape[0]):
        duan = min_boduan.iloc[i]
        start_date = str(duan.start_date)
        end_date = str(duan.end_date)
        comfirm_date = str(duan.comfirm_date)
        prev_start_date = min_boduan.iloc[i - 1].start_date
        situation = duan.bd_type
        situation_inverse = 'raise' if situation == 'decline' else 'decline'
        df['future_minute_situation'].ix[start_date:end_date] = situation
        df['now_minute_situation'].ix[start_date:comfirm_date] = situation_inverse
        df['now_minute_situation'].ix[comfirm_date:end_date] = situation
        df['future_min_start'].ix[start_date:end_date] = start_date
        df['future_min_end'].ix[start_date:end_date] = end_date
        df['now_min_start'].ix[start_date:comfirm_date] = prev_start_date
        df['now_min_start'].ix[comfirm_date:end_date] = start_date

    return df


def mapping(df_day, df_min):
    mapping_num = []
    mapping_table = []
    location = 0
    for i in range(len(df_day)):

        start = df_day.ix[i].start_date
        end = df_day.ix[i].end_date
        mapping_df = df_min[
            (df_min.start_date >= start) & (
                df_min.end_date <= end)].copy()

        if not mapping_df.empty:
            a = mapping_df.index[0]
            b = mapping_df.index[-1]
            location = b
            if df_min.ix[b].bd_type == df_day.ix[i].bd_type and df_min.ix[
                a].bd_type != df_day.ix[i].bd_type:
                mapping_df = df_min.ix[a - 1:b].copy()

            if df_min.ix[a].bd_type == df_day.ix[i].bd_type and df_min.ix[
                b].bd_type != df_day.ix[i].bd_type:
                mapping_df = df_min.ix[a:b + 1].copy()
                location = b + 1
            if df_min.ix[a].bd_type != df_day.ix[i].bd_type and df_min.ix[
                b].bd_type != df_day.ix[i].bd_type:
                mapping_df = df_min.ix[a - 1:b + 1].copy()
                location = b + 1



        else:
            if not mapping_table:
                mapping_table.append(df_min.ix[0])
            else:
                mapping_table.append(df_min.ix[location + 1])
            location += 1

            mapping_num.append(1)
            continue

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
    return mapping_table