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
from app.models import Auth0User, Comment
from collabo_rate import settings
from .forms import ArticleCreateForm, CommentCreateForm
from .models import Article
from .utils import SUBCATEGORIES


def home_view(request):
    """
    Renders the home page with trending tags, latest articles, and recent authors.
    """
    # Get top 10 trending tags in order of popularity
    articles = Article.objects.filter(published=True)
    tag_ids = articles.values_list("tags", flat=True)
    trending_tags = (
        Tag.objects.filter(id__in=tag_ids)
        .annotate(num_times=Count("taggit_taggeditem_items"))
        .order_by("-num_times")[:10]
    )

    # Get top 5 latest articles
    articles = Article.objects.filter(published=True).order_by("-created_at")[:5]
    recent_authors = Auth0User.objects.all().order_by("-date_joined")[:5]

    return render(
        request,
        "app/home.html",
        {
            "trending_tags": trending_tags,
            "articles": articles,
            "recent_authors": recent_authors,
        },
    )


def login_view(request):
    """
    Redirects to the Auth0 login page for user authentication.
    """
    # Redirect to Auth0 login page
    domain = settings.SOCIAL_AUTH_AUTH0_DOMAIN
    client_id = settings.SOCIAL_AUTH_AUTH0_KEY
    redirect_uri = quote_plus(settings.SOCIAL_AUTH_AUTH0_CALLBACK_URL)
    return redirect(
        f"https://{domain}/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=openid%20profile%20email%20offline_access%20read:current_user%20update:current_user_metadata"
    )


@login_required(redirect_field_name="home")
def logout_view(request):
    """
    Logs out the user and redirects to the home page.
    """
    auth_logout(request)
    return redirect("/home/")


def auth0_callback(request):
    """
    Handles the Auth0 callback after successful authentication.
    """
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

    # Log the user in and redirect to the home page
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return redirect("/home/")


# User Profile      ------------------------------------------------------------
@login_required(redirect_field_name="home")
def edit_profile_view(request):
    """
    Renders the edit profile page with the user's current information.
    """
    # Update user profile
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return render(request, "app/user.html", {"form": form})
    else:
        form = EditProfileForm(instance=request.user)

    # Get the user's articles
    return render(request, "app/user.html", {"form": form, "user": request.user})


@login_required(redirect_field_name="home")
def view_user_profile_view(request, user_id):
    """
    Renders the user profile page with the user's information.
    """
    # Get the user's articles and comments
    if int(request.user.id) == int(user_id):
        # Redirect to the user's profile page if they are viewing their own profile
        return redirect("profile")

    # Get the user's articles and comments
    author = get_object_or_404(Auth0User, id=user_id)

    # Get the user's articles and comments
    articles = Article.objects.filter(author=author, published=True).order_by(
        "-created_at"
    )

    return render(
        request, "app/view_user.html", {"author": author, "articles": articles}
    )


# Articles          ------------------------------------------------------------
def list_articles_view(request):
    """
    Renders the article list page with all published articles.
    """
    articles = Article.objects.filter(published=True)

    # Create a dictionary to group the articles by category
    articles_by_category = {}
    for article in articles:
        category = article.main_category
        if category not in articles_by_category:
            articles_by_category[category] = []
        articles_by_category[category].append(article)

    # Get the user's articles and comments
    return render(
        request,
        "app/articles/article_list.html",
        {"title": "Explore Articles", "articles_by_category": articles_by_category},
    )


def list_my_articles_view(request):
    """
    Renders the article list page with the user's articles.
    """
    # Get the user's articles
    articles = Article.objects.filter(author=request.user).order_by("-created_at")

    # Create a dictionary to group the articles by category
    articles_by_category = {}
    for article in articles:
        category = article.main_category
        if category not in articles_by_category:
            articles_by_category[category] = []
        articles_by_category[category].append(article)

    return render(
        request,
        "app/articles/article_list.html",
        {"title": "Explore My Articles", "articles_by_category": articles_by_category},
    )


def list_my_drafted_articles_view(request):
    """
    Renders the article list page with the user's drafted articles.
    """
    # Get the user's articles
    articles = Article.objects.filter(author=request.user, published=False).order_by(
        "-created_at"
    )

    # Create a dictionary to group the articles by category
    articles_by_category = {}
    for article in articles:
        category = article.main_category
        if category not in articles_by_category:
            articles_by_category[category] = []
        articles_by_category[category].append(article)

    return render(
        request,
        "app/articles/article_list.html",
        {
            "title": "Explore My Drafted Articles",
            "articles_by_category": articles_by_category,
        },
    )


def list_articles_by_tag_view(request, tag):
    """
    Renders the article list page with articles that have the specified tag.
    """
    # Get the articles with the specified tag
    tag = get_object_or_404(Tag, slug=tag)
    articles = Article.objects.filter(tags=tag, published=True).order_by("-created_at")
    return render(
        request,
        "app/articles/articles_tagged.html",
        {"title": "Explore Articles By Tag", "tag": tag, "articles": articles},
    )


def list_articles_by_search_view(request):
    """
    Renders the article list page with articles that match the search query.
    """
    # Get the articles that match the search query
    query = request.GET.get("q")

    # Create a dictionary to group the articles by category
    articles = Article.objects.filter(
        Q(title__icontains=query)
        | Q(description__icontains=query)
        | Q(tags__name__in=[query]) & Q(published=True)
    ).distinct()

    return render(
        request,
        "app/articles/articles_searched.html",
        {"query": query, "articles": articles},
    )


@login_required(redirect_field_name="home")
def create_article_view(request):
    """
    Renders the article create page with the article creation form.
    """
    # Create a dictionary to group the subcategories by category
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


@login_required(redirect_field_name="home")
def edit_article_view(request, article_id):
    """
    Renders the article edit page with the article edit form.
    """
    article = get_object_or_404(Article, id=article_id)
    if request.user != article.author:
        return redirect("home")
    form = ArticleCreateForm(
        request.POST or None, request.FILES or None, instance=article
    )
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
    """
    Renders the article detail page with the article and its comments.
    """

    # Get the article and its comments
    article = get_object_or_404(Article, id=article_id)
    comments = Comment.objects.filter(article=article)

    if request.method == "POST":
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.save()
            return redirect("article_detail", article_id=article_id)
    else:
        form = CommentCreateForm()

    return render(
        request,
        "app/articles/article_detail.html",
        {"article": article, "comments": comments, "form": form},
    )


@login_required(redirect_field_name="home")
def get_article_subcategories_view(request):
    """
    Returns the subcategories for the specified main category.
    THis is used only during article creation and editing.
    """
    main_category = request.GET.get("option")
    subcategories = SUBCATEGORIES.get(main_category, [])
    options_html = ""
    for category in subcategories:
        options_html += f'<option value="{category[0]}">{category[1]}</option>'
    return HttpResponse(options_html)


# comments          ------------------------------------------------------------
@login_required(redirect_field_name="home")
def delete_comment_view(request, comment_id, article_id):
    """
    Deletes the specified comment.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect("home")
    comment.delete()
    return redirect("article_detail", article_id=article_id)
