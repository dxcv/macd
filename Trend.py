import pandas as pd
import numpy as np


class Trend:

    def __init__(self):
        pass

    @staticmethod
    def MA_mark(close, period):
        ma_close = pd.rolling_mean(close, window=period)
        ma_close = ma_close.dropna()
        close = close.ix[ma_close.index]
        bias = (close - ma_close).values
        close = close.values
        price_change = []
        for i in range(1, len(ma_close)):

            if bias[i - 1] < 0 < bias[i]:
                price_change.append(1)

            if bias[i - 1] > 0 > bias[i]:
                price_change.append(-1)

            if bias[i - 1] > 0 and bias[i] > 0 and close[i] > close[i - 1]:
                price_change.append(1)

            if bias[i - 1] > 0 and bias[i] > 0 and close[i] < close[i - 1]:
                price_change.append(0)

            if bias[i - 1] < 0 and bias[i] < 0 and close[i] > close[i - 1]:
                price_change.append(0)

            if bias[i - 1] < 0 and bias[i] < 0 and close[i] < close[i - 1]:
                price_change.append(-1)

        distance = [np.sum(price_change[:i])
                    for i in range(0, len(price_change))]
        return distance

    @staticmethod
    def Trend_continue(distance):
        breakpoint = list()
        #distance = self.distance
        breakpoint.append(0)
        for i in range(1, len(distance) - 1):
            if distance[i + 1] != distance[i]:
                flag = True
                j = i - 1
                temp = 0
                while flag and j >= 0:
                    temp = distance[i] - distance[j]
                    if temp != 0:
                        flag = True
                    j -= 1

                if temp * (distance[i] - distance[i + 1]) < 0:
                    breakpoint.append(i)
        breakpoint.append(len(distance) - 1)
        breakpoint_value = [distance[i] for i in breakpoint]
        D = np.array([breakpoint_value[i] - breakpoint_value[i - 1]
                      for i in range(1, len(breakpoint_value))])

        return np.sum(D**2)

    def fluctutate_interval(self, distance):
        if not distance:
            return []
        else:
            n = len(distance)
            max_gap = 0
            for j in range(n):
                for k in range(n):
                    if np.abs(distance[j] - distance[k]) > max_gap:
                        max_gap = np.abs(distance[j] - distance[k])

            Tao = []
            for y in range(n):
                for x in range(y):
                    if np.abs(distance[x] - distance[y]) == max_gap:
                        Tao.append([x, y])

            x_bound = n
            choose_pair = []
            for pair in Tao:
                if pair[0] < x_bound:
                    x_bound = pair[0]
                    choose_pair = pair
            if choose_pair[0] == 0:
                left_interval = []
            else:
                left_interval = distance[:choose_pair[0] + 1]
            if choose_pair[1] == n - 1:
                right_interval = []
            else:
                right_interval = distance[choose_pair[1]:]
            result = list()
            result.append(choose_pair)
            result.extend(self.fluctutate_interval(left_interval))
            right_result = self.fluctutate_interval(right_interval)
            if right_result:
                right_result = [[pair[0] +
                                 choose_pair[1], pair[1] +
                                 choose_pair[1]] for pair in right_result]

            result.extend(right_result)
            return result

    def Trend_fluctuate(self, distance):
        pair_list = self.fluctutate_interval(distance)
        distance_list = np.array(
            [distance[pair[0]] - distance[pair[1]] for pair in pair_list])
        return np.sum(distance_list**2)

    def Trend_caculate(self, close, period):
        distance = self.MA_mark(close, period)
        N = len(distance)
        return max(self.Trend_continue(distance),
                   self.Trend_fluctuate(distance)) / np.power(N, 1.5)
