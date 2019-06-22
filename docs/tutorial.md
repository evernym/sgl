## Tutorial

### Rules

A __rule__ is a JSON object in the form `{"grant": privileges, "to": criterion}`. 

#### Privileges
The `privileges` field is an array of strings that name privileges meaningful
in your business logic.

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
See [Reference](reference.md) for an explanation of `disjoint`.

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

#### Practical Example

Suppose you are building software that enforces guardianship procedures
for an orphan child in a refugee camp (one of the use cases for which
SGL was developed). The rules you want to enforce are:

* A grandparent can approve medical care or school enrollment for the child,
and can delegate their permissions to another adult.
* A grandparent and a sibling *together but not separately* can get
rations for the child.
* Two grandparents or one grandparent plus the majority of a tribal
council of 5 elders can approve travel outside the camp, or appoint
a new guardian.

You could turn this into three SGL rules, as follows:

```JSON
{
  "grant": ["medical", "school", "delegate"],
  "to": {"role": "grandparent"}
}
```

```JSON
{
  "grant": ["rations"],
  "to": {
    "all": [
      {"role": "grandparent"},
      {"role": "sibling"}
    ]
  }
}
```

```JSON
{
  "grant": ["travel", "appoint"],
  "to": {
    "any": [
      {"n": 2, "role": "grandparent"},
      {
        "all": [
          {"role": "grandparent"},
          {"n": 3, "role": "tribal_council"}
        ]
      }
    ]
  }
}
```

Now, when a person shows up at the school with a small child in tow, and asks
to enroll them, you can ask them for proof of the privileges that they have.
Suppose they produce such proof, and it looks like this (embodied in JSON
or in a python `Principal` object):

```JSON
{"roles": ["grandparent"]}
```

When you call `satisfies(this_grandparent, school_rule)`, the result will be
`True`. But if a sibling shows up...

```JSON
{"roles": ["grandparent"]}
```

...and attempts the same thing, `satisfies(this_sibling, school_rule)` will return
`False`.

## See also
* [Overview](../README.md)
* [Reference](reference.md)