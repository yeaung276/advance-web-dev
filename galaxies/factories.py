import factory
from factory.django import DjangoModelFactory
from .models import Galaxy


class GalaxyFactory(DjangoModelFactory):
    class Meta: # type: ignore
        model = Galaxy

    name = factory.Sequence(lambda n: f"Galaxy-{n}") # type: ignore
