from django.urls import path, include

from .views import home_view, login_view, logout_view, auth0_callback

urlpatterns = [
    path("", home_view, name="home"),
    path("callback/", auth0_callback, name="auth0_callback"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("", include("django.contrib.auth.urls")),
    path("social/", include("social_django.urls")),
]
