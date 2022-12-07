import xgboost as xgb
import pandas as pd
import numpy as np
from ..RunParser import *


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

    def predict(self, param_set: pd.DataFrame):
        return self.model.predict(param_set)
