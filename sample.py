from sgl.rule import Rule
from sgl.principal import Principal
from sgl.api import satisfies

my_rule = Rule.from_json('{"grant": ["enter_top_secret"], "to": { "role": "trusted" }}')
people = [
    Principal.from_json('{"id": "Bob", "roles": ["employee"]}'),
    Principal.from_json('{"id": "Alice", "roles": ["employee", "trusted"]}')
]

for person in people:
    print(f"Welcome, {person.id}." if satisfies(person, my_rule) else f"Access denied, {person.id}.")
