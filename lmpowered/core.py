from typing import List

from langmodels.evaluation import evaluate_model_on_string, TokenTypeSubset
from langmodels.evaluation.metrics import EvaluationScenario
from langmodels.model import TrainedModel
from lmpowered.util.entropyresult import EntropyLine, Token, EntropyResult


def calculate_entropies_of_string(model: TrainedModel, text: str, extension ='java', metrics ='full_token_entropy'):
    evaluations = evaluate_model_on_string(model, text, extension, metrics = {metrics},
                                           token_type_subsets={TokenTypeSubset.full_set()})

    scenario = EvaluationScenario(metric_name = metrics, type_subset=TokenTypeSubset.full_set())
    lines: List[EntropyLine] = []
    for evaluation in evaluations:
        evaluation_result = evaluation.scenarios[scenario]
        tokens: List[Token] = []
        for (prep_token, token_type, value) in zip(evaluation_result.tokens, evaluation_result.token_types, evaluation_result.values):
            tokens.append(Token(prep_token, value, token_type))
        lines.append(EntropyLine(evaluation.text, evaluation_result.aggregated_value, tokens))

    return EntropyResult(lines, metrics)