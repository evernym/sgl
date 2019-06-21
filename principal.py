import json
from typing import List, Set, Union

from .dbc import *


class Principal:
    def __init__(self, id: str = None, roles: Union[List[str], Set[str]] = None):
        self.id = self.roles = None
        precondition(bool(id) or bool(roles), 'either "id" or "roles" must have a meaningful value.')
        if id:
            precondition_is_str(id, "id")
            self.id = id
        if roles:
            precondition_nonempty_sequence_of_str(roles, "roles")
            self.roles = sorted(set(roles))

    def __str__(self):
        return self.to_json()

    def to_dict(self) -> dict:
        if self.id and self.roles:
            return self.__dict__
        if self.id:
            return {"id": self.id}
        return {"roles": self.roles}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, value: dict) -> 'Principal':
        precondition(isinstance(value, dict), '"value" must be a dict')
        return Principal(value.get('id'), value.get('roles'))

    @classmethod
    def from_json(cls, json_text: str) -> 'Principal':
        precondition(json_text, '"json_text" must be non-empty.')
        precondition_is_str(json_text, "json_text")
        return Principal.from_dict(json.loads(json_text))

    def __eq__(self, other):
        if isinstance(other, Principal):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __hash__(self):
        return hash((self.id, str(self.roles))) if self.id else hash(id(self))


