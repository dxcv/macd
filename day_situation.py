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
