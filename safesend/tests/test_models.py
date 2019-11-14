from django.test import TestCase
from datetime import timedelta

from django.utils import timezone
from safesend.models import URL


class SharableBaseTestCase(TestCase):
    def test_is_expired(self):
        self.url_model = URL.objects.create(url="http://www.wp.pl")
        self.assertFalse(self.url_model.is_expired)

        self.url_model.created_at = timezone.now() - timedelta(hours=24)
        self.assertTrue(self.url_model.is_expired)

        self.url_model.created_at = timezone.now() - timedelta(hours=24)
        self.assertTrue(self.url_model.is_expired)
