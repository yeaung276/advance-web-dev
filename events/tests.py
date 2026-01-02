from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from .models import Event, AttributeName
from .factories import (
    EventFactory,
    ClaimedTypeFactory,
    HostGalaxyFactory,
    AttributeFactory,
)
from sources.factories import SourceFactory
from subtypes.factories import SubTypeFactory
from galaxies.factories import GalaxyFactory


class EventAPITest(APITestCase):
    """Test Event API endpoints with OSC schema serializer"""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_event_osc_schema(self):
        """
        Verify OSC schema serialization with source aliasing and entity merging.
        """
        # Create sources
        source1 = SourceFactory(name="Source One")
        source2 = SourceFactory(name="Source Two")
        source3 = SourceFactory(name="Source Three")

        # Create event
        event = EventFactory(name="SN2024test")

        # Create claimed types
        subtype1 = SubTypeFactory(name="Type Ia")
        subtype2 = SubTypeFactory(name="Type Ib")
        ClaimedTypeFactory(event=event, sub_type=subtype1, source=source1)
        ClaimedTypeFactory(event=event, sub_type=subtype2, source=source2)

        # Create host galaxies
        galaxy1 = GalaxyFactory(name="NGC 1234")
        galaxy2 = GalaxyFactory(name="NGC 5678")
        HostGalaxyFactory(event=event, galaxy=galaxy1, source=source1)
        HostGalaxyFactory(event=event, galaxy=galaxy2, source=source3)

        # Create attributes
        AttributeFactory(
            event=event,
            name=AttributeName.REDSHIFT,
            value=0.05,
            unit="",
            source=source1,
        )
        AttributeFactory(
            event=event,
            name=AttributeName.REDSHIFT,
            value=0.05,  # should merge
            unit="",
            source=source2,
        )
        AttributeFactory(
            event=event,
            name=AttributeName.VELOCITY,
            value=15000.0,
            unit="km/s",
            source=source3,
        )
        AttributeFactory(
            event=event,
            name=AttributeName.LUMDIST,
            value=200.0,
            unit="Mpc",
            source=source1,
        )

        response = self.client.get(f"/api/events/{event.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify OSC schema structure
        data = response.data  # type: ignore
        event_data = data[event.name]

        self.assertIn(event.name, data)
        self.assertIn("schema", event_data)
        self.assertIn("name", event_data)
        self.assertEqual(event_data["name"], "SN2024test")

        # Verify sources array and its structure
        self.assertIn("sources", event_data)
        sources = event_data["sources"]
        self.assertGreater(len(sources), 0)

        for source in sources:
            self.assertIn("id", source)
            self.assertIn("name", source)
            self.assertIn("alias", source)
            self.assertIn("url", source)
            self.assertIn("doi", source)
            self.assertIn("secondary", source)

        # Verify source aliases start from "2" (OSC convention)
        aliases = [s["alias"] for s in sources]
        self.assertIn("2", aliases)

        # Verify claimed types
        self.assertIn("claimedtype", event_data)
        claimed_types = event_data["claimedtype"]
        self.assertEqual(len(claimed_types), 2)
        for ct in claimed_types:
            self.assertIn("source", ct)
            self.assertIn("name", ct)
            self.assertTrue(ct["source"].replace(",", "").isdigit())

        # Verify host galaxies
        self.assertIn("hostgalaxy", event_data)
        host_galaxies = event_data["hostgalaxy"]
        self.assertEqual(len(host_galaxies), 2)
        for hg in host_galaxies:
            self.assertIn("source", hg)
            self.assertIn("name", hg)

        # Verify attributes
        self.assertIn("redshift", event_data)
        self.assertIn("velocity", event_data)
        self.assertIn("lumdist", event_data)

        # Verify entity merging
        # Two redshift values should be merged into single entry with comma-separated source aliases
        redshift_entries = event_data["redshift"]
        self.assertEqual(len(redshift_entries), 1)
        redshift_entry = redshift_entries[0]
        self.assertIn(",", redshift_entry["source"])

        # Velocity should not merged
        velocity_entries = event_data["velocity"]
        self.assertEqual(len(velocity_entries), 1)
        self.assertNotIn(",", velocity_entries[0]["source"])

    def test_list_events_with_pagination(self):
        """
        Test list endpoint with pagination
        """
        # Create 15 events
        events = [EventFactory() for _ in range(15)]

        # Request first page with page_size=10
        response = self.client.get("/api/events/?page=1&page_size=10")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify pagination
        self.assertIn("count", response.data)  # type: ignore
        self.assertIn("next", response.data)  # type: ignore
        self.assertIn("previous", response.data)  # type: ignore
        self.assertIn("results", response.data)  # type: ignore

        self.assertEqual(response.data["count"], 15)  # type: ignore
        self.assertIsNotNone(response.data["next"])  # type: ignore
        self.assertIsNone(response.data["previous"])  # type: ignore

        results = response.data["results"]  # type: ignore
        self.assertEqual(len(results), 10)

        # Verify event's fields
        for event_data in results:
            self.assertIn("id", event_data)
            self.assertIn("name", event_data)
            self.assertEqual(len(event_data.keys()), 2)

        # Verify second page
        response_page2 = self.client.get("/api/events/?page=2&page_size=10")
        self.assertEqual(response_page2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_page2.data["results"]), 5)  # type: ignore
        self.assertIsNone(response_page2.data["next"])  # type: ignore


