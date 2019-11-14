from django.db import models

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    user_agent = models.TextField()

    def __str__(self):
        return self.username
