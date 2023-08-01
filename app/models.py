from django.db import models
from django.contrib.auth.models import AbstractUser


class Auth0User(AbstractUser):
    """
    This class extends the default Django user model with an Auth0 ID field.
    """

    auth0_id = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    link1 = models.URLField(blank=True, null=True)
    link2 = models.URLField(blank=True, null=True)
    link3 = models.URLField(blank=True, null=True)
    link4 = models.URLField(blank=True, null=True)
    link5 = models.URLField(blank=True, null=True)


class UserFollowing(models.Model):
    """
    This class represents a user following relationship. It is a many-to-many
    relationship between two user profiles.
    """

    user = models.ForeignKey(
        Auth0User, on_delete=models.CASCADE, related_name="following"
    )
    followed_user = models.ForeignKey(
        Auth0User, on_delete=models.CASCADE, related_name="followed_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "followed_user"], name="unique_following"
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} follows {self.followed_user}"


class UserPost(models.Model):
    """
    This class represents a user post, which is a many-to-one relationship
    with the user profile.
    """

    user = models.ForeignKey(Auth0User, on_delete=models.CASCADE, related_name="posts")
    text = models.TextField()
    image = models.ImageField(upload_to="posts/", blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(Auth0User, related_name="post_likes", blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} at {self.created_at}"


class UserComment(models.Model):
    """
    This class represents a user comment, which is a many-to-many relationship
    between two user profiles.
    """

    user = models.ForeignKey(
        Auth0User, on_delete=models.CASCADE, related_name="comments"
    )
    post = models.ForeignKey(
        UserPost, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(Auth0User, related_name="comment_likes", blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} at {self.created_at}"


class UserRating(models.Model):
    """
    This class represents a user rating, which is a many-to-many relationship
    between two user profiles.
    """

    user = models.ForeignKey(
        Auth0User, on_delete=models.CASCADE, related_name="ratings"
    )
    post = models.ForeignKey(UserPost, on_delete=models.CASCADE, related_name="ratings")
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(Auth0User, related_name="rating_likes", blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} at {self.created_at}"
