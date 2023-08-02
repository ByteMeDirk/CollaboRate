from django import forms
from taggit.forms import TagWidget

from .models import Auth0User, Article, Comment, Rating
from .utils import MAIN_CATEGORIES, SUBCATEGORIES
from ckeditor.fields import RichTextField
from taggit.managers import TagField


class EditProfileForm(forms.ModelForm):
    """
    This class represents a form for editing a user profile.
    """

    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=False
    )

    class Meta:
        model = Auth0User
        fields = [
            "bio",
            "avatar",
            "location",
            "first_name",
            "last_name",
            "additional_name",
            "date_of_birth",
            "website",
            "education",
            "industry",
        ]


class ArticleCreateForm(forms.ModelForm):
    """
    This class represents a form for creating an article.
    """

    main_category = forms.CharField(
        max_length=50,
        widget=forms.Select(choices=MAIN_CATEGORIES),
        required=True,
    )
    body = RichTextField(blank=True, null=True)

    class Meta:
        model = Article
        fields = ["title", "body", "main_category", "subcategory", "tags"]
        widgets = {
            "tags": TagWidget(),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["value"]
