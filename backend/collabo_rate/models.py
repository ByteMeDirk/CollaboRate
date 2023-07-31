from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractUser
from django.db import models


class Site(models.Model):
    """
    Site model for storing site information such as name, description, and logo.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to='site/logo/', blank=True)

    class Meta:
        verbose_name = 'site'
        verbose_name_plural = 'sites'

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    User model for storing user information such as avatar, bio, location, and website.
    """
    avatar = models.ImageField(upload_to='user/avatar/%Y/%m/%d', blank=True, default="users/avatars/default.jpg")
    bio = models.TextField(blank=True, max_length=500)
    location = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True, max_length=200)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.username


class Category(models.Model):
    """
    Category model for storing category information such as name, slug, and description.
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    description = models.TextField()

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Tag model for storing tag information such as name, slug, and description.
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    description = models.TextField()

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'

    def __str__(self):
        return self.name


class Post(models.Model):
    """
    Post model for storing post information such as title, slug, content, featured image, and published status.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    content = RichTextField()
    featured_image = models.ImageField(
        upload_to='posts/featured_images/%Y/%m/%d/')
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateField(auto_now=True)

    # Each post can receive likes from multiple users, and each user can like multiple posts
    likes = models.ManyToManyField(User, related_name='post_like')

    # Each post belong to one user and one category.
    # Each post has many tags, and each tag has many posts.
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True)
    tag = models.ManyToManyField(Tag)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'post'
        verbose_name_plural = 'posts'

    def __str__(self):
        return self.title

    def get_number_of_likes(self):
        return self.likes.count()


class Comment(models.Model):
    """
    Comment model for storing comment information such as content, created date, and approved status.
    """
    content = models.TextField(max_length=1000)
    created_at = models.DateField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    # Each comment can receive likes from multiple users, and each user can like multiple comments
    likes = models.ManyToManyField(User, related_name='comment_like')

    # Each comment belongs to one user and one post
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'comment'
        verbose_name_plural = 'comments'

    def __str__(self):
        if len(self.content) > 50:
            comment = self.content[:50] + '...'
        else:
            comment = self.content
        return comment

    def get_number_of_likes(self):
        return self.likes.count()
