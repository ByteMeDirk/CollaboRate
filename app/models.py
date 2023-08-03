from django.contrib.auth.models import AbstractUser
from django.db import models
from taggit.managers import TaggableManager
from tinymce.models import HTMLField

from .utils import MAIN_CATEGORIES


class Auth0User(AbstractUser):
    """
    This class extends the default Django user model with an Auth0 ID field.
    """
    auth0_id = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="static/avatars/", blank=True, null=True, default="static/avatars/default.png")
    location = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    # Custom fields similar to LinkedIn
    website = models.CharField(max_length=255, blank=True, null=True)
    additional_name = models.CharField(max_length=255, blank=True, null=True)
    education = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username


class Article(models.Model):
    """
    This class represents an article.
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    author = models.ForeignKey(Auth0User, on_delete=models.CASCADE)
    body = HTMLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    main_category = models.CharField(
        max_length=50, choices=MAIN_CATEGORIES, default="Uncategorized"
    )
    subcategory = models.CharField(max_length=50, default="Uncategorized")
    tags = TaggableManager()
    published = models.BooleanField(default=False)
    comments = models.ManyToManyField(Auth0User, through="Comment", related_name="comments")


class Comment(models.Model):
    """
    This class represents a comment.
    """
    content = HTMLField(blank=True, null=True)
    author = models.ForeignKey(Auth0User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
