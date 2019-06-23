# Custom Properties

Most of the examples in the documentation focus on the `id` and `roles`
that belong to principals; this is how you get [Role-Based Access Control](
https://en.wikipedia.org/wiki/Role-based_access_control), which is a
common feature request in business software.

### Example: doctor discount

But some situations call for privileges to be based on other
characteristics besides `roles` and `id`. For example, how could you use
SGL to authorize doctors to receive a discount on insurance if they have
more than 20 years of experience, and if they are a fellow of the 
American Academy of Family Physicians (possess the FAAFP certification)?

The answer is that principal objects can have as many additional
properties as are useful in a particular system. For example:

```JSON
{ 
  "id": "Prabhakar Ro", 
  "years_exp": 27, 
  "certifications": ["ABPP", "MCHES", "CHSE", "FAAFP"]
}
``` 

And rule objects can then reference these properties in exactly the same
way that they reference `id` and `roles`:

```JSON
{ 
    "grant": "insurance-discount",
    "when": {
        "any": [
            {"years_exp": 20, "op": ">"},
            {"certifications": "FAAFP"}
        ]
    }
}
``` 

### Operators

Did you raise your eyebrows at the claim that this is "exactly the same"
way that `id` and `roles` work? Was that because the `op` in the `years_exp`
condition?

The fact is, each type of condition has an `op` field, but usually it is
omitted because its default value is correct. But other operators are
possible:

* __comparison__: `=` (the default for scalar values); also `<`, `>`,
`<=`, `>=`, `!=`
* __sets__: `in` (the default for array values); also `not in`
and `contains`. When the comparison operators are used with a value
that's a set, they are testing the set's size. Thus, if we wanted to
say that the insurance discount from our example above depended not on
a specific certification, but having 3 or more certications, we could
revise the rule to:

    ```JSON
    { 
        "grant": "insurance-discount",
        "when": {
            "any": [
                {"years_exp": 20, "op": ">"},
                {"certifications": 3, "op": ">="}
            ]
        }
    }    
    ```
    
* __fuzzy__: `like` (regex). Possibilities like `stddev`/`zscore` and
 `soundex` are conceivable in this category, but not currently implemented. 