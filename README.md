[![CircleCI](https://circleci.com/gh/dhh1128/sgl.svg?style=svg)](
https://circleci.com/gh/dhh1128/sgl)

# SGL (Structured Grant Language)

SGL is a simple but flexible JSON-based DSL for granting and testing
permissions (authorization). You can use this language to write powerful
but easy-to-read rules about who can do what, and then evaluate the
rules to enforce business logic.

For example, here's an SGL rule that expresses the idea that only people
with "trusted" status should enter a top-secret area:

```JSON
{"grant": ["enter_top_secret"], "to": { "role": "trusted" }}
```

And here's how you might use that rule in code:

```python
from sgl.api import satisfies

my_rule = {"grant": ["enter_top_secret"], "to": { "role": "trusted" }}
people = [
    {"id": "Bob", "roles": ["employee"]},
    {"id": "Alice", "roles": ["employee", "trusted"]}
]

for person in people:
    name = person['id']
    print(f"Welcome, {name}." if satisfies(person, my_rule) else f"Access denied, {name}.")
```

If you ran this code, you'd see:

```bash
$ python sample_code.py
Access denied, Bob.
Welcome, Alice.
```

SGL supports arbitrarily complex rules with boolean operators and
requirements about multiple parties being jointly authorized. However,
you should be able to learn the whole language in 5 minutes. See the
[tutorial](https://dhh1128.github.io/sgl/docs/tutorial.html).

SGL is not integrated with any particular enforcement mechanism, because
it's designed for problems where you have to do your own enforcement.
Hooking it up to enforcement mechanisms is trivial, though.

## See also
* [Tutorial](https://dhh1128.github.io/sgl/docs/tutorial.html)
* [Reference](https://dhh1128.github.io/sgl/docs/tutorial.html)