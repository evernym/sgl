[![CircleCI](https://circleci.com/gh/dhh1128/sgl.svg?style=svg)](
https://circleci.com/gh/dhh1128/sgl)

# SGL (Simple Grant Language)

SGL is a simple but flexible [DSL](
https://en.wikipedia.org/wiki/Domain-specific_language) for granting and
testing privileges (authorization). You can use it to write rules about
who should be able to do what, and then to compare people to the rules
to enforce business logic. Among other things, this lets you create
custom [Role-Based Access Control](
https://en.wikipedia.org/wiki/Role-based_access_control) mechanisms.

For example, here's an SGL rule that says only members of the press
should be allowed backstage at a concert:

```JSON
{"grant": ["backstage"], "to": { "role": "press" }}
```

And here's how you might use that rule in code:

```python
from sgl.api import satisfies

my_rule = {"grant": ["backstage"], "to": { "role": "press" }}

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
However, you should be able to learn the whole language in 10 minutes.
See the [tutorial](https://dhh1128.github.io/sgl/docs/tutorial.html).

>Note: SGL can be rendered in various styles. The docs generally use the
recommended JSON rendering, since JSON is familiar, broadly supported,
and easy to read. For information about SGL in ProtoBuf, MsgPack, CBOR,
or other styles, see [Other Renderings](
https://dhh1128.github.io/sgl/docs/other-renderings.html).

SGL is not integrated with any particular enforcement mechanism, because
it's designed for problems where you have to do your own enforcement.
Hooking it up to enforcement mechanisms is trivial, though.

## See also
* [Tutorial](https://dhh1128.github.io/sgl/docs/tutorial.html)
* [Reference](https://dhh1128.github.io/sgl/docs/tutorial.html)