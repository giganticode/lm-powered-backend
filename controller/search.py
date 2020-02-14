from core import calculate_entropies_of_string
from langmodels.model import TrainedModel


def search(content: str, search_phrase: str, model: TrainedModel, search_interval: int, metrics):
    lines = content.splitlines()
    originalContent = lines.copy()
    searchContent = lines.copy()

    i = 0
    while i < len(originalContent):
        originalContent.insert(i, '//')
        searchContent.insert(i, '//' + search_phrase)
        i += (search_interval + 1)

    original_entropies = calculate_entropies_of_string(model, "\n".join(originalContent), 'java', metrics = metrics)
    model.reset()
    search_entropies = calculate_entropies_of_string(model, "\n".join(searchContent), 'java', metrics = metrics)
    return original_entropies, search_entropies
