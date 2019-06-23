import json
from typing import Sequence, Union, List, Set

from .dbc import *
from .principal import Principal
from .rule import Rule
from .condition import Condition


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'to_dict'):
            return o.to_dict()
        return json.JSONEncoder.default(self, o)


def _unique_combinations(items, n):
    if n == 0:
        yield []
    else:
        for i in range(len(items)):
            for cc in _unique_combinations(items[i + 1:], n - 1):
                yield [items[i]] + cc


def _flatten_to_single_set(list_of_sets: List[set]) -> set:
    flat = set()
    for subset in list_of_sets:
        flat = flat.union(subset)
    return flat


def _get_min_group_size(cond):
    if cond.id:
        return 1
    elif cond.roles:
        return cond.n
    elif cond.any:
        n = 1000000000
        for c in cond.any:
            m = _get_min_group_size(c)
            if m < n:
                n = m
        return n
    else:
        n = 0
        for c in cond.all:
            n += _get_min_group_size(c)
        return n


def _get_matching_minimal_subsets(group: Set[Principal], c: Condition) -> List[Set[Principal]]:
    """
    Return a list of all minimal subsets of the group that match a condition. "Minimal" means that
    any group members unnecessary to the match have been stripped out, though some matches may take
    more principals than others. This is useful when we're trying to find disjoint combinations of
    unique individuals that match multiple condition.

    Note: semantically, this function deals with sets of sets, not lists of sets. However, it takes
    and returns a *list* of sets to avoid doing extra coding work to enforce uniqueness of the
    items in the outer container. (The uniqueness is already enforced by our algorithm; we don't
    need the set datatype to do it for us as well.)
    """
    answer = []
    if group and c:
        if c.id:
            for p in group:
                if p.id == c.id:
                    answer.append({p})
        elif c.roles:
            with_role = []
            for p in group:
                if p.roles and (c.roles in p.roles):
                    with_role.append(p)
            answer = [set(uc) for uc in _unique_combinations(with_role, c.n)]
        else:
            if c.any:
                matches = []
                for subcondition in c.any:
                    subsets = _get_matching_minimal_subsets(group, subcondition)
                    if subsets:
                        subset_for_this_criterion = _flatten_to_single_set(subsets)
                        matches.append(subset_for_this_criterion)
                if matches:
                    if c.n == 1:
                        answer = matches
                    else:
                        # Some of the logic that builds sets can't use lists or sets as
                        # elements, because they are unhashable. Create a wrapper class to
                        # work around this.
                        class HashableSet:
                            def __init__(self, set):
                                self.set = set
                            def __hash__(self):
                                return id(self)
                        list_of_lists_of_hashable_set = _unique_combinations(
                                [HashableSet(m) for m in matches], c.n)
                        if list_of_lists_of_hashable_set:
                            # We have to merge the inner lists of sets, so we end up with
                            # a single list of sets.
                            for what_should_be_flat_list in list_of_lists_of_hashable_set:
                                list_of_sets = [item.set for item in what_should_be_flat_list]
                                answer.append(_flatten_to_single_set(list_of_sets))

            elif c.all:
                first_subcondition = c.all[0]
                # The computation that follows is expensive -- up to factorial with the number of condition inside
                # the tree beneath the "all" expression, and possibly a few levels of recursion. Do some simple
                # optimizations. These may not actually speed up the code that much, most of the time. However,
                # they should avoid going through complex codepaths when simple logic will suffice, which should
                # be useful in debugging regardless.

                # Recurse to figure out all the ways we can satisfy this first subcondition.
                subsets = _get_matching_minimal_subsets(group, first_subcondition)

                # Optimization 1: skip rest of algorithm if we only have a list of 1.
                if len(c.all) == 1:
                    return subsets

                # Did we have any success on the first subcondition?
                if subsets:
                    # Build a new Condition that represents all the subconditions besides the first subcondition.
                    rest_of_subconditions = Condition(all=c.all[1:]) if len(c.all) > 2 else c.all[1]

                    # Optimization 2: figure out the minimum group size we need for the rest of the subconditions.
                    # Use that to skip any calculations that are doomed to failure. Part 1:
                    min_group_remainder_size = _get_min_group_size(rest_of_subconditions)
                    group_len = len(group)

                    # Try each subset to see if there's a way that, using this particular subset
                    # to satisfy the first subcondition, the rest of the subconditions can be satisfied
                    # with the remainder of the group. We have to try each subset, because some of them
                    # might overlap while others do not.
                    for subset in subsets:

                        # Optimization 2, part 2
                        if group_len - len(subset) < min_group_remainder_size:
                            continue

                        # Who's left if we use this subset to satisfy the first subcondition?
                        group_remainder = group - subset
                        # This test is probably redundant, since Optimization 2 should have eliminated
                        # empty groups. But we include it just to make the code robust.
                        if group_remainder:
                            # Okay, this is where we recurse instead of writing another inner loop.
                            # If this recursive call succeeds, then we've found a solution.
                            subsets_for_remainder = _get_matching_minimal_subsets(group_remainder, rest_of_subconditions)
                            if subsets_for_remainder:
                                # All of the subsets that satisfy the remainder need to be augmented by the subset
                                # that satisfies the first subcondition.
                                solution = [x.union(subset) for x in subsets_for_remainder]
                                answer.append(_flatten_to_single_set(solution))
            else:
                # This is a bit of an anomaly. None of conditions are set, so we don't have anything
                # to evaluate. This shouldn't happen -- the constructor of Condition disallows it. But
                # if it *does* happen, drop through.
                pass

    # We might have changed answer since we set its default value, or we might have let it
    # as an empty list. Either way, that's the correct answer if we get to this line.
    return answer


