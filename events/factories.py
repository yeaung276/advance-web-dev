import factory
from factory.django import DjangoModelFactory
from .models import Event, ClaimedType, HostGalaxy, Attribute, AttributeName
from sources.factories import SourceFactory
from subtypes.factories import SubTypeFactory
from galaxies.factories import GalaxyFactory


class EventFactory(DjangoModelFactory):
    class Meta:  # type: ignore
        model = Event

    name = factory.Sequence(lambda n: f"SN{2024 + n // 1000}A{n % 1000:03d}")  # type: ignore


class ClaimedTypeFactory(DjangoModelFactory):
    class Meta:  # type: ignore
        model = ClaimedType

    event = factory.SubFactory(EventFactory)  # type: ignore
    sub_type = factory.SubFactory(SubTypeFactory)  # type: ignore
    source = factory.SubFactory(SourceFactory)  # type: ignore


class HostGalaxyFactory(DjangoModelFactory):
    class Meta:  # type: ignore
        model = HostGalaxy

    event = factory.SubFactory(EventFactory)  # type: ignore
    galaxy = factory.SubFactory(GalaxyFactory)  # type: ignore
    source = factory.SubFactory(SourceFactory)  # type: ignore


class AttributeFactory(DjangoModelFactory):
    class Meta:  # type: ignore
        model = Attribute

    event = factory.SubFactory(EventFactory)  # type: ignore
    name = factory.Iterator([choice[0] for choice in AttributeName.choices])  # type: ignore
    source = factory.SubFactory(SourceFactory)  # type: ignore
    value = factory.Faker("pyfloat", positive=True, max_value=1000)  # type: ignore
    unit = factory.Iterator(["km/s", "Mpc", "", "mag"])  # type: ignore
