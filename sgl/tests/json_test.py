import json
import pytest

from ..dbc import PreconditionViolation
from ..api import CustomJSONEncoder
from ..principal import Principal
from ..rule import Rule
from ..whom import Whom

from .model import principals
from .model import whoms
from .model import rules


def run_to_from_json_roundtrip(dynload):
    for o in dynload.objs:
        j = o.to_json()
        assert dynload.cls.from_json(j) == o


def run_customencoder_roundtrip(dynload):
    for o in dynload.objs:
        j = json.dumps(o, cls=CustomJSONEncoder)
        assert dynload.cls.from_json(j) == o


def test_principal_empty_rejected():
    with pytest.raises(PreconditionViolation):
        Principal()
    with pytest.raises(PreconditionViolation):
        Principal(id='')
    with pytest.raises(PreconditionViolation):
        Principal('', [])


def test_principal_non_str_id_rejected():
    with pytest.raises(PreconditionViolation):
        Principal(1, ["abc"])


def test_principal_non_str_role_rejected():
    with pytest.raises(PreconditionViolation):
        Principal(roles=[1])


def test_principal_str_role_rejected():
    with pytest.raises(PreconditionViolation):
        Principal(roles="abc")


# Required for forward compatibility
def test_principal_ignores_extra_fields_in_dict():
    assert Principal.from_dict({"id": "x", "a": 1, "b": 2.3, "c": [4, 5], "d": {}}) == Principal.from_dict({"id": "x"})


def test_principal_to_json_hardcoded():
    assert principals.bob.to_json() == '{"id": "Bob"}'
    assert principals.employee_and_investor.to_json() == '{"id": "12345", "roles": ["employee", "investor"]}'


def test_principal_to_from_json_roundtrip():
    run_to_from_json_roundtrip(principals)


def test_principal_custemencoder_roundtrip():
    run_customencoder_roundtrip(principals)


def test_whom_empty_rejected():
    with pytest.raises(PreconditionViolation):
        Whom()
    with pytest.raises(PreconditionViolation):
        Whom(any={})
    with pytest.raises(PreconditionViolation):
        Whom(all={})
    with pytest.raises(PreconditionViolation):
        Whom(id='')


def test_whom_mutually_exclusive_rejected():
    with pytest.raises(PreconditionViolation):
        Whom(id="a", role="b")
    with pytest.raises(PreconditionViolation):
        Whom(role="b", any=[whoms.bob])
    with pytest.raises(PreconditionViolation):
        Whom(any=[whoms.bob], all=[whoms.grandparent])


def test_whom_id_must_be_str():
    with pytest.raises(PreconditionViolation):
        Whom(id=1)


# Required for forward compatibility
def test_whom_ignores_extra_fields_in_dict():
    assert Whom.from_dict({"id": "x", "a": 1, "b": 2.3, "c": [4, 5], "d": {}}) == Whom.from_dict({"id": "x"})


def test_whom_to_json_hardcoded():
    assert whoms.bob.to_json() == '{"id": "Bob"}'
    assert whoms.majority_tribal_council.to_json() == '{"n": 3, "role": "tribal_council"}'


def test_whom_to_from_json_roundtrip():
    run_to_from_json_roundtrip(whoms)


def test_whom_customencoder_roundtrip():
    run_customencoder_roundtrip(whoms)


def test_rule_rejects_empty_privs():
    with pytest.raises(PreconditionViolation):
        Rule([], whoms.bob)


def test_rule_rejects_non_sequence_of_strs_privs():
    with pytest.raises(PreconditionViolation):
        Rule("abc", whoms.bob)


# Required for forward compatibility
def test_rule_ignores_extra_fields_in_dict():
    assert Rule.from_dict({"grant": ["x"], "to": {"id": "y"}, "a": 1, "b": 2.3, "c": [4, 5], "d": {}}) \
           == Rule.from_dict({"grant": ["x"], "to": {"id": "y"}})


def test_rule_to_json_hardcoded():
    assert rules.enter_to_bob.to_json() == '{"grant": ["enter"], "to": {"id": "Bob"}}'
    assert rules.rations_to_grandparent_and_sibling.to_json() == \
           '{"grant": ["rations"], "to": {"all": [{"role": "grandparent"}, {"role": "sibling"}]}}'


def test_rule_to_from_json_roundtrip():
    run_to_from_json_roundtrip(rules)


def test_rule_custemencoder_roundtrip():
    run_customencoder_roundtrip(rules)
