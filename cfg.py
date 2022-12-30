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
        # string parameters
        self.str_clk = "CLOCK_PERIOD"
        self.str_util = "CORE_UTIL"
        self.str_fanout = "set_max_fanout"
        self.str_transition = "set_max_transition"
        self.str_cap = "set_max_capacitance"
        self.str_eco = "eco_max_distance"
        self.str_den = "max_density"
        self.str_wire = "wire_length_opt"
        self.str_clk_power = "clock_power_driven"
        self.str_congestion = "congestion_effort"
        self.str_uniform = "uniform_density"

        # string levels
        self.str_low = "low"
        self.str_med = "medium"
        self.str_high = "high"
        self.str_std = "standard"
        self.str_auto = "auto"

        # string results
        self.str_power = "power"
        self.str_wns = "wns"
        self.str_tns = "tns"
        self.str_area = "area"
        self.str_wirelength = "wire_length"

        self.mac_ppa = "/Users/ppa.json"
        self.server_ppa = "/users/cad_data/ppa.json"
