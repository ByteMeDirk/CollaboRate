from django.db import models
from django.contrib.auth.models import AbstractUser


class Auth0User(AbstractUser):
    """
    This class extends the default Django user model with an Auth0 ID field.
    """

    auth0_id = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True, default="static/avatars/default.png")
    avatar = models.ImageField(upload_to="static/avatars/", blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    # Custom fields similar to LinkedIn
    website = models.CharField(max_length=255, blank=True, null=True)
    additional_name = models.CharField(max_length=255, blank=True, null=True)
    education = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username
