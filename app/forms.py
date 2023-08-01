from django import forms
from .models import Auth0User


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
