# SGL
## Reference

### Structures

#### Rule.`grant`
Contains a set of strings that name privileges or roles meaningful
in your business domain. You make these up. Case-sensitive. Order
doesn't matter. Duplicates are removed.

#### Rule.`to`
Contains a criterion in one of the [4 forms discussed in the tutorial](
tutorial.md#criterion).

#### Principal.`id`
Contains a string that uniquely identifies the principal. This might be
an employee UUID, a customer email address, or a first name. ID is
optional and, when present, are used to match against a rule that
uses a [criterion in the form `{"id": value}`](#criterion-id).

#### Principal.`roles`
A set of strings that names privileges belonging to this principal.
These are matched against a rule in the form `{"role": value}` and
therefore share all the same semantics as [Rule.`grant`](#rule-grant)
and [Criterion.`role`](#criterion-role).

#### Criterion.`id`
Gives an `id` that must be present in the group in order to satisfy
the rule.

#### Criterion.`role`
Gives a role that must be present in the group to satisfy the rule.
Mutually exclusive with `id`, `any`, and `all`. When this form of
criterion is used, `n` is meaningful; otherwise it is ignored.

#### Criterion.`n`
Tells how many unique instances of a role must be present to satisfy
the rule. Only meaningful when `role` is also present. When omitted,
default value is 1. Must be a positive integer (or a float castable
to integer without data loss).

#### Criterion.`all`
Mutually exclusive with Criterion.`id`, Criterion.`role`, and Criterion.`any`.
Value is an array of Criterion objects, all of which must be satisfied
satisfy the parent criterion.

See the note about [`disjoint`](#disjoint) for advanced usage.

#### Criterion.`any`
Mutually exclusive with Criterion.`id`, Criterion.`role`, and Criterion.`all`.
Value is an array of Criterion objects, any of which can satisfy the parent
criterion.

### API

#### `satisfies()`

The `satisfies(group, criterion, disjoint=True) -> bool` function tells
whether a particular group satisfies the criterion, as [described in the
tutorial](#what-sgl-code-does).

* `disjoint` controls whether the subset of the group that satisfies
each part of a criterion tree must be disjoint (non-overlapping). Normally,
you want `disjoint` to be true. For example, if your criteria include
a requirement that 2 people with the `employee` privilege and 2 with
the `investor` privilege cooperate to exercise a privilege like
`board_vote_of_no_confidence`, you don't want 2 employees who are also
investors to satisfy both criteria; you want 4 people at a minimum.
Setting `disjoint` to `False` allows the overlap.

## See also
* [Overview](../README.md)
* [Tutorial](tutorial.md)