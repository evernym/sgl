import json
import math
from typing import Sequence

from .dbc import *


class Condition:
    def __init__(self, id: str = None, n: int = None, role: str = None,
                 all: Sequence['Condition'] = None, any: Sequence['Condition'] = None):
        specified = [True for x in [id, role, all, any] if bool(x)]
        precondition(len(specified) == 1,
                     'the "id", "role", "all", and "any" parameters are mutually exclusive, and one must be specified.')
        self.id = self.n = self.role = self.all = self.any = None
        if id:
            precondition_is_str(id, "id")
            self.id = id
        elif role:
            self.role = role
            if isinstance(n, float):
                precondition(n <= math.floor(n) and n >= math.ceil(n),
                             '"n" must be castable to int without losing precision.')
                n = int(n)
            elif n is None:
                n = 1
            precondition(isinstance(n, int) and n > 0, '"n" must be a positive integer.')
            self.n = n
        elif all:
            precondition_nonempty_sequence_of_x(all, "all", Condition)
            self.all = all
        else: #if any:
            precondition_nonempty_sequence_of_x(any, "any", Condition)
            self.n = n if (n and n > 1) else 1
            self.any = any

    def __str__(self):
        return self.to_json()

    def to_dict(self) -> dict:
        if self.id:
            return {"id": self.id}
        if self.role:
            if self.n == 1:
                return {"role": self.role}
            else:
                return {"n": self.n, "role": self.role}
        if self.all:
            return {"all": [x.to_dict() for x in self.all]}

        if self.n > 1:
            return {"any": [x.to_dict() for x in self.any], "n": self.n}
        else:
            return {"any": [x.to_dict() for x in self.any]}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, value: dict) -> 'Condition':
        precondition(isinstance(value, dict), '"value" must be a dict')
        all = value.get('all')
        if all:
            all = [Condition.from_dict(x) for x in all]
        any = value.get('any')
        if any:
            any = [Condition.from_dict(x) for x in any]
        return Condition(value.get('id'), value.get('n'), value.get('role'), all, any)

    @classmethod
    def from_json(cls, json_text: str) -> 'Condition':
        precondition(json_text, '"json_text" must be non-empty.')
        precondition_is_str(json_text, "json_text")
        return Condition.from_dict(json.loads(json_text))

    def __eq__(self, other):
        if isinstance(other, Condition):
            return self.__dict__ == other.__dict__
        return NotImplemented

