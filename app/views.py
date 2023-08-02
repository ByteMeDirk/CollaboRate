from urllib.parse import quote_plus

from auth0.authentication import GetToken, Users
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from taggit.models import Tag
from app.forms import EditProfileForm
from app.models import Auth0User
from django.contrib.auth import login, logout as auth_logout
from collabo_rate import settings
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Article, Comment, Rating
from .forms import ArticleCreateForm, CommentForm, RatingForm

from .utils import MAIN_CATEGORIES, SUBCATEGORIES


def home_view(request):
    return render(request, "app/home.html", {})


def login_view(request):
    domain = settings.SOCIAL_AUTH_AUTH0_DOMAIN
    client_id = settings.SOCIAL_AUTH_AUTH0_KEY
    redirect_uri = quote_plus(settings.SOCIAL_AUTH_AUTH0_CALLBACK_URL)
    return redirect(
        f"https://{domain}/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=openid%20profile%20email%20offline_access%20read:current_user%20update:current_user_metadata"
    )


@login_required
def logout_view(request):
    auth_logout(request)
    return redirect("/home/")


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
    token = get_token.authorization_code(code, settings.SOCIAL_AUTH_AUTH0_CALLBACK_URL)
    user_info = auth0_users.userinfo(token["access_token"])

    user, created = Auth0User.objects.get_or_create(auth0_id=user_info["sub"])
    if created:
        user.username = user_info["nickname"]
        user.email = user_info["email"]
        user.save()

    # Log the user in and redirect to the desired page
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return redirect("/home/")


# User Profile      ------------------------------------------------------------
@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return render(request, "app/user.html", {"form": form})
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, "app/user.html", {"form": form, "user": request.user})


# Articles          ------------------------------------------------------------
def list_articles_view(request):
    context = {"articles": Article.objects.all()}
    return render(request, "app/articles/article_list.html", context)


def list_articles_by_tag_view(request, tag):
    tag = get_object_or_404(Tag, slug=tag)
    articles = Article.objects.filter(tags=tag)
    return render(
        request, "app/articles/articles_tagged.html", {"tag": tag, "articles": articles}
    )


def create_article_view(request):
    form = ArticleCreateForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        # Set user as author and save
        article = form.save(commit=False)
        article.author = request.user
        if request.POST["set_published"] == "Publish":
            article.published = True
        article.save()
        form.save_m2m()  # Save tags
        return redirect("home")
    return render(
        request,
        "app/articles/article_create.html",
        {"form": form, "subcategories": SUBCATEGORIES},
    )


def get_article_subcategories_view(request):
    main_category = request.GET.get("option")
    subcategories = SUBCATEGORIES.get(main_category, [])
    options_html = ""
    for category in subcategories:
        options_html += f'<option value="{category[0]}">{category[1]}</option>'
    return HttpResponse(options_html)
