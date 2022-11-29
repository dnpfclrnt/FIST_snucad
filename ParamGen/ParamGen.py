from ..Clustering import Cluster
import random


class ModelLess:
    def __init__(self, feature_importance: list,
                 num_importance: int, setting_json: str):
        cluster = Cluster(feature_importance=feature_importance,
                          num_important=num_importance)
        self.cluster = cluster.gen_cluster(setting_json)

    def param_set(self, num_sample: int):
        if len(self.cluster.keys()) < num_sample:
            raise ValueError("cluster must be larger than sampling number. \
            got cluster #= {}, sample #= {}".format(len(self.cluster.keys()),
                                                    num_sample))
        sample_cluster_list = random.sample(self.cluster.keys(), num_sample)
        param_set = []
        for cluster in sample_cluster_list:
            sample = random.sample(self.cluster[cluster], 1)
            param_set.append(sample)
        return param_set
