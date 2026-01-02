from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Source
from .serializers import SourceSerializer
from .factories import SourceFactory


class SourceSerializerTestCase(TestCase):
    """Test the Source serializer"""

    def test_source_serialization(self):
        """Test that Source instances serialize correctly to JSON"""
        source = SourceFactory(
            name="Astronomical Journal",
            url="https://example.com/paper",
            bibcode="2024ApJ...123..1A",
            doi="10.1000/test.123",
            secondary=True
        )
        serializer = SourceSerializer(source)
        
        # Verify all fields are present
        self.assertIn('id', serializer.data)
        self.assertIn('name', serializer.data)
        self.assertIn('url', serializer.data)
        self.assertIn('bibcode', serializer.data)
        self.assertIn('doi', serializer.data)
        self.assertIn('secondary', serializer.data)
        
        # Verify all values are correct
        self.assertEqual(serializer.data['name'], "Astronomical Journal") # type: ignore
        self.assertEqual(serializer.data['url'], "https://example.com/paper") # type: ignore
        self.assertEqual(serializer.data['bibcode'], "2024ApJ...123..1A") # type: ignore
        self.assertEqual(serializer.data['doi'], "10.1000/test.123") # type: ignore
        self.assertEqual(serializer.data['secondary'], True) # type: ignore
        self.assertEqual(serializer.data['id'], source.id) # type: ignore


class SourceAPITestCase(APITestCase):
    """Test the Source API endpoints with authentication"""

    def setUp(self):
        """Set up test data and user"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.source = SourceFactory(name="Nature Astronomy")

    def test_list_sources_unauthenticated(self):
        """Test that unauthenticated users can list sources"""
        response = self.client.get('/api/sources/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1) # type: ignore

    def test_create_source_unauthenticated_fails(self):
        """Test that unauthenticated users cannot create sources"""
        data = {
            'name': 'Science Magazine',
            'url': 'https://example.com',
            'secondary': False
        }
        response = self.client.post('/api/sources/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_source_authenticated_succeeds(self):
        """Test that authenticated users can create sources"""
        self.client.force_authenticate(user=self.user) # type: ignore
        data = {
            'name': 'The Astrophysical Journal',
            'url': 'https://iopscience.iop.org',
            'bibcode': '2025ApJ...999..1B',
            'doi': '10.3847/1538-4357/test',
            'secondary': False
        }
        response = self.client.post('/api/sources/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'The Astrophysical Journal') # type: ignore
        self.assertEqual(response.data['bibcode'], '2025ApJ...999..1B') # type: ignore
        
        self.assertTrue(Source.objects.filter(name='The Astrophysical Journal').exists())
