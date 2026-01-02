from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import SubType
from .serializers import SubTypeSerializer
from .factories import SubTypeFactory


class SubTypeSerializerTestCase(TestCase):
    """Test the SubType serializer"""

    def test_subtype_serialization(self):
        """Test that SubType instances serialize correctly to JSON"""
        subtype = SubTypeFactory(name="Ia")
        serializer = SubTypeSerializer(subtype)
        
        # Verify all fields are present
        self.assertIn('id', serializer.data)
        self.assertIn('name', serializer.data)
        
        # Verify all values are correct
        self.assertEqual(serializer.data['name'], "Ia") # type: ignore
        self.assertEqual(serializer.data['id'], subtype.id) # type: ignore


class SubTypeAPITestCase(APITestCase):
    """Test the SubType API endpoints with authentication"""

    def setUp(self):
        """Set up test data and user"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.subtype = SubTypeFactory(name="Ib")

    def test_list_subtypes_unauthenticated(self):
        """Test that unauthenticated users can list subtypes"""
        response = self.client.get('/api/subtypes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1) # type: ignore

    def test_create_subtype_unauthenticated_fails(self):
        """Test that unauthenticated users cannot create subtypes"""
        data = {'name': 'Ic'}
        response = self.client.post('/api/subtypes/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_subtype_authenticated_succeeds(self):
        """Test that authenticated users can create subtypes"""
        self.client.force_authenticate(user=self.user) # type: ignore
        data = {'name': 'IIb'}
        response = self.client.post('/api/subtypes/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'IIb') # type: ignore
        
        self.assertTrue(SubType.objects.filter(name='IIb').exists())
