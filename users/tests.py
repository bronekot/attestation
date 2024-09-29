from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class JWTAuthTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass", is_active=True)

    def test_obtain_jwt_token(self):
        url = reverse("token_obtain_pair")
        data = {"username": "testuser", "password": "testpass"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_access_protected_route(self):
        url = reverse("token_obtain_pair")
        data = {"username": "testuser", "password": "testpass"}
        response = self.client.post(url, data)
        access_token = response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(reverse("supplier-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
