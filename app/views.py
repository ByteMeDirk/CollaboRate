from urllib.parse import quote_plus

from auth0.authentication import GetToken, Users
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from app.models import Auth0User
from django.contrib.auth import login, logout as auth_logout
from collabo_rate import settings


def home_view(request):
    return render(request, "app/home.html", {})


def login_view(request):
    domain = settings.SOCIAL_AUTH_AUTH0_DOMAIN
    client_id = settings.SOCIAL_AUTH_AUTH0_KEY
    redirect_uri = quote_plus(settings.SOCIAL_AUTH_AUTH0_CALLBACK_URL)
    return redirect(
        f"https://{domain}/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
    )


@login_required
def logout_view(request):
    auth_logout(request)
    domain = settings.SOCIAL_AUTH_AUTH0_DOMAIN
    client_id = settings.SOCIAL_AUTH_AUTH0_KEY
    return_to = "http://127.0.0.1:8000"  # this can be current domain
    return redirect(
        f"https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}"
    )


def auth0_callback(request):
    # Get the authorization code from the callback URL
    code = request.GET.get("code")

    # Exchange the authorization code for an access token and ID token
    get_token = GetToken(
        settings.SOCIAL_AUTH_AUTH0_DOMAIN,
        settings.SOCIAL_AUTH_AUTH0_KEY,
        settings.SOCIAL_AUTH_AUTH0_SECRET,
    )
    auth0_users = Users(settings.SOCIAL_AUTH_AUTH0_DOMAIN)
    token = get_token.authorization_code(code, "http://localhost:8000/auth0_callback")
    user_info = auth0_users.userinfo(token["access_token"])

    user, created = Auth0User.objects.get_or_create(auth0_id=user_info["sub"])
    if created:
        user.username = user_info["nickname"]
        user.email = user_info["email"]
        user.auth0_id = user_info["sub"]
        user.save()

    # Log the user in and redirect to the desired page
    login(request, user)
    return redirect("/")
