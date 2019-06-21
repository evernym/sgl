import json
from typing import Sequence, Union, List, Set

from .dbc import *
from .principal import Principal
from .rule import Rule
from .whom import Whom


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


def _get_min_group_size(criteria):
    if criteria.id:
        return 1
    elif criteria.role:
        return criteria.n
    elif criteria.any:
        n = 1000000000
        for c in criteria.any:
            m = _get_min_group_size(c)
            if m < n:
                n = m
        return n
    else:
        n = 0
        for c in criteria.all:
            n += _get_min_group_size(c)
        return n


def _get_matching_minimal_subsets(group: Set[Principal], criterion: Whom) -> List[Set[Principal]]:
    """
    Return a list of all minimal subsets of the group that match a criterion. "Minimal" means that
    any group members unnecessary to the match have been stripped out, though some matches may take
    more principals than others. This is useful when we're trying to find disjoint combinations of
    unique individuals that match multiple criteria.

    Note: semantically, this function deals with sets of sets, not lists of sets. However, it takes
    and returns a *list* of sets to avoid doing extra coding work to enforce uniqueness of the
    items in the outer container. (The uniqueness is already enforced by our algorithm; we don't
    need the set datatype to do it for us as well.)
    """
    answer = []
    if group and criterion:
        if criterion.id:
            for p in group:
                if p.id == criterion.id:
                    answer.append({p})
        elif criterion.role:
            with_role = []
            for p in group:
                if p.roles and (criterion.role in p.roles):
                    with_role.append(p)
            answer = [set(uc) for uc in _unique_combinations(with_role, criterion.n)]
        else:
            if criterion.any:
                for subcriterion in criterion.any:
                    subsets = _get_matching_minimal_subsets(group, subcriterion)
                    if subsets:
                        subset_for_this_criterion = _flatten_to_single_set(subsets)
                        answer.append(subset_for_this_criterion)

            elif criterion.all:
                first_subcriterion = criterion.all[0]
                # The computation that follows is expensive -- up to factorial with the number of criteria inside
                # the tree beneath the "all" expression, and possibly a few levels of recursion. Do some simple
                # optimizations. These may not actually speed up the code that much, most of the time. However,
                # they should avoid going through complex codepaths when simple logic will suffice, which should
                # be useful in debugging regardless.

                # Recurse to figure out all the ways we can satisfy this first subcriterion.
                subsets = _get_matching_minimal_subsets(group, first_subcriterion)

                # Optimization 1: skip rest of algorithm if we only have a list of 1.
                if len(criterion.all) == 1:
                    return subsets

                # Did we have any success on the first subcriterion?
                if subsets:
                    # Build a new Whom that represents all the subcriteria besides the first subcriterion.
                    rest_of_subcriteria = Whom(all=criterion.all[1:]) if len(criterion.all) > 2 else criterion.all[1]

                    # Optimization 2: figure out the minimum group size we need for the rest of the criteria.
                    # Use that to skip any calculations that are doomed to failure. Part 1:
                    min_group_remainder_size = _get_min_group_size(rest_of_subcriteria)
                    group_len = len(group)

                    # Try each subset to see if there's a way that, using this particular subset
                    # to satisfy the first subcriterion, the rest of the subcriteria can be satisfied
                    # with the remainder of the group. We have to try each subset, because some of them
                    # might overlap while others do not.
                    for subset in subsets:

                        # Optimization 2, part 2
                        if group_len - len(subset) < min_group_remainder_size:
                            continue

                        # Who's left if we use this subset to satisfy the first subcriterion?
                        group_remainder = group - subset
                        # This test is probably redundant, since Optimization 2 should have eliminated
                        # empty groups. But we include it just to make the code robust.
                        if group_remainder:
                            # Okay, this is where we recurse instead of writing another inner loop.
                            # If this recursive call succeeds, then we've found a solution.
                            subsets_for_remainder = _get_matching_minimal_subsets(group_remainder, rest_of_subcriteria)
                            if subsets_for_remainder:
                                # All of the subsets that satisfy the remainder need to be augmented by the subset
                                # that satisfies the first subcriterion.
                                solution = [x.union(subset) for x in subsets_for_remainder]
                                answer.append(_flatten_to_single_set(solution))
            else:
                # This is a bit of an anomaly. None of criteria are set, so we don't have anything
                # to evaluate. This shouldn't happen -- the constructor of Whom disallows it. But
                # if it *does* happen, drop through.
                pass

    # We might have changed answer since we set its default value, or we might have let it
    # as an empty list. Either way, that's the correct answer if we get to this line.
    return answer


def satisfies(group: Union[Principal, Sequence[Principal], dict],
              criteria: Union[Rule, Whom, dict], disjoint=True) -> bool:
    precondition(group, '"group" cannot be empty.')
    if isinstance(group, dict):
        group = [Principal.from_dict(group)]
    elif isinstance(group, Principal):
        group = [group]
    else:
        precondition_nonempty_sequence_of_x(group, "group", Principal)
    group = set(group)
    if isinstance(criteria, dict):
        precondition(criteria, '"criteria" cannot be empty.')
        # Get a Whom object that we can test against.
        to = criteria.get("criteria")
        # Does the dict contain a Rule?
        if criteria:
            # If yes, just convert the .criteria property from it into a Whom.
            criteria = Whom.from_dict(criteria)
        else:
            # If not, convert the whole dict into a Whom.
            criteria = Whom.from_dict(criteria)
    elif isinstance(criteria, Rule):
        criteria = criteria.to
    elif isinstance(criteria, Whom):
        pass
    else:
        raise PreconditionViolation('"criteria" must be a Rule, Whom, or non-empty dict.')
    # Now that we've checked all preconditions, call the internal function that does all the
    # work and that is recursive.
    return _check_satisfies(group, criteria, disjoint)


def _check_satisfies(group: Set[Principal], criteria: Whom, disjoint) -> bool:
    # If the criteria call for us to match by id, do so. Note that we do
    # NOT need to also match by other characteristics; although a Principal can
    # have both an id and roles, criteria cannot use both at the same time.
    if criteria.id:
        for p in group:
            if p.id == criteria.id:
                return True
    # If we have to match by role, see if our set of group include enough
    # that have the required role.
    elif criteria.role:
        n = criteria.n
        for p in group:
            if p.roles and (criteria.role in p.roles):
                n -= 1
                if n == 0:
                    return True
    # If we are looking for a match against any one of several criteria,
    # test each criterion individual, and return true if we find one
    # that matches.
    elif criteria.any:
        for criterion in criteria.any:
            if _check_satisfies(group, criterion, None):
                return True
        return False
    elif criteria.all:
        # If we're doing all (boolean AND) and disjoint subsets, we have to calculate
        # the actual subsets of the group that satisfy subsets of the criteria,
        # before we can return True or False.
        if disjoint:
            disjoint_subsets = _get_matching_minimal_subsets(group, criteria)
            disjoint_subsets = bool(disjoint_subsets)
            return disjoint_subsets

        # This is much easier. Just see if all criteria are satisfied without checking to
        # see if the subsets of group that satisfies each are disjoint.
        else:
            for criterion in criteria.all:
                if not _check_satisfies(group, criterion, False):
                    return False
            return True
    return False

