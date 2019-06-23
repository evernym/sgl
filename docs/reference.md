# SGL Reference

>NOTE 1: SGL can be [rendered in various styles](
https://dhh1128.github.io/sgl/docs/renderings.html). The definitions
given here in the reference section just use the recommended JSON
rendering, for conciseness and simplicity. It is assumed that you can
interpolate into ProtoBuf, MsgPack, CBOR, human-friendly text, or
another rendering if that is of interest to you.

### Rules
A __rule__ is an object in the form:

```JSON
{"id": x, "grant": privileges, "to": criterion}
```

#### Rule.id
This field is optional and often omitted. If present, it provides a
convenient identifier that can be used to refer to the rule.

#### Rule.grant
Contains a set of strings that name privileges meaningful in your
problem domain. For more on semantics, see [Privileges](#privileges)
below.

#### Rule.to
Contains a [criterion](#criterion).
 
### Privileges
You make up privilege names. They should be short tokens without leading,
trailing, or internal whitespace, and without punctuation characters
that could cause problems for parsers. Unicode is supported in [NFKC
form](https://unicode.org/reports/tr15/); however, `snake_case` ASCII is
recommended for maximum interoperability. Privileges are compared
case-sensitive. Order doesn't matter, and duplicates are removed.

### Criterion
A __criterion__ defines who gets the privileges listed in a [rule](
#rules).

There are 4 variants of criterion. The variants cannot be combined (e.g.,
mixing "id" with "role" or "any" or "all", although they can be
implemented with a single structure that assigns `null` to unused fields).

#### Criterion with id
This variant requires a specific identifier:
 
```JSON
{"id": "Fred"}
```
    
#### Criterion with role
This variant requires one or more principals holding a role:
 
```JSON
{"n": 3, "role": "friend"}
```

The `n` field is optional. If omitted, `"n": 1` is assumed.
    
#### Criterion with any
This variant provides boolean OR features. It requires a match against
any of the criteria nested in its array:

```JSON
{"any": [
    {"role": "grandparent"},
    {"role": "sibling"}
]}
```

Criteria with `any` can also have an `n` field. If present, it specifies
that `n` subcriteria must be satisfied from among all the alternatives
(instead of the default, 1). __Note that this is NOT requiring *n*
matching principals from the group__. This criterion says that out of
the list of 3 subcriteria, any 2 must be satisfied, NOT that any of the
3 listed roles must match twice:
    
```JSON
{"any": [
    {"role": "employee"},
    {"role": "investor"},
    {"role": "customer"}
], "n": 2}
```

In this situation, `n` can be a number larger than the number of elements
in the `any` array of criteria. For example, if the above rule were
changed so `n` equaled 5, the semantics would be that 5 times a match
would have to be found for one of the 3 listed subcriteria. (The behavior
here is affected by the [`disjoint`](#disjoint) parameter to the 
`satisfies()` API.)

#### Criterion with all
This provides boolean AND features. It requires a match against all of
the criteria nested in its array:

```JSON
{"any": [
    {"role": "employee"},
    {"role": "customer"},
    {"id":  "8675309"}
]}
```

See the note about [`disjoint`](#disjoint) for advanced usage.

### Principal

#### Principal.id
Contains a string that uniquely identifies the principal. This might be
an employee UUID, a customer email address, or a first name. The `id`
field is optional and, when present, iw used to match against a [
criterion with id](#criterion-with-id).

#### Principal.roles
A set of strings that name roles belonging to this principal.
These are matched against a [criterion with role](#criterion-with-role).

Role names have the same [rules about format and comparison as privilege
names](#privileges).

### API

#### `satisfies()`

Python:

```python
def satisfies(group, criteria, disjoint=True) -> bool  
```

Tells whether a group satisfies the criteria embodied in a rule.
See [Reference](reference.md#satisfies) for an explanation of `disjoint`.

Here, `group` is one or more [principals](#principal)--the set about
which we want to check privileges. Taking advantage of python's loose
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
[disjoing]: #disjoint

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