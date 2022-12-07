import json
import random
import os
from tqdm import tqdm


_clk = "CLOCK_PERIOD"
_core = "CORE_UTIL"
_fo = "set_max_fanout"
_tran = "set_max_transition"
_cap = "set_max_capacitance"
_eco = "eco_max_distance"
_dense = "max_density"
_wire = "wire_length_opt"
_timing = "timing_effort"
_clk_pwr = "clock_power_driven"
_congest = "congestion_effort"
_uniform = "uniform_density"
param_list = ["CLOCK_PERIOD", "CORE_UTIL",
              "set_max_fanout", "set_max_transition",
              "set_max_capacitance", "eco_max_distance",
              "max_density", "wire_length_opt",
              "timing_effort", "clock_power_driven",
              "congestion_effort", "uniform_density"]


class Cluster:
    def __init__(self, important_feature: list, param_setup: dict):
        """
        This is cluster itself.
        :param important_feature: This saves the value of important features
        ex) [500, 500, None, None, 80, 4, 5, 20, None, None, None, low, false]
        :param param_setup:
        """
        self.important_feature = important_feature
        self.param_setup = param_setup

    def random_gen(self):
        """
        This function is used to generate random paramter set
        """
        def gen(param: dict or list):
            if type(param) == dict:
                return random.randrange(param["min"], param["max"], param["step"])
            else:
                return random.sample(param, 1)
        param_set = []
        idx = 0
        for feature in self.important_feature:
            if feature is not None:
                param_set.append(feature)
            else:
                parameter = gen(self.param_setup[param_list[idx]])
                param_set.append(parameter)
            idx += 1
        return param_set


class ClusterGen:
    def __init__(self, feature_importance: list, param_setup_json: str,
                 num_important_feature: int):
        if not os.path.isdir(param_setup_json):
            raise FileExistsError("{}: File not found".format(param_setup_json))
        with open(param_setup_json, "r") as f:
            param_setup = json.load(f)
        temp_fi = feature_importance
        temp_fi.sort()
        threshold = temp_fi[11 - num_important_feature]

        def permute(root_list: list, depth: int):
            if depth == len(root_list) - 1:
                if root_list[depth] is None:
                    current_list = [[None]]
                else:
                    current_list = []
                    for element in root_list[depth]:
                        current_list.append([element])
                return current_list
            else:
                after_lists = permute(root_list, depth+1)
                dest_list = []
                if root_list[depth] is None:
                    for after in after_lists:
                        after.insert(0, None)
                        dest_list.append(after)
                else:
                    for after in after_lists:
                        for element in root_list[depth]:
                            current = after.copy()
                            current.insert(0, element)
                            dest_list.append(current)
                return dest_list

        temp = []
        self.cluster_list = []
        for i in range(12):
            if feature_importance[i] < threshold:
                temp.append(None)
            else:
                setup = param_setup[param_list[i]]
                if type(setup) == dict:
                    to_list = range(setup["min"], setup["max"] + 1,
                                    setup["step"])
                    temp.append(to_list)
                else:
                    temp.append(setup)
        for param_set in permute(temp, 0):
            cluster = Cluster(param_set, param_setup)
            self.cluster_list.append(cluster)
