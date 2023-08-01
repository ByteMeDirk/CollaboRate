from django.urls import path, include

from .views import home, login, logout

urlpatterns = [
    path("", home, name="home"),
    path("login/", login, name="login"),
    path("logout", logout, name="logout"),
    path("", include("django.contrib.auth.urls")),
    path("", include("social_django.urls")),
]
