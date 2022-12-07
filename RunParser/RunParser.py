import json
import os


def encode(params: tuple or list):
    enc = []
    for param in params:
        element = param
        if type(param) is not str:
            element = str(param)
        enc.append(element)
    return "_".join(enc)


def decode(params: str):
    split = params.split("_")
    dec = []
    for i in range(12):
        if i == 0 or i == 1 or i == 3 or i == 4:
            dec.append(float(split[i]))
        elif i == 2 or i == 5 or i == 6:
            dec.append(int(split[i]))
        else:
            dec.append(split[i])
    return dec


class RunParser:
    def __init__(self, result_path: str):
        """
        This is run parser for FIST.
        With fixed result directory, it will update the json file
        :param result_path: ppa directory
        """
        self.json_path = None
        if not os.path.isdir(result_path):
            os.mkdir(result_path)
        trial = 0
        self.result_path = os.path.join(result_path, str(trial))
        while os.path.isdir(self.result_path):
            trial += 1
            self.result_path = os.path.join(result_path, str(trial))
        os.mkdir(self.result_path)
        name = "fist.json"
        self.json_path = os.path.join(self.result_path, name)

    def update_cluster(self, cluster: list, ppa: dict):
        """
        This will used for model-less sampling and exploration step
        This will label entire cluster for same ppa
        :param cluster: list of parameter sets in a cluster
        :param ppa: label for current parameter
        :return: nothing. Writes a json file
        """
        cluster_json = os.path.join(self.result_path, "cluster.json")
        if os.path.isfile(cluster_json):
            with open(cluster_json, "r") as f:
                prev_cluster = json.load(f)
            for sample in cluster:
                if encode(sample) not in prev_cluster.keys():
                    prev_cluster[encode(sample)] = ppa
        else:
            prev_cluster = {}
            for sample in cluster:
                prev_cluster[encode(sample)] = ppa
        with open(cluster_json, "w") as f:
            json.dump(prev_cluster, f)

    def update_result(self, sample: list, ppa: dict):
        """
        This method will write a result of single sample
        :param sample: list of parameters
        :param ppa: output from current parameter
        :return: dictionary of current result
        """
        if not os.path.isfile(self.json_path):
            cur_result = {
                encode(sample): ppa
            }
            with open(self.json_path, "w") as f:
                print(cur_result)
                json.dump(cur_result, f)
            return cur_result
        with open(self.json_path, "r") as f:
            cur_result = json.load(f)
        if encode(sample) not in cur_result.keys():
            cur_result[encode(sample)] = ppa
            with open(self.json_path, "w") as f:
                json.dump(cur_result, f)
        return cur_result

    def result(self):
        with open(self.json_path, "r") as f:
            result = json.load(f)
        return result
