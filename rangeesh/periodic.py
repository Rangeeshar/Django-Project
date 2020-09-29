import os
import sys
import django
import requests as rq

REQUEST_URI = "https://swapi.dev/api/people/?search={}"
# Turn off bytecode generation
sys.dont_write_bytecode = True
# Django specific settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "galactica.settings")
django.setup()
from star_wars.models import People

# model fields
FIELDS = [
    "birth_year",
    "created",
    "name",
    "gender",
    "height",
    "mass",
    "eye_color",
]

# Ignoring as these are dynamic and will change
IGNORE = ["_state", "edited", "created", "id"]

# Getting instances of objects and checking
def check_and_update(m1, m2):
    values = {k: v for k, v in m1.__dict__.items() if k not in IGNORE}
    other_values = {k: v for k, v in m2.__dict__.items() if k not in IGNORE}
    # Getting unmatching records and taking update fields to insert
    difference = {
        i: other_values[i] for i in values.keys() if other_values[i] != values[i]
    }
    try:
        if difference and People.objects.filter(id=m2.id):
            People.objects.filter(id=m2.id).update(**difference)  # Updating in People

    except Exception as e:
        return False

    return True


def compare(data, record):
    # Creating a temp obj and return if needs a change.
    people_obj = People(
        birth_year=data.get("birth_year"),
        eye_color=data.get("eye_color"),
        gender="Undisclosed" if data.get("gender") == "n/a" else data.get("gender"),
        height=int(data.get("height", 0)),
        mass="0" if data.get("mass") == "unknown" else data.get("mass"),
        name=data.get("name"),
        created=data.get("created"),
    )

    if check_and_update(people_obj, record):
        return True
    else:
        return False


for record in People.objects.all():
    try:
        response = rq.get(REQUEST_URI.format(record.name)).json()
    except Exception as e:
        print("Exception while making external call: {}".format(e))
    data = response["results"][0]
    result = compare(data, record)
    if not result:
        print("Error for record: {}".format(record.id))

print("Check And Updation Exited Successfully")
