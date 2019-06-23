# These first few lines let sample.py run from a folder in a weird location
# relative to source code. They wouldn't be needed if sgl is installed as
# a python package.
import os, sys
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))

from sgl.api import satisfies

my_rule = {"grant": ["backstage"], "when": { "roles": "press" }}

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