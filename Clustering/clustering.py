import json
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


class Cluster:
    def __init__(self, feature_importance: list, num_important: int):
        self.fi = feature_importance
        self.sort = feature_importance
        self.sort.sort()
        threshold = self.sort[num_important - 1]
        self.important_features = []
        self.param_dict = {}
        self.cluster_dict = {}
        idx = 0
        for fi in self.fi:
            if fi > threshold:
                self.important_features.append(idx)

    def encode(self, params: list):
        if len(params) != 12:
            raise ValueError("Number of params must be 12 got", len(params))
        idx = 0
        encoded = []
        for param in params:
            if idx not in self.important_features:
                idx += 1
                continue
            else:
                enc = param
                if type(param) is not str:
                    enc = str(param)
                encoded.append(enc)
                idx += 1
        return "_".join(encoded)

    def gen_cluster(self, json_path: str):
        with open(json_path, "r") as f:
            setting = json.load(f)

        # Create param dict
        for param in setting.keys():
            if type(setting[param]) is list:
                self.param_dict[param] = setting[param]
            elif type(setting[param]) is dict:
                if "min" not in setting[param].keys() or \
                    "max" not in setting[param].keys() or \
                        "step" not in setting[param].keys():
                    raise ValueError("There must be min, max, step in \
                                     parameter setting for {}".format(param))

                def convert(target: dict):
                    num_step = (target["max"] - target["min"]) // target["step"]
                    if target["max"] != target["min"] + num_step * target["step"]:
                        raise ValueError("There is some remainder for \
                                        current parameter setting")
                    ret = []
                    for i in range(num_step):
                        ret.append(target["min"] + target["step"] * i)
                    return ret

                self.param_dict[param] = convert(setting[param])
            else:
                raise TypeError("Parameter setting must be either dict / list")
        permute = self.permute()

        for param_set in permute:
            key = self.encode(param_set)
            if key not in self.cluster_dict.keys():
                self.cluster_dict[key] = [param_set]
            else:
                self.cluster_dict[key].append(param_set)

    def permute(self):
        target = self.param_dict
        ret = []
        for clk in target[_clk]:
            for core in target[_core]:
                for fo in target[_fo]:
                    for tran in target[_tran]:
                        for cap in target[_cap]:
                            for eco in target[_eco]:
                                for den in target[_dense]:
                                    for wire in target[_wire]:
                                        for timing in target[_timing]:
                                            for clk_pwr in target[_clk_pwr]:
                                                for cong in target[_congest]:
                                                    for uni in target[_uniform]:
                                                        ret.append([clk, core, fo, tran, cap, eco, den,
                                                                    wire, timing, clk_pwr, cong, uni])
        return  ret
