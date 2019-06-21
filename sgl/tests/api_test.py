import pytest

from ..api import *
from .model import *


def test_bob_satisfies_id_bob():
    assert satisfies(principals.bob, whoms.bob)
    assert satisfies(principals.bob, rules.enter_to_bob)


def test_carl_doesnt_satisfy_id_bob():
    assert not satisfies(principals.grandpa_carl, whoms.bob)


def test_bob_matches_1_and_with_id_bob():
    assert satisfies([principals.bob], whoms.all_with_1_id)


def test_emily_matches_1_or_with_id_emily():
    assert satisfies(principals.sister_emily, whoms.any_with_1_id)


def test_group_with_bob_matches_1_or_with_id_bob():
    assert satisfies([principals.sister_emily, principals.grandma_carol, principals.bob], whoms.any_with_1_id)


def test_empty_rule_fails():
    with pytest.raises(PreconditionViolation):
        satisfies(principals.bob, None)


def test_grandma_satisfies_grandparent():
    assert satisfies(principals.grandma_extra, rules.three_privs_to_grandparent)


def test_2_grandparents_satisfies_1():
    assert satisfies([principals.grandma_carol, principals.grandpa_carl], rules.three_privs_to_grandparent)


def test_1_grandparent_doesnt_satisfy_2():
    assert not satisfies([principals.grandma_carol], rules.spoil_child_to_2_grandparents)


def test_2_grandparents_satisfies_2():
    assert satisfies([principals.grandma_carol, principals.grandpa_carl], rules.spoil_child_to_2_grandparents)


def test_multirole_satisfies_1():
    assert satisfies(principals.employee_and_investor, rules.enter_to_employee)


def test_others_dont_satisfy_grandparent():
    assert not satisfies([
        principals.sister_emily,
        principals.tribal_council,
        principals.bob,
        principals.employee
    ], rules.three_privs_to_grandparent)


def test_same_2_grandparents():
    assert not satisfies([principals.grandpa_carl, principals.grandpa_carl], whoms.two_grandparents)


def test_either_sibling_or_investor():
    assert satisfies([principals.investor, principals.grandma_extra], Whom(any=[whoms.sibling, whoms.grandparent]))
    assert satisfies([principals.brother_extra, principals.investor], Whom(any=[whoms.sibling, whoms.grandparent]))
    assert satisfies([principals.brother_extra, principals.grandma_extra], Whom(any=[whoms.sibling, whoms.grandparent]))


def test_2_grandparents_trusted():
    assert satisfies([principals.grandma_carol, principals.grandpa_carl], whoms.trusted)
    assert satisfies([principals.grandma_carol, principals.bob, principals.grandpa_carl], whoms.trusted)


def test_1_grandparent_3_tribal_council_trusted():
    extra = Principal.from_dict({"roles": ["tribal_council"]})
    assert satisfies([
        principals.grandma_carol,
        principals.sister_emily,
        principals.investor,
        principals.tribal_council,
        principals.tribal_council_fatima,
        extra],
    whoms.trusted)


def check_disjoint_and_not(group, criteria, expected_when_disjoint = False):
    assert satisfies(group, criteria, disjoint=False)
    assert satisfies(group, criteria, disjoint=True) == expected_when_disjoint


def test_same_person_for_all_not_disjoint():
    check_disjoint_and_not(principals.employee_and_investor, rules.call_meeting_to_employee_and_investor)

def test_overlap_for_all_disjoint():
    check_disjoint_and_not([
        principals.employee_and_investor,
        principals.investor
    ], Whom(all=[whoms.employee_and_investor, Whom.from_dict({"n": 2, "role": "investor"})]))

def test_same_person_for_all_disjoint():
    check_disjoint_and_not(principals.employee_and_investor, rules.call_meeting_to_employee_and_investor)


# This test is the simplest one I could imagine that exercises the logic where
# disjoint subsets are calculated. The next test is similar, but does much more
# complex work. Hopefully the debugging can take place on this one.
def test_easiest_all_disjoint():
    criteria = Whom(all=[
        Whom(n=2, role="employee"),
        Whom(n=2, role="investor"),
    ])
    # The list of principals should not satisfy the criteria listed above, because
    # we're asking for two employees and two investors -- and what we have is one
    # employee, one investor, and one employee+investor.
    assert not satisfies(principals.objs, criteria)


def test_complex_all_disjoint():
    criteria = Whom(all=[
        whoms.bob,
        Whom(n=2, role="sibling"),
        Whom(all=[
            whoms.trusted,
            Whom(all=[
                Whom(n=2, role="employee"),
                Whom(n=2, role="investor"),
            ])
        ])
    ])
    # The list of principals should not satisfy the criteria listed above, because
    # we're asking for two employees and two investors -- and what we have is one
    # employee, one investor, and one employee+investor.
    assert not satisfies(principals.objs, criteria)
    # All 3 ways to fix the problem should result in a positive answer.
    assert satisfies(principals.objs + [Principal(roles=["investor"])], criteria)
    assert satisfies(principals.objs + [Principal(roles=["employee"])], criteria)
    assert satisfies(principals.objs + [Principal(roles=["employee", "investor"])], criteria)