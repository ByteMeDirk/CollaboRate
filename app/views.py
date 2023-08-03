from urllib.parse import quote_plus

from auth0.authentication import GetToken, Users
from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from taggit.models import Tag

from app.forms import EditProfileForm
from app.models import Auth0User
from collabo_rate import settings
from .forms import ArticleCreateForm
from .models import Article
from .utils import SUBCATEGORIES


def home_view(request):
    # get top 10 tags in order of popularity in taggit form articles where published is true
    articles = Article.objects.filter(published=True)
    tag_ids = articles.values_list('tags', flat=True)
    trending_tags = Tag.objects.filter(id__in=tag_ids).annotate(num_times=Count('taggit_taggeditem_items')).order_by(
        '-num_times')[:10]
    # get top 5 latest articles where published is true
    articles = Article.objects.filter(published=True).order_by("-created_at")[:5]
    return render(request, "app/home.html", {"trending_tags": trending_tags, "articles": articles})


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


@login_required
def view_user_profile_view(request, user_id):
    # if user is current user, redirect to edit profile
    if int(request.user.id) == int(user_id):
        return redirect("profile")
    author = get_object_or_404(Auth0User, id=user_id)
    articles = Article.objects.filter(author=author, published=True).order_by("-created_at")
    return render(request, "app/view_user.html", {"author": author, "articles": articles})


# Articles          ------------------------------------------------------------
def list_articles_view(request):
    articles = Article.objects.filter(published=True)

    # Create a dictionary to group the articles by category
    articles_by_category = {}
    for article in articles:
        category = article.main_category
        if category not in articles_by_category:
            articles_by_category[category] = []
        articles_by_category[category].append(article)

    return render(request, "app/articles/article_list.html",
                  {"title": "Explore Articles", "articles_by_category": articles_by_category})


def list_my_articles_view(request):
    articles = Article.objects.filter(author=request.user).order_by("-created_at")
    # Create a dictionary to group the articles by category
    articles_by_category = {}
    for article in articles:
        category = article.main_category
        if category not in articles_by_category:
            articles_by_category[category] = []
        articles_by_category[category].append(article)
    return render(request, "app/articles/article_list.html",
                  {"title": "Explore My Articles", "articles_by_category": articles_by_category})


def list_my_drafted_articles_view(request):
    articles = Article.objects.filter(author=request.user, published=False).order_by("-created_at")
    # Create a dictionary to group the articles by category
    articles_by_category = {}
    for article in articles:
        category = article.main_category
        if category not in articles_by_category:
            articles_by_category[category] = []
        articles_by_category[category].append(article)
    return render(request, "app/articles/article_list.html",
                  {"title": "Explore My Drafted Articles", "articles_by_category": articles_by_category})


def list_articles_by_tag_view(request, tag):
    tag = get_object_or_404(Tag, slug=tag)
    articles = Article.objects.filter(tags=tag, published=True).order_by("-created_at")
    return render(
        request, "app/articles/articles_tagged.html",
        {"title": "Explore Articles By Tag", "tag": tag, "articles": articles}
    )


def list_articles_by_search_view(request):
    query = request.GET.get("q")
    articles = Article.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query) | Q(tags__name__in=[query]) & Q(published=True)
    ).distinct()
    return render(
        request, "app/articles/articles_searched.html", {"query": query, "articles": articles}
    )


@login_required
def create_article_view(request):
    form = ArticleCreateForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        # Set user as author and save
        article = form.save(commit=False)
        article.author = request.user
        if request.POST["set_published"] == "Publish":
            article.published = True
        elif request.POST["set_published"] == "Draft":
            article.published = False
        article.save()
        form.save_m2m()  # Save tags
        return redirect("home")
    return render(
        request,
        "app/articles/article_create.html",
        {"form": form, "subcategories": SUBCATEGORIES},
    )


def edit_article_view(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.user != article.author:
        return redirect("home")
    form = ArticleCreateForm(request.POST or None, request.FILES or None, instance=article)
    if form.is_valid():
        # Set user as author and save
        article = form.save(commit=False)
        article.author = request.user
        if request.POST["set_published"] == "Publish":
            article.published = True
        elif request.POST["set_published"] == "Draft":
            article.published = False
        article.save()
        form.save_m2m()  # Save tags
        return redirect("home")
    return render(
        request,
        "app/articles/article_create.html",
        {"form": form, "subcategories": SUBCATEGORIES},
    )


def detail_article_view(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    return render(request, "app/articles/article_detail.html", {"article": article})


@login_required
def get_article_subcategories_view(request):
    main_category = request.GET.get("option")
    subcategories = SUBCATEGORIES.get(main_category, [])
    options_html = ""
    for category in subcategories:
        options_html += f'<option value="{category[0]}">{category[1]}</option>'
    return HttpResponse(options_html)
