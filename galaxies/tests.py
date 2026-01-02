from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Galaxy
from .serializers import GalaxySerializer
from .factories import GalaxyFactory


class GalaxySerializerTestCase(TestCase):
    """Test the Galaxy serializer"""

    def test_galaxy_serialization(self):
        """Test that Galaxy instances serialize correctly to JSON"""
        galaxy = GalaxyFactory(name="Andromeda")
        serializer = GalaxySerializer(galaxy)
        
        # Verify all fields are present
        self.assertIn('id', serializer.data)
        self.assertIn('name', serializer.data)
        
        # Verify all values are correct
        self.assertEqual(serializer.data['name'], "Andromeda") # type: ignore
        self.assertEqual(serializer.data['id'], galaxy.id) # type: ignore


class GalaxyAPITestCase(APITestCase):
    """Test the Galaxy API endpoints with authentication"""

    def setUp(self):
        """Set up test data and user"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.galaxy = GalaxyFactory(name="Milky Way")

    def test_list_galaxies_unauthenticated(self):
        """Test that unauthenticated users can list galaxies"""
        response = self.client.get('/api/galaxies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1) # type: ignore

    def test_create_galaxy_unauthenticated_fails(self):
        """Test that unauthenticated users cannot create galaxies"""
        data = {'name': 'Triangulum'}
        response = self.client.post('/api/galaxies/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_galaxy_authenticated_succeeds(self):
        """Test that authenticated users can create galaxies"""
        self.client.force_authenticate(user=self.user) # type: ignore
        data = {'name': 'Sombrero'}
        response = self.client.post('/api/galaxies/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Sombrero') # type: ignore
        
        self.assertTrue(Galaxy.objects.filter(name='Sombrero').exists())
