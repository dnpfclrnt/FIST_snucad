from ..Clustering import ClusterGen


class ModelLess:
    def __init__(self, feature_importance: list,
                 num_importance: int, setting_json: str,
                 num_params: int = 100):
        self.cluster_list = ClusterGen(feature_importance,
                                       setting_json,
                                       num_importance)
        self.params = self.cluster_list.generate_param_set_model_less(num_params)
