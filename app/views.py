from django.contrib.auth import login
from django.shortcuts import render, redirect

from app.models import Auth0User
from django.contrib.auth import logout as auth_logout


def home(request):
    return render(request, "app/home.html", {})


def login(request):
    return render(request, "app/login.html", {})


def logout(request):
    auth_logout(request)
    return redirect("/")


def auth0_callback(request):
    # Here, you should handle the callback from Auth0 and get the user info
    # For demonstration, we assume you have the user_info

    user_info = {}  # Get user info from Auth0

    user, created = Auth0User.objects.get_or_create(auth0_id=user_info["sub"])
    if created:
        user.username = user_info["nickname"]
        user.email = user_info["email"]
        user.save()

    # Log the user in and redirect to the desired page
    login(request, user)
    return redirect("/")
