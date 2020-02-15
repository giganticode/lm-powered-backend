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


@dataclass
class EntropyLine(object):
    text: str
    line_entropy: float
    tokens: [Token]


@dataclass
class EntropyResult(object):
    lines: [EntropyLine]
    metrics: str