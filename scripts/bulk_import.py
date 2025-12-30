import os
import sys
import json
from pathlib import Path
import django
from django.db import connection

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIRECTORY = BASE_DIR / "data"
BATCH_SIZE = 500

sys.path.append(BASE_DIR.as_posix())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supernovae.settings")

django.setup()
connection.ensure_connection()

# Data migration logic
# Cleanup everything
from galaxies.models import Galaxy
from subtypes.models import SubType
from sources.models import Source
from events.models import Event, Attribute, ClaimedType, HostGalaxy

Attribute.objects.all().delete()
ClaimedType.objects.all().delete()
HostGalaxy.objects.all().delete()
Event.objects.all().delete()

Galaxy.objects.all().delete()
SubType.objects.all().delete()
Source.objects.all().delete()


# Load all galaxies
with open(DATA_DIRECTORY / "galaxies.json", "r") as f:
    data = json.load(f)

galaxies = [Galaxy(name=row["name"]) for row in data]

Galaxy.objects.bulk_create(galaxies, batch_size=BATCH_SIZE)

# Load all subtypes
with open(DATA_DIRECTORY / "subtypes.json", "r") as f:
    data = json.load(f)

subtypes = [SubType(name=row["name"]) for row in data]

SubType.objects.bulk_create(subtypes, batch_size=BATCH_SIZE)

# Load all Sources
with open(DATA_DIRECTORY / "sources.json", "r") as f:
    data = json.load(f)

sources = [
    Source(
        name=row["name"],
        url=row.get("url"),
        bibcode=row.get("bibcode"),
        doi=row.get("doi"),
        secondary=row.get("secondary", False),
    )
    for row in data
]

Source.objects.bulk_create(sources, batch_size=BATCH_SIZE)

# Import all supernova events
# Read the data
with open(DATA_DIRECTORY / "supernova.json", "r") as f:
    data = json.load(f)

for row in data:
    # create source alias -> id map
    source_alias = {
        s["alias"]: Source.objects.get(name=s["name"], url=s["url"])
        for s in row["sources"]
    }

    # create event
    event = Event.objects.create(name=row["name"])

    # create attributes for each source
    attributes = []
    for attr in row["attributes"]:
        for s in attr["source"].split(","):
            attributes.append(
                Attribute(
                    name=attr["name"],
                    value=attr["value"],
                    unit=attr["unit"] or "",
                    source=source_alias[s],
                    event=event,
                )
            )
    Attribute.objects.bulk_create(attributes, batch_size=BATCH_SIZE)

    # create hostgalaxy
    host_galaxy = []
    for g in row["hostgalaxy"]:
        for s in g["source"].split(","):
            host_galaxy.append(
                HostGalaxy(
                    galaxy=Galaxy.objects.get(name=g["name"]),
                    source=source_alias[s],
                    event=event,
                )
            )
    HostGalaxy.objects.bulk_create(host_galaxy)

    # create type classification(claimedType)
    claimed_type = []
    for c in row["subtype"]:
        for s in c["source"].split(","):
            claimed_type.append(
                ClaimedType(
                    sub_type=SubType.objects.get(name=c["name"]),
                    source=source_alias[s],
                    event=event,
                )
            )
    ClaimedType.objects.bulk_create(claimed_type)
