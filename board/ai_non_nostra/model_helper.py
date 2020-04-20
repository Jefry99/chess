"""
Helper methods for working with trained models.
"""

def load_best_model_weight(model):
    """
    :param chess_zero.agent.model.ChessModel model:
    :return:
    """
    return model.load(model.config.resource.model_best_config_path, model.config.resource.model_best_weight_path)


def save_as_best_model(model):
    """

    :param chess_zero.agent.model.ChessModel model:
    :return:
    """
    return model.save(model.config.resource.model_best_config_path, model.config.resource.model_best_weight_path)


def reload_best_model_weight_if_changed(model):
    """

    :param chess_zero.agent.model.ChessModel model:
    :return:
    """
    if model.config.model.distributed:
        return load_best_model_weight(model)
    else:
        digest = model.fetch_digest(model.config.resource.model_best_weight_path)
        if digest != model.digest:
            return load_best_model_weight(model)

        return False
