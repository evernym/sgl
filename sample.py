from sgl.api import satisfies

my_rule = {"grant": ["enter_top_secret"], "to": { "role": "trusted" }}
people = [
    {"id": "Bob", "roles": ["employee"]},
    {"id": "Alice", "roles": ["employee", "trusted"]}
]

for person in people:
    name = person['id']
    print(f"Welcome, {name}." if satisfies(person, my_rule) else f"Access denied, {name}.")

