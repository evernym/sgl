import json
import pytest

from ..dbc import PreconditionViolation
from ..api import CustomJSONEncoder
from ..principal import Principal
from ..rule import Rule
from ..condition import Condition

from .examples import *


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
    assert p.bob.to_json() == '{"id": "Bob"}'
    assert p.employee_and_investor.to_json() == '{"id": "12345", "roles": ["employee", "investor"]}'


def test_principal_to_from_json_roundtrip():
    run_to_from_json_roundtrip(p)


def test_principal_custemencoder_roundtrip():
    run_customencoder_roundtrip(p)


def test_whom_empty_rejected():
    with pytest.raises(PreconditionViolation):
        Condition()
    with pytest.raises(PreconditionViolation):
        Condition(any={})
    with pytest.raises(PreconditionViolation):
        Condition(all={})
    with pytest.raises(PreconditionViolation):
        Condition(id='')


def test_whom_mutually_exclusive_rejected():
    with pytest.raises(PreconditionViolation):
        Condition(id="a", role="b")
    with pytest.raises(PreconditionViolation):
        Condition(role="b", any=[c.bob])
    with pytest.raises(PreconditionViolation):
        Condition(any=[c.bob], all=[c.grandparent])


def test_whom_id_must_be_str():
    with pytest.raises(PreconditionViolation):
        Condition(id=1)


# Required for forward compatibility
def test_whom_ignores_extra_fields_in_dict():
    assert Condition.from_dict({"id": "x", "a": 1, "b": 2.3, "c": [4, 5], "d": {}}) == Condition.from_dict({"id": "x"})


def test_whom_to_json_hardcoded():
    assert c.bob.to_json() == '{"id": "Bob"}'
    assert c.majority_tribal_council.to_json() == '{"n": 3, "role": "tribal_council"}'


def test_whom_to_from_json_roundtrip():
    run_to_from_json_roundtrip(c)


def test_whom_customencoder_roundtrip():
    run_customencoder_roundtrip(c)


def test_rule_rejects_empty_privs():
    with pytest.raises(PreconditionViolation):
        Rule([], c.bob)


def test_rule_rejects_non_sequence_of_strs_privs():
    with pytest.raises(PreconditionViolation):
        Rule("abc", c.bob)


# Required for forward compatibility
def test_rule_ignores_extra_fields_in_dict():
    assert Rule.from_dict({"grant": ["x"], "when": {"id": "y"}, "a": 1, "b": 2.3, "c": [4, 5], "d": {}}) \
           == Rule.from_dict({"grant": ["x"], "when": {"id": "y"}})


def test_rule_to_json_hardcoded():
    assert r.enter_to_bob.to_json() == '{"grant": ["enter"], "when": {"id": "Bob"}}'
    assert r.rations_to_grandparent_and_sibling.to_json() == \
           '{"grant": ["rations"], "when": {"all": [{"role": "grandparent"}, {"role": "sibling"}]}}'


def test_rule_to_from_json_roundtrip():
    run_to_from_json_roundtrip(r)


def test_rule_custemencoder_roundtrip():
    run_customencoder_roundtrip(r)
