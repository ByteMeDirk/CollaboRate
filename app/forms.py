from django import forms
from taggit.forms import TagWidget
from tinymce.widgets import TinyMCE

from .models import Auth0User, Article, Comment
from .utils import MAIN_CATEGORIES


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
    description = forms.CharField(
        max_length=250,
        widget=forms.Textarea(attrs={"rows": 2}),
        required=True,
        help_text="A short description of the article. Max 250 characters.",
    )

    main_category = forms.CharField(
        max_length=50,
        widget=forms.Select(choices=MAIN_CATEGORIES),
        required=True,
    )
    body = forms.CharField(
        widget=TinyMCE(
            attrs={'required': False, 'cols': 30, 'rows': 10}
        )
    )

    class Meta:
        model = Article
        fields = ["title", "description", "body", "main_category", "subcategory", "tags"]
        widgets = {
            "tags": TagWidget(),
        }


class ArticleEditForm(forms.ModelForm):
    """
    This class represents a form for editing an article.
    """
    description = forms.CharField(
        max_length=250,
        widget=forms.Textarea(attrs={"rows": 2}),
        required=True,
        help_text="A short description of the article. Max 250 characters.",
    )

    main_category = forms.CharField(
        max_length=50,
        widget=forms.Select(choices=MAIN_CATEGORIES),
        required=True,
    )
    body = forms.CharField(
        widget=TinyMCE(
            attrs={'required': False, 'cols': 30, 'rows': 10}
        )
    )

    class Meta:
        model = Article
        fields = ["title", "description", "body", "main_category", "subcategory", "tags"]
        widgets = {
            "tags": TagWidget(),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
