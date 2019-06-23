import pytest

from ..api import *
from .examples import *
from ..condition import Condition


def test_bob_satisfies_id_bob():
    assert satisfies(p.bob, c.bob)
    assert satisfies(p.bob, r.enter_to_bob)


def test_carl_doesnt_satisfy_id_bob():
    assert not satisfies(p.grandpa_carl, c.bob)


def test_bob_matches_1_and_with_id_bob():
    assert satisfies([p.bob], c.all_with_1_id)


def test_emily_matches_1_or_with_id_emily():
    assert satisfies(p.sister_emily, c.any_with_1_id)


def test_group_with_bob_matches_1_or_with_id_bob():
    assert satisfies([p.sister_emily, p.grandma_carol, p.bob], c.any_with_1_id)


def test_empty_rule_fails():
    with pytest.raises(PreconditionViolation):
        satisfies(p.bob, None)


def test_grandma_satisfies_grandparent():
    assert satisfies(p.grandma_extra, r.three_privs_to_grandparent)


def test_2_grandparents_satisfies_1():
    assert satisfies([p.grandma_carol, p.grandpa_carl], r.three_privs_to_grandparent)


def test_1_grandparent_doesnt_satisfy_2():
    assert not satisfies([p.grandma_carol], r.spoil_child_to_2_grandparents)


def test_2_grandparents_satisfies_2():
    assert satisfies([p.grandma_carol, p.grandpa_carl], r.spoil_child_to_2_grandparents)


def test_multirole_satisfies_1():
    assert satisfies(p.employee_and_investor, r.enter_to_employee)


def test_others_dont_satisfy_grandparent():
    assert not satisfies([
        p.sister_emily,
        p.tribal_council,
        p.bob,
        p.employee
    ], r.three_privs_to_grandparent)


def test_same_2_grandparents():
    assert not satisfies([p.grandpa_carl, p.grandpa_carl], c.two_grandparents)


def test_either_sibling_or_investor():
    assert satisfies([p.investor, p.grandma_extra], Condition(any=[c.sibling, c.grandparent]))
    assert satisfies([p.brother_extra, p.investor], Condition(any=[c.sibling, c.grandparent]))
    assert satisfies([p.brother_extra, p.grandma_extra], Condition(any=[c.sibling, c.grandparent]))


def test_2_grandparents_trusted():
    assert satisfies([p.grandma_carol, p.grandpa_carl], c.trusted)
    assert satisfies([p.grandma_carol, p.bob, p.grandpa_carl], c.trusted)


def test_1_grandparent_3_tribal_council_trusted():
    extra = Principal.from_dict({"roles": ["tribal_council"]})
    assert satisfies([
        p.grandma_carol,
        p.sister_emily,
        p.investor,
        p.tribal_council,
        p.tribal_council_fatima,
        extra],
    c.trusted)


def check_disjoint_and_not(group, c, expected_when_disjoint = False):
    assert satisfies(group, c, disjoint=False)
    assert satisfies(group, c, disjoint=True) == expected_when_disjoint


def test_same_person_for_all_not_disjoint():
    check_disjoint_and_not(p.employee_and_investor, r.call_meeting_to_employee_and_investor)


def test_overlap_for_all_disjoint():
    check_disjoint_and_not([
        p.employee_and_investor,
        p.investor
    ], Condition(all=[c.employee_and_investor, Condition.from_dict({"n": 2, "role": "investor"})]))


def test_same_person_for_all_disjoint():
    check_disjoint_and_not(p.employee_and_investor, r.call_meeting_to_employee_and_investor)


# This test is the simplest one I could imagine that exercises the logic where
# disjoint subsets are calculated. The next test is similar, but does much more
# complex work. Hopefully the debugging can take place on this one.
def test_easiest_all_disjoint():
    x = Condition(all=[
        Condition(n=2, role="employee"),
        Condition(n=2, role="investor"),
    ])
    # The list of p should not satisfy the c listed above, because
    # we're asking for two employees and two investors -- and what we have is one
    # employee, one investor, and one employee+investor.
    assert not satisfies(p.objs, x)


def test_without_disjoint_3_satisfies_2_plus_2():
    x = Condition(all=[
        Condition(n=2, role="employee"),
        Condition(n=2, role="investor"),
    ])
    assert satisfies(p.objs, x, disjoint=False)


def test_complex_all_disjoint():
    x = Condition(all=[
        c.bob,
        Condition(n=2, role="sibling"),
        Condition(all=[
            c.trusted,
            Condition(all=[
                Condition(n=2, role="employee"),
                Condition(n=2, role="investor"),
            ])
        ])
    ])
    # The list of p should not satisfy the c listed above, because
    # we're asking for two employees and two investors -- and what we have is one
    # employee, one investor, and one employee+investor.
    assert not satisfies(p.objs, x)
    # All 3 ways to fix the problem should result in a positive answer.
    assert satisfies(p.objs + [Principal(roles=["investor"])], x)
    assert satisfies(p.objs + [Principal(roles=["employee"])], x)
    assert satisfies(p.objs + [Principal(roles=["employee", "investor"])], x)


def test_satisfies_tolerates_dicts():
    satisfies({"id": "Fred"}, c.bob)
    satisfies(p.bob, {"id": "Bob"})
    satisfies(p.bob, {"grant": "enter", "when": {"id": "Bob"}})


def donttest_any_with_n_3():
    x = Condition.from_dict(
        {"any": [
            {"role": "grandparent"},
            {"role": "sibling"}
        ], "n": 3}
    )
    p = p # to be concise
    assert not satisfies([p.grandpa_carl, p.grandma_carol, p.investor], x)
    assert not satisfies([p.grandpa_carl, p.sister_emily, p.investor], x)
    assert satisfies([p.grandpa_carl, p.grandma_carol, p.sister_emily, p.investor], x)
    assert satisfies([p.grandpa_carl, p.sister_emily, p.brother_extra, p.investor], x)
