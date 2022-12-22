import numpy as np
import json
import os


class PrevRunParser:
    def __init__(self, PPA_json: str, target_design: str,
                 weight: tuple):
        """
        This class parses previous design
        :param PPA_json:  A json file that saves PPA from prev designs
        :param target_design: Design to get transferred from
        :param weight: weight for PPA. This will be used to calculate scores
        """
        if not os.path.isfile(PPA_json):
            raise ValueError("PPA json file not exists")
        with open(PPA_json) as f:
            ppa = json.load(f)
        self.prev_ppa = ppa[target_design]
        self.weight = weight
        self.prev_runs = []
        for param_str in self.prev_ppa.keys():
            run = self.prev_ppa[param_str]
            param_set = "_".split(param_str)
            label = [run["power"], run["wns"], run["tns"], run["area"], run["wire_length"]]
            for i in range(len(label)):
                label[i] = float(label[i])
            wa = weight[0] * label[0]
            wa += weight[1] * label[1]
            wa += weight[2] * label[2]
            wa += weight[3] * label[3]
            wa += weight[4] * label[4]
            label.append(wa)
            self.prev_runs.append([param_set, label])

    def encode(self, param_set: list, idx: int or list):
        """
        This method encodes a parameter set with masking
        :param param_set: a list of parameters
        :param idx: target index to mask
        :return: returns a string of parameters in encoded form
        """
        enc = []
        cur_idx = 0
        for param in param_set:
            converted = param
            if type(param) is not str:
                converted = str(param)
            if type(idx) == list:
                if cur_idx in idx:
                    enc.append(converted)
            elif type(idx) == int:
                if cur_idx != idx:
                    enc.append(converted)
            else:
                raise TypeError("Idx must be int or list type")
            cur_idx += 1
        enc = "_".join(enc)
        return enc

    def get_sum_variance(self, idx: int, mode: str):
        """
        This calculates the sum of variance
        With masking target index, this will calculate the feature importance.
        :param idx: target parameter index
        :param mode: metric. "power", "performance", "area", "all"
        :return: sum of variances
        """
        mode = mode.lower()
        if mode not in ["power", "performance", "area", "all"]:
            raise ValueError("Mode must be one of 'power', 'performance', 'area', \
            'all' got {}".format(mode))
        runs = self.prev_runs
        encoded = {}
        for run in runs:
            param_set = run[0]
            enc = self.encode(param_set, idx)
            print(enc)
            if enc in encoded.keys():
                if mode == "power":
                    encoded[enc].append(run[1][0])
                elif mode == "performance":
                    perf = run[1][1] * self.weight[1]
                    perf += run[1][2] * self.weight[2]
                    encoded[enc].append(perf)
                elif mode == "area":
                    encoded[enc].append(run[1][3])
                elif mode == "all":
                    encoded[enc].append(run[1][-1])
            else:
                if mode == "power":
                    encoded[enc] = [run[1][0]]
                elif mode == "performance":
                    perf = run[1][1] * self.weight[1]
                    perf += run[1][2] * self.weight[2]
                    encoded[enc] = [perf]
                elif mode == "area":
                    encoded[enc] = [run[1][3]]
                elif mode == "all":
                    encoded[enc] = [run[1][-1]]
        sum_var = 0
        for feature in encoded.keys():
            score_arr = np.array(encoded[feature])
            var = float(np.var(score_arr))
            sum_var += pow(var, 2)
        return sum_var


class FeatureImportance:
    def __init__(self, PPA_json=None, target_design=None, weight=None,
                 prev_data=False):
        """
        This will calculate the feature importance
        according to the paper FIST
        :param prev_data: if there is any previous data, it's better to used this as True
        """
        self.prev_data = prev_data
        self.default_importance = [5, 5, 5, 5, 4, 4, 5, 4, 4, 3, 5, 4]
        self.ppa_json = PPA_json
        self.target_design = target_design
        self.weight = weight
        self.prev_run = None
        self.mode = None

    def gen_feature_importance(self, mode=None):
        """
        This will generate feature importance of parameters
        according to previous run
        :param mode: mode is analysis type mode
            ["power", "performance", "area", "all"]
        :return:
        """
        if self.prev_data is False:
            return self.default_importance
        else:
            self.load(mode)
            if self.prev_run is None \
                    or self.mode is None:
                raise ValueError("There is no previous run")

            importance = []
            for i in range(12):
                var = self.prev_run.get_sum_variance(i, self.mode)
                importance.append(var)
            return importance

    def load(self, mode: str):
        self.prev_run = PrevRunParser(PPA_json=self.ppa_json,
                                      target_design=self.target_design,
                                      weight=self.weight)
        self.mode = mode
