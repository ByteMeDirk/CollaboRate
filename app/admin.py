from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import Auth0User

admin.site.register(Auth0User, UserAdmin)
