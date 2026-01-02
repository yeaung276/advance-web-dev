from django.test import TestCase, Client
from django.urls import reverse

from events.factories import EventFactory, ClaimedTypeFactory, HostGalaxyFactory, AttributeFactory
from events.models import Event, AttributeName
from sources.factories import SourceFactory
from subtypes.factories import SubTypeFactory
from galaxies.factories import GalaxyFactory


class EventSearchViewTest(TestCase):
    """Test event search functionality"""

    def setUp(self):
        self.client = Client()
        self.url = reverse("frontend:search_event")

    def test_search_existing_event_returns_json(self):
        """
        Test that searching for an existing event returns the event data as JSON
        """
        # Create event with full data
        source = SourceFactory(name="Test Source")
        subtype = SubTypeFactory(name="Ia")
        galaxy = GalaxyFactory(name="NGC 1234")
        
        event = EventFactory(name="SN2024TEST")
        ClaimedTypeFactory(event=event, sub_type=subtype, source=source)
        HostGalaxyFactory(event=event, galaxy=galaxy, source=source)
        AttributeFactory(
            event=event,
            name=AttributeName.REDSHIFT,
            value=0.05,
            unit="",
            source=source,
        )

        response = self.client.get(self.url, {"name": "SN2024TEST"})

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["error"])
        self.assertIsNotNone(response.context["event_json"])
        
        # Verify event data structure
        event_json = response.context["event_json"]
        self.assertIn("SN2024TEST", event_json)
        self.assertEqual(event_json["SN2024TEST"]["name"], "SN2024TEST")
        self.assertIn("claimedtype", event_json["SN2024TEST"])
        self.assertIn("hostgalaxy", event_json["SN2024TEST"])

    def test_search_nonexistent_event_returns_error(self):
        """
        Test that searching for a non-existent event returns an error message
        """
        response = self.client.get(self.url, {"name": "NONEXISTENT"})

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["event_json"])
        self.assertIsNotNone(response.context["error"])
        self.assertIn("NONEXISTENT", response.context["error"])
        self.assertIn("not found", response.context["error"])


class EventCreationViewTest(TestCase):
    """Test event creation view with formsets"""

    def setUp(self):
        self.client = Client()
        self.url = reverse("frontend:create_event")

    def test_get_creates_empty_forms(self):
        """
        Test that GET request initializes all forms and formsets properly
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        
        # Verify all forms are in context
        self.assertIn("event_form", response.context)
        self.assertIn("attr_formset", response.context)
        self.assertIn("claimed_type_formset", response.context)
        self.assertIn("host_galaxy_formset", response.context)
        
        # Verify forms are not bound
        self.assertFalse(response.context["event_form"].is_bound)
        self.assertFalse(response.context["attr_formset"].is_bound)
