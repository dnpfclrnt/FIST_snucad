import xgboost as xgb
import pandas as pd


class Trainer:
    def __init__(self, cluster: dict, mode:str):
        self.cluster = cluster
        self.mode = mode
