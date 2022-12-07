import os
import sys
import numpy as np
from tqdm import tqdm

from FeatureImportnace import FeatureImportance
from Clustering import ClusterGen
from RunParser import *
from Model import Trainer
sys.path.insert(1, "../../")
from CADRunner import CADRunner
from DBWriter import DBWriter

data_dir = "/home/users/cad_data/"
ppa_filename = "ppa.json"
CAD_DIR = "/home/users/cjeon7/dso/snucad_placement_runner"
weight = (0.1, 0.1, 0.1, 0.1, 2)
none = "none"
low = "low"
medium = "medium"
high = "high"
standard = "standard"
true = "true"
false = "false"
auto = "auto"


def convert_enum_to_str(params: list):
    for i in range(len(params)):
        if params[7] == 0:
            params[7] = none
        elif params[7] == 1:
            params[7] = medium
        else:
            params[7] = high

        if params[8] == 0:
            params[8] = medium
        else:
            params[8] = high

        if params[9] == 0:
            params[9] = low
        elif params[9] == 1:
            params[9] = standard
        else:
            params[9] = high

        if params[10] == 0:
            params[10] = low
        elif params[10] == 1:
            params[10] = medium
        elif params[10] == 2:
            params[10] = high
        else:
            params[10] = auto

        if params[11] == 0:
            params[11] = true
        else:
            params[11] = false
    return params


class RunCAD:
    def __init__(self, design: str,
                 CLOCK_PERIOD=500, CORE_UTIL=70,
                 set_max_fanout=200, set_max_transition=200,
                 set_max_capacitance=4, eco_max_distance=15,
                 max_density=50, wire_length_opt="medium",
                 timing_effort="medium",
                 clock_power_driven="standard",
                 congestion_effort="auto",
                 uniform_density="false"):
        """
        This is running script for FIST
        To run snucad_placement_runner, it must follow current step.
        :param design: design to tune
        """
        self.design = design
        self.runner = CADRunner(mode="transfer",
                                stage="place",
                                design=self.design,
                                framework="FIST")
        self.runner.transfer_params(CLOCK_PERIOD=CLOCK_PERIOD,
                                    CORE_UTIL=CORE_UTIL,
                                    set_max_fanout=set_max_fanout,
                                    set_max_transition=set_max_transition,
                                    set_max_capacitance=set_max_capacitance,
                                    eco_max_distance=eco_max_distance,
                                    max_density=max_density,
                                    wire_length_opt=wire_length_opt,
                                    timing_effort=timing_effort,
                                    clock_power_driven=clock_power_driven,
                                    congestion_effort=congestion_effort,
                                    uniform_density=uniform_density)
        self.run_dir = self.runner.get_dir()
        self.result_dir = os.path.join(self.run_dir, "data", "02_pnr_c")
        self.writer = DBWriter(db_dir=data_dir,
                               design=self.design)

    def run(self):
        cur_dir = os.getcwd()
        prev_ppa = self.writer.check_prev_run(self.runner.str_param)
        if not os.path.isdir(self.result_dir):
            os.chdir(CAD_DIR)
            self.runner.run()
        else:
            if prev_ppa is not None:
                return prev_ppa
            else:
                os.chdir(CAD_DIR)
                self.runner.run()
        power, perf, area, wire_length = self.writer.parse(self.result_dir)
        self.writer.write(write_dir=data_dir, filename=ppa_filename,
                          param_set=self.runner.str_param)
        os.chdir(cur_dir)
        ppa = {
            'power': power,
            'wns': perf[0],
            'tns': perf[1],
            'area': area,
            'wire_length': wire_length
        }
        return ppa


