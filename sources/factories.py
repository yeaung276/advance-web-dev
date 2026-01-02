import factory
from factory.django import DjangoModelFactory
from .models import Source


class SourceFactory(DjangoModelFactory):
    class Meta: # type: ignore
        model = Source

    name = factory.Sequence(lambda n: f"Source-{n}") # type: ignore
    url = factory.Faker("url") # type: ignore
    bibcode = factory.Sequence(lambda n: f"2024ApJ...{n:03d}..1A") # type: ignore
    doi = factory.Sequence(lambda n: f"10.1000/test.{n}") # type: ignore
    secondary = False
