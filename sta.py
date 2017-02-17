# -*- coding: utf-8 -*-
import pandas as pd


class statistic:
    def __init__(self, split ):
        self.split = split
        self.boduan =split.boduan
        self.close =split.close
        self.ret_sta = pd.DataFrame({})
        self.limit_ret_sta = pd.DataFrame({})
        self.time_len = pd.DataFrame({})
        self.limit_time_len = pd.DataFrame({})
        self.continue_ret = pd.DataFrame({})
        self.limit_continue_ret = pd.DataFrame({})
        self.continue_time = pd.DataFrame({})
        self.limit_continue_time = pd.DataFrame({})
        self.trade_result = pd.DataFrame({})



    def returns_sta(self, bottom, top):
        boduan = self.boduan
        rai = boduan[boduan.bd_type == "raise"].returns
        dec = boduan[boduan.bd_type == "decline"].returns



        rai_l = len(rai)
        dec_l = len(dec)
        rai = rai.sort_values()[int(bottom * rai_l):int(top * rai_l)]
        dec = dec.sort_values()[int(bottom * dec_l):int(top * dec_l)]

        rai_sta_adj = [rai.mean(), rai.std(), rai.quantile(), rai.max(), rai.min(), len(rai)]
        dec_sta_adj = [dec.mean(), dec.std(), dec.quantile(), dec.min(), dec.max(), len(dec)]

        return  pd.DataFrame(
            {'raise': rai_sta_adj, "decine": dec_sta_adj}, index=[
        'mean', 'std', 'median', 'max', 'min', 'sample_num']).T

    def time_sta(self, bottom, top):
        boduan = self.boduan
        rai = boduan[boduan.bd_type == "raise"].timedelta
        dec = boduan[boduan.bd_type == "decline"].timedelta
        rai_l = len(rai)
        dec_l = len(dec)
        rai = rai.sort_values()[int(bottom * rai_l):int(top * rai_l)]
        dec = dec.sort_values()[int(bottom * dec_l):int(top * dec_l)]

        rai_sta_adj = [rai.mean(), rai.std(), rai.quantile(), rai.max(), rai.min(), len(rai)]
        dec_sta_adj = [dec.mean(), dec.std(), dec.quantile(), dec.max(), dec.min(), len(dec)]

        return  pd.DataFrame(
            {'raise': rai_sta_adj, "decline": dec_sta_adj}, index=[
        'mean', 'std', 'median', 'max', 'min', 'sample_num']).T



    def continue_sta(self, bottom , top):
        boduan = self.boduan
        rai = boduan[boduan.bd_type == "raise"].afterreturns
        dec = boduan[boduan.bd_type == "decline"].afterreturns
        rai_l = len(rai)
        dec_l = len(dec)
        rai = rai.sort_values()[int(bottom * rai_l):int(top * rai_l)]
        dec = dec.sort_values()[int(bottom * dec_l):int(top * dec_l)]

        rai_sta_adj = [rai.mean(), rai.std(), rai.quantile(), rai.max(), rai.min(), rai[rai < 0.005].shape[0],
                       rai[rai < 0.005].shape[0] / (rai.shape[0] + 0.0), len(rai)]
        dec_sta_adj = [dec.mean(),
                       dec.std(),
                       dec.quantile(),
                       dec.max(),
                       dec.min(),
                       dec[dec > -0.005].shape[0],
                       dec[dec > -0.005].shape[0] / (dec.shape[0] + 0.0),
                       len(dec)]

        return  pd.DataFrame({'raise_returns': rai_sta_adj, "decline_returns": dec_sta_adj}, index=[
        'mean', 'std', 'median', 'max', 'min', 'invalid', 'percentage', 'sample_num']).T

    def continue_sta_day(self, bottom, top):
        boduan = self.boduan
        rai = boduan[boduan.bd_type == "raise"].aftertime
        dec = boduan[boduan.bd_type == "decline"].aftertime



        rai_l = len(rai)
        dec_l = len(dec)
        rai = rai.sort_values()[int(bottom * rai_l):int(top * rai_l)]
        dec = dec.sort_values()[int(bottom * dec_l):int(top * dec_l)]

        rai_sta_adj = [rai.mean(), rai.std(), rai.quantile(), rai.max(), rai.min(), rai[rai <= 3].shape[0],
                       rai[rai <= 3].shape[0] / (rai.shape[0] + 0.0), len(rai)]
        dec_sta_adj = [dec.mean(),
                       dec.std(),
                       dec.quantile(),
                       dec.max(),
                       dec.min(),
                       dec[dec <= 3].shape[0],
                       dec[dec <= 3].shape[0] / (dec.shape[0] + 0.0),
                       len(dec)]


        return pd.DataFrame({'rasie_time': rai_sta_adj, "decline_time": dec_sta_adj}, index=[
        'mean', 'std', 'median', 'max', 'min', 'invalid', 'percentage', 'sample_num']).T

    def trade_boduan(self, ratio):
        close = self.close
        boduan = self.boduan
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

    def result(self):
        self.ret_sta = self.returns_sta(0.0, 1.0)
        self.limit_ret_sta = self.returns_sta(0.1, 0.9)
        self.time_len = self.time_sta(0.0, 1.0)
        self.limit_time_len = self.time_sta(0.1, 0.9)
        self.continue_ret = self.continue_sta(0.0, 1.0)
        self.limit_continue_ret = self.continue_sta(0.1, 0.9)
        self.continue_time = self.continue_sta_day(0.0, 1.0)
        self.limit_continue_time = self.continue_sta_day(0.1, 0.9)
        self.trade_result = self.trade_boduan(0.0)