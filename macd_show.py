# -*- coding: utf-8 -*-
from macd_split import *
from sta import *
from inject import *
from Tkinter import *
import tkFileDialog
import pandas as pd
import os
ISOTIMEFORMAT = "%Y-%m-%d %X"
root_user = Tk()


def getYesterday():
    today = datetime.date.today()
    oneday = datetime.timedelta(days=0)
    yesterday = today - oneday
    return yesterday


class Show_Macd:

    def __init__(self, root):
        self.root = root
        frame = Frame(self.root, width=200, height=200)

        Button(
            frame,
            text="从文件导入分钟数据",
            command=lambda: self.openfile(),
            font=(
                "Arial",
                12),
            width=20,
            height=2).pack(
            side=TOP)

        Button(
            frame,
            text="从wind导入近期分钟数据",
            command=lambda: self.wind_data_min(),
            font=(
                "Arial",
                12),
            width=20,
            height=2).pack(
            side=TOP)

        Button(
            frame,
            text="从wind导入近期日线数据",
            command=lambda: self.wind_data_day(),
            font=(
                "Arial",
                12),
            width=20,
            height=2).pack(
            side=TOP)

        Button(
            frame,
            text="得到价格分段数据",
            command=lambda: self.execute(),
            font=(
                "Arial",
                12),
            width=20,
            height=2).pack(
            side=BOTTOM)

        Button(
            frame,
            text="波段统计",
            command=lambda: self.tongji(),
            font=(
                "Arial",
                12),
            width=20,
            height=2).pack(
            side=BOTTOM)

        Button(
            frame,
            text="储存",
            command=lambda: self.save(),
            font=(
                "Arial",
                12),
            width=20,
            height=2).pack(
            side=BOTTOM)

        self.t1 = Text(frame, width=100, height=40)
        self.t1.pack()
        self.t2 = Text(frame, width=20, height=2)
        self.t2.pack()
        v1 = StringVar()
        v2 = StringVar()
        v_file = StringVar()

        l = Label(frame, text="请在第一行输入万德指数代码，第二行输入窗口时间(天),第三行输入存储位置",
                  bg="green", font=("Arial", 12), width=70, height=2)

        self.l = l
        self.l.pack()

        self.v1 = v1
        self.v1.set("")
        e1 = Entry(frame, textvariable=v1, width=30)
        self.e1 = e1
        self.e1.pack(padx=20)

        self.v2 = v2
        self.v2.set("")
        e2 = Entry(frame, textvariable=v2, width=30)
        self.e2 = e2
        self.e2.pack(padx=20)

        self.v_file = v_file
        self.v_file.set("")
        e_file = Entry(frame, textvariable=v_file, width=30)
        self.e_file = e_file
        self.e_file.pack(padx=20)
        frame.pack()

        self.fname = ""
        self.day_close = pd.DataFrame({})
        self.min_close = pd.DataFrame({})
        self.minute = MACD_split(self.min_close)
        self.day = MACD_split(self.day_close)
        self.min_sta = statistic(self.minute)
        self.day_sta = statistic(self.day)
        self.mapping_object = inject(self.minute, self.day)

    def openfile(self):
        self.t2.delete(0.0, END)
        num = int(self.v2.get())
        fname = tkFileDialog.askopenfilename()
        self.fname = fname
        priceSeries = pd.read_excel(self.fname)
        priceSeries['time'] = priceSeries['time'].map(
            lambda x: datetime.datetime.strptime(
                str(x), "%Y-%m-%d %H:%M:%S"))
        priceSeries = priceSeries.set_index("time")
        nowtime = getYesterday().strftime('%Y-%m-%d') + " 15:01:00"
        lasttime = priceSeries.index[-1]
        code = self.v1.get()
        newdata = get_min_data(code, ["close"], 30, lasttime, nowtime)
        close = pd.concat([priceSeries.close, newdata[1:].close])
        self.min_close = close[-num * 8:]
        self.minute = MACD_split(self.min_close)
        if newdata.shape[0] >= 40:
            close_df = pd.DataFrame({'time': list(close.index), 'close': close})
            close_df.to_excel(self.fname)
        self.t2.insert(END, "导入分钟数据完毕！")

    def wind_data_min(self):
        self.t2.delete(0.0, END)
        code = self.v1.get()
        num = self.v2.get()
        num = int(num)
        nowtime = getYesterday().strftime('%Y-%m-%d') + " 15:01:00"
        lasttime = w.tdaysoffset(-num,
                                 nowtime).Data[0][0].strftime("%Y-%m-%d %X")
        close = get_min_data(code, ["close"], 30, lasttime, nowtime).close
        self.min_close = close
        self.minute = MACD_split(self.min_close)
        self.t2.insert(END, "导入分钟数据完毕！")

    def wind_data_day(self):
        self.t2.delete(0.0, END)
        code = self.v1.get()
        num = self.v2.get()
        num = int(num)
        nowtime = getYesterday().strftime('%Y-%m-%d')
        if num == 0:
            lasttime = self.min_close.index[0]
        else:
            lasttime = w.tdaysoffset(-num,
                                     nowtime).Data[0][0].strftime("%Y-%m-%d %X")
        close = get_data(code, ["close"], "D", lasttime, nowtime).close
        self.day_close = close
        self.day = MACD_split(self.day_close)
        self.t2.insert(END, "导入日数据完毕！")

    def price_split(self, ptype):

        if ptype == "day":
            self.day.run()
            date, bd_type = self.day.now_situation()
            boduan = self.day.boduan
        else:
            self.minute.run()
            date, bd_type = self.minute.now_situation()
            boduan = self.minute.boduan

        code = self.v1.get()
        self.t1.insert(END, "============================================\n")
        self.t1.insert(END, "指数价格分段%s\n" % code)
        self.t1.insert(
            END, "波段开始时间          波段结束时间          波段确认时间          波段涨跌\n")

        for i in range(boduan.shape[0]):
            temp = boduan.iloc[i]
            self.t1.insert(END, str(temp.start_date) +
                           "   " +
                           str(temp.end_date) +
                           "   " +
                           str(temp.comfirm_date) +
                           "   " +
                           temp.bd_type +
                           "\n")

        if date:
            if bd_type == "raise":
                self.t1.insert(END, "在%s确认上涨趋势\n" % date)
            else:
                self.t1.insert(END, "在%s确认下跌趋势\n" % date)

    def execute(self):
        self.price_split("minute")
        self.price_split("day")

    def tongji(self):
        min_sta = statistic(self.minute)
        day_sta = statistic(self.day)
        mapping_object = inject(self.minute, self.day)
        self.day_sta = day_sta
        self.min_sta = min_sta
        self.min_sta.result()
        self.day_sta.result()
        mapping_object.run()
        self.mapping_object = mapping_object
        self.minute = mapping_object.minute
        self.day = mapping_object.day

    def save(self):
        filepath = self.e_file.get()
        code = self.v1.get()
        filepath += "\%s" % code
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        min_boduan = self.minute.boduan
        day_boduan = self.day.boduan
        day_time_len = self.day_sta.time_len
        day_limit_time_len = self.day_sta.limit_time_len
        day_ret_sta = self.day_sta.ret_sta
        day_limit_ret_sta = self.day_sta.limit_ret_sta
        day_continue_ret = self.day_sta.continue_ret
        day_limit_continue_ret = self.day_sta.limit_continue_ret
        day_continue_time = self.day_sta.limit_continue_time
        day_limit_continue_time = self.day_sta.limit_continue_time

        min_time_len = self.min_sta.time_len
        min_limit_time_len = self.min_sta.limit_time_len
        min_ret_sta = self.min_sta.ret_sta
        min_limit_ret_sta = self.min_sta.limit_ret_sta
        min_continue_ret = self.min_sta.continue_ret
        min_limit_continue_ret = self.min_sta.limit_continue_ret
        min_continue_time = self.min_sta.limit_continue_time
        min_limit_continue_time = self.min_sta.limit_continue_time

        misplace_point = self.mapping_object.misplace_point
        zuji = self.mapping_object.zuji_situation
        tupo = self.mapping_object.tupo_situation
        zt = self.mapping_object.zujiplustupo

        writer_day = pd.ExcelWriter(filepath + "\\day_boduan.xlsx")
        writet_minute = pd.ExcelWriter(filepath + "\\minute_boduan.xlsx")
        writer_pre = pd.ExcelWriter(filepath + "\\pre_judge.xlsx")

        day_boduan.to_excel(writer_day, sheet_name="day_boduan")
        day_ret_sta.to_excel(writer_day, sheet_name="day_ret_sta")
        day_limit_ret_sta.to_excel(writer_day, sheet_name="day_limit_ret_sta")
        day_time_len.to_excel(writer_day, sheet_name="day_time_len")
        day_limit_time_len.to_excel(
            writer_day, sheet_name="day_limit_time_len")
        day_continue_ret.to_excel(writer_day, sheet_name="day_continue_ret")
        day_limit_continue_ret.to_excel(
            writer_day, sheet_name="day_limit_continue_ret")
        day_continue_time.to_excel(writer_day, sheet_name="day_continue_time")
        day_limit_continue_time.to_excel(
            writer_day, sheet_name="day_limit_continue_time")

        min_boduan.to_excel(writet_minute, sheet_name="min_boduan")
        min_ret_sta.to_excel(writet_minute, sheet_name="min_ret_sta")
        min_limit_ret_sta.to_excel(
            writet_minute, sheet_name="min_limit_ret_sta")
        min_time_len.to_excel(writet_minute, sheet_name="min_time_len")
        min_limit_time_len.to_excel(
            writet_minute, sheet_name="min_limit_time_len")
        min_continue_ret.to_excel(writet_minute, sheet_name="min_ret_sta")
        min_limit_continue_ret.to_excel(
            writet_minute, sheet_name="min_continue_ret")
        min_continue_time.to_excel(
            writet_minute, sheet_name="min_continue_time")
        min_limit_continue_time.to_excel(
            writet_minute, sheet_name="min_limit_continue_time")

        misplace_point.to_excel(writer_pre, sheet_name="misplace")
        zuji.to_excel(writer_pre, sheet_name="zuji")
        tupo.to_excel(writer_pre, sheet_name="tupo")
        zt.to_excel(writer_pre, sheet_name="zt")
        writer_day.save()
        writet_minute.save()
        writer_pre.save()
        code_data_split = self.day

        writer_boduan = pd.ExcelWriter(filepath + "\\boduan_mapping.xlsx")
        duan_detail = self.mapping_object.min_boduan_list
        for i in range(len(duan_detail)):
            ithbd = code_data_split.boduan.ix[i]
            start = ithbd.start_date.strftime("%Y-%m-%d")
            end = ithbd.end_date.strftime("%Y-%m-%d")
            duan_detail[i].to_excel(writer_boduan,
                                    sheet_name=start + "-%s.csv" % end)
        writer_boduan.save()


sa = Show_Macd(root_user)
root_user.mainloop()
