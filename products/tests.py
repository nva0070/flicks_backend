# products/tests.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import Shop, Product

User = get_user_model()

class APIEndpointTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create test shop
        self.shop = Shop.objects.create(
            name='Test Shop',
            description='A test shop',
            address='123 Test St',
            phone='1234567890',
            email='shop@example.com',
            owner=self.user
        )
        
        # Set up API client
        self.client = APIClient()
    
    def test_login(self):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('access' in response.data)
        
        # Save token for authenticated requests
        self.token = response.data['access']
    
    def test_store_info(self):
        self.test_login()  # Get token first
        url = reverse('store-info')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)