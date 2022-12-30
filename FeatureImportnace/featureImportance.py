import json
import numpy
import os
from utils import *


def parse_prev_run(prev_design_name:str=None):
    """
    Parse data with previous design name. 
    
    If there is any run of prev design, it will return the result in "list"
    Else, it will return "None"
    """
    if prev_design_name is None:
        raise ValueError("Prev design name must be given")
    ppa_json = config.server_ppa
    if not os.path.isfile(ppa_json):
        raise FileNotFoundError("File {} not exists".format(ppa_json))
    with open(ppa_json, "r") as f:
        ppa = json.load(f)
    if prev_design_name not in ppa.keys():
        # There is no run for previous design
        return None
    if len(ppa.keys()) == 0: 
        # There is previous design name, but there is no run
        return None
    prev_runs = ppa(prev_design_name)
    prev_results = []
    for param_set in prev_runs.keys():
        param_list = param_set.split("_")
        for i in range(len(param_list)):
            if check_int(param_list[i]):
                param_list[i] = int(param_list[i])
        run_ppa_result = prev_runs[param_set]
        label = [run_ppa_result[config.result_name.power],
                 run_ppa_result[config.result_name.wns],
                 run_ppa_result[config.result_name.tns],
                 run_ppa_result[config.result_name.area],
                 run_ppa_result[config.result_name.wirelength]]
        prev_results.append([param_list, label])
    return prev_results


def get_sum_variance(prev_result: list, mask_idx: int or list) -> float:
    


class FeatureImportance:
    def __init__(self, prev_design_name:str=None, ppa_json:str=None,
                 weight:tuple=None) -> None:
        self.prev_design_name = prev_design_name
        self.ppa_json = ppa_json
        if weight is None:
            raise ValueError("Weight is mandatory for feature importance")
        self.weight = weight
        self.default_fi = [5, 5, 5, 5, 4, 4, 5, 4, 4, 3, 5, 4]

    def gen_fi(self) -> list:
        if self.prev_design_name is None:
            return self.default_fi
