from sgl import *


def get_all(prefix, of_type):
    g = globals()
    return [x for x in [g[x] for x in g if x.startswith(prefix)] if isinstance(x, of_type)]


p_Bob = Principal("Bob")
p_grandparent_and_sibling = Principal(roles=['sibling', 'grandparent'])
p_grandpa = Principal(id='Carl', roles=['grandparent'])
p_grandma = Principal(id='Alice', roles=['grandparent'])
p_sister = Principal(id='Susie', roles=['sibling'])
p_tribal_council_1 = Principal(roles=['tribal_council'])
p_tribal_council_1 = Principal(roles=['tribal_council'])

all_principals = get_all('p_', Principal)

Who_Bob = Who(id='Bob')
Who_all_with_1_id = Who(all=[Who_Bob])
Who_any_with_1_id = Who(any=[Who_Bob])
Who_1_grandparent = Who(n=1, role='grandparent')
Who_1_sibling = Who(role='sibling')
Who_2_grandparents = Who(n=2, role='grandparent')
Who_majority_tribal_council = Who(n=0.5001, role='tribal_council')
Who_trusted = Who(any = [
    Who_2_grandparents,
    Who(all = [Who_1_grandparent, Who_majority_tribal_council])
])

all_whos = get_all('Who_', Who)

grant_to_Bob = Grant(Who_Bob, "enter")
grant_to_1_grandparent = Grant(Who_1_grandparent, ["medical", "school", "delegate"])
grant_to_2_grandparents = Grant(Who_2_grandparents, ["foo"])
grant_to_1_grandparent_and_1_sibling = Grant(Who(all = [Who_1_grandparent, Who_1_sibling]), ['rations'])
grant_to_trusted = Grant(Who_trusted, ['travel', 'appoint'])

all_grants = get_all('grant_', Grant)


def test_Principal_to_json():
    assert p_Bob.to_json() == '{"id": "Bob"}'
    assert p_grandparent_and_sibling.to_json() == '{"roles": ["sibling", "grandparent"]}'


def test_Principal_json_roundtrip():
    for p in all_principals:
        json = p.to_json()
        assert Principal.from_json(json) == p


def test_Who_to_json():
    assert Who_Bob.to_json() == '{"id": "Bob"}'
    assert Who_1_grandparent.to_json() == '{"n": 1, "role": "grandparent"}'


def test_Who_json_roundtrip():
    for who in all_whos:
        json = who.to_json()
        assert Who.from_json(json) == who


def test_grant_to_json():
    assert grant_to_Bob.to_json() == '{"grant": {"id": "Bob"}, "privs": "enter"}'
    assert grant_to_1_grandparent_and_1_sibling.to_json() == \
           '{"grant": {"all": [{"n": 1, "role": "grandparent"}, {"n": 1, "role": "sibling"}]}, "privs": ["rations"]}'


def test_grant_json_roundtrip():
    for grant in all_grants:
        json = grant.to_json()
        assert Grant.from_json(json) == grant


def test_Bob_matches_id():
    assert is_authorized(p_Bob, Who_Bob)


def test_Bob_matches_and_with_1_id():
    assert is_authorized([p_Bob], Who_all_with_1_id)


def test_Bob_matches_or_with_1_id():
    assert is_authorized(p_Bob, Who_any_with_1_id)


def test_empty_grant_doesnt_apply():
    assert not is_authorized([p_Bob], None)


def test_grant_to_id_applies():
    assert is_authorized([p_Bob], grant_to_Bob)


def test_grant_to_1_grandparent_applies():
    assert is_authorized(p_grandpa, grant_to_1_grandparent)


def test_grant_to_1_grandparent_applies_to_2():
    assert is_authorized([p_grandma, p_grandpa], grant_to_1_grandparent)


def test_grant_to_1_grandparent_applies_to_multirole():
    assert is_authorized([p_grandparent_and_sibling], grant_to_1_grandparent)


def test_grant_to_1_grandparent_doesnt_apply_to_others():
    assert not is_authorized([p_sister, p_tribal_council_1, p_Bob], grant_to_1_grandparent)


def test_grant_to_2_grandparent_doesnt_apply_to_1():
    assert not is_authorized([p_grandpa], grant_to_2_grandparents)


if __name__ == '__main__':
    import pytest
    pytest.main()