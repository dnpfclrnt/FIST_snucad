import xgboost as xgb
import pandas as pd
import numpy as np

from RunParser import *
# from ..RunParser import *
sample = [350.0, 80.0, '64', 160.0, 12.0, 10.0, 80.0, 'none', 'high', 'standard', 'medium', 'false']
none = "none"
low = "low"
medium = "medium"
high = "high"
standard = "standard"
true = "true"


def convert_enum(cur: list):
    for j in range(len(cur)):
        if cur[7] == none:
            cur[7] = 0
        elif cur[7] == medium:
            cur[7] = 1
        else:
            cur[7] = 2

        if cur[8] == medium:
            cur[8] = 0
        else:
            cur[8] = 1

        if cur[9] == low:
            cur[9] = 0
        elif cur[9] == standard:
            cur[9] = 1
        else:
            cur[9] = 2

        if cur[10] == low:
            cur[10] = 0
        elif cur[10] == medium:
            cur[10] = 1
        elif cur[10] == high:
            cur[10] = 2
        else:
            cur[10] = 3

        if cur[11] == true:
            cur[11] = 0
        else:
            cur[11] = 1
    return cur


class Trainer:
    def __init__(self, mode: str, result: dict, weight: tuple):
        self.mode = mode.lower()
        self.result = result
        self.weight = weight
        self.model = None

    def construct_data(self):
        data = []
        result = []
        for param in self.result.keys():
            data.append(decode(param))
            if self.mode == "power":
                result.append(self.result[param]["power"])
            elif self.mode == "performance":
                perf = self.result[param]["wns"] * self.weight[1]
                perf = self.result[param]['tns'] * self.weight[2]
                result.append(perf)
            elif self.mode == "area":
                result.append(self.result[param]["area"])
            else:
                score = self.weight[0] * self.result[param]["power"]
                score += self.weight[1] * self.result[param]["tns"]
                score += self.weight[3] * self.result[param]["wns"]
                score += self.weight[2] * self.result[param]["area"]
                score += self.weight[3] * self.result[param]["wire_length"]
                result.append(score)
        for i in range(len(data)):
            data[i] = convert_enum(data[i])

            # print("data: ", data[i], "result: ", result[i])

        data = np.array(data)
        result = np.array(result)
        X = pd.DataFrame(data)
        y = pd.DataFrame(result)
        return X, y

    def train(self, max_depth=int, learning_rate=0.001):
        X, y = self.construct_data()
        # data_dmatrix = xgb.DMatrix(data=X, label=y)
        self.model = xgb.XGBRegressor(learning_rate=learning_rate,
                                      max_depth=max_depth)
        self.model.fit(X, y)

    def predict(self, param_set: list):
        data = convert_enum(param_set)
        data = np.array(data)
        print("data = ", data, len(data), type(data))
        return self.model.predict(data)
