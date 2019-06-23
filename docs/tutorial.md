# SGL Tutorial

SGL __rules__ grant __privileges__ to __principals__ (people, devices,
software packages, or other entities) when (if) they satisfy
__conditions__.


### General Pattern

To use SGL, follow this pattern:

1. Name the privileges that are relevant to your problem domain.
2. Choose conditions that govern how the privileges apply to your use
cases.
3. Write rules that express your decisions.
4. Assign properties to the principals that need privileges.
5. As privileges need to be tested during system operation, call SGL
APIs to make decisions.

### Example

Suppose you are building software that enforces guardianship procedures
for orphan children in a refugee camp (one of the use cases for which
SGL was developed). You need something a bit fancier that just "X is the
guardian of Y" -- an older sibling might have a few guardianship
privileges, a grandparent more privileges, etc.

#### Step 1: name privileges

In step 1, you might name the following privileges that guardians could
have:

* __medical-care__: Consent to medical treatment.
* __school__: Enroll or unenroll dependent in school programs.
* __rations__: Receive food, hygiene items, clothing, and other materials allocated to the dependent.
* __travel__: Take the dependent outside the camp.

#### Step 2: choose conditions

In step 2, you might come up with the following guidelines about how
privileges should work:

* A grandparent can approve medical care or school enrollment for the
child.
* Either a grandparent or a sibling can get rations for the child.
* Because travel outside the camp is risky, two grandparents or one
grandparent plus the majority of a tribal council of 5 elders must
approve travel outside the camp.

#### Step 3: write rules

You could turn these decisions into 3 SGL rules, which, in the JSON
[rendering style](renderings.md), look like:

```JSON
{
  "grant": ["medical", "school"],
  "when": {"roles": "grandparent"}
}
```

```JSON
{
  "grant": ["rations"],
  "when": {
    "any": [
      {"roles": "grandparent"},
      {"roles": "sibling"}
    ]
  }
}
```

```JSON
{
  "grant": ["travel", "appoint"],
  "when": {
    "any": [
      {"n": 2, "roles": "grandparent"},
      {
        "all": [
          {"roles": "grandparent"},
          {"n": 3, "roles": "tribal_council"}
        ]
      }
    ]
  }
}
```

#### Step 4: assign properties

So far we've decided that grandparents and siblings have certain
privileges--but just who __are__ the grandparents and siblings of a given
orphan, and what, specifically, do we know about them?

Now is when you answer that question. You can store your answers in any
way you like: by issuing [verifiable credentials](
https://w3c.github.io/vc-data-model/), by adding custom properties in
LDAP, by creating a database of people and their relationships, etc.

However, in the next step, we will have to call SGL APIs. These require
that knowledge about principals be expressed in a standard format (one or
more SGL `Principal` objects). Therefore, whatever storage mechanism you
pick, you must be able to produce data like this:

```JSON
[
    { "id": "Amena", "roles": ["grandparent", "tribal_council"] },
    { "id": "Sayid", "roles": ["sibling"] },
    { "id": "Tarek", "roles": ["tribal_council"] },
    { "id": "Uri", "roles": ["tribal_council"] }
]
```

>NOTE: In this tutorial, the only properties we are tracking and testing rules
against for principals are the `id` and `roles` properties, but we can
have much richer principals if that's helpful. See [Custom Properties](
custom-properties.md) for more information. 

#### Step 5: call APIs to make decisions

Now, when a group of adults shows up at the camp gate with an orphan
in tow, and asks to travel with the child, you can use SGL to decide if
they're authorized, or if their request should be denied. To do this,
you identify the orphan, then look through your stored data to see who
has particular roles with respect to her. You build a list of data items
like the one shown in step 4, describing all the principals in the group.
Then you call SGL's `satisfies()` API:

```python
if satisfies(group, travel_rule, disjoint=True):
    open_gate()
```

If the list were identical to the one in step 4, `satisfies()` would
return `False`, because the condition of (2\*grandparent or
(1\*grandparent + 3\*tribal_council)) is not satisfied by the group.
(The `disjoint=True` arg prevents Amena from using both of her roles in
the same rule; if she wants to claim to be a grandparent, then she can't
vote as a tribal council member, and vice versa.)

If `disjoint` were set to `False`, or if a new adult joined the group,
and that person were either a tribal council member or the child's
grandparent, then `satisfies()` would return `True`.

All of the ingredients used by SGL--rules, privileges, principals, and
condition--can be much fancier than what's shown in this scenario. 

## See also
* [Overview](../README.md)
* [Reference](reference.md)
* [Renderings](renderings.md)
* [Custom Properties](custom-properties.md)