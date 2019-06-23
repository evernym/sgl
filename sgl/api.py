import json
from typing import Sequence, Union, List, Set

from .dbc import *
from .principal import Principal
from .rule import Rule
from .criterion import Criterion


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


def _get_min_group_size(criterion):
    if criterion.id:
        return 1
    elif criterion.role:
        return criterion.n
    elif criterion.any:
        n = 1000000000
        for c in criterion.any:
            m = _get_min_group_size(c)
            if m < n:
                n = m
        return n
    else:
        n = 0
        for c in criterion.all:
            n += _get_min_group_size(c)
        return n


def _get_matching_minimal_subsets(group: Set[Principal], criterion: Criterion) -> List[Set[Principal]]:
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
                matches = []
                for subcriterion in criterion.any:
                    subsets = _get_matching_minimal_subsets(group, subcriterion)
                    if subsets:
                        subset_for_this_criterion = _flatten_to_single_set(subsets)
                        matches.append(subset_for_this_criterion)
                if matches:
                    if criterion.n == 1:
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
                                [HashableSet(m) for m in matches], criterion.n)
                        if list_of_lists_of_hashable_set:
                            # We have to merge the inner lists of sets, so we end up with
                            # a single list of sets.
                            for what_should_be_flat_list in list_of_lists_of_hashable_set:
                                list_of_sets = [item.set for item in what_should_be_flat_list]
                                answer.append(_flatten_to_single_set(list_of_sets))

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
                    # Build a new Criterion that represents all the subcriteria besides the first subcriterion.
                    rest_of_subcriteria = Criterion(all=criterion.all[1:]) if len(criterion.all) > 2 else criterion.all[1]

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
                # to evaluate. This shouldn't happen -- the constructor of Criterion disallows it. But
                # if it *does* happen, drop through.
                pass

    # We might have changed answer since we set its default value, or we might have let it
    # as an empty list. Either way, that's the correct answer if we get to this line.
    return answer


def satisfies(group: Union[Principal, Sequence[Principal], dict],
              criterion: Union[Rule, Criterion, dict], disjoint=True) -> bool:
    precondition(group, '"group" cannot be empty.')
    if isinstance(group, dict):
        group = [Principal.from_dict(group)]
    elif isinstance(group, Principal):
        group = [group]
    else:
        precondition_nonempty_sequence_of_x(group, "group", Principal)
    group = set(group)
    if isinstance(criterion, dict):
        precondition(criterion, '"criterion" cannot be empty.')
        # Get a Criterion object that we can test against.
        to = criterion.get("to")
        # Does the dict contain a Rule?
        if to:
            # If yes, just convert the .to property from it into a Criterion.
            criterion = Criterion.from_dict(to)
        else:
            # If not, convert the whole dict into a Criterion.
            criterion = Criterion.from_dict(criterion)
    elif isinstance(criterion, Rule):
        criterion = criterion.to
    elif isinstance(criterion, Criterion):
        pass
    else:
        raise PreconditionViolation('"criterion" must be a Rule, Criterion, or non-empty dict.')
    # Now that we've checked all preconditions, call the internal function that does all the
    # work and that is recursive.
    return _check_satisfies(group, criterion, disjoint)


def _check_satisfies(group: Set[Principal], criterion: Criterion, disjoint) -> bool:
    # If the criterion calls for us to match by id, do so. Note that we do
    # NOT need to also match by other characteristics; although a Principal can
    # have both an id and roles, criteria cannot use both at the same time.
    if criterion.id:
        for p in group:
            if p.id == criterion.id:
                return True
    # If we have to match by role, see if our group includes enough that have the
    # required role.
    elif criterion.role:
        n = criterion.n
        for p in group:
            if p.roles and (criterion.role in p.roles):
                n -= 1
                if n == 0:
                    return True
    # If we are looking for a match against any one of several criteria,
    # test each criterion individually, and return true if we find one
    # (or, for n > 1, n) match(es).
    elif criterion.any:
        n = criterion.n if criterion.n else 1
        for criterion in criterion.any:
            if _check_satisfies(group, criterion, None):
                n -= 1
                if n == 0:
                    return True
        return False
    elif criterion.all:
        # If we're doing all (boolean AND) and disjoint subsets, we have to calculate
        # the actual subsets of the group that satisfy subsets of the criterion,
        # before we can return True or False.
        if disjoint:
            disjoint_subsets = _get_matching_minimal_subsets(group, criterion)
            return bool(disjoint_subsets)

        # This is much easier. Just see if all criterion are satisfied without checking to
        # see if the subsets of group that satisfies each are disjoint.
        else:
            for criterion in criterion.all:
                if not _check_satisfies(group, criterion, False):
                    return False
            return True
    return False
