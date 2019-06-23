# SGL
## Reference

### Rules
A __rule__ is a JSON object in the form:

```JSON
{"grant": privileges, "to": criterion}
```

#### Privileges
The `privileges` field is an array of tokens (strings) that name
privileges meaningful in your problem domain.

#### Criterion
The `criterion` field defines who gets the privileges listed
in the `grant`. The `criterion` is a JSON object that can take one of
4 forms:

1. A specific identifier.
 
    ```JSON
    {"id": "Fred"}
    ```
2. Members of a set, such as "3 of my friends".
 
    ```JSON
    {"n": 3, "role": "friend"}
    ```
    
3. An "any" rule (boolean OR) to match any nested criterion in its array,
such as "a parent or a sibling":

    ```JSON
    {"any": [
        {"role": "parent"},
        {"role": "sibling"}
    ]}
    ```
    
    Note that the inner criteria here use form #2 (members of a set), but
    `n` has been omitted as unnecessary, leaving it with its default value
    of 1.

4. An "all" rule (boolean AND) to match all of the nested criteria in its
array, such as "an employee, a customer, and a person with id "86745309":

    ```JSON
    {"any": [
        {"role": "employee"},
        {"role": "customer"},
        {"id":  "8675309"}
    ]}
    ```

Using `any` and `all`, rules can be composed--nested and combined to tree
structures of arbitrary complexity.

### Implementations

SGL is usable in any programming language that supports JSON.
The initial implementation is in python. Ports in other languages will
be forthcoming. 

### What SGL code does

An implementation of SGL provides one or more APIs to test whether a
particular group satisfies the criteria in the rule. For example, it
answers questions like, "The group I'm testing contains a person with
`id`=`Bob` and the roles `maintenance` and `employee`; given these
privileges, do my rules allow him to turn off the air conditioning?" 

The implementation in python does this with a single API:

```python
def satisfies(group, criteria, disjoint=True) -> bool  
```

This tells whether a group satisfies the criteria embodied in a rule.
See [Reference](reference.md#satisfies) for an explanation of `disjoint`.

Here, `group` is one or more people--the set about which we want to 
check privileges. The python implementation provides a `Principal` object
that makes building `group` easy. Taking advantage of python's loose
typing, `group` can be an array of `Principal`, or a single `Principal`,
or a `dict` built from `Principal`-compatible JSON. A `Principal`
identifies an entity with an `id` or a set of `roles` that the entity
holds, or both. So a valid `group` arg might be:

```JSON
[ {"id": "Bob", "roles": ["employee", "friend"]} ]
```

or maybe:

```python
Principal( id="Sally", roles=["CEO"] )
```


### Structures

#### Rule.grant
Contains a set of strings that name privileges or roles meaningful
in your business domain. You make these up. Case-sensitive. Order
doesn't matter. Duplicates are removed.

#### Rule.to
Contains a criterion in one of the [4 forms discussed in the tutorial](
tutorial.md#criterion).

#### Principal.id
Contains a string that uniquely identifies the principal. This might be
an employee UUID, a customer email address, or a first name. ID is
optional and, when present, are used to match against a rule that
uses a [criterion in the form `{"id": value}`](#criterion-id).

#### Principal.roles
A set of strings that names privileges belonging to this principal.
These are matched against a rule in the form `{"role": value}` and
therefore share all the same semantics as [Rule.grant`](#rule-grant)
and [Criterion.role`](#criterion-role).

#### Criterion.id
Gives an `id` that must be present in the group in order to satisfy
the rule.

#### Criterion.role
Gives a role that must be present in the group to satisfy the rule.
Mutually exclusive with `id`, `any`, and `all`. When this form of
criterion is used, `n` is meaningful; otherwise it is ignored.

#### Criterion.n
Tells how many unique instances of a role must be present to satisfy
the rule. Only meaningful when `role` is also present. When omitted,
default value is 1. Must be a positive integer (or a float castable
to integer without data loss).

#### Criterion.all
Mutually exclusive with Criterion.id`, Criterion.role`, and Criterion.any`.
Value is an array of Criterion objects, all of which must be satisfied
satisfy the parent criterion.

See the note about [`disjoint`](#disjoint) for advanced usage.

#### Criterion.any
Mutually exclusive with Criterion.id`, Criterion.role`, and Criterion.all`.
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