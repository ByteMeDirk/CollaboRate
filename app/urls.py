from django.urls import path, include

from .views import home_view, login_view, logout_view

urlpatterns = [
    path("", home_view, name="home"),
    path("login/", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("", include("django.contrib.auth.urls")),
    path("", include("social_django.urls")),
]
