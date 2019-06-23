[![CircleCI](https://circleci.com/gh/dhh1128/sgl.svg?style=svg)](
https://circleci.com/gh/dhh1128/sgl)

# SGL (Simple Grant Language)

SGL is a simple but flexible [DSL](
https://en.wikipedia.org/wiki/Domain-specific_language) for granting and
testing privileges (authorization). You can use it to write rules about
who should be able to do what, and then to compare circumstances to the
rules to enforce custom logic. This lets you create your own [Role-Based
Access Control]( https://en.wikipedia.org/wiki/Role-based_access_control)
mechanisms, as well as authorizations based on other criteria.

For example, here's an SGL rule that says only members of the press
should be allowed backstage at a concert:

```JSON
{"grant": ["backstage"], "when": { "role": "press" }}
```

And here's how you might use that rule in code:

```python
from sgl.api import satisfies

my_rule = {"grant": ["backstage"], "when": { "role": "press" }}

people = [
    {"id": "Alex", "roles": ["ticket-holder"]},
    {"id": "Sofia", "roles": ["ticket-holder", "premium"]}
]

for person in people:
    name = person['id']
    if satisfies(person, my_rule):
        print(f"Welcome backstage, {name}.")
    else:
        print(f"Sorry, this area is restricted, {name}.")
```

If you ran this code, you'd see:

```bash
$ python sample_code.py
Sorry, this area is restricted, Alex.
Welcome backstage, Sofia.
```

SGL supports arbitrarily complex rules with boolean operators, as well
as rules that require multiple people to jointly exercise a privilege.
However, it's simple enough that you should be able to learn it in just
a few minutes. See the [tutorial](
https://dhh1128.github.io/sgl/docs/tutorial.html).

>Note: SGL can be [rendered in various styles](
https://dhh1128.github.io/sgl/docs/renderings.html). The example above
uses the recommended JSON rendering, since JSON is familiar, broadly
supported, and easy to read. Other possibilities include ProtoBuf,
MsgPack, CBOR, and human-friendly text.

SGL is not integrated with any particular enforcement mechanism, because
it's designed for problems where you have to do your own enforcement.
Hooking it up to enforcement mechanisms is trivial, though.

## See also
* [Tutorial](https://dhh1128.github.io/sgl/docs/tutorial.html)
* [Reference](https://dhh1128.github.io/sgl/docs/reference.html)