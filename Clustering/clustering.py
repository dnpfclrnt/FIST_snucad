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


def permute(root_list: list, depth: int = 0):
    """
    This generates entire combinations of several lists
    :param root_list: List of lists to combine
    :param depth: Needed for recursion
    :return: Combined set of lists
    """
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


class Cluster:
    def __init__(self, important_feature: list, param_setup: dict):
        """
        This is cluster itself.
        :param important_feature: This saves the value of important features
        ex) [500, 500, None, None, 80, 4, 5, 20, None, None, None, low, false]
        :param param_setup: dictionary files loaded from assets/setup.json
        """
        self.important_feature = important_feature
        self.param_setup = param_setup

    def random_gen(self):
        """
        This function is used to generate random parameter set
        """
        def gen(param: dict or list):
            if type(param) == dict:
                return random.randrange(param["min"], param["max"], param["step"])
            else:
                return random.sample(param, 1)[0]
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

    def generate_all(self):
        """
        This generates entire parameter set
        :return: All possible combination sets.
        """
        entire_set = []
        for i in range(12):
            if self.important_feature[i] is not None:
                entire_set.append([self.important_feature[i]])
            else:
                param = self.param_setup[param_list[i]]
                if type(param) is dict:
                    current = range(param["min"], param["max"] + 1, param["step"])
                    entire_set.append(current)
                elif type(param) is list:
                    entire_set.append(param)
                else:
                    raise TypeError("Setup must be dict of list type")
        return permute(entire_set)


class ClusterGen:
    def __init__(self, feature_importance: list, param_setup_json: str,
                 num_important_feature: int = 6):
        """
        This will automatically generate the list of classes
        :param feature_importance:  Feature importance calculated from featureImportance.py
        :param param_setup_json: assets/setup.json
        :param num_important_feature: number of important features. Default = 6
        """
        if not os.path.isfile(param_setup_json):
            raise FileExistsError("{}: File not found".format(param_setup_json))
        with open(param_setup_json, "r") as f:
            param_setup = json.load(f)
        temp_fi = feature_importance.copy()
        temp_fi.sort()
        threshold = temp_fi[11 - num_important_feature]
        print("=================================")
        print("threshold")
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
        for param_set in tqdm(permute(temp)):
            cluster = Cluster(param_set, param_setup)
            self.cluster_list.append(cluster)

    def generate_param_set_model_less(self, num_params: int = 100):
        """
        Generates the number of requested samples
        This will be used in model-less sampling
        :param num_params: number of clusters to generate parameter
        :return: List of parameter set
        """
        random_clusters = random.sample(self.cluster_list, num_params)
        samples = []
        sample_cluster = []
        for cluster in random_clusters:
            samples.append(cluster.random_gen())
            idx = self.cluster_list.index(cluster)
            cur_cluster = self.cluster_list.pop(idx)
            sample_cluster.append(cur_cluster)
        return samples, sample_cluster

    def get_random_cluster(self, num_cluster: int = 50):
        random_clusters = random.sample(self.cluster_list, num_cluster)
        return random_clusters
