import atexit
import logging
from collections import defaultdict
from multiprocessing import Lock
from multiprocessing.managers import BaseManager
from typing import List, Dict, Mapping

import langmodels
from langmodels import repository
from langmodels.model import TrainedModel


logger = logging.getLogger(__name__)

logger.info(f"Using langmodels version: {langmodels.__version__}")

_lock = Lock()

_common_model_pool: Dict[str, List[TrainedModel]] = {}


def _get_model(model_id: str):
    if model_id in _common_model_pool:
        return _common_model_pool[model_id].pop()

    return repository.load_model_by_id(model_id)


def _return_model_to_pool(model: TrainedModel):
    _common_model_pool[model.id].append(model)


_per_user_model_pool = {}


def _default_model_preferences() -> Mapping[str, Mapping[str, str]]:
    default_model_id = repository.query_all_models()[0].id
    return defaultdict(lambda: {k: default_model_id
                                for k in ['search', 'risk', 'autocompletion', 'compare.1', 'compare.2']})


_user_model_preferences = _default_model_preferences()


def _count_active_models():
    return sum(map(lambda x: len(x.keys()), _per_user_model_pool.values()))


def change_preferred_model(user_id: str, purpose: str, model_id: str) -> None:
    with _lock:
        _user_model_preferences[user_id][purpose] = model_id


def get_model_for_user(user_id: str, purpose: str) -> TrainedModel:
    with _lock:
        if user_id not in _per_user_model_pool:
            _per_user_model_pool[user_id] = {}

        if purpose not in _per_user_model_pool[user_id]:
            model_id = _user_model_preferences[user_id][purpose]
            _per_user_model_pool[user_id][purpose] = _get_model(model_id)
            logging.info(f"The number of active models: {_count_active_models()}")

        return _per_user_model_pool[user_id][purpose]


def release_model(user_id: str, purpose: str) -> None:
    with _lock:
        if user_id not in _per_user_model_pool or purpose not in _per_user_model_pool[user_id]:
            raise ValueError(f"Model {user_id}/{purpose} can not be released cause it is not being held.")

        _return_model_to_pool(_per_user_model_pool[user_id][purpose])
        del _per_user_model_pool[user_id][purpose]
        logging.info(f"The number of active models: {_count_active_models()}")


@atexit.register
def shut_down():
    pass


if __name__ == '__main__':
    manager = BaseManager(('', 37844), b'password')
    manager.register(get_model_for_user.__name__, get_model_for_user)
    manager.register(release_model.__name__, release_model)
    server = manager.get_server()
    server.serve_forever()