import xgboost as xgb
import pandas as pd
import numpy as np
from ..RunParser import RunParser


class Trainer:
    def __init__(self, cluster: dict, mode: str,
                 result: dict, weight: tuple):
        self.cluster = cluster
        self.mode = mode.lower()
        self.result = result
        self.weight = weight
        self.reg = None

    def construct_data(self):
        data = []
        result = []
        for param in self.result.keys():
            data.append(list(param))
            if self.mode == "power":
                result.append(self.result[param]["power"])
            elif self.mode == "performance":
                result.append(self.result[param]["performance"])
            elif self.mode == "area":
                result.append(self.result[param]["area"])
            else:
                score = self.weight[0] * self.result[param]["power"]
                score += self.weight[1] * self.result[param]["performance"]
                score += self.weight[2] * self.result[param]["area"]
                result.append(score)
        data = np.array(data)
        result = np.array(result)
        X = pd.DataFrame(data)
        y = pd.DataFrame(result)
        return X, y

    def train(self, max_depth=int, learning_rate=0.001):
        X, y = self.construct_data()
        # data_dmatrix = xgb.DMatrix(data=X, label=y)
        self.reg = xgb.XGBRegressor(learning_rate=learning_rate,
                                    max_depth=max_depth)
        self.reg.fit(X, y)
