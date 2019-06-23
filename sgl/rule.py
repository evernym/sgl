import json
from typing import Sequence

from .dbc import *
from .condition import Condition


class Rule:
    def __init__(self, privs: Sequence[str], when: Condition):
        precondition_nonempty_sequence_of_str(privs, "privs")
        self.privs = sorted(set(privs))
        if isinstance(when, dict):
            self.when = Condition.from_dict(when)
        elif isinstance(when, Condition):
            self.when = when
        else:
            raise PreconditionViolation('"when" must be a Condition or dict.')

    def __str__(self):
        return self.to_json()

    def to_dict(self):
        return {"grant": self.privs, "when": self.when.to_dict()}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, value: dict) -> 'Rule':
        precondition(isinstance(value, dict), '"value" must be a dict')
        return Rule(value.get("grant"), value.get("when"))

    @classmethod
    def from_json(cls, json_text: str) -> 'Rule':
        precondition(json_text, '"json_text" must be non-empty.')
        precondition_is_str(json_text, "json_text")
        return Rule.from_dict(json.loads(json_text))

    def __eq__(self, other):
        if isinstance(other, Rule):
            return self.__dict__ == other.__dict__
        return NotImplemented


