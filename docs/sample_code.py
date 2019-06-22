# These first few lines let sample.py run from a folder in a weird location
# relative to source code. They wouldn't be needed if sgl is installed as
# a python package.
import os, sys
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))

from sgl.api import satisfies

my_rule = {"grant": ["enter_top_secret"], "to": { "role": "trusted" }}
people = [
    {"id": "Bob", "roles": ["employee"]},
    {"id": "Alice", "roles": ["employee", "trusted"]}
]

for person in people:
    name = person['id']
    print(f"Welcome, {name}." if satisfies(person, my_rule) else f"Access denied, {name}.")

