from django.urls import path, include

from .views import home_view, login_view, logout_view, auth0_callback

urlpatterns = [
    # Auth0 authentication
    path("callback/", auth0_callback, name="auth0_callback"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("social_auth/", include("social_django.urls")),
    # Local apps
    path("home/", home_view, name="home"),
]
