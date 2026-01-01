from django import forms
from django.forms import inlineformset_factory
from events.models import Event, Attribute, ClaimedType, HostGalaxy


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["name"]


AttributeFormSet = inlineformset_factory(
    Event,
    Attribute,
    fields=["name", "source", "value", "unit"],
    extra=1,
    can_delete=False,
)

ClaimedTypeFormSet = inlineformset_factory(
    Event,
    ClaimedType,
    fields=["sub_type", "source"],
    extra=1,
    can_delete=False,
)

HostGalaxyFormSet = inlineformset_factory(
    Event,
    HostGalaxy,
    fields=["galaxy", "source"],
    extra=1,
    can_delete=False,
)
