import factory
from factory.django import DjangoModelFactory
from .models import SubType


class SubTypeFactory(DjangoModelFactory):
    class Meta: # type: ignore
        model = SubType

    name = factory.Sequence(lambda n: f"Type-{n}") # type: ignore
