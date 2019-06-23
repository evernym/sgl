# SGL Renderings

A __rendering__ is a way to represent the semantics of SGL constructs.
There are many possible renderings of SGL. The python implementation
is JSON-centric.

### JSON

The default and recommended rendering is JSON. In this rendering, each
object ([rule](reference.md#rules), [criterion](reference.md#criterion),
and [principal](reference.md#principal) is a JSON object -- `{...}`. 
Sets are JSON arrays -- `[...]`.

### Protobuf

TODO

### MsgPack

TODO

### Human-friendly text

This might be a useful rendering when displaying rules to people who
are not developers. For example, it could be used in documentation, 
academic papers, error messages, and so forth.

In this rendering, rules look like:

```text
Grant priv1, priv2, priv3 if id is "Bob". 
Grant priv4 if role is role1.
Grant priv5, priv6 if any of (subcriterion1; subcriterion2).
Grant priv7 if 2 of (subcriterion3; subcriterion4; subcriterion5).
Grant priv8 if all of (subcriterion6; subcriterion7).
```

Note the capital letter on "Grant", the period at the end of each
rule/sentence, and the semicolons that separate subcriteria. The words
"Grant", "if", "is", "of", "any" and "all" function like reserved words
in the syntax. Note that only `id` is quoted; because names of priviliges
and roles are tokens without whitespace, no quotes are needed or allowed
around these.

Descriptions of principals are written like this:

```text
Principal "Bob" has roles role1, role2, role3.
Principal 2 has roles role4, role5. 
```

The first form is used when the principal has an id. The second form
uses an unquoted number to indicate that an ephemeral ID has been assigned.

## See also
* [Overview](../README.md)
* [Tutorial](tutorial.md)
* [Reference](reference.md)
