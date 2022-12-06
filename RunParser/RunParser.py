import json
import os


class RunParser:
    def __init__(self, result_path: str):
        self.json_path = None
        if not os.path.isdir(result_path):
            os.mkdir(result_path)
        trial = 0
        self.result_path = os.path.join(result_path, str(trial))
        while not os.path.isdir(self.result_path):
            trial += 1
            self.result_path = os.path.join(result_path, str(trial))
        os.mkdir(self.result_path)
        name = "fist.json"
        self.json_path = os.path.join(self.result_path, name)

    def update_cluster(self, cluster: list, ppa: dict):
        cur_result = self.result()
        for sample in cluster:
            if tuple(sample) not in cur_result.keys():
                cur_result[tuple(sample)] = ppa
        with open(self.result_path, "w") as f:
            json.dump(cur_result, f)

    def update(self, sample: list, ppa: dict):
        with open(self.result_path, "r") as f:
            cur_result = json.load(f)
        if tuple(sample) not in cur_result.keys():
            cur_result[tuple(sample)] = ppa
            with open(self.result_path, "w") as f:
                json.dump(cur_result, f)
        return cur_result

    def result(self):
        with open(self.result_path, "r") as f:
            result = json.load(f)
        return result
