from langmodels.model import TrainedModel, ModelDescription
from langmodels.evaluation.common import EvaluationScenario
import langmodels.modelregistry as modelRegistry
from dataclasses import dataclass
import json

@dataclass
class Token(object):
    text: str
    entropy: float

    def __init__(self, text: str, entropy: float):
        self.text = text
        self.entropy = entropy

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def serialize(self):
        return self.toJSON()

@dataclass
class EntropyLine(object):
    text: str
    line_entropy: float
    tokens: [Token]

    def __init__(self, text: str, line_entropy: float):
        self.text = text
        self.line_entropy = line_entropy
        self.tokens = []

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    def serialize(self):
        return self.toJSON()

@dataclass
class EntropyResult(object):
    lines: [EntropyLine]
    metrics: str
    token_type: str
    languagemodel: str

    def __init__(self, languagemodel, metrics = 'full_token_entropy', token_type = 'all'):
        self.lines = []
        self.languagemodel = languagemodel     
        self.metrics = metrics
        self.token_type = token_type

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def serialize(self):
        return self.toJSON()