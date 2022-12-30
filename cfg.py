import json
import os


# Default parameters
param_file = "assets/setup.json"
param_dir = os.path.join(os.getcwd(),
                         param_file)
num_params = 12


class Config:
    def __init__(self) -> None:
        if not os.path.isfile(param_dir):
            raise FileNotFoundError("{} not exists".format(param_dir))
        self.num_params = num_params
        with open(param_dir, "r") as f:
            self.params = json.load(f)
        if len(self.params.keys()) != self.num_params:
            raise ValueError("Setup # params = {}, # required params = {}".format(
                len(self.params.keys()), self.num_params
            ))
        self.param_name = StringParams()
        self.result_name = StringResults()
        self.level = StringLevels()

        # Weight
        self.weight = {}
        self.weight[self.result_name.power] = 0.001
        self.weight[self.result_name.wns] = 0.001
        self.weight[self.result_name.tns] = 0.001
        self.weight[self.result_name.area] = 0.001
        self.weight[self.result_name.wirelength] = 0.1

        self.mac_ppa = "/Users/ppa.json"
        self.server_ppa = "/users/cad_data/ppa.json"



class StringParams:
    def __init__(self) -> None:
        # string parameters
        self.clk = "CLOCK_PERIOD"
        self.util = "CORE_UTIL"
        self.fanout = "set_max_fanout"
        self.transition = "set_max_transition"
        self.cap = "set_max_capacitance"
        self.eco = "eco_max_distance"
        self.den = "max_density"
        self.wire = "wire_length_opt"
        self.clk_power = "clock_power_driven"
        self.congestion = "congestion_effort"
        self.uniform = "uniform_density"


class StringLevels:
    def __init__(self) -> None:
        # string levels
        self.low = "low"
        self.med = "medium"
        self.high = "high"
        self.std = "standard"
        self.auto = "auto"


class StringResults:
    def __init__(self) -> None:
        # string results
        self.power = "power"
        self.wns = "wns"
        self.tns = "tns"
        self.area = "area"
        self.wirelength = "wire_length"
