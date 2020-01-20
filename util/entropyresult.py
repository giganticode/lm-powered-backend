import json

from dataclasses import dataclass


@dataclass
class Token(object):
    text: str
    entropy: float
    type: str

    def __init__(self, text: str, entropy: float, type: str):
        self.text = text
        self.entropy = entropy
        self.type = type

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def serialize(self):
        return self.toJSON()


@dataclass
class EntropyLine(object):
    text: str
    line_entropy: float
    tokens: [Token]

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    def serialize(self):
        return self.toJSON()


@dataclass
class EntropyResult(object):
    lines: [EntropyLine]
    metrics: str
    languagemodel: str

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def serialize(self):
        return self.toJSON()