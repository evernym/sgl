import json


class PreconditionViolation(BaseException):
    def __init__(self, msg):
        BaseException.__init__(self, "Precondition violated: " + msg)


def _precondition(expr, msg):
    if not bool(expr):
        raise PreconditionViolation(msg)
    
    
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'as_json_serializable'):
            return o.as_json_serializable()
        return json.JSONEncoder.default(self, o)


class Who:
    def __init__(self, id: str = None, n: int = None, role: str = None, all: list = None, any: list = None):
        specified = [True for x in [id, role, all, any] if bool(x)]
        _precondition(len(specified) == 1, "the 'id', 'role', 'all', and 'any' parameters are mutually exclusive, and one must be specified.")
        self.id = self.n = self.role = self.all = self.any = None
        if role:
            self.role = role
            if not n:
                n = 1
            _precondition((isinstance(n, int) and n > 0) or (isinstance(n, float) and n < 1.0 and n > 0.0),
                         "'n' must be a positive integer or a floating point number between 0 and 1, exclusive.")
            self.n = n
        elif id:
            self.id = id
        elif all:
            self.all = all
        elif any:
            self.any = any

    def __str__(self):
        return self.to_json()

    def as_json_serializable(self) -> dict:
        if self.id:
            return {"id": self.id}
        if self.role:
            return {"n": self.n, "role": self.role}
        if self.all:
            return {"all": [x.as_json_serializable() for x in self.all]}
        return {"any": [x.as_json_serializable() for x in self.any]}

    def to_json(self) -> str:
        return json.dumps(self.as_json_serializable())

    @classmethod
    def from_dict(cls, dict):
        if isinstance(dict, Who):
            return dict
        all = dict.get('all')
        if all:
            all = [Who.from_dict(x) for x in all]
        any = dict.get('any')
        if any:
            any = [Who.from_dict(x) for x in any]
        return Who(dict.get('id'), dict.get('n'), dict.get('role'), all, any)

    @classmethod
    def from_json(cls, json_text):
        return Who.from_dict(json.loads(json_text))

    def __eq__(self, other):
        if isinstance(other, Who):
            return self.__dict__ == other.__dict__
        return NotImplemented



class Grant:
    def __init__(self, who: Who, privs: list):
        if isinstance(who, dict):
            self.who = Who.from_dict(who)
        elif isinstance(who, Who):
            self.who = who
        else:
            _precondition(False, "grant must be a Who or dict.")
        _precondition(privs, "privs must not be empty.")
        self.privs = privs

    def __str__(self):
        return self.to_json()

    def as_json_serializable(self):
        return {"grant": self.who.as_json_serializable(), "privs": self.privs}

    def to_json(self) -> str:
        return json.dumps(self.as_json_serializable())

    @classmethod
    def from_dict(cls, dict):
        return Grant(dict.get('grant'), dict.get('privs'))

    @classmethod
    def from_json(cls, json_text):
        return Grant.from_dict(json.loads(json_text))

    def __eq__(self, other):
        if isinstance(other, Grant):
            return self.__dict__ == other.__dict__
        return NotImplemented


class Principal:
    def __init__(self, id: str = None, roles: list = None):
        _precondition(bool(id) or bool(roles), "either id or roles must have a meaningful value.")
        self.id = self.roles = None
        if id:
            _precondition(isinstance(id, str), "id must be a str.")
            self.id = id
        if roles:
            _precondition(isinstance(roles, list), "role must be a list of str.")
            self.roles = roles

    def __str__(self):
        return self.to_json()

    def as_json_serializable(self):
        if self.id and self.roles:
            return self.__dict__
        if self.id:
            return {"id": self.id}
        return {"roles": self.roles}

    def to_json(self) -> str:
        return json.dumps(self.as_json_serializable())

    @classmethod
    def from_dict(cls, dict):
        return Principal(dict.get('id'), dict.get('roles'))

    @classmethod
    def from_json(cls, json_text):
        return Principal.from_dict(json.loads(json_text))

    def __eq__(self, other):
        if isinstance(other, Principal):
            return self.__dict__ == other.__dict__
        return NotImplemented


def _one_matches_who_ignoring_n(individual: Principal, who: Who) -> bool:
    if individual and who:
        if who.id:
            return individual.id == who.id
        elif who.role:
            return individual.roles and (who.role in individual.roles)
        elif who.any:
            for item in who.any:
                if _one_matches_who_ignoring_n(individual, item):
                    return True
        else:
            for item in who.all:
                if not _one_matches_who_ignoring_n(individual, item):
                    return False
            return True
    return False


def is_authorized(individual_or_group, grant_or_who) -> bool:
    if individual_or_group and grant_or_who:
        who = grant_or_who if isinstance(grant_or_who, Who) else grant_or_who.who
        group = [individual_or_group] if isinstance(individual_or_group, Principal) else individual_or_group
        if who.id:
            for individual in group:
                if individual.id == who.id:
                    return True
        elif who.role:
            n = who.n
            for individual in group:
                if individual.roles and (who.role in individual.roles):
                    n -= 1
                    if n == 0:
                        return True
        elif who.any:
            for item in who.any:
                if is_authorized(group, item):
                    return True
            return False
        elif who.all:
            for item in who.all:
                if not is_authorized(group, item):
                    return False
            return True
    return False


def _unique_combinations(items, n):
    if n == 0:
        yield {}
    else:
        for i in range(len(items)):
            for cc in _unique_combinations(items[i + 1:], n - 1):
                yield {items[i]} + cc


def _get_matching_minimal_subsets(group: set, who: Who) -> set:
    """
    Returns a set of all smallest subsets of the group that match the criteria in who.
    """
    answer = set()
    if group and who:
        if who.id:
            for individual in group:
                if individual.id == who.id:
                    answer.add({individual})
        elif who.role:
            individuals_with_role = set()
            for individual in group:
                if individual.roles and (who.role in individual.roles):
                    individuals_with_role.add(individual)
            answer = _unique_combinations(individuals_with_role, who.n)
        elif who.any:
            for item in who.any:
                if is_authorized(group, item):
                    answer = group
                    break
        elif who.all:
            pass
    return answer