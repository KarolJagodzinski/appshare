import os
import uuid
from datetime import timedelta
from django.utils import timezone

from django.db import models
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from accounts.models import User


class SharableBase(models.Model):
    password = models.CharField(max_length=255)
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    visit_counter = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete="cascade", null=True)

    class Meta:
        abstract = True

    @property
    def is_expired(self):
        """
        Entry is invalid when 24 hours have passed since creation.
        """
        return timezone.now() > self.created_at + timedelta(hours=24)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def save(self, hash_password=True, **kwargs):
        if self.password and hash_password:
            self.password = make_password(self.password, settings.HASH_SALT)

        super().save(**kwargs)


class File(SharableBase):
    file = models.FileField(upload_to=settings.UPLOAD_FILES_DIR)

    @property
    def type(self):
        return "f"

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    def __repr__(self):
        return f"<File: {self.file.name }>"

    def __str__(self):
        return f"<File: uuid={self.uuid }>"


class URL(SharableBase):
    url = models.URLField()

    @property
    def type(self):
        return "u"

    def __repr__(self):
        return f"<URL: {self.url}>"

    def __str__(self):
        return self.url
