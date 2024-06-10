from django.urls import path, re_path
from .views import HomeView, ArticleDetailView, AddPostView, UpdatePostView, DeletePostView, AddCategoryView, CategoryView, CategoryListView, LikeView, AddCommentView, SearchArticles
from ckeditor_uploader import views as ckeditor_views
from .ckeditor_custom_uploader import custom_upload

urlpatterns = [
    # path('', views.home, name="home"),
    path('', HomeView.as_view(), name="home"),
    path('article/<slug:slug>', ArticleDetailView.as_view(), name='article-detail'),
    path('add_post/', AddPostView.as_view(), name='add_post'),
    path('add_category/', AddCategoryView.as_view(), name='add_category'),
    path('article/edit/<int:pk>', UpdatePostView.as_view(), name='update_post'),
    path('article/<int:pk>/remove', DeletePostView.as_view(), name='delete_post'),
    path('category/<str:cats>/', CategoryView.as_view(), name='category'),
    path('category-list/', CategoryListView, name='category-list'),
    path('like/<slug:slug>', LikeView, name='like_post'),
    path('article/<int:pk>/comment/', AddCommentView.as_view(), name='add_comment'),
    path('search_articles/', SearchArticles, name='search-articles'),
    path('ckeditor/upload/', custom_upload, name='ckeditor_upload'),
    re_path(r'^ckeditor/browse/', ckeditor_views.browse, name='ckeditor_browse'),
]