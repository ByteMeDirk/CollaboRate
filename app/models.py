from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractUser
from django.db import models
from taggit.managers import TaggableManager

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

    # Rating matrix, users start with 15 and max is 30
    reputation = models.IntegerField(default=15, blank=True, null=True)

    # Custom fields similar to LinkedIn
    website = models.CharField(max_length=255, blank=True, null=True)
    additional_name = models.CharField(max_length=255, blank=True, null=True)
    education = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True, null=True)

    def calculate_reputation(self):
        ratings = self.rating_set.all()
        total = sum([rating.value for rating in ratings])
        count = len(ratings)
        return total / count if count > 0 else 0

    def calculate_authority(self):
        ratings = self.rating_set.all()
        total = sum([rating.value for rating in ratings])
        count = len(ratings)
        return total / count if count > 0 else 0

    def __str__(self):
        return self.username


class Article(models.Model):
    """
    This class represents an article.
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    author = models.ForeignKey(Auth0User, on_delete=models.CASCADE)
    body = RichTextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    raters = models.ManyToManyField(
        Auth0User, through="Rating", related_name="rated_articles"
    )

    main_category = models.CharField(
        max_length=50, choices=MAIN_CATEGORIES, default="IT"
    )
    subcategory = models.CharField(max_length=50, default="AI")
    tags = TaggableManager()
    published = models.BooleanField(default=False)

    def calculate_rating(self):
        ratings = self.rating_set.all()
        total = sum(
            [
                rating.value * rating.user.reputation * rating.user.authority
                for rating in ratings
            ]
        )
        count = sum(
            [rating.user.reputation * rating.user.authority for rating in ratings]
        )
        return total / count if count > 0 else 0


class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(Auth0User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    raters = models.ManyToManyField(
        Auth0User, through="Rating", related_name="rated_comments"
    )

    def calculate_rating(self):
        ratings = self.rating_set.all()
        total = sum(
            [
                rating.value * rating.user.reputation * rating.user.authority
                for rating in ratings
            ]
        )
        count = sum(
            [rating.user.reputation * rating.user.authority for rating in ratings]
        )
        return total / count if count > 0 else 0


class Rating(models.Model):
    user = models.ForeignKey(Auth0User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    value = models.IntegerField()