def satisfies(group: Union[Principal, Sequence[Principal], dict],
              condition: Union[Rule, Condition, dict], disjoint=True) -> bool:
    precondition(group, '"group" cannot be empty.')
    if isinstance(group, dict):
        group = [Principal.from_dict(group)]
    elif isinstance(group, Principal):
        group = [group]
    else:
        precondition_nonempty_sequence_of_x(group, "group", Principal)
    group = set(group)
    if isinstance(condition, dict):
        precondition(condition, '"condition" cannot be empty.')
        # Get a Condition object that we can test against.
        to = condition.get("when")
        # Does the dict contain a Rule?
        if to:
            # If yes, just convert the .when property from it into a Condition.
            condition = Condition.from_dict(to)
        else:
            # If not, convert the whole dict into a Condition.
            condition = Condition.from_dict(condition)
    elif isinstance(condition, Rule):
        condition = condition.when
    elif isinstance(condition, Condition):
        pass
    else:
        raise PreconditionViolation('"condition" must be a Rule, Condition, or non-empty dict.')
    # Now that we've checked all preconditions, call the internal function that does all the
    # work and that is recursive.
    return _check_satisfies(group, condition, disjoint)


def _check_satisfies(group: Set[Principal], c: Condition, disjoint) -> bool:
    # If the condition calls for us to match by id, do so. Note that we do
    # NOT need to also match by other characteristics; although a Principal can
    # have both an id and roles, condition cannot use both at the same time.
    if c.id:
        for p in group:
            if p.id == c.id:
                return True
    # If we have to match by role, see if our group includes enough that have the
    # required role.
    elif c.roles:
        n = c.n
        for p in group:
            if p.roles and (c.roles in p.roles):
                n -= 1
                if n == 0:
                    return True
    # If we are looking for a match against any one of several conditions,
    # test each condition individually, and return true if we find the right
    # number of matches.
    elif c.any:
        n = c.n if c.n else 1
        for condition in c.any:
            if _check_satisfies(group, condition, None):
                n -= 1
                if n == 0:
                    return True
        return False
    elif c.all:
        # If we're doing all (boolean AND) and disjoint subsets, we have to calculate
        # the actual subsets of the group that satisfy subsets of the c,
        # before we can return True or False.
        if disjoint:
            disjoint_subsets = _get_matching_minimal_subsets(group, c)
            return bool(disjoint_subsets)

        # This is much easier. Just see if all c are satisfied without checking to
        # see if the subsets of group that satisfies each are disjoint.
        else:
            for c in c.all:
                if not _check_satisfies(group, c, False):
                    return False
            return True
    return False