class FIST:
    def __init__(self, cad_tool_dir: str, tune_design: str,
                 transfer_design: str = None, tune_target=None,
                 param_setup_json: str = None, num_important_feature: int = 5,
                 result_dir: str = "result"):
        self.cad_dir = cad_tool_dir
        self.tune_design = tune_design
        self.tune_target = tune_target
        self.transfer_design=transfer_design
        if transfer_design is None:
            feature_importance = FeatureImportance(weight=weight)
            self.feature_importance = feature_importance.gen_feature_importance()
        else:
            ppa_dir = os.path.join(data_dir, "ppa.json")
            feature_importance = FeatureImportance(PPA_json=ppa_dir,
                                                   target_design=transfer_design,
                                                   weight=weight,
                                                   prev_data=True)
            self.feature_importance = feature_importance.gen_feature_importance(tune_target)

        self.cluster_gen = ClusterGen(self.feature_importance,
                                      param_setup_json,
                                      num_important_feature)
        self.init_cluster_num = len(self.cluster_gen.cluster_list)
        self.all_cluster = self.cluster_gen.cluster_list.copy()
        self.runParser = RunParser(result_dir)
        self.model_less_result = None
        self.runs = {}

    def model_less(self, num_model_less: int):
        params, clusters = self.cluster_gen.generate_param_set_model_less(num_model_less)
        result_dict = {}
        idx = 0
        for param in params:
            runner = RunCAD(design=self.tune_design,
                            CLOCK_PERIOD=param[0],
                            CORE_UTIL=param[1],
                            set_max_fanout=param[2],
                            set_max_transition=param[3],
                            set_max_capacitance=param[4],
                            eco_max_distance=param[5],
                            max_density=param[6],
                            wire_length_opt=param[7],
                            timing_effort=param[8],
                            clock_power_driven=param[9],
                            congestion_effort=param[10],
                            uniform_density=param[11])
            ppa = runner.run()
            self.runParser.update_result(param, ppa)
            all_param = clusters[idx].generate_all()
            for key in ppa.keys():
                ppa[key] = float(ppa[key])
            self.runs[encode(param)] = ppa
            for feature in all_param:
                result_dict[encode(feature)] = ppa
            idx += 1
        self.model_less_result = result_dict
        return self.model_less_result

    def exploit(self, num_exploit: int):
        clusters = self.cluster_gen.get_random_cluster(num_exploit)
        for cluster in clusters:
            model = Trainer(mode=self.tune_target,
                            result=self.model_less_result,
                            weight=weight)
            model.train()
            param_set = cluster.generate_all()
            ppa = model.predict(param_set)
            max_idx = np.argmin(np.absolute(ppa))
            param = convert_enum_to_str(param_set[max_idx])
            runner = RunCAD(design=self.tune_design,
                            CLOCK_PERIOD=param[0],
                            CORE_UTIL=param[1],
                            set_max_fanout=param[2],
                            set_max_transition=param[3],
                            set_max_capacitance=param[4],
                            eco_max_distance=param[5],
                            max_density=param[6],
                            wire_length_opt=param[7],
                            timing_effort=param[8],
                            clock_power_driven=param[9],
                            congestion_effort=param[10],
                            uniform_density=param[11])
            ppa = runner.run()
            self.runParser.update_result(param, ppa)
            for key in ppa.keys():
                ppa[key] = float(ppa[key])
            self.runs[encode(param)] = ppa
            for feature in param_set:
                self.model_less_result[encode(feature)] = ppa

    def explore(self, num_explore: int):
        param_set = self.generate_all_params()
        for i in range(num_explore):
            model = Trainer(mode=self.tune_target,
                            result=self.runs,
                            weight=weight)
            model.train()
            ppa = model.predict(param_set)
            max_idx = np.argmin(np.absolute(ppa))
            param = convert_enum_to_str(param_set[max_idx])
            runner = RunCAD(design=self.tune_design,
                            CLOCK_PERIOD=param[0],
                            CORE_UTIL=param[1],
                            set_max_fanout=param[2],
                            set_max_transition=param[3],
                            set_max_capacitance=param[4],
                            eco_max_distance=param[5],
                            max_density=param[6],
                            wire_length_opt=param[7],
                            timing_effort=param[8],
                            clock_power_driven=param[9],
                            congestion_effort=param[10],
                            uniform_density=param[11])
            ppa = runner.run()
            self.runParser.update_result(param, ppa)
            for key in ppa.keys():
                ppa[key] = float(ppa[key])
            self.runs[encode(param)] = ppa
            print("PROC: Iteration {} param {}, PPA: {}".format(i + 1, param, ppa))

    def generate_all_params(self):
        all_params = []
        print("Remaining clusters = ", len(self.cluster_gen.cluster_list), "/",
              self.init_cluster_num)
        for cluster in self.all_cluster:
            params = cluster.generate_all()
            all_params += params
        return all_params


if __name__ == "__main__":
    fist = FIST(cad_tool_dir=CAD_DIR, tune_design="mem_ctrl",
                transfer_design=None, tune_target="all",
                param_setup_json="assets/setup.json", num_important_feature=5,
                result_dir="result")
    model_less_dict = fist.model_less(1)
    fist.exploit(1)
    fist.explore(1)

