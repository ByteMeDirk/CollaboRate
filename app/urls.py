from django.urls import path, include

from .views import (
    home_view,
    login_view,
    logout_view,
    auth0_callback,
    edit_profile_view,
    view_user_profile_view,
    list_articles_view,
    create_article_view,
    get_article_subcategories_view,
    list_articles_by_tag_view,
    detail_article_view,
    list_articles_by_search_view,
    list_my_articles_view,
    edit_article_view,
    list_my_drafted_articles_view,
    delete_comment_view,
)

urlpatterns = [
    # Auth0 authentication ------------------------------------------------
    path("callback/", auth0_callback, name="auth0_callback"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("social_auth/", include("social_django.urls")),
    path("tinymce/", include("tinymce.urls")),
    # Local apps ----------------------------------------------------------
    path("home/", home_view, name="home"),
    path("user/profile/", edit_profile_view, name="profile"),
    path("user/<str:user_id>/", view_user_profile_view, name="view_user"),
    # articles  -----------------------------------------------------------
    path("articles/", list_articles_view, name="article_list"),
    path("articles/create/", create_article_view, name="article_create"),
    path(
        "articles/subcategories/",
        get_article_subcategories_view,
        name="article_subcategories",
    ),
    path("articles/tags/<str:tag>", list_articles_by_tag_view, name="article_tags"),
    path("articles/<int:article_id>/", detail_article_view, name="article_detail"),
    path("articles/search/", list_articles_by_search_view, name="article_search"),
    path("articles/my/", list_my_articles_view, name="article_my"),
    path(
        "articles/my/drafts/", list_my_drafted_articles_view, name="article_my_drafts"
    ),
    path("articles/<int:article_id>/edit/", edit_article_view, name="article_edit"),
    # comments  -----------------------------------------------------------
    path(
        "comments/<int:comment_id>/<int:article_id>/delete/",
        delete_comment_view,
        name="comment_delete",
    ),
]
