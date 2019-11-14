from datetime import timedelta

from django.test import TestCase, Client
from django.shortcuts import reverse

from safesend.models import URL


class RetrieveSecretAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = URL.objects.create(url="http://test.com")

    def test_get_url_not_expired(self):
        response = self.client.post(reverse("retrieve-url", args=[self.url.uuid]))
        self.assertEqual(response.status_code, 200)

    def test_get_url_expired(self):
        self.url.created_at -= timedelta(hours=26)
        self.url.save()
        response = self.client.post(reverse("retrieve-url", args=[self.url.uuid]))
        self.assertEqual(response.status_code, 404)
