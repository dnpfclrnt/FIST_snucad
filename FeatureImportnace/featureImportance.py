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
        for param_str in self.prev_ppa.keys():
            run = self.prev_ppa[param_str]
            param_set = "_".split(param_str)
            label = [run["power"], run["wns"], run["tns"], run["area"], run["wirelength"]]
            wa = weight[0] * label[0]
            wa += weight[1] * label[1]
            wa += weight[2] * label[2]
            label.append(wa)
            self.prev_runs.append([param_set, label])



class PrevSamples:
    def __init__(self, PPA_json: str, weight: tuple):
        if os.path.isfile(PPA_json):
            raise ValueError("PPA json does not exists")
        with open(PPA_json) as f:
            ppa = json.load(f)
        self.prev_runs = []
        self.weight = weight
        for key in ppa.keys():
            run = ppa[key]
            single_feature = [run["CLOCK_PERIOD"], run["CORE_UTIL"],
                              run["set_max_fanout"], run["set_max_transition"],
                              run["set_max_capacitance"],
                              run["eco_max_distance"], run["max_density"],
                              run["wire_length_opt"], run["timing_effort"],
                              run["clock_power_driven"], run["congestion_effort"],
                              run["uniform_density"]]
            label = [run["power"], run["perf"], run["area"], run["wirelength"]]
            wa = weight[0] * label[0]
            wa += weight[1] * label[1]
            wa += weight[2] * label[2]
            label.append(wa)
            self.prev_runs.append([single_feature, label])

    def encode(self, param_set: list, idx: int):
        # idx means masking idx
        enc = []
        cur_idx = 0
        for feature in param_set:
            if cur_idx != idx:
                converted = feature
                if type(feature) is not str:
                    converted = str(feature)
                enc.append(converted)
            idx += 1
        enc = "_".join(enc)
        return enc, self.prev_runs[idx][1]

    def get_variance(self, idx: int, mode: str):
        """
        This calculates the sum of variance
        :param idx: target parameter index
        :param mode: metric. "power", "performance", "area", "all"
        :return:
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
            if enc in encoded.keys():
                if mode == "power":
                    encoded[enc].append(run[1][0])
                elif mode == "performance":
                    encoded[enc].append(run[1][1])
                elif mode == "area":
                    encoded[enc].append(run[1][2])
                elif mode == "all":
                    encoded[enc].append(run[1][3])
            else:
                if mode == "power":
                    encoded[enc] = [(run[1][0])]
                elif mode == "performance":
                    encoded[enc] = [(run[1][1])]
                elif mode == "area":
                    encoded[enc] = [(run[1][2])]
                elif mode == "all":
                    encoded[enc] = [(run[1][3])]
        sum_var = 0
        for feature in encoded.keys():
            score_arr = np.array(encoded[feature])
            var = float(np.var(score_arr))
            sum_var += pow(var, 2)
        return sum_var


class FeatureImportance:
    def __init__(self, prev_data: bool):
        """
        This will calculate the feature importance
        according to the paper FIST
        :param prev_data: if there is any previous data, it's better to used this as True
        """
        self.prev_data = prev_data
        # CLOCK_PERIOD, CORE_UTIL, set_max_fanout, set_max_capacitance
        # eco_max_distance, max_density, wire_length_opt, timing_effort,
        # clock_power_driven, congestion_effort, uniform_density
        self.default_importance = [5, 5, 5, 5, 4, 4, 5, 4, 4, 3, 5, 4]
        self.prev_run = None
        self.mode = None

    def gen_feature_importance(self, sample=None, mode=None):
        if self.prev_data is False:
            return self.default_importance
        else:
            self.get_samples(sample, mode)
            if self.prev_run is None \
                    or self.mode is None:
                raise ValueError("There is no previous run")

            importance = []
            for i in range(12):
                var = self.prev_run.get_variance(i, self.mode)
                importance.append(var)
            return importance

    def get_samples(self, sample: PrevSamples, mode: str):
        self.prev_run = sample
        self.mode = mode