class SupernovaUncertaintyAPITest(APITestCase):
    """Test supernova uncertainty endpoint"""

    def setUp(self):
        self.client = APIClient()

    def test_source_aggregation(self):
        """
        Verify correct counting of distinct sources across relationships.
        """
        # Create sources
        s1 = SourceFactory(name="Source 1")
        s2 = SourceFactory(name="Source 2")
        s3 = SourceFactory(name="Source 3")
        s4 = SourceFactory(name="Source 4")

        # Create subtypes
        type_ia = SubTypeFactory(name="Ia")
        type_ib = SubTypeFactory(name="Ib")

        # Create galaxies
        galaxy1 = GalaxyFactory(name="NGC 1111")

        # Event 1: Multiple sources across claimed types and host galaxies
        event1 = EventFactory(name="SN2024X")
        ClaimedTypeFactory(event=event1, sub_type=type_ia, source=s1)
        ClaimedTypeFactory(event=event1, sub_type=type_ib, source=s2)
        ClaimedTypeFactory(event=event1, sub_type=type_ia, source=s3)
        HostGalaxyFactory(event=event1, galaxy=galaxy1, source=s2)
        HostGalaxyFactory(event=event1, galaxy=galaxy1, source=s4)

        # Event 2: Single source
        event2 = EventFactory(name="SN2024Y")
        ClaimedTypeFactory(event=event2, sub_type=type_ia, source=s1)
        HostGalaxyFactory(event=event2, galaxy=galaxy1, source=s1)

        response = self.client.get("/api/events/supernova-uncertainty")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Find our events in response
        event1_data = next((e for e in response.data if e["name"] == "SN2024X"), None)  # type: ignore
        event2_data = next((e for e in response.data if e["name"] == "SN2024Y"), None)  # type: ignore

        self.assertIsNotNone(event1_data)
        self.assertIsNotNone(event2_data)

        # Event 1 should have:
        # - subtype_sources: 3 distinct (s1, s2, s3)
        # - host_sources: 2 distinct (s2, s4)
        # - total_sources: 5 (3 + 2, s2 counted in both)
        self.assertEqual(event1_data["subtype_sources"], 3)  # type: ignore
        self.assertEqual(event1_data["host_sources"], 2)  # type: ignore
        self.assertEqual(event1_data["total_sources"], 5)  # type: ignore

        # Event 2 should have:
        # - subtype_sources: 1 distinct (s1)
        # - host_sources: 1 distinct (s1)
        # - total_sources: 2 (1 + 1, s1 counted in both)
        self.assertEqual(event2_data["subtype_sources"], 1)  # type: ignore
        self.assertEqual(event2_data["host_sources"], 1)  # type: ignore
        self.assertEqual(event2_data["total_sources"], 2)  # type: ignore


class SubtypeConflictAPITest(APITestCase):
    """Test subtype conflict detection endpoint"""

    def setUp(self):
        self.client = APIClient()

    def test_conflict_detection(self):
        """
        Verify correct identification of conflicting subtype classifications.
        """
        # Create sources
        source1 = SourceFactory(name="Source A")
        source2 = SourceFactory(name="Source B")
        source3 = SourceFactory(name="Source C")

        # Create subtypes
        type_ia = SubTypeFactory(name="Ia")
        type_ib = SubTypeFactory(name="Ib")
        type_ic = SubTypeFactory(name="Ic")
        type_ii = SubTypeFactory(name="II")

        # Event 1: Conflicted - 3 different subtypes
        event1 = EventFactory(name="SN2024A")
        ClaimedTypeFactory(event=event1, sub_type=type_ia, source=source1)
        ClaimedTypeFactory(event=event1, sub_type=type_ib, source=source2)
        ClaimedTypeFactory(event=event1, sub_type=type_ii, source=source3)

        # Event 2: Conflicted - 2 different subtypes
        event2 = EventFactory(name="SN2024B")
        ClaimedTypeFactory(event=event2, sub_type=type_ia, source=source1)
        ClaimedTypeFactory(event=event2, sub_type=type_ic, source=source2)

        # Event 3: No conflict - only 1 subtype
        event3 = EventFactory(name="SN2024C")
        ClaimedTypeFactory(event=event3, sub_type=type_ia, source=source1)
        ClaimedTypeFactory(event=event3, sub_type=type_ia, source=source2)

        # Event 4: No conflict - single claim
        event4 = EventFactory(name="SN2024D")
        ClaimedTypeFactory(event=event4, sub_type=type_ib, source=source1)

        response = self.client.get("/api/events/subtype-uncertainty")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        subtype_map = {item["sub_type__name"]: item["conflicted_event_count"] for item in response.data}  # type: ignore

        # Type Ia appears in 2 conflicted events (event1, event2)
        self.assertEqual(subtype_map.get("Ia"), 2)

        # Type Ib appears in 1 conflicted event (event1)
        self.assertEqual(subtype_map.get("Ib"), 1)

        # Type Ic appears in 1 conflicted event (event2)
        self.assertEqual(subtype_map.get("Ic"), 1)

        # Type II appears in 1 conflicted event (event1)
        self.assertEqual(subtype_map.get("II"), 1)

        # Verify event3 and event4 are NOT included
        all_conflicted_events = set()
        for item in response.data:  # type: ignore
            all_conflicted_events.add(item["conflicted_event_count"])
